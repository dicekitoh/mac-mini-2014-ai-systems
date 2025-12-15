#!/usr/bin/env python3
"""
Google Contacts認証トークン作成
"""

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts.pickle'

def create_contacts_token():
    """Google Contacts認証トークンを作成"""
    creds = None
    
    # 既存トークンを削除
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
    
    # 新しいフローでブラウザを使わずに認証
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES)
    
    # 手動認証フローを開始
    print("=== Google Contacts認証が必要です ===")
    print("以下のURLにアクセスしてください:")
    
    # 認証URLを取得
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"\n{auth_url}\n")
    
    # 認証コードを手動入力
    auth_code = input("認証コードを入力してください: ")
    
    # トークンを取得
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    
    # トークンを保存
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ Google Contacts認証トークンを作成しました: {TOKEN_FILE}")
    return creds

if __name__ == '__main__':
    create_contacts_token()