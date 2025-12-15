#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contact Manager v2 Bot Token Monitor and Auto-Refresh System
Google連絡先APIトークンの自動監視・更新システム
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

class ContactManagerTokenMonitor:
    def __init__(self, token_file='/home/fujinosuke/google_contacts/token.pickle'):
        self.token_file = token_file
        self.backup_file = token_file + '.backup'
        self.monitoring_interval = 3600  # 1時間ごとにチェック
        self.bot_script = 'contact_manager_v2_bot_production.py'
        self.working_dir = '/home/fujinosuke/google_contacts'
        
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
            elif creds and not creds.expired:
                logger.info("Token is still valid, forcing refresh for safety...")
                try:
                    creds.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    logger.info("Preventive token refresh successful")
                    return True
                except Exception as e:
                    logger.warning(f"Preventive refresh failed: {e}")
                    return False
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
            result = subprocess.run(['pgrep', '-f', self.bot_script], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                logger.warning("Contact Manager Bot not running, attempting restart...")
                # Bot再起動
                subprocess.run([
                    'bash', '-c',
                    f'cd {self.working_dir} && source google_env/bin/activate && '
                    f'nohup python3 {self.bot_script} > bot_production_permanent.log 2>&1 &'
                ])
                time.sleep(5)  # 起動待機
                logger.info("Contact Manager Bot restarted")
                return True
            else:
                logger.info(f"Contact Manager Bot running (PID: {result.stdout.strip()})")
                return True
                
        except Exception as e:
            logger.error(f"Error checking/restarting bot: {e}")
            return False
    
    def check_api_connectivity(self):
        """Google People APIへの接続をテスト"""
        try:
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            import requests
            # 自分の連絡先情報を取得してテスト
            url = 'https://people.googleapis.com/v1/people/me?personFields=names'
            headers = {'Authorization': f'Bearer {creds.token}'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                logger.info("Google People API connectivity test passed")
                return True
            else:
                logger.error(f"API test failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"API connectivity test error: {e}")
            return False
    
    def monitor_loop(self):
        """継続的な監視ループ"""
        logger.info("Starting Contact Manager token monitor service...")
        
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
                        subprocess.run(['pkill', '-f', self.bot_script])
                        time.sleep(2)
                        self.ensure_bot_running()
                    else:
                        logger.error("Token refresh failed")
                
                # API接続テスト
                if not self.check_api_connectivity():
                    logger.warning("API connectivity issue detected, refreshing token...")
                    self.refresh_token()
                    subprocess.run(['pkill', '-f', self.bot_script])
                    time.sleep(2)
                    self.ensure_bot_running()
                
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
    # 作業ディレクトリをContact Manager Botのディレクトリに変更
    os.chdir('/home/fujinosuke/google_contacts')
    
    monitor = ContactManagerTokenMonitor()
    
    # 単発チェックモード
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--check':
        is_valid, message = monitor.check_token_validity()
        print(f"Token status: {message}")
        print(f"API connectivity: {'OK' if monitor.check_api_connectivity() else 'FAILED'}")
        if not is_valid:
            print("Attempting to refresh token...")
            if monitor.refresh_token():
                print("Token refreshed successfully")
            else:
                print("Token refresh failed")
    else:
        # 継続監視モード
        monitor.monitor_loop()