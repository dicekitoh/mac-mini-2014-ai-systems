#!/usr/bin/env python3
"""
Google Drive API 認証完了スクリプト
"""

import json
import pickle
import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def exchange_code_for_token(auth_code):
    """認証コードをアクセストークンに交換"""
    
    # OAuth設定（正しいclient_secret使用）
    client_id = "136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com"
    client_secret = "***REMOVED***"  # 確認済み正しい値
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    
    # トークン交換エンドポイント
    token_url = "https://oauth2.googleapis.com/token"
    
    # リクエストデータ
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    # トークンを取得
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✓ トークン取得成功！")
        
        # Credentialsオブジェクトを作成
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_url,
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # トークンを保存
        token_file = '/home/rootmax/token_drive.pickle'
        with open(token_file, 'wb') as f:
            pickle.dump(creds, f)
        print(f"✓ トークンを保存しました: {token_file}")
        
        return creds
    else:
        print(f"✗ エラー: {response.status_code}")
        print(response.json())
        return None

def test_drive_access(creds):
    """Google Driveへのアクセスをテスト"""
    try:
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=creds)
        
        # ファイル一覧を取得
        results = service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            print(f"\n✓ Google Driveアクセス成功！")
            print(f"ファイル数: {len(files)}\n")
            
            print(f"{'ファイル名':<40} {'タイプ':<30} {'更新日時':<20}")
            print("-" * 90)
            
            for file in files:
                name = file['name'][:40]
                mime = file['mimeType'].split('.')[-1][:30]
                modified = file.get('modifiedTime', 'N/A')[:19]
                print(f"{name:<40} {mime:<30} {modified:<20}")
        else:
            print("\nGoogle Driveにファイルがありません")
            
        # MacMini2014用のスクリプトも作成
        create_macmini_script()
        
    except Exception as e:
        print(f"\n✗ エラー: {e}")

def create_macmini_script():
    """MacMini2014用のアクセススクリプトを作成"""
    script_content = '''#!/usr/bin/env python3
import pickle
import os
from googleapiclient.discovery import build

# トークンファイル
TOKEN_FILE = '/home/fujinosuke/google/token_drive.pickle'

def list_drive_files():
    """Google Driveのファイル一覧を表示"""
    
    # トークンを読み込み
    with open(TOKEN_FILE, 'rb') as f:
        creds = pickle.load(f)
    
    # Drive APIサービス
    service = build('drive', 'v3', credentials=creds)
    
    # ファイル一覧を取得
    results = service.files().list(
        pageSize=20,
        fields="files(id, name, mimeType, modifiedTime, size)"
    ).execute()
    
    files = results.get('files', [])
    
    print(f"\\nGoogle Driveファイル一覧 ({len(files)}件)\\n")
    
    for file in files:
        size_mb = int(file.get('size', 0)) / 1024 / 1024 if file.get('size') else 0
        print(f"📄 {file['name']}")
        print(f"   ID: {file['id']}")
        print(f"   タイプ: {file['mimeType']}")
        print(f"   サイズ: {size_mb:.2f} MB")
        print()

if __name__ == '__main__':
    list_drive_files()
'''
    
    with open('/home/rootmax/google_drive_access_macmini.py', 'w') as f:
        f.write(script_content)
    
    print("\n✓ MacMini2014用スクリプトを作成しました: google_drive_access_macmini.py")

# メイン処理
if __name__ == "__main__":
    auth_code = "4/1AUJR-x7Zb1E-uE7tWFzzBujODx4tIyM0Y6zaTfQzeGHPLp94glMKvsIKXko"
    
    print("=== Google Drive API 認証処理 ===\n")
    
    # トークンを取得
    creds = exchange_code_for_token(auth_code)
    
    if creds:
        # アクセステスト
        test_drive_access(creds)
        
        print("\n=== 認証完了 ===")
        print("\n今後のアクセス方法:")
        print("1. ローカル: python3 /home/rootmax/google_drive_access_macmini.py")
        print("2. MacMini2014にトークンをコピー後: python3 google_drive_access_macmini.py")