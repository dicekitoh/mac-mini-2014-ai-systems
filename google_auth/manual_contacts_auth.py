#!/usr/bin/env python3
"""
Google Contacts手動認証
認証コード: 4/0AeanS0biWw5F4gkmr8rHmxelJ4l5HMj9OisBnlHwJGvKZKJH3i6tBpwm9meCNFl1zJfKAQ
"""

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts.pickle'

def create_contacts_token_manual():
    """手動認証コードでGoogle Contactsトークンを作成"""
    
    # 認証コード（手動で取得済み）
    auth_code = "4/0AeanS0biWw5F4gkmr8rHmxelJ4l5HMj9OisBnlHwJGvKZKJH3i6tBpwm9meCNFl1zJfKAQ"
    
    # 新しいフローを作成
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE, SCOPES)
    
    # 手動認証フロー
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    try:
        # トークンを取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ Google Contacts認証トークンを作成しました: {TOKEN_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return False

if __name__ == '__main__':
    create_contacts_token_manual()