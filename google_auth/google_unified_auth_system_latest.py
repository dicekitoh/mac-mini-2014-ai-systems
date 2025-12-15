#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google統一認証システム - 企業レベル24時間認証維持
全てのGoogleサービスに対応する強固な認証基盤
"""

import os
import pickle
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/fujinosuke/google_auth_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedGoogleAuthSystem:
    """統一Google認証システム - 企業レベル24時間維持"""
    
    # 全Google APIサービスの包括的スコープ
    ALL_SCOPES = [
        # Core APIs
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/spreadsheets',
        
        # Gmail
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        
        # Calendar
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/calendar.readonly',
        
        # Tasks
        'https://www.googleapis.com/auth/tasks',
        'https://www.googleapis.com/auth/tasks.readonly',
        
        # Contacts
        'https://www.googleapis.com/auth/contacts',
        'https://www.googleapis.com/auth/contacts.readonly',
        
        # User Info
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
        
        # Photos
        'https://www.googleapis.com/auth/photoslibrary.readonly',
        
        # YouTube
        'https://www.googleapis.com/auth/youtube.readonly',
    ]
    
    def __init__(self, base_dir='/home/fujinosuke'):
        self.base_dir = Path(base_dir)
        self.credentials_file = self.base_dir / 'credentials_drive.json'
        self.unified_token_file = self.base_dir / 'unified_google_token.pickle'
        self.config_file = self.base_dir / 'unified_auth_config.json'
        self.backup_dir = self.base_dir / 'auth_backups'
        
        # 認証管理
        self.creds = None
        self.services = {}
        self.refresh_lock = threading.Lock()
        self.monitoring_active = True
        
        # 設定
        self.config = self._load_config()
        
        # バックアップディレクトリ作成
        self.backup_dir.mkdir(exist_ok=True)
        
        # システム初期化
        self._initialize_system()
    
    def _load_config(self):
        """設定読み込み"""
        default_config = {
            'refresh_interval_seconds': 3000,  # 50分
            'token_validity_check_seconds': 600,  # 10分
            'max_retry_attempts': 5,
            'backup_retention_days': 30,
            'monitoring_enabled': True,
            'auto_repair_enabled': True,
            'emergency_refresh_margin_minutes': 10,
            'last_successful_refresh': None,
            'refresh_failure_count': 0,
            'system_start_time': datetime.now().isoformat()
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.error(f"設定読み込みエラー: {e}")
        
        return default_config
    
    def _save_config(self):
        """設定保存"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
    
    def _initialize_system(self):
        """システム初期化"""
        logger.info("🚀 統一Google認証システム初期化開始")
        
        # 既存トークンからの移行
        self._migrate_existing_tokens()
        
        # 認証実行
        if self._authenticate():
            logger.info("✅ 初期認証成功")
            self._start_monitoring_threads()
        else:
            logger.error("❌ 初期認証失敗")
    
    def _migrate_existing_tokens(self):
        """既存トークンからの移行"""
        existing_tokens = [
            self.base_dir / 'token_drive.pickle',
            self.base_dir / 'google_tasks_new.pickle',
            self.base_dir / 'google' / 'token_contacts_real.pickle',
            self.base_dir / 'google_contacts' / 'contact_manager_v2_bot_github' / 'token.pickle'
        ]
        
        best_token = None
        best_expiry = None
        
        for token_file in existing_tokens:
            if token_file.exists():
                try:
                    with open(token_file, 'rb') as f:
                        creds = pickle.load(f)
                    
                    if creds.valid and creds.refresh_token:
                        # 有効期限が最も長いトークンを選択
                        if best_token is None or (
                            hasattr(creds, 'expiry') and creds.expiry and
                            (best_expiry is None or creds.expiry > best_expiry)
                        ):
                            best_token = creds
                            best_expiry = creds.expiry if hasattr(creds, 'expiry') else None
                            logger.info(f"✅ 有効なトークン発見: {token_file}")
                
                except Exception as e:
                    logger.warning(f"トークン読み込みエラー {token_file}: {e}")
        
        if best_token:
            # 統一トークンとして保存
            self._save_unified_token(best_token)
            logger.info("✅ 既存トークンを統一システムに移行完了")
        else:
            logger.warning("⚠️ 有効な既存トークンが見つかりません")
    
    def _authenticate(self):
        """認証実行"""
        with self.refresh_lock:
            # 統一トークン読み込み
            if self.unified_token_file.exists():
                try:
                    with open(self.unified_token_file, 'rb') as f:
                        self.creds = pickle.load(f)
                    logger.info("✅ 統一トークン読み込み成功")
                except Exception as e:
                    logger.error(f"統一トークン読み込みエラー: {e}")
            
            # トークン有効性確認・リフレッシュ
            if self.creds:
                if not self.creds.valid:
                    if self.creds.expired and self.creds.refresh_token:
                        try:
                            logger.info("🔄 トークンリフレッシュ実行中...")
                            self.creds.refresh(Request())
                            self._save_unified_token(self.creds)
                            self._update_refresh_success()
                            logger.info("✅ トークンリフレッシュ成功")
                        except Exception as e:
                            logger.error(f"リフレッシュエラー: {e}")
                            self._update_refresh_failure()
                            return False
                
                # サービス初期化
                return self._initialize_services()
            
            return False
    
    def _save_unified_token(self, creds):
        """統一トークン保存"""
        try:
            # バックアップ作成
            if self.unified_token_file.exists():
                backup_file = self.backup_dir / f"token_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pickle"
                import shutil
                shutil.copy2(self.unified_token_file, backup_file)
            
            # 新しいトークン保存
            with open(self.unified_token_file, 'wb') as f:
                pickle.dump(creds, f)
            
            logger.info(f"💾 統一トークン保存完了: {self.unified_token_file}")
            
            # 古いバックアップ削除
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"トークン保存エラー: {e}")
    
    def _initialize_services(self):
        """全Googleサービス初期化"""
        if not self.creds or not self.creds.valid:
            return False
        
        service_configs = [
            ('drive', 'v3'),
            ('docs', 'v1'),
            ('sheets', 'v4'),
            ('gmail', 'v1'),
            ('calendar', 'v3'),
            ('tasks', 'v1'),
            ('people', 'v1'),  # Contacts
            ('photoslibrary', 'v1'),
            ('youtube', 'v3'),
        ]
        
        initialized_services = []
        
        for service_name, version in service_configs:
            try:
                service = build(service_name, version, credentials=self.creds)
                self.services[service_name] = service
                initialized_services.append(service_name)
            except Exception as e:
                logger.warning(f"サービス初期化失敗 {service_name}: {e}")
        
        logger.info(f"✅ 初期化完了サービス: {', '.join(initialized_services)}")
        return len(initialized_services) > 0
    
    def _start_monitoring_threads(self):
        """監視スレッド開始"""
        if not self.config['monitoring_enabled']:
            return
        
        # 定期リフレッシュスレッド
        refresh_thread = threading.Thread(
            target=self._refresh_monitoring_loop, 
            daemon=True,
            name="GoogleAuthRefreshMonitor"
        )
        refresh_thread.start()
        
        # トークン有効性監視スレッド
        validity_thread = threading.Thread(
            target=self._validity_monitoring_loop,
            daemon=True,
            name="GoogleAuthValidityMonitor"
        )
        validity_thread.start()
        
        logger.info("🔄 認証監視スレッド開始")
    
    def _refresh_monitoring_loop(self):
        """定期リフレッシュ監視ループ"""
        while self.monitoring_active:
            try:
                time.sleep(self.config['refresh_interval_seconds'])
                self._periodic_refresh()
            except Exception as e:
                logger.error(f"定期リフレッシュエラー: {e}")
    
    def _validity_monitoring_loop(self):
        """トークン有効性監視ループ"""
        while self.monitoring_active:
            try:
                time.sleep(self.config['token_validity_check_seconds'])
                self._check_token_validity()
            except Exception as e:
                logger.error(f"有効性監視エラー: {e}")
    
    def _periodic_refresh(self):
        """定期リフレッシュ実行"""
        if not self.creds:
            return
        
        try:
            # リフレッシュ必要性判定
            if self._should_refresh():
                logger.info("🔄 定期リフレッシュ実行...")
                with self.refresh_lock:
                    self.creds.refresh(Request())
                    self._save_unified_token(self.creds)
                    self._initialize_services()
                    self._update_refresh_success()
                logger.info("✅ 定期リフレッシュ完了")
        except Exception as e:
            logger.error(f"定期リフレッシュエラー: {e}")
            self._update_refresh_failure()
    
    def _should_refresh(self):
        """リフレッシュ必要性判定"""
        if not self.creds or not hasattr(self.creds, 'expiry') or not self.creds.expiry:
            return False
        
        margin = timedelta(minutes=self.config['emergency_refresh_margin_minutes'])
        return datetime.utcnow() >= (self.creds.expiry - margin)
    
    def _check_token_validity(self):
        """トークン有効性確認"""
        if not self.creds:
            logger.warning("⚠️ 認証情報なし")
            return
        
        if not self.creds.valid:
            logger.warning("⚠️ トークン無効 - 緊急リフレッシュ実行")
            if self.config['auto_repair_enabled']:
                self._emergency_refresh()
    
    def _emergency_refresh(self):
        """緊急リフレッシュ"""
        try:
            logger.info("🚨 緊急リフレッシュ実行...")
            with self.refresh_lock:
                if self.creds.refresh_token:
                    self.creds.refresh(Request())
                    self._save_unified_token(self.creds)
                    self._initialize_services()
                    self._update_refresh_success()
                    logger.info("✅ 緊急リフレッシュ成功")
                else:
                    logger.error("❌ リフレッシュトークンなし")
        except Exception as e:
            logger.error(f"緊急リフレッシュエラー: {e}")
            self._update_refresh_failure()
    
    def _update_refresh_success(self):
        """リフレッシュ成功記録"""
        self.config['last_successful_refresh'] = datetime.now().isoformat()
        self.config['refresh_failure_count'] = 0
        self._save_config()
    
    def _update_refresh_failure(self):
        """リフレッシュ失敗記録"""
        self.config['refresh_failure_count'] += 1
        self._save_config()
        
        if self.config['refresh_failure_count'] >= self.config['max_retry_attempts']:
            logger.error("🚨 最大リトライ回数に到達 - 手動介入が必要")
    
    def _cleanup_old_backups(self):
        """古いバックアップ削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['backup_retention_days'])
            
            for backup_file in self.backup_dir.glob("token_backup_*.pickle"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"🗑️ 古いバックアップ削除: {backup_file}")
        except Exception as e:
            logger.error(f"バックアップ削除エラー: {e}")
    
    # Public API
    
    def get_service(self, service_name):
        """サービス取得"""
        return self.services.get(service_name)
    
    def is_authenticated(self):
        """認証状態確認"""
        return self.creds and self.creds.valid
    
    def get_system_status(self):
        """システム状態取得"""
        status = {
            'authenticated': self.is_authenticated(),
            'services_count': len(self.services),
            'available_services': list(self.services.keys()),
            'monitoring_active': self.monitoring_active,
            'last_refresh': self.config.get('last_successful_refresh'),
            'failure_count': self.config.get('refresh_failure_count', 0),
            'system_uptime': datetime.now().isoformat(),
            'config': self.config
        }
        
        if self.creds and hasattr(self.creds, 'expiry') and self.creds.expiry:
            time_until_expiry = self.creds.expiry - datetime.utcnow()
            status['token_expiry'] = self.creds.expiry.isoformat()
            status['hours_until_expiry'] = time_until_expiry.total_seconds() / 3600
        
        return status
    
    def force_refresh(self):
        """強制リフレッシュ"""
        return self._authenticate()
    
    def shutdown(self):
        """システムシャットダウン"""
        self.monitoring_active = False
        logger.info("🛑 統一認証システム停止")

# グローバルインスタンス
_unified_auth = None

def get_unified_auth():
    """統一認証システム取得"""
    global _unified_auth
    if _unified_auth is None:
        _unified_auth = UnifiedGoogleAuthSystem()
    return _unified_auth

# 便利関数

def create_document(title, content):
    """Google ドキュメント作成"""
    auth = get_unified_auth()
    if not auth.is_authenticated():
        return {"error": "認証エラー"}
    
    try:
        import tempfile
        
        # 一時ファイル作成
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        drive_service = auth.get_service('drive')
        
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(temp_file, mimetype='text/plain', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink,name'
        ).execute()
        
        os.unlink(temp_file)
        
        return {
            "success": True,
            "name": file.get('name'),
            "url": file.get('webViewLink'),
            "id": file.get('id')
        }
        
    except Exception as e:
        logger.error(f"ドキュメント作成エラー: {e}")
        return {"error": str(e)}

def create_spreadsheet(title, data=None):
    """Google スプレッドシート作成"""
    auth = get_unified_auth()
    if not auth.is_authenticated():
        return {"error": "認証エラー"}
    
    try:
        sheets_service = auth.get_service('sheets')
        
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        
        sheet = sheets_service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        
        result = {
            "success": True,
            "name": title,
            "url": sheet.get('spreadsheetUrl'),
            "id": sheet.get('spreadsheetId')
        }
        
        if data:
            range_name = 'A1'
            value_range_body = {'values': data}
            
            sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet.get('spreadsheetId'),
                range=range_name,
                valueInputOption='RAW',
                body=value_range_body
            ).execute()
            
            result['data_inserted'] = True
        
        return result
        
    except Exception as e:
        logger.error(f"スプレッドシート作成エラー: {e}")
        return {"error": str(e)}

if __name__ == '__main__':
    # システムテスト
    auth_system = get_unified_auth()
    
    print("=== 統一Google認証システム ===")
    status = auth_system.get_system_status()
    
    print(f"認証状態: {'✅' if status['authenticated'] else '❌'}")
    print(f"利用可能サービス: {len(status['available_services'])}個")
    print(f"サービス一覧: {', '.join(status['available_services'])}")
    
    if status.get('hours_until_expiry'):
        print(f"トークン残り時間: {status['hours_until_expiry']:.1f}時間")
    
    print(f"監視状態: {'✅ 稼働中' if status['monitoring_active'] else '❌ 停止'}")
    print(f"失敗回数: {status['failure_count']}")
    
    if auth_system.is_authenticated():
        print("\n🧪 テストドキュメント作成...")
        test_content = f"""統一認証システムテスト
作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

このドキュメントは統一Google認証システムによって作成されました。
24時間認証維持により、いつでも認証の手間なくGoogle サービスを利用できます。

利用可能サービス:
{chr(10).join('- ' + service for service in status['available_services'])}
"""
        
        result = create_document("統一認証システムテスト", test_content)
        if result.get('success'):
            print(f"✅ テスト成功: {result['url']}")
        else:
            print(f"❌ テストエラー: {result.get('error')}")