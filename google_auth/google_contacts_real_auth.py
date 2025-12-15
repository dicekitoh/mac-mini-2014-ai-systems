#!/usr/bin/env python3
"""
Google Contacts 本格認証システム
実際のGoogle Contactsから連絡先を取得
"""

import pickle
import os.path
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'

def setup_google_contacts_auth():
    """Google Contacts認証セットアップ（手動フロー）"""
    print("=== Google Contacts 本格認証開始 ===")
    
    # 既存トークンを削除
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("既存トークンを削除しました")
    
    try:
        # 認証フロー作成
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        
        # 手動認証URL生成
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print(f"\\n以下のURLにアクセスして認証してください:")
        print(f"{auth_url}")
        print("\\n認証後に表示される認証コードをコピーしてください")
        
        # 認証情報をファイルに保存（手動入力用）
        auth_info = {
            "auth_url": auth_url,
            "redirect_uri": flow.redirect_uri,
            "client_id": flow.client_config['client_id'],
            "client_secret": flow.client_config['client_secret'],
            "scopes": SCOPES
        }
        
        with open('/home/fujinosuke/google/contacts_auth_info.json', 'w') as f:
            json.dump(auth_info, f, indent=2)
        
        print("\\n認証情報を /home/fujinosuke/google/contacts_auth_info.json に保存しました")
        print("\\n次のステップ:")
        print("1. 上記URLにアクセス")
        print("2. Googleアカウントでログイン")
        print("3. 連絡先へのアクセスを許可")
        print("4. 表示される認証コードをメモ")
        print("5. complete_contacts_auth.py スクリプトで認証完了")
        
        return True
        
    except Exception as e:
        print(f"認証セットアップエラー: {e}")
        return False

def test_existing_auth():
    """既存認証のテスト"""
    if not os.path.exists(TOKEN_FILE):
        print("認証トークンが存在しません")
        return False
    
    try:
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
        
        if creds and creds.valid:
            service = build('people', 'v1', credentials=creds)
            
            # テスト検索
            results = service.people().connections().list(
                resourceName='people/me',
                pageSize=10,
                personFields='names,phoneNumbers'
            ).execute()
            
            connections = results.get('connections', [])
            print(f"✅ Google Contacts接続成功: {len(connections)}件の連絡先を取得")
            return True
            
    except Exception as e:
        print(f"認証テストエラー: {e}")
        return False

if __name__ == '__main__':
    # 既存認証をテスト
    if test_existing_auth():
        print("既存認証が有効です")
    else:
        # 新しい認証をセットアップ
        setup_google_contacts_auth()