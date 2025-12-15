#\!/usr/bin/env python3
import os
import sys
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_with_code(auth_code):
    """認証コードを使ってGoogle Drive APIの認証を行う"""
    
    # 認証情報ファイル
    cred_file = '/home/fujinosuke/google/credentials.json'
    if not os.path.exists(cred_file):
        print('認証情報ファイルが見つかりません')
        return False
    
    try:
        # 認証フロー
        flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
        
        # 認証URLを生成（stateを取得するため）
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        # 認証コードでトークンを取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークンを保存
        token_file = '/home/fujinosuke/google/token_drive.pickle'
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print('認証成功！')
        print(f'トークンを保存しました: {token_file}')
        
        # Drive APIでテスト
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=10,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print('\nGoogle Driveのファイル:')
            for file in files:
                print(f"- {file['name']} ({file['mimeType']})")
        else:
            print('\nGoogle Driveにファイルがありません')
            
        return True
        
    except Exception as e:
        print(f'認証エラー: {e}')
        return False

def show_auth_url():
    """認証URLを表示"""
    cred_file = '/home/fujinosuke/google/credentials.json'
    flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    print('\n認証URL:')
    print('=' * 80)
    print(auth_url)
    print('=' * 80)
    print('\n上記URLをブラウザで開いて、認証コードを取得してください。')
    print('その後、このスクリプトを以下のように実行してください:')
    print(f'python3 {os.path.basename(__file__)} <認証コード>')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        auth_code = sys.argv[1]
        print(f'認証コードで認証を試みます...')
        authenticate_with_code(auth_code)
    else:
        show_auth_url()
