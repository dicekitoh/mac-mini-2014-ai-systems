#!/usr/bin/env python3
"""
Google Contacts APIトークン更新スクリプト
期限切れトークンを新しいトークンで更新
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

def refresh_contacts_token():
    """Google Contactsトークン更新"""
    creds = None
    
    print("🔐 Google Contactsトークン更新開始")
    print(f"認証ファイル: {CREDENTIALS_FILE}")
    print(f"トークンファイル: {TOKEN_FILE}")
    
    # 既存トークンを確認
    if os.path.exists(TOKEN_FILE):
        print("📁 既存トークンファイル発見")
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            print("✅ 既存トークン読み込み成功")
        except Exception as e:
            print(f"❌ 既存トークン読み込みエラー: {e}")
            creds = None
    
    # トークンの更新または新規取得
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 トークン更新を試行中...")
            try:
                creds.refresh(Request())
                print("✅ トークン更新成功")
            except Exception as e:
                print(f"❌ トークン更新失敗: {e}")
                print("🆕 新規認証を開始します")
                creds = None
        
        if not creds:
            print("🆕 新規認証フローを開始")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=8080)
                print("✅ 新規認証成功")
            except Exception as e:
                print(f"❌ 新規認証エラー: {e}")
                return False
    
    # トークンを保存
    try:
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print(f"💾 トークンファイル保存成功: {TOKEN_FILE}")
    except Exception as e:
        print(f"❌ トークンファイル保存エラー: {e}")
        return False
    
    # 接続テスト
    try:
        service = build('people', 'v1', credentials=creds)
        
        # 簡単な接続テスト
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1,
            personFields='names'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"🧪 接続テスト成功: {len(connections)}件の連絡先にアクセス可能")
        print("✅ Google Contacts API準備完了")
        return True
        
    except Exception as e:
        print(f"❌ 接続テストエラー: {e}")
        return False

def main():
    """メイン関数"""
    print("🔧 Google Contacts APIトークン更新ツール")
    print("=" * 50)
    
    success = refresh_contacts_token()
    
    if success:
        print("\n🎉 トークン更新完了！")
        print("これでN8Nワークフローで使用可能です")
    else:
        print("\n❌ トークン更新失敗")
        print("認証設定を確認してください")

if __name__ == "__main__":
    main()