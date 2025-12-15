#!/usr/bin/env python3
"""
Google Contacts認証完了（手動コード入力）
"""

import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_verified.pickle'
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def complete_auth_manual(auth_code):
    """手動認証コードで認証完了"""
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # 認証コードでトークン取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークン保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Google Contacts認証完了！")
        print("google_contacts_direct_auth.py を再実行してください")
        return True
        
    except Exception as e:
        print(f"❌ 認証エラー: {e}")
        return False

if __name__ == '__main__':
    print("=== Google Contacts 手動認証完了 ===")
    auth_code = input("認証コードを入力してください: ").strip()
    
    if auth_code:
        complete_auth_manual(auth_code)
    else:
        print("認証コードが入力されませんでした")