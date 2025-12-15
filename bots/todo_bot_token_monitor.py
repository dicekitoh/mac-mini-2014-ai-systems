#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Todo Bot Token Monitor and Auto-Refresh System
自動的にトークンの有効期限を監視し、期限切れ前に更新する
"""

import os
import pickle
import logging
import time
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import subprocess
import json

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TokenMonitor:
    def __init__(self, token_file='/home/fujinosuke/google_tasks_new.pickle'):
        self.token_file = token_file
        self.backup_file = token_file + '.backup'
        self.monitoring_interval = 3600  # 1時間ごとにチェック
        
    def check_token_validity(self):
        """トークンの有効性をチェック"""
        try:
            if not os.path.exists(self.token_file):
                logger.error(f"Token file {self.token_file} not found")
                return False, "Token file not found"
                
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if not creds:
                return False, "No credentials found"
                
            # トークンの有効期限をチェック
            if hasattr(creds, 'expiry') and creds.expiry:
                time_until_expiry = creds.expiry - datetime.utcnow()
                hours_until_expiry = time_until_expiry.total_seconds() / 3600
                
                if hours_until_expiry < 0:
                    return False, "Token already expired"
                elif hours_until_expiry < 2:  # 2時間以内に期限切れ
                    return False, f"Token expiring in {hours_until_expiry:.1f} hours"
                else:
                    return True, f"Token valid for {hours_until_expiry:.1f} hours"
            else:
                # 有効期限情報がない場合、とりあえず有効とみなす
                return True, "Token validity unknown (no expiry info)"
                
        except Exception as e:
            logger.error(f"Error checking token: {e}")
            return False, f"Error: {str(e)}"
    
    def refresh_token(self):
        """トークンをリフレッシュ"""
        try:
            # バックアップ作成
            if os.path.exists(self.token_file):
                subprocess.run(['cp', self.token_file, self.backup_file])
                logger.info(f"Created backup at {self.backup_file}")
            
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
                
                # 更新したトークンを保存
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                
                logger.info("Token refreshed successfully")
                return True
            else:
                logger.warning("Token cannot be refreshed (no refresh_token)")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            # エラー時はバックアップから復元
            if os.path.exists(self.backup_file):
                subprocess.run(['cp', self.backup_file, self.token_file])
                logger.info("Restored from backup")
            return False
    
    def ensure_bot_running(self):
        """Botが稼働しているか確認し、必要なら再起動"""
        try:
            # プロセスチェック
            result = subprocess.run(['pgrep', '-f', 'simple_todo_bot.py'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                logger.warning("Todo bot not running, attempting restart...")
                # Bot再起動
                subprocess.run([
                    'bash', '-c',
                    'cd /home/fujinosuke && source todo_env/bin/activate && '
                    'nohup python3 simple_todo_bot.py > simple_todo_bot.log 2>&1 &'
                ])
                time.sleep(5)  # 起動待機
                logger.info("Todo bot restarted")
                return True
            else:
                logger.info(f"Todo bot running (PID: {result.stdout.strip()})")
                return True
                
        except Exception as e:
            logger.error(f"Error checking/restarting bot: {e}")
            return False
    
    def monitor_loop(self):
        """継続的な監視ループ"""
        logger.info("Starting token monitor service...")
        
        while True:
            try:
                # トークンチェック
                is_valid, message = self.check_token_validity()
                logger.info(f"Token status: {message}")
                
                if not is_valid:
                    logger.warning("Token needs refresh")
                    if self.refresh_token():
                        logger.info("Token refresh successful")
                        # Bot再起動して新しいトークンを読み込ませる
                        subprocess.run(['pkill', '-f', 'simple_todo_bot.py'])
                        time.sleep(2)
                        self.ensure_bot_running()
                    else:
                        logger.error("Token refresh failed")
                
                # Botの稼働確認
                self.ensure_bot_running()
                
                # 次のチェックまで待機
                logger.info(f"Next check in {self.monitoring_interval/60} minutes")
                time.sleep(self.monitoring_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(60)  # エラー時は1分後に再試行

if __name__ == "__main__":
    monitor = TokenMonitor()
    
    # 単発チェックモード
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--check':
        is_valid, message = monitor.check_token_validity()
        print(f"Token status: {message}")
        if not is_valid:
            print("Attempting to refresh token...")
            if monitor.refresh_token():
                print("Token refreshed successfully")
            else:
                print("Token refresh failed")
    else:
        # 継続監視モード
        monitor.monitor_loop()