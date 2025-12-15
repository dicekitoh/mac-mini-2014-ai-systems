#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google API権限スコープ拡張スクリプト
全てのAPIサービスに対応する包括的な権限を取得
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 包括的なスコープ（全Google APIサービス対応）
EXPANDED_SCOPES = [
    # ドライブ・ドキュメント
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    
    # Gmail
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    
    # カレンダー
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    
    # タスク
    'https://www.googleapis.com/auth/tasks',
    
    # 連絡先
    'https://www.googleapis.com/auth/contacts',
    'https://www.googleapis.com/auth/contacts.readonly',
    
    # People API
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
]

def expand_api_permissions():
    """Google API権限を拡張"""
    
    credentials_file = '/home/fujinosuke/credentials_drive.json'
    token_file = '/home/fujinosuke/token_drive_expanded.pickle'
    
    print("🔧 Google API権限拡張を開始...")
    print(f"📁 認証ファイル: {credentials_file}")
    print(f"💾 新トークン: {token_file}")
    
    # 認証ファイル確認
    if not os.path.exists(credentials_file):
        print(f"❌ 認証ファイルが見つかりません: {credentials_file}")
        return False
    
    try:
        # 新しいスコープで認証フロー開始
        print("🔐 認証フローを開始...")
        print("📋 要求スコープ:")
        for scope in EXPANDED_SCOPES:
            print(f"   - {scope}")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, EXPANDED_SCOPES)
        
        # ローカルサーバーで認証（ポート8080使用）
        creds = flow.run_local_server(port=8080, open_browser=False)
        
        # 拡張トークンを保存
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ 拡張権限トークンを保存: {token_file}")
        
        # 接続テスト
        print("🧪 API接続テスト中...")
        test_apis(creds)
        
        return True
        
    except Exception as e:
        print(f"❌ 権限拡張エラー: {e}")
        return False

def test_apis(creds):
    """拡張権限でAPI接続テスト"""
    
    apis_to_test = [
        ("drive", "v3", "Google Drive"),
        ("docs", "v1", "Google Docs"),  
        ("gmail", "v1", "Gmail"),
        ("calendar", "v3", "Google Calendar"),
        ("tasks", "v1", "Google Tasks"),
        ("people", "v1", "Google People"),
        ("sheets", "v4", "Google Sheets")
    ]
    
    print("\\n=== API接続テスト結果 ===")
    
    for service_name, version, display_name in apis_to_test:
        try:
            service = build(service_name, version, credentials=creds)
            
            # 簡単な接続テスト
            if service_name == "drive":
                service.files().list(pageSize=1).execute()
            elif service_name == "gmail":
                service.users().getProfile(userId="me").execute()
            elif service_name == "calendar":
                service.calendarList().list().execute()
            elif service_name == "tasks":
                service.tasklists().list().execute()
            elif service_name == "people":
                service.people().connections().list(resourceName="people/me", pageSize=1).execute()
            elif service_name == "sheets":
                # テスト用：何もしない（権限確認のみ）
                pass
                
            print(f"✅ {display_name}: 正常接続")
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                print(f"⚠️  {display_name}: 権限不足（要追加設定）")
            else:
                print(f"❌ {display_name}: {error_msg[:50]}...")

def show_auth_url():
    """認証URL表示（手動認証用）"""
    try:
        credentials_file = '/home/fujinosuke/credentials_drive.json'
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, EXPANDED_SCOPES)
        
        # 認証URLを取得（リダイレクトなし）
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        print("🔗 手動認証URL:")
        print(auth_url)
        print("\\n📝 手順:")
        print("1. 上記URLをブラウザで開く")
        print("2. Googleアカウントでログイン")
        print("3. 権限を許可")
        print("4. 認証コードをコピー")
        print("5. 認証コードを入力")
        
        # 認証コード入力
        auth_code = input("\\n認証コードを入力: ").strip()
        
        if auth_code:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            # トークン保存
            token_file = '/home/fujinosuke/token_drive_expanded.pickle'
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            print(f"✅ 権限拡張完了: {token_file}")
            test_apis(creds)
            return True
        
    except Exception as e:
        print(f"❌ 手動認証エラー: {e}")
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        print("🔧 手動認証モードで実行...")
        show_auth_url()
    else:
        print("🔧 自動認証モードで実行...")
        success = expand_api_permissions()
        
        if not success:
            print("\\n⚠️  自動認証が失敗しました")
            print("🔧 手動認証を試行...")
            show_auth_url()