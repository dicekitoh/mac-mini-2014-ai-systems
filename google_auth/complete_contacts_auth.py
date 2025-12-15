#!/usr/bin/env python3
"""
Google Contacts認証完了スクリプト
認証コードを使ってトークンを作成
"""

import pickle
import json
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'
AUTH_INFO_FILE = '/home/fujinosuke/google/contacts_auth_info.json'

def complete_auth_with_code(auth_code):
    """認証コードでトークン作成"""
    try:
        # 認証情報読み込み
        with open(AUTH_INFO_FILE, 'r') as f:
            auth_info = json.load(f)
        
        # フロー再作成
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, auth_info['scopes'])
        flow.redirect_uri = auth_info['redirect_uri']
        
        # 認証コードでトークン取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークン保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ Google Contacts認証完了！")
        print(f"トークンファイル: {TOKEN_FILE}")
        
        # 接続テスト
        test_connection(creds)
        return True
        
    except Exception as e:
        print(f"❌ 認証完了エラー: {e}")
        return False

def test_connection(creds):
    """Google Contacts接続テスト"""
    try:
        service = build('people', 'v1', credentials=creds)
        
        # 連絡先取得テスト
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=5,
            personFields='names,phoneNumbers,emailAddresses'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"\\n📞 Google Contacts接続テスト成功!")
        print(f"取得可能連絡先数: {len(connections)}件")
        
        # 最初の2件を表示
        for i, person in enumerate(connections[:2]):
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName', '名前不明')
                print(f"  {i+1}. {name}")
        
        print("\\n🎉 Contact Manager BOTで実際の連絡先検索が可能になりました！")
        
    except Exception as e:
        print(f"接続テストエラー: {e}")

# メイン実行部分
if __name__ == '__main__':
    print("=== Google Contacts認証コード入力 ===")
    
    # 認証コード入力（実際の値に置き換える）
    auth_code = input("認証コードを入力してください: ").strip()
    
    if auth_code:
        complete_auth_with_code(auth_code)
    else:
        print("認証コードが入力されませんでした")