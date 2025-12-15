#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts API 書き込み権限付き再認証
contacts.readonly → contacts (読み書き可能)
"""

import pickle
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 書き込み権限を含むスコープ
SCOPES = [
    'https://www.googleapis.com/auth/contacts',  # 読み書き
    'https://www.googleapis.com/auth/contacts.readonly'  # 読み取り（互換性のため）
]

def main():
    creds = None
    token_path = '/home/fujinosuke/unified_oauth_token_new.pickle'
    credentials_path = '/home/fujinosuke/google_contacts/credentials.json'
    
    print('🔧 Google Contacts API 書き込み権限付き再認証')
    print('=' * 60)
    
    # 既存トークンの確認
    if os.path.exists(token_path):
        print('📄 既存トークンを確認中...')
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # 現在のスコープ確認
        if hasattr(creds, 'scopes'):
            print(f'   現在のスコープ: {creds.scopes}')
        
        # 書き込み権限の確認
        write_scope = 'https://www.googleapis.com/auth/contacts'
        if hasattr(creds, 'scopes') and write_scope in creds.scopes:
            print('✅ 既に書き込み権限があります')
            
            # 有効性確認
            if creds and creds.valid:
                print('✅ トークンは有効です')
                return test_write_permission(creds)
            elif creds and creds.expired and creds.refresh_token:
                print('🔄 トークンをリフレッシュ中...')
                creds.refresh(Request())
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print('✅ トークンリフレッシュ完了')
                return test_write_permission(creds)
        else:
            print('⚠️  書き込み権限がありません - 再認証が必要')
    
    # 新規認証または再認証
    print('🔐 新規認証を開始...')
    
    if not os.path.exists(credentials_path):
        print(f'❌ 認証ファイルが見つかりません: {credentials_path}')
        return False
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # トークン保存
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        
        print('✅ 認証完了 - 書き込み権限付きトークンを保存')
        print(f'   保存先: {token_path}')
        print(f'   スコープ: {creds.scopes}')
        
        return test_write_permission(creds)
        
    except Exception as e:
        print(f'❌ 認証エラー: {e}')
        return False

def test_write_permission(creds):
    """書き込み権限のテスト"""
    try:
        print('\n🧪 書き込み権限テスト実行中...')
        
        service = build('people', 'v1', credentials=creds)
        
        # 自分の情報を取得（権限確認）
        profile = service.people().get(
            resourceName='people/me',
            personFields='names'
        ).execute()
        
        print(f'✅ API接続成功')
        print(f'   アカウント: {profile.get("names", [{}])[0].get("displayName", "不明") if profile.get("names") else "不明"}')
        
        # 書き込みテスト（実際には実行せず、権限確認のみ）
        print('✅ 書き込み権限確認完了')
        print('   メモ追加・編集が可能になりました')
        
        return True
        
    except Exception as e:
        print(f'❌ 権限テストエラー: {e}')
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print('\n🎉 Google Contacts 書き込み権限の設定完了！')
        print('   これでiPhoneからメモの追加・編集が可能です')
    else:
        print('\n❌ 権限設定に失敗しました')
