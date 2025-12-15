#\!/usr/bin/env python3
# Google Tasks API認証セットアップスクリプト

import os
import pickle
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 設定
SCOPES = ['https://www.googleapis.com/auth/tasks']
TOKEN_FILE = 'google_tasks_token_new.pickle'
CREDENTIALS_JSON = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "project_id": "YOUR_PROJECT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["http://localhost"]
    }
}

def create_token():
    """新しいトークンを作成"""
    creds = None
    
    # 既存トークンを読み込み
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 有効なトークンがない場合は新規作成
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ トークンをリフレッシュしました")
            except Exception as e:
                print(f"❌ リフレッシュ失敗: {e}")
                creds = None
        
        if not creds:
            print("新しい認証フローを開始します...")
            print("\n重要: ブラウザが開かない場合は、表示されるURLを手動でブラウザに貼り付けてください")
            
            # 一時的にcredentials.jsonを作成
            with open('temp_credentials.json', 'w') as f:
                json.dump(CREDENTIALS_JSON, f)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'temp_credentials.json', SCOPES)
            
            # ポート8080でリダイレクトURIを設定
            creds = flow.run_local_server(port=8080, open_browser=False)
            
            # 一時ファイルを削除
            os.remove('temp_credentials.json')
            
            print("✅ 新しいトークンを取得しました")
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def test_api_connection(creds):
    """API接続をテスト"""
    try:
        service = build('tasks', 'v1', credentials=creds)
        
        # タスクリストを取得
        results = service.tasklists().list(maxResults=10).execute()
        lists = results.get('items', [])
        
        print(f"\n📋 タスクリスト数: {len(lists)}")
        for task_list in lists:
            print(f"  - {task_list['title']} (ID: {task_list['id']})")
        
        # 最初のリストにテストタスクを追加
        if lists:
            task = {
                'title': 'API接続テスト - 削除してOK',
                'notes': 'Google Tasks API接続テスト用タスク'
            }
            result = service.tasks().insert(
                tasklist=lists[0]['id'],
                body=task
            ).execute()
            print(f"\n✅ テストタスク作成成功: {result['title']}")
            return True
    except Exception as e:
        print(f"\n❌ API接続エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("Google Tasks API 認証セットアップ")
    print("=" * 50)
    
    # CLIENT_IDとCLIENT_SECRETが設定されているか確認
    if "YOUR_CLIENT_ID" in CREDENTIALS_JSON["installed"]["client_id"]:
        print("\n⚠️  CLIENT_IDとCLIENT_SECRETを設定してください")
        print("Google Cloud Consoleで取得した認証情報を使用します")
        print("https://console.cloud.google.com/apis/credentials")
        return
    
    # 認証実行
    creds = create_token()
    
    if creds:
        print("\n認証成功！API接続をテストします...")
        if test_api_connection(creds):
            print("\n🎉 Google Tasks API接続成功！")
            print(f"トークンファイル: {TOKEN_FILE}")
        else:
            print("\n⚠️  API接続に失敗しました")
    else:
        print("\n❌ 認証に失敗しました")

if __name__ == '__main__':
    main()
