#\!/usr/bin/env python3
import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def setup_drive_auth():
    """Google Drive API認証のセットアップ"""
    print('=== Google Drive API 認証セットアップ ===\n')
    
    # 認証情報ファイルの確認
    cred_file = '/home/fujinosuke/google/credentials.json'
    if os.path.exists(cred_file):
        with open(cred_file, 'r') as f:
            cred_data = json.load(f)
            client_id = cred_data['installed']['client_id']
            print(f'認証情報ファイル: {cred_file}')
            print(f'Client ID: {client_id[:30]}...')
            print(f'プロジェクト: civil-authority-462513-a9\n')
    else:
        print('認証情報ファイルが見つかりません')
        return
    
    # 認証フロー開始
    flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
    
    # 認証URLを生成
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    
    print('以下の手順で認証を行ってください:\n')
    print('1. 下記のURLをブラウザで開く')
    print('2. Googleアカウントでログイン')
    print('3. 「このアプリを信頼しますか？」で「許可」をクリック')
    print('4. 表示される認証コードをコピー\n')
    
    print('認証URL:')
    print('=' * 80)
    print(auth_url)
    print('=' * 80)
    print()
    
    # 認証コード入力待ち
    print('認証コードを入力してください（または「quit」で終了）:')
    code = input('> ')
    
    if code.lower() == 'quit':
        print('認証をキャンセルしました')
        return
    
    try:
        # 認証コードでトークンを取得
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # トークンを保存
        token_file = '/home/fujinosuke/google/token_drive.pickle'
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print('\n認証成功！')
        print(f'トークンを保存しました: {token_file}')
        
        # Drive APIでテスト
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=5,
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print('\nGoogle Driveのファイル（最初の5件）:')
            for file in files:
                print(f"- {file['name']}")
        else:
            print('\nGoogle Driveにファイルがありません')
            
    except Exception as e:
        print(f'\n認証エラー: {e}')
        print('\n考えられる原因:')
        print('1. 認証コードが正しくない')
        print('2. Google Drive APIが有効になっていない')
        print('3. 認証コードの有効期限が切れた（数分で期限切れ）')
        print('\nGoogle Cloud Consoleで確認してください:')
        print('https://console.cloud.google.com/apis/library/drive.googleapis.com?project=civil-authority-462513-a9')

if __name__ == '__main__':
    setup_drive_auth()
