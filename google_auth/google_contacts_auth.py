#!/usr/bin/env python3
"""
Google Contacts API認証スクリプト
初回認証用
"""

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'

def authenticate_google_contacts():
    """Google Contacts API認証"""
    creds = None
    
    # トークンファイルが存在する場合はロード
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ トークンを更新しました")
            except Exception as e:
                print(f"❌ トークン更新エラー: {e}")
                creds = None
        
        if not creds:
            # 新規認証フロー
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ 認証ファイルが見つかりません: {CREDENTIALS_FILE}")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ 新規認証を完了しました")
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print(f"✅ トークンを保存しました: {TOKEN_FILE}")
    
    return creds

def test_api_connection(creds):
    """API接続テスト"""
    try:
        service = build('people', 'v1', credentials=creds)
        
        # 基本的な接続テスト - 少数の連絡先を取得
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=10,
            personFields='names'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"✅ API接続成功: {len(connections)}件の連絡先にアクセス可能")
        
        # 連絡先の一部を表示
        print("\n🔍 最初の連絡先（テスト）:")
        for i, person in enumerate(connections[:3]):
            names = person.get('names', [])
            if names:
                display_name = names[0].get('displayName', 'Unknown')
                print(f"  {i+1}. {display_name}")
        
        return service
        
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
        return None

def main():
    """メイン関数"""
    print("🔑 Google Contacts API認証システム")
    print("=" * 40)
    
    # 認証実行
    creds = authenticate_google_contacts()
    if not creds:
        print("❌ 認証に失敗しました")
        return
    
    print("✅ 認証成功")
    
    # API接続テスト
    service = test_api_connection(creds)
    if service:
        print("\n✅ Google Contacts APIの準備が完了しました")
        print(f"トークンファイル: {TOKEN_FILE}")
    else:
        print("❌ API接続テストに失敗しました")

if __name__ == "__main__":
    main()