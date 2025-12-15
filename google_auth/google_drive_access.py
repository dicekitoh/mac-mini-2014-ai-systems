#\!/usr/bin/env python3
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Drive API のスコープ
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    """Google Drive API の認証を行う"""
    creds = None
    token_file = 'token_drive.pickle'
    
    # 既存のトークンをロード
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # トークンが無効な場合は再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 既存の認証情報ファイルを使用
            if os.path.exists('/home/fujinosuke/google/credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/home/fujinosuke/google/credentials.json', SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            
            # ローカルサーバーなしで認証
            creds = flow.run_local_server(port=0)
        
        # トークンを保存
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def list_files(service, query=None):
    """Google Drive のファイル一覧を取得"""
    try:
        # デフォルトクエリ
        if not query:
            query = "'root' in parents and trashed = false"
        
        results = service.files().list(
            q=query,
            pageSize=20,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print('ファイルが見つかりませんでした。')
            return
        
        print(f'\n見つかったファイル数: {len(items)}\n')
        print(f'{名前:<40} {タイプ:<30} {更新日時:<20}')
        print('-' * 90)
        
        for item in items:
            name = item['name'][:40]
            mime = item['mimeType'].split('.')[-1][:30]
            modified = item.get('modifiedTime', 'N/A')[:19]
            print(f'{name:<40} {mime:<30} {modified:<20}')
        
    except HttpError as error:
        print(f'エラーが発生しました: {error}')

def main():
    """メイン処理"""
    print('Google Drive に接続しています...')
    
    # 認証
    creds = authenticate()
    
    # Drive API サービスを構築
    service = build('drive', 'v3', credentials=creds)
    
    print('\n=== Google Drive ファイル一覧 ===')
    
    # ルートディレクトリのファイルを表示
    list_files(service)
    
    # 最近変更されたファイルを表示
    print('\n\n=== 最近変更されたファイル ===')
    list_files(service, "trashed = false order by modifiedTime desc")

if __name__ == '__main__':
    main()
