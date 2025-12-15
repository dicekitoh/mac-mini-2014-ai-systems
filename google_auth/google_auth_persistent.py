#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API認証の24時間永続化システム
自動リフレッシュ機能付きトークン管理
"""

import os
import pickle
import json
import time
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import threading
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersistentGoogleAuth:
    """24時間認証維持クラス"""
    
    def __init__(self, credentials_file='/home/fujinosuke/credentials_drive.json'):
        self.credentials_file = credentials_file
        self.token_file = '/home/fujinosuke/token_persistent.pickle'
        self.config_file = '/home/fujinosuke/auth_config.json'
        self.creds = None
        self.services = {}
        
        # 基本スコープ（必要最小限）
        self.scopes = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        self.load_config()
        self.authenticate()
        self.start_auto_refresh()
    
    def load_config(self):
        """設定ファイル読み込み"""
        default_config = {
            'auto_refresh_interval': 3300,  # 55分（1時間より少し前）
            'max_retry_attempts': 3,
            'last_refresh': None,
            'refresh_enabled': True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
            
        self.save_config()
    
    def save_config(self):
        """設定ファイル保存"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"設定保存エラー: {e}")
    
    def authenticate(self):
        """認証実行（既存トークン優先）"""
        # 既存トークン確認
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                logger.info("✅ 既存トークン読み込み成功")
            except Exception as e:
                logger.error(f"既存トークン読み込みエラー: {e}")
                
        # トークン有効性確認
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("🔄 トークンリフレッシュ中...")
                try:
                    self.creds.refresh(Request())
                    self.save_token()
                    logger.info("✅ トークンリフレッシュ成功")
                except Exception as e:
                    logger.error(f"リフレッシュエラー: {e}")
                    self.creds = None
        
        # 新規認証が必要な場合
        if not self.creds or not self.creds.valid:
            logger.warning("⚠️ 新規認証が必要です")
            return False
            
        # サービス初期化
        self.init_services()
        self.config['last_refresh'] = datetime.now().isoformat()
        self.save_config()
        return True
    
    def save_token(self):
        """トークン保存"""
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            logger.info("💾 トークン保存完了")
        except Exception as e:
            logger.error(f"トークン保存エラー: {e}")
    
    def init_services(self):
        """Google APIサービス初期化"""
        if not self.creds or not self.creds.valid:
            return False
            
        try:
            self.services = {
                'drive': build('drive', 'v3', credentials=self.creds),
                'docs': build('docs', 'v1', credentials=self.creds),
                'sheets': build('sheets', 'v4', credentials=self.creds)
            }
            logger.info("✅ Google APIサービス初期化完了")
            return True
        except Exception as e:
            logger.error(f"サービス初期化エラー: {e}")
            return False
    
    def start_auto_refresh(self):
        """自動リフレッシュ開始"""
        if not self.config['refresh_enabled']:
            return
            
        def refresh_loop():
            while self.config['refresh_enabled']:
                time.sleep(self.config['auto_refresh_interval'])
                self.refresh_token()
        
        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()
        logger.info(f"🔄 自動リフレッシュ開始 (間隔: {self.config['auto_refresh_interval']}秒)")
    
    def refresh_token(self):
        """トークンリフレッシュ"""
        if not self.creds:
            return False
            
        try:
            if self.creds.expired or self._should_refresh():
                logger.info("🔄 定期トークンリフレッシュ実行...")
                self.creds.refresh(Request())
                self.save_token()
                self.init_services()
                self.config['last_refresh'] = datetime.now().isoformat()
                self.save_config()
                logger.info("✅ 定期リフレッシュ完了")
                return True
        except Exception as e:
            logger.error(f"定期リフレッシュエラー: {e}")
            return False
    
    def _should_refresh(self):
        """リフレッシュ必要性判定"""
        if not self.creds.expiry:
            return False
        
        # 有効期限の10分前にリフレッシュ
        refresh_time = self.creds.expiry - timedelta(minutes=10)
        return datetime.utcnow() >= refresh_time
    
    def get_service(self, service_name):
        """サービス取得"""
        if service_name in self.services:
            return self.services[service_name]
        return None
    
    def is_authenticated(self):
        """認証状態確認"""
        return self.creds and self.creds.valid
    
    def get_status(self):
        """認証状態詳細"""
        if not self.creds:
            return {"status": "未認証", "valid": False}
        
        status = {
            "status": "認証済み" if self.creds.valid else "期限切れ",
            "valid": self.creds.valid,
            "expiry": self.creds.expiry.isoformat() if self.creds.expiry else None,
            "last_refresh": self.config.get('last_refresh'),
            "auto_refresh": self.config['refresh_enabled'],
            "services": list(self.services.keys())
        }
        return status

# グローバルインスタンス
_auth_instance = None

def get_google_auth():
    """グローバル認証インスタンス取得"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = PersistentGoogleAuth()
    return _auth_instance

def create_document(title, content):
    """Google ドキュメント作成（認証自動処理）"""
    auth = get_google_auth()
    
    if not auth.is_authenticated():
        return {"error": "認証が必要です"}
    
    try:
        # 一時ファイル作成
        temp_file = f"/tmp/{title.replace(' ', '_')}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Google ドキュメントとしてアップロード
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
        
        os.remove(temp_file)
        
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
    """Google スプレッドシート作成（認証自動処理）"""
    auth = get_google_auth()
    
    if not auth.is_authenticated():
        return {"error": "認証が必要です"}
    
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
        
        # データがある場合は挿入
        if data:
            range_name = 'A1'
            value_range_body = {
                'values': data
            }
            
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
    # テスト実行
    auth = get_google_auth()
    
    print("=== Google認証永続化システム ===")
    print(f"認証状態: {auth.get_status()}")
    
    if auth.is_authenticated():
        print("✅ 24時間認証維持システム稼働中")
        
        # テストドキュメント作成
        test_content = f"""テストドキュメント
作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

24時間認証維持システムのテストです。
このシステムにより、認証の手間なくGoogle ドキュメントを作成できます。
"""
        
        result = create_document("24時間認証テスト", test_content)
        if result.get('success'):
            print(f"✅ テストドキュメント作成成功: {result['url']}")
        else:
            print(f"❌ テストエラー: {result.get('error')}")
    else:
        print("❌ 認証が必要です")