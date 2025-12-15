#!/usr/bin/env python3
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Drive API スコープ
SCOPES = ['https://www.googleapis.com/auth/drive']

def create_drive_token():
    """Google Drive用のトークンを作成"""
    
    # 既存のGoogle認証トークンを確認
    existing_tokens = [
        '/home/fujinosuke/google/token_contacts_real.pickle',
        '/home/fujinosuke/google_contacts/token.pickle',
        '/home/fujinosuke/google_tasks_new.pickle'
    ]
    
    creds = None
    
    # 既存のトークンからGoogle認証情報を取得
    for token_file in existing_tokens:
        if os.path.exists(token_file):
            try:
                with open(token_file, 'rb') as token:
                    test_creds = pickle.load(token)
                    
                # 新しいスコープでリフレッシュトークンを使用
                if hasattr(test_creds, 'refresh_token') and test_creds.refresh_token:
                    print(f'Using refresh token from: {token_file}')
                    
                    # 新しいクレデンシャルを作成
                    creds = Credentials(
                        token=None,
                        refresh_token=test_creds.refresh_token,
                        token_uri=test_creds.token_uri,
                        client_id=test_creds.client_id,
                        client_secret=test_creds.client_secret,
                        scopes=SCOPES
                    )
                    
                    # トークンをリフレッシュ
                    creds.refresh(Request())
                    print('Drive token created successfully using refresh token!')
                    break
                    
            except Exception as e:
                print(f'Failed to use token from {token_file}: {e}')
                continue
    
    if creds and creds.valid:
        # Drive用トークンを保存
        with open('/home/fujinosuke/token_drive.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        # Drive APIテスト
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        print(f'Drive API test successful! Found {len(files)} files:')
        for file in files[:3]:
            print(f'  - {file["name"]}')
        
        return True
    else:
        print('Failed to create valid Drive credentials')
        return False

if __name__ == '__main__':
    create_drive_token()