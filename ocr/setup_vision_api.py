#!/usr/bin/env python3
"""
Google Vision API セットアップ・認証スクリプト
Vision APIを有効化し、適切な認証設定を行う
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

class VisionAPISetup:
    def __init__(self):
        self.project_id = 'civil-authority-462513-a9'
        self.credentials_file = '/home/fujinosuke/google_contacts/credentials.json'
        self.token_file = '/home/fujinosuke/google_contacts/token.pickle'
        self.vision_scopes = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/cloud-vision'
        ]
        
        print(f"🔧 Google Vision API セットアップ")
        print(f"プロジェクトID: {self.project_id}")
        print(f"認証ファイル: {self.credentials_file}")
    
    def check_credentials_file(self):
        """認証ファイルの確認"""
        if not os.path.exists(self.credentials_file):
            print(f"❌ 認証ファイルが見つかりません: {self.credentials_file}")
            return False
        
        try:
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                client_id = creds_data['installed']['client_id']
                project_id = creds_data['installed']['project_id']
                print(f"✅ 認証ファイル確認済み")
                print(f"  Client ID: {client_id}")
                print(f"  Project: {project_id}")
                return True
            else:
                print(f"❌ 認証ファイル形式が無効")
                return False
                
        except Exception as e:
            print(f"❌ 認証ファイル読み込みエラー: {e}")
            return False
    
    def check_vision_api_enabled(self):
        """Vision APIが有効かチェック"""
        try:
            # Google Cloud API経由でVision APIの状態確認
            url = f"https://serviceusage.googleapis.com/v1/projects/{self.project_id}/services/vision.googleapis.com"
            
            # 現在の認証トークンを使用
            creds = self.get_current_credentials()
            if not creds:
                print("⚠️ 認証が必要です")
                return False
            
            headers = {'Authorization': f'Bearer {creds.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                service_info = response.json()
                state = service_info.get('state', 'DISABLED')
                print(f"📊 Vision API状態: {state}")
                return state == 'ENABLED'
            else:
                print(f"⚠️ API状態確認不可: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Vision API状態確認エラー: {e}")
            return False
    
    def enable_vision_api(self):
        """Vision APIを有効化"""
        try:
            print("🔄 Vision API有効化中...")
            
            url = f"https://serviceusage.googleapis.com/v1/projects/{self.project_id}/services/vision.googleapis.com:enable"
            
            creds = self.get_current_credentials()
            if not creds:
                print("❌ 認証が必要です")
                return False
            
            headers = {
                'Authorization': f'Bearer {creds.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json={}, timeout=30)
            
            if response.status_code == 200:
                print("✅ Vision API有効化成功")
                return True
            else:
                print(f"❌ Vision API有効化失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Vision API有効化エラー: {e}")
            return False
    
    def get_current_credentials(self):
        """現在の認証情報を取得"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                
                if creds and creds.valid:
                    return creds
                elif creds and creds.expired and creds.refresh_token:
                    print("🔄 トークン更新中...")
                    creds.refresh(Request())
                    
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    
                    return creds
            except Exception as e:
                print(f"⚠️ 既存トークン読み込みエラー: {e}")
        
        return None
    
    def authenticate_with_vision_scopes(self):
        """Vision APIスコープで認証"""
        try:
            print("🔑 Vision APIスコープで認証開始...")
            
            # 既存トークンを削除してフレッシュな認証
            if os.path.exists(self.token_file):
                backup_file = f"{self.token_file}.backup_{int(__import__('time').time())}"
                os.rename(self.token_file, backup_file)
                print(f"📁 既存トークンをバックアップ: {backup_file}")
            
            # 新しい認証フロー
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, 
                self.vision_scopes
            )
            
            print("🌐 ブラウザで認証を開始します...")
            print("⚠️ ローカルサーバーポート8080を使用します")
            
            creds = flow.run_local_server(port=8080, prompt='consent')
            
            # トークン保存
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            print("✅ Vision API認証成功")
            print(f"📁 トークン保存: {self.token_file}")
            
            return creds
            
        except Exception as e:
            print(f"❌ Vision API認証エラー: {e}")
            return None
    
    def test_vision_api_access(self):
        """Vision APIアクセステスト"""
        try:
            print("🔍 Vision APIアクセステスト...")
            
            creds = self.get_current_credentials()
            if not creds:
                print("❌ 認証情報がありません")
                return False
            
            # Vision API テスト呼び出し
            url = "https://vision.googleapis.com/v1/images:annotate"
            headers = {
                'Authorization': f'Bearer {creds.token}',
                'Content-Type': 'application/json'
            }
            
            # 小さなテスト画像（1x1 白色PNG）
            test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            
            test_request = {
                'requests': [{
                    'image': {'content': test_image_b64},
                    'features': [{'type': 'TEXT_DETECTION', 'maxResults': 1}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=test_request, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Vision APIアクセス成功")
                print(f"📄 レスポンス: {json.dumps(result, indent=2)[:200]}...")
                return True
            else:
                print(f"❌ Vision APIアクセス失敗: {response.status_code}")
                print(f"📄 エラー: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Vision APIテストエラー: {e}")
            return False
    
    def setup_complete_flow(self):
        """完全セットアップフロー"""
        print("=" * 60)
        print("Google Vision API 完全セットアップ")
        print("=" * 60)
        
        # 1. 認証ファイル確認
        if not self.check_credentials_file():
            return False
        
        # 2. 現在の認証状況確認
        current_creds = self.get_current_credentials()
        if current_creds:
            print("✅ 既存認証情報を確認")
            
            # Vision API状態確認
            if self.check_vision_api_enabled():
                print("✅ Vision API は既に有効です")
            else:
                print("⚠️ Vision API有効化が必要")
                if not self.enable_vision_api():
                    print("❌ Vision API有効化に失敗")
        
        # 3. Vision APIスコープで再認証
        print("\n🔑 Vision APIスコープで認証...")
        creds = self.authenticate_with_vision_scopes()
        if not creds:
            return False
        
        # 4. Vision APIアクセステスト
        print("\n🔍 Vision APIアクセステスト...")
        if not self.test_vision_api_access():
            return False
        
        print("\n" + "=" * 60)
        print("✅ Google Vision API セットアップ完了")
        print("=" * 60)
        print(f"📁 認証ファイル: {self.credentials_file}")
        print(f"📁 トークンファイル: {self.token_file}")
        print(f"🔑 認証スコープ: {', '.join(self.vision_scopes)}")
        print(f"🌐 プロジェクト: {self.project_id}")
        print("\n🎯 OCRテスト実行可能")
        
        return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test-only':
        # アクセステストのみ
        setup = VisionAPISetup()
        success = setup.test_vision_api_access()
        sys.exit(0 if success else 1)
    
    # 完全セットアップ
    setup = VisionAPISetup()
    success = setup.setup_complete_flow()
    
    if success:
        print("\n🚀 OCRテストを実行できます:")
        print("  python3 /home/fujinosuke/google_vision_ocr_test.py /home/fujinosuke/telegram_images/telegram_image_6859639046_20250615_200032.jpg")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()