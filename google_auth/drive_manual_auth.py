#!/usr/bin/env python3
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Drive API スコープ
SCOPES = ['https://www.googleapis.com/auth/drive']

def manual_drive_auth():
    """手動でGoogle Drive認証を実行"""
    
    print('=== Google Drive API 手動認証 ===')
    
    # credentials.jsonの存在確認
    creds_file = '/home/fujinosuke/credentials_drive.json'
    if not os.path.exists(creds_file):
        print(f'認証ファイルが見つかりません: {creds_file}')
        return False
    
    try:
        # OAuth flow を作成
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
        
        # 認証URLを生成
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        
        print('\\n1. 以下のURLをブラウザで開いてください:')
        print(f'{auth_url}')
        print('\\n2. Googleアカウントでログインし、権限を許可してください')
        print('3. 認証コードをコピーしてください')
        print('\\n認証コード入力待機中...')
        
        # 手動で認証コードを提供
        # この部分は実際の運用では入力プロンプトになります
        print('\\n認証が必要です。ブラウザで上記URLにアクセスして認証コードを取得してください。')
        print('認証コードを使用してトークンを作成するには、以下のコードを実行してください:')
        print()
        print('# 認証コードを取得後、以下を実行:')
        print('flow.fetch_token(code="YOUR_AUTH_CODE_HERE")')
        print('creds = flow.credentials')
        print('pickle.dump(creds, open("/home/fujinosuke/token_drive.pickle", "wb"))')
        
        return auth_url
        
    except Exception as e:
        print(f'認証エラー: {e}')
        return False

def test_existing_drive_token():
    """既存のDriveトークンをテスト"""
    token_file = '/home/fujinosuke/token_drive.pickle'
    
    if not os.path.exists(token_file):
        print('Driveトークンが存在しません')
        return False
    
    try:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
        
        # トークンの有効性確認
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # 更新されたトークンを保存
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print('Driveトークンをリフレッシュしました')
            else:
                print('トークンが無効です')
                return False
        
        # Drive APIテスト
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        print(f'✅ Google Drive接続成功! ファイル数: {len(files)}')
        for file in files[:3]:
            print(f'  📁 {file["name"]}')
        
        return True
        
    except Exception as e:
        print(f'Driveトークンテストエラー: {e}')
        return False

if __name__ == '__main__':
    # 既存トークンテスト
    if test_existing_drive_token():
        print('Google Drive接続完了!')
    else:
        print('新しい認証が必要です:')
        manual_drive_auth()