#!/usr/bin/env python3
"""
Blogger自動投稿システム 常時監視・待機システム
Mac mini 2014専用 - 継続的監視・自動復旧機能
"""

import os
import sys
import json
import time
import logging
import datetime
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

class BloggerSystemMonitor:
    def __init__(self):
        self.base_dir = Path("/home/fujinosuke/projects/blogger_auto_post_system")
        self.venv_path = self.base_dir / "blog_env"
        self.log_dir = self.base_dir / "monitoring" / "logs"
        self.config_dir = self.base_dir / "config"
        
        # ログディレクトリ作成
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ログ設定
        log_file = self.log_dir / f"blogger_monitor_{datetime.date.today().isoformat()}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_environment(self):
        """環境の確認"""
        try:
            # ベースディレクトリ
            if not self.base_dir.exists():
                self.logger.error(f"ベースディレクトリが見つかりません: {self.base_dir}")
                return False
            
            # 仮想環境
            activate_path = self.venv_path / "bin" / "activate"
            if not activate_path.exists():
                self.logger.error(f"仮想環境が見つかりません: {activate_path}")
                return False
            
            # 設定ディレクトリ
            if not self.config_dir.exists():
                self.logger.warning(f"設定ディレクトリが見つかりません: {self.config_dir}")
            
            self.logger.info("✅ 環境確認完了")
            return True
        except Exception as e:
            self.logger.error(f"環境確認エラー: {e}")
            return False
    
    def check_authentication(self):
        """認証状態の確認"""
        try:
            credentials_files = [
                self.config_dir / "credentials.json",
                self.base_dir / "google_api_complete_token.pkl",
                self.config_dir / "google_api_complete_token.pkl"
            ]
            
            auth_status = {}
            for cred_file in credentials_files:
                if cred_file.exists():
                    auth_status[cred_file.name] = "✅ 存在"
                    # ファイルサイズチェック
                    size = cred_file.stat().st_size
                    auth_status[f"{cred_file.name}_size"] = f"{size} bytes"
                else:
                    auth_status[cred_file.name] = "❌ 不存在"
            
            self.logger.info(f"📋 認証ファイル状況: {auth_status}")
            
            # 基本的な認証ファイルの存在確認
            has_credentials = any(cred_file.exists() for cred_file in credentials_files)
            return has_credentials
        except Exception as e:
            self.logger.error(f"認証確認エラー: {e}")
            return False
    
    async def test_blogger_system(self):
        """Bloggerシステムテスト"""
        try:
            test_script = self.base_dir / "test_blog_system.py"
            if not test_script.exists():
                self.logger.error(f"テストスクリプトが見つかりません: {test_script}")
                return False
            
            # 仮想環境での実行
            cmd = f"cd {self.base_dir} && {self.venv_path}/bin/python test_blog_system.py --dry-run 2>/dev/null"
            
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=40)
            
            if proc.returncode == 0:
                self.logger.info("✅ Bloggerシステムテスト: 成功")
                return True
            else:
                # エラー内容を分析
                error_msg = stderr.decode() if stderr else "不明なエラー"
                if "認証" in error_msg or "auth" in error_msg.lower():
                    self.logger.warning("⚠️ Bloggerシステムテスト: 認証エラー")
                    return "auth_error"
                else:
                    self.logger.error(f"❌ Bloggerシステムテスト: 失敗 - {error_msg[:200]}")
                    return False
        except asyncio.TimeoutError:
            self.logger.error("❌ Bloggerシステムテスト: タイムアウト")
            return False
        except Exception as e:
            self.logger.error(f"Bloggerシステムテストエラー: {e}")
            return False
    
    async def attempt_auth_repair(self):
        """認証修復試行"""
        self.logger.info("🔄 Blogger認証修復を試行...")
        
        try:
            # 認証修復スクリプト実行
            repair_scripts = [
                self.base_dir / "fix_auth.py",
                self.base_dir / "simple_auth.py",
                self.base_dir / "refresh_auth.py"
            ]
            
            for script in repair_scripts:
                if script.exists():
                    self.logger.info(f"🔧 認証修復スクリプト実行: {script.name}")
                    
                    cmd = f"cd {self.base_dir} && timeout 25s {self.venv_path}/bin/python {script.name}"
                    proc = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    try:
                        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
                        
                        if proc.returncode == 0:
                            self.logger.info(f"✅ 認証修復成功: {script.name}")
                            return True
                        else:
                            self.logger.warning(f"⚠️ 認証修復失敗: {script.name}")
                    except asyncio.TimeoutError:
                        self.logger.warning(f"⚠️ 認証修復タイムアウト: {script.name}")
                        proc.kill()
                        continue
            
            self.logger.error("❌ 全ての認証修復試行が失敗")
            return False
        except Exception as e:
            self.logger.error(f"認証修復試行エラー: {e}")
            return False
    
    def log_system_status(self):
        """システム状況記録"""
        try:
            # プロセス情報
            blog_processes = subprocess.run(
                "ps aux | grep -i blog | grep -v grep | wc -l", 
                shell=True, capture_output=True, text=True
            )
            
            # ディスク使用量
            disk_usage = subprocess.run(
                f"du -sh {self.base_dir} 2>/dev/null || echo '不明'", 
                shell=True, capture_output=True, text=True
            )
            
            self.logger.info(f"📊 システム状況 - Blog関連プロセス: {blog_processes.stdout.strip()}, ディスク使用: {disk_usage.stdout.strip()}")
        except Exception as e:
            self.logger.warning(f"システム状況取得エラー: {e}")
    
    async def run_monitoring_cycle(self):
        """監視サイクル実行"""
        start_time = datetime.datetime.now()
        self.logger.info(f"🚀 Blogger監視開始: {start_time}")
        
        # 環境チェック
        if not self.check_environment():
            self.logger.critical("💥 環境チェック失敗")
            return False
        
        # 認証チェック
        auth_ok = self.check_authentication()
        if not auth_ok:
            self.logger.warning("⚠️ 認証ファイル不足")
        
        # システムテスト
        system_status = await self.test_blogger_system()
        
        if system_status == "auth_error":
            self.logger.warning("⚠️ 認証エラー検出 - 修復を試行")
            repair_success = await self.attempt_auth_repair()
            if repair_success:
                # 再テスト
                system_status = await self.test_blogger_system()
        
        # システム状況記録
        self.log_system_status()
        
        # 結果サマリ
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if system_status is True:
            self.logger.info(f"✅ 監視サイクル完了: {duration:.1f}秒 - システム正常")
            return True
        elif system_status == "auth_error":
            self.logger.warning(f"⚠️ 監視サイクル完了: {duration:.1f}秒 - 認証要修復")
            return "auth_error"
        else:
            self.logger.error(f"❌ 監視サイクル完了: {duration:.1f}秒 - システム異常")
            return False

def main():
    """メイン実行"""
    monitor = BloggerSystemMonitor()
    
    # 単発実行
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        success = asyncio.run(monitor.run_monitoring_cycle())
        if success is True:
            sys.exit(0)
        elif success == "auth_error":
            sys.exit(2)
        else:
            sys.exit(1)
    
    # 継続監視モード
    monitor.logger.info("🎯 Blogger自動投稿システム継続監視開始")
    
    consecutive_failures = 0
    consecutive_auth_errors = 0
    max_failures = 3
    max_auth_errors = 5
    
    try:
        while True:
            success = asyncio.run(monitor.run_monitoring_cycle())
            
            if success is True:
                consecutive_failures = 0
                consecutive_auth_errors = 0
                time.sleep(600)  # 10分待機
            elif success == "auth_error":
                consecutive_auth_errors += 1
                monitor.logger.warning(f"💥 連続認証エラー: {consecutive_auth_errors}/{max_auth_errors}")
                
                if consecutive_auth_errors >= max_auth_errors:
                    monitor.logger.critical("💀 認証エラーが続いています。手動修復が必要です。")
                    break
                
                time.sleep(180)  # 認証エラー時は3分待機
            else:
                consecutive_failures += 1
                monitor.logger.error(f"💥 連続失敗回数: {consecutive_failures}/{max_failures}")
                
                if consecutive_failures >= max_failures:
                    monitor.logger.critical("💀 最大失敗回数に達しました。監視を停止します。")
                    break
                
                time.sleep(120)  # 失敗時は2分待機
                
    except KeyboardInterrupt:
        monitor.logger.info("👋 監視を停止しました")
    except Exception as e:
        monitor.logger.critical(f"💥 予期しないエラー: {e}")

if __name__ == "__main__":
    main()