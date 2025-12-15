#!/usr/bin/env python3
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Drive API スコープ
SCOPES = ['https://www.googleapis.com/auth/drive']

def fix_drive_auth():
    """動作中のGoogle認証設定を使用してDrive認証を修正"""
    
    print('=== Google Drive認証修正 ===')
    
    # 動作中のGoogle認証ファイルを使用
    working_creds_files = [
        '/home/fujinosuke/google/credentials.json',  # 動作中のContacts認証
        '/home/fujinosuke/google_api/credentials.json'  # 別の動作中認証
    ]
    
    for creds_file in working_creds_files:
        if os.path.exists(creds_file):
            print(f'動作中の認証ファイルを使用: {creds_file}')
            
            try:
                # OAuth flowを作成（redirect_uri設定を修正）
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_file, 
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # 明示的にredirect_uriを指定
                )
                
                # 認証URLを生成
                auth_url, _ = flow.authorization_url(
                    prompt='consent', 
                    access_type='offline',
                    include_granted_scopes='true'
                )
                
                print('\\n✅ 修正済み認証URL:')
                print(f'{auth_url}')
                print('\\n📋 使用方法:')
                print('1. 上記URLをブラウザで開く')
                print('2. Googleアカウントでログイン・権限許可')
                print('3. 認証コードをコピー')
                print('4. 以下のコマンドで認証完了:')
                print()
                print('cd /home/fujinosuke/google_env && source bin/activate')
                print('python3 -c "')
                print('from google_auth_oauthlib.flow import InstalledAppFlow')
                print('import pickle')
                print(f'flow = InstalledAppFlow.from_client_secrets_file(\\"{creds_file}\\", [\\\"https://www.googleapis.com/auth/drive\\\"], redirect_uri=\\\"urn:ietf:wg:oauth:2.0:oob\\\")')
                print('flow.fetch_token(code=\\\"YOUR_AUTH_CODE_HERE\\\")')
                print('pickle.dump(flow.credentials, open(\\\"/home/fujinosuke/token_drive.pickle\\\", \\\"wb\\\"))')
                print('print(\\\"Drive認証完了!\\\")')
                print('"')
                
                return True
                
            except Exception as e:
                print(f'認証ファイル {creds_file} でエラー: {e}')
                continue
    
    print('動作中の認証ファイルが見つかりません')
    return False

def create_simple_drive_test():
    """簡易Drive接続テスト用スクリプトを作成"""
    test_script = '''#!/usr/bin/env python3
import pickle
import os
from googleapiclient.discovery import build

def test_drive_connection():
    """Drive接続をテスト"""
    token_file = '/home/fujinosuke/token_drive.pickle'
    
    if not os.path.exists(token_file):
        print('❌ Driveトークンが見つかりません')
        return False
    
    try:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
        
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=10, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        print(f'✅ Google Drive接続成功!')
        print(f'📁 ファイル数: {len(files)}')
        
        for i, file in enumerate(files[:5]):
            print(f'  {i+1}. {file["name"]} ({file.get("mimeType", "unknown")})')
        
        return True
        
    except Exception as e:
        print(f'❌ Drive接続エラー: {e}')
        return False

if __name__ == '__main__':
    test_drive_connection()
'''
    
    with open('/home/fujinosuke/test_drive_connection.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print('Drive接続テストスクリプトを作成: /home/fujinosuke/test_drive_connection.py')

if __name__ == '__main__':
    if fix_drive_auth():
        create_simple_drive_test()
    else:
        print('認証修正に失敗しました')