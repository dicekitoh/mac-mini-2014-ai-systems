#!/usr/bin/env python3
"""
Google Docs API クイックテスト
サービスアカウント認証用
"""

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = '/home/fujinosuke/google_docs_service_key.json'
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def quick_test():
    if not os.path.exists(KEY_FILE):
        print(f"❌ サービスアカウントキーファイルが必要: {KEY_FILE}")
        return False
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE, scopes=SCOPES)
        
        docs_service = build('docs', 'v1', credentials=credentials)
        
        # 簡単なドキュメント作成テスト
        doc = docs_service.documents().create(
            body={'title': 'テスト成功！'}).execute()
        
        print(f"✅ 成功! ドキュメントID: {doc['documentId']}")
        print(f"URL: https://docs.google.com/document/d/{doc['documentId']}/edit")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    quick_test()
