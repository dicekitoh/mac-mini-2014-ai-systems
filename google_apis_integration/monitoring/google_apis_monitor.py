#!/usr/bin/env python3
"""
Google APIs 常時接続監視システム
Mac mini 2014 - 継続的接続確保
"""

import os
import sys
import json
import time
import logging
import datetime
import subprocess
from pathlib import Path

class GoogleAPIsMonitor:
    def __init__(self):
        self.base_dir = Path("/home/fujinosuke/projects/google_apis_integration")
        self.venv_path = self.base_dir / "google_apis_venv"
        self.log_dir = self.base_dir / "monitoring" / "logs"
        self.credentials_dir = self.base_dir / "01_authentication"
        
        # ログディレクトリ作成
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # ログ設定
        log_file = self.log_dir / f"google_apis_monitor_{datetime.date.today().isoformat()}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_venv_activation(self):
        """仮想環境の確認とアクティベーション"""
        try:
            activate_path = self.venv_path / "bin" / "activate"
            if not activate_path.exists():
                self.logger.error(f"仮想環境が見つかりません: {activate_path}")
                return False
            
            self.logger.info("✅ 仮想環境確認完了")
            return True
        except Exception as e:
            self.logger.error(f"仮想環境確認エラー: {e}")
            return False
    
    def check_credentials(self):
        """認証情報の確認"""
        try:
            credentials_file = self.credentials_dir / "credentials.json"
            token_file = self.credentials_dir / "token.json"
            
            if credentials_file.exists():
                with open(credentials_file, 'r') as f:
                    creds = json.load(f)
                    project_id = creds.get('installed', {}).get('project_id', 'N/A')
                    self.logger.info(f"📋 プロジェクトID: {project_id}")
            
            if token_file.exists():
                self.logger.info("🔐 認証トークン: 存在")
            else:
                self.logger.warning("⚠️ 認証トークン: 未設定")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"認証情報確認エラー: {e}")
            return False
    
    def test_google_apis_connection(self):
        """Google APIs接続テスト"""
        try:
            # 仮想環境での実行
            test_script = self.base_dir / "google_apis_test.py"
            if not test_script.exists():
                self.logger.error(f"テストスクリプトが見つかりません: {test_script}")
                return False
            
            cmd = f"cd {self.base_dir} && source {self.venv_path}/bin/activate && python google_apis_test.py"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.logger.info("✅ Google APIs接続テスト: 成功")
                return True
            else:
                self.logger.error(f"❌ Google APIs接続テスト: 失敗\n{result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Google APIs接続テスト: タイムアウト")
            return False
        except Exception as e:
            self.logger.error(f"Google APIs接続テストエラー: {e}")
            return False
    
    def attempt_reconnection(self):
        """再接続試行"""
        self.logger.info("🔄 Google APIs再接続を試行...")
        
        # 認証ファイル確認
        if not self.check_credentials():
            self.logger.error("❌ 認証情報に問題があります。手動での認証が必要です。")
            return False
        
        # 再接続テスト
        return self.test_google_apis_connection()
    
    def log_system_status(self):
        """システム状況記録"""
        try:
            # CPU使用率
            cpu_usage = subprocess.run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1", 
                                     shell=True, capture_output=True, text=True)
            
            # メモリ使用率
            memory_usage = subprocess.run("free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'", 
                                        shell=True, capture_output=True, text=True)
            
            self.logger.info(f"📊 システム状況 - CPU: {cpu_usage.stdout.strip()}%, Memory: {memory_usage.stdout.strip()}%")
        except Exception as e:
            self.logger.warning(f"システム状況取得エラー: {e}")
    
    def run_monitoring_cycle(self):
        """監視サイクル実行"""
        start_time = datetime.datetime.now()
        self.logger.info(f"🚀 Google APIs監視開始: {start_time}")
        
        # 基本チェック
        if not self.check_venv_activation():
            self.logger.critical("💥 仮想環境チェック失敗")
            return False
        
        if not self.check_credentials():
            self.logger.critical("💥 認証情報チェック失敗")
            return False
        
        # 接続テスト
        connection_ok = self.test_google_apis_connection()
        
        if not connection_ok:
            self.logger.warning("⚠️ 接続失敗 - 再接続を試行")
            connection_ok = self.attempt_reconnection()
        
        # システム状況記録
        self.log_system_status()
        
        # 結果サマリ
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if connection_ok:
            self.logger.info(f"✅ 監視サイクル完了: {duration:.1f}秒 - 接続正常")
        else:
            self.logger.error(f"❌ 監視サイクル完了: {duration:.1f}秒 - 接続異常")
        
        return connection_ok

def main():
    """メイン実行"""
    monitor = GoogleAPIsMonitor()
    
    # 単発実行
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        success = monitor.run_monitoring_cycle()
        sys.exit(0 if success else 1)
    
    # 継続監視モード
    monitor.logger.info("🎯 Google APIs継続監視モード開始")
    
    consecutive_failures = 0
    max_failures = 3
    
    try:
        while True:
            success = monitor.run_monitoring_cycle()
            
            if success:
                consecutive_failures = 0
                time.sleep(300)  # 5分待機
            else:
                consecutive_failures += 1
                monitor.logger.error(f"💥 連続失敗回数: {consecutive_failures}/{max_failures}")
                
                if consecutive_failures >= max_failures:
                    monitor.logger.critical("💀 最大失敗回数に達しました。監視を停止します。")
                    break
                
                time.sleep(60)  # 失敗時は1分待機
                
    except KeyboardInterrupt:
        monitor.logger.info("👋 監視を停止しました")
    except Exception as e:
        monitor.logger.critical(f"💥 予期しないエラー: {e}")

if __name__ == "__main__":
    main()