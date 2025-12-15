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
    """Google Drive API の認証を行う（ヘッドレス）"""
    creds = None
    token_file = 'token_drive.pickle'
    
    # 既存のトークンをロード
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # 既存の連絡先トークンを試す
    if not creds and os.path.exists('/home/fujinosuke/google/token_contacts_real.pickle'):
        try:
            with open('/home/fujinosuke/google/token_contacts_real.pickle', 'rb') as token:
                creds = pickle.load(token)
            # スコープを更新
            creds._scopes = SCOPES
            creds.refresh(Request())
            print('既存の認証情報を使用して Google Drive に接続しました。')
        except Exception as e:
            print(f'既存トークンの使用に失敗: {e}')
            creds = None
    
    # トークンが無効な場合は再認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None
        
        if not creds:
            print('\n新しい認証が必要です。')
            print('以下のURLをブラウザで開いて認証してください:')
            
            if os.path.exists('/home/fujinosuke/google/credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/home/fujinosuke/google/credentials.json', SCOPES)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
            
            # 認証URLを生成
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f'\n{auth_url}\n')
            
            # 認証コードを入力
            code = input('認証コードを入力してください: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
        
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
    
    try:
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
        
    except Exception as e:
        print(f'エラー: {e}')
        print('\nGoogle Drive APIが有効になっていない可能性があります。')
        print('以下のURLでDrive APIを有効にしてください:')
        print('https://console.cloud.google.com/apis/library/drive.googleapis.com')

if __name__ == '__main__':
    main()
