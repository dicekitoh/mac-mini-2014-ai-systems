#!/usr/bin/env python3
import os
import sys
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def setup_drive_auth_with_code(auth_code=None):
    """Google Drive API認証のセットアップ（コード付き）"""
    print('=== Google Drive API 認証セットアップ ===\n')
    
    # 認証情報ファイルの確認
    cred_file = '/home/fujinosuke/google/credentials.json'
    if not os.path.exists(cred_file):
        print('❌ 認証情報ファイルが見つかりません')
        return False
    
    with open(cred_file, 'r') as f:
        cred_data = json.load(f)
        client_id = cred_data['installed']['client_id']
        print(f'✅ 認証情報ファイル: {cred_file}')
        print(f'📋 Client ID: {client_id[:30]}...\n')
    
    # 認証フロー開始
    flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
    
    if not auth_code:
        # 認証URLを生成
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )
        
        print('📝 以下のURLをブラウザで開いて認証してください:\n')
        print('=' * 80)
        print(auth_url)
        print('=' * 80)
        print('\n認証後、表示されるコードを以下のコマンドで入力してください:')
        print(f'python3 {sys.argv[0]} "認証コード"')
        return False
    
    try:
        # 認証コードでトークンを取得
        print(f'🔐 認証コードでトークンを取得中...')
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークンを保存（google_authディレクトリに保存）
        token_dir = '/home/fujinosuke/projects/google_auth'
        os.makedirs(token_dir, exist_ok=True)
        token_file = os.path.join(token_dir, 'token_drive.pickle')
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f'\n✅ 認証成功！')
        print(f'💾 トークンを保存しました: {token_file}')
        
        # Drive APIでテスト
        print('\n🔍 Google Drive接続テスト中...')
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=5,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print('\n📁 Google Driveのファイル（最初の5件）:')
            for file in files:
                print(f"  - {file['name']} ({file.get('mimeType', 'unknown')})")
        else:
            print('\n📁 Google Driveにファイルがありません')
        
        return True
            
    except Exception as e:
        print(f'\n❌ 認証エラー: {e}')
        print('\n💡 考えられる原因:')
        print('  1. 認証コードが正しくない')
        print('  2. 認証コードの有効期限が切れた（数分で期限切れ）')
        print('  3. Google Drive APIが有効になっていない')
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # コマンドライン引数から認証コードを取得
        auth_code = sys.argv[1]
        setup_drive_auth_with_code(auth_code)
    else:
        # 認証URLを表示
        setup_drive_auth_with_code()