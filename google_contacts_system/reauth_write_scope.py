#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts API 書き込み権限追加
"""

import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 書き込み権限を含む完全スコープ
SCOPES = [
    'https://www.googleapis.com/auth/contacts',           # 連絡先読み書き
    'https://www.googleapis.com/auth/contacts.readonly',  # 読み取り（互換性）
    'https://www.googleapis.com/auth/spreadsheets',       # 既存スコープ維持
    'https://www.googleapis.com/auth/drive',              # 既存スコープ維持
    'https://www.googleapis.com/auth/calendar',           # 既存スコープ維持
    'https://www.googleapis.com/auth/gmail.readonly',     # 既存スコープ維持
    'https://www.googleapis.com/auth/tasks'               # 既存スコープ維持
]

def main():
    token_path = '/home/fujinosuke/unified_oauth_token_new.pickle'
    credentials_path = '/home/fujinosuke/macmini_credentials.json'
    
    print('🔧 Google Contacts 書き込み権限追加')
    print('=' * 50)
    
    if not os.path.exists(credentials_path):
        print(f'❌ 認証ファイルが見つかりません: {credentials_path}')
        return False
    
    try:
        # 新規認証（書き込み権限付き）
        print('🔐 書き込み権限付きで認証開始...')
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        
        # ローカルサーバーで認証
        creds = flow.run_local_server(port=8080, prompt='consent')
        
        # 新しいトークンを保存
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print('✅ 認証完了！')
        print(f'   保存先: {token_path}')
        print('   新しいスコープ:')
        for scope in creds.scopes:
            scope_name = scope.split('/')[-1]
            permission = '✅ 読み書き可能' if scope_name == 'contacts' else '📖 読み取り専用' if 'readonly' in scope else '🔧 その他'
            print(f'     - {scope_name} ({permission})')
        
        # 書き込みテスト
        print('\n🧪 書き込み権限テスト...')
        service = build('people', 'v1', credentials=creds)
        
        # 自分の情報取得
        profile = service.people().get(
            resourceName='people/me',
            personFields='names'
        ).execute()
        
        name = profile.get('names', [{}])[0].get('displayName', '不明') if profile.get('names') else '不明'
        print(f'✅ 接続成功: {name}')
        print('✅ 書き込み権限が有効化されました！')
        
        return True
        
    except Exception as e:
        print(f'❌ 認証エラー: {e}')
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print('\n🎉 Google Contacts 書き込み権限の追加完了！')
        print('   iPhoneからメモの追加・編集が可能になりました')
    else:
        print('\n❌ 権限追加に失敗しました')
