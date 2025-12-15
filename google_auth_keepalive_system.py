#!/usr/bin/env python3
"""
Google API認証24時間維持システム
全サービスの自動更新・監視・アラート機能
"""

import pickle
import os
import json
import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import time
import threading

class GoogleAuthKeepAlive:
    def __init__(self, config_file='/home/fujinosuke/projects/google_auth_config.json'):
        self.config_file = config_file
        self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """設定ファイル読み込み"""
        default_config = {
            "token_files": {
                "統合認証": "/home/fujinosuke/projects/google_auth/unified_google_token.pickle",
                "Google Contacts": "/home/fujinosuke/google_contacts/token.pickle", 
                "Google Drive": "/home/fujinosuke/projects/google_auth/token_drive.pickle",
                "Google Docs": "/home/fujinosuke/projects/google_auth/google_docs_token.pickle",
                "永続認証": "/home/fujinosuke/projects/google_auth/token_persistent.pickle",
                "連絡先リアル": "/home/fujinosuke/google/token_contacts_real.pickle",
                "Bot用連絡先": "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/token.pickle"
            },
            "refresh_settings": {
                "check_interval_minutes": 30,  # 30分ごとにチェック
                "refresh_before_expiry_hours": 6,  # 期限6時間前に更新
                "max_retry_attempts": 3,
                "retry_delay_seconds": 300  # 5分待機
            },
            "alert_settings": {
                "enable_email_alerts": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "itoh@thinksblog.com",
                "sender_password": "***REMOVED***",
                "alert_email": "itoh@thinksblog.com",
                "alert_on_failure": True,
                "alert_on_success": False,
                "daily_status_report": True
            },
            "logging": {
                "log_file": "/home/fujinosuke/logs/google_auth_keepalive.log",
                "max_log_size_mb": 10,
                "backup_count": 5
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """設定ファイル保存"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def setup_logging(self):
        """ログ設定"""
        log_dir = os.path.dirname(self.config['logging']['log_file'])
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['log_file'], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_token_status(self, token_path):
        """トークンの状態確認"""
        if not os.path.exists(token_path):
            return {
                'exists': False,
                'valid': False,
                'expires_in_hours': 0,
                'needs_refresh': True,
                'error': 'File not found'
            }
        
        try:
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
            
            is_valid = creds.valid if hasattr(creds, 'valid') else False
            is_expired = creds.expired if hasattr(creds, 'expired') else True
            
            expires_in_hours = 0
            if hasattr(creds, 'expiry') and creds.expiry:
                time_until_expiry = creds.expiry - datetime.utcnow()
                expires_in_hours = time_until_expiry.total_seconds() / 3600
            
            needs_refresh = (
                not is_valid or 
                expires_in_hours < self.config['refresh_settings']['refresh_before_expiry_hours']
            )
            
            return {
                'exists': True,
                'valid': is_valid,
                'expired': is_expired,
                'expires_in_hours': expires_in_hours,
                'needs_refresh': needs_refresh,
                'has_refresh_token': hasattr(creds, 'refresh_token') and creds.refresh_token,
                'scopes': getattr(creds, 'scopes', []),
                'credentials': creds
            }
            
        except Exception as e:
            return {
                'exists': True,
                'valid': False,
                'expires_in_hours': 0,
                'needs_refresh': True,
                'error': str(e)
            }
    
    def refresh_token(self, token_path, service_name):
        """トークン更新実行"""
        self.logger.info(f"🔄 {service_name} トークン更新開始")
        
        try:
            status = self.check_token_status(token_path)
            if not status.get('has_refresh_token'):
                self.logger.error(f"❌ {service_name}: 更新トークンなし")
                return False
            
            creds = status['credentials']
            
            # バックアップ作成
            backup_path = f"{token_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_path, 'wb') as f:
                pickle.dump(creds, f)
            
            # トークン更新
            creds.refresh(Request())
            
            # 更新されたトークンを保存
            with open(token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            self.logger.info(f"✅ {service_name} トークン更新成功")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ {service_name} トークン更新失敗: {str(e)}")
            return False
    
    def send_alert(self, subject, message, is_error=False):
        """アラートメール送信"""
        if not self.config['alert_settings']['enable_email_alerts']:
            return
        
        if is_error and not self.config['alert_settings']['alert_on_failure']:
            return
        
        if not is_error and not self.config['alert_settings']['alert_on_success']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['alert_settings']['sender_email']
            msg['To'] = self.config['alert_settings']['alert_email']
            msg['Subject'] = f"[MacMini2014] {subject}"
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(
                self.config['alert_settings']['smtp_server'],
                self.config['alert_settings']['smtp_port']
            )
            server.starttls()
            server.login(
                self.config['alert_settings']['sender_email'],
                self.config['alert_settings']['sender_password']
            )
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"📧 アラートメール送信成功: {subject}")
            
        except Exception as e:
            self.logger.error(f"❌ アラートメール送信失敗: {str(e)}")
    
    def run_check_cycle(self):
        """チェックサイクル実行"""
        self.logger.info("🔍 Google API認証チェック開始")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checked': 0,
            'refreshed': 0,
            'failed': 0,
            'services': {}
        }
        
        for service_name, token_path in self.config['token_files'].items():
            results['checked'] += 1
            
            status = self.check_token_status(token_path)
            service_result = {
                'status': status,
                'refreshed': False,
                'refresh_attempts': 0
            }
            
            self.logger.info(
                f"📋 {service_name}: "
                f"有効={status.get('valid', False)}, "
                f"期限まで={status.get('expires_in_hours', 0):.1f}時間"
            )
            
            # 更新が必要な場合
            if status.get('needs_refresh') and status.get('has_refresh_token'):
                max_attempts = self.config['refresh_settings']['max_retry_attempts']
                
                for attempt in range(max_attempts):
                    service_result['refresh_attempts'] += 1
                    
                    if self.refresh_token(token_path, service_name):
                        service_result['refreshed'] = True
                        results['refreshed'] += 1
                        break
                    else:
                        if attempt < max_attempts - 1:
                            time.sleep(self.config['refresh_settings']['retry_delay_seconds'])
                
                if not service_result['refreshed']:
                    results['failed'] += 1
                    self.send_alert(
                        f"Google API認証更新失敗: {service_name}",
                        f"サービス: {service_name}\n"
                        f"トークンファイル: {token_path}\n"
                        f"試行回数: {max_attempts}\n"
                        f"時刻: {datetime.now()}",
                        is_error=True
                    )
            
            results['services'][service_name] = service_result
        
        # 結果ログ
        self.logger.info(
            f"📊 チェック完了: "
            f"確認={results['checked']}, "
            f"更新={results['refreshed']}, "
            f"失敗={results['failed']}"
        )
        
        # 失敗があった場合のアラート
        if results['failed'] > 0:
            self.send_alert(
                "Google API認証エラー検出",
                f"失敗したサービス数: {results['failed']}\n"
                f"詳細はログファイルを確認してください。\n"
                f"ログ: {self.config['logging']['log_file']}",
                is_error=True
            )
        
        return results
    
    def run_daemon(self):
        """デーモンモード実行"""
        self.logger.info("🚀 Google API認証維持デーモン開始")
        
        check_interval = self.config['refresh_settings']['check_interval_minutes'] * 60
        last_daily_report = datetime.now().date()
        
        while True:
            try:
                # チェック実行
                results = self.run_check_cycle()
                
                # 日次レポート
                current_date = datetime.now().date()
                if (current_date > last_daily_report and 
                    self.config['alert_settings']['daily_status_report']):
                    
                    self.send_daily_report()
                    last_daily_report = current_date
                
                # 次回チェックまで待機
                self.logger.info(f"⏰ {check_interval//60}分後に次回チェック")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 デーモン停止要求を受信")
                break
            except Exception as e:
                self.logger.error(f"❌ デーモン実行エラー: {str(e)}")
                time.sleep(60)  # エラー時は1分待機
    
    def send_daily_report(self):
        """日次ステータスレポート送信"""
        report_data = []
        
        for service_name, token_path in self.config['token_files'].items():
            status = self.check_token_status(token_path)
            report_data.append({
                'service': service_name,
                'valid': status.get('valid', False),
                'expires_in_hours': status.get('expires_in_hours', 0),
                'scopes': len(status.get('scopes', []))
            })
        
        # レポート作成
        report = "📊 Google API認証 日次ステータスレポート\n"
        report += f"日付: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 50 + "\n\n"
        
        for data in report_data:
            status_icon = "✅" if data['valid'] else "❌"
            report += f"{status_icon} {data['service']}\n"
            report += f"   有効性: {'有効' if data['valid'] else '無効'}\n"
            report += f"   期限まで: {data['expires_in_hours']:.1f}時間\n"
            report += f"   スコープ数: {data['scopes']}\n\n"
        
        self.send_alert("Google API認証 日次レポート", report, is_error=False)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Google API認証24時間維持システム')
    parser.add_argument('--daemon', action='store_true', help='デーモンモードで実行')
    parser.add_argument('--check', action='store_true', help='一度だけチェック実行')
    parser.add_argument('--config', type=str, help='設定ファイルパス')
    
    args = parser.parse_args()
    
    # システム初期化
    config_file = args.config or '/home/fujinosuke/projects/google_auth_config.json'
    keepalive = GoogleAuthKeepAlive(config_file)
    
    if args.daemon:
        keepalive.run_daemon()
    elif args.check:
        results = keepalive.run_check_cycle()
        print(f"\n📊 結果: 確認={results['checked']}, 更新={results['refreshed']}, 失敗={results['failed']}")
    else:
        print("使用方法:")
        print("  --daemon    : 24時間監視モード")  
        print("  --check     : 一回だけチェック")
        print("  --config    : 設定ファイル指定")

if __name__ == '__main__':
    main()