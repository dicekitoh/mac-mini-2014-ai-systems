#!/usr/bin/env python3
"""
既存のGoogle認証を使用してDriveアクセスを試行
"""

import requests
import json
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def try_existing_tokens():
    """既存のトークンでDriveアクセスを試す"""
    
    # 既存のトークンファイルパス（MacMini2014の情報から）
    token_paths = [
        '/home/rootmax/token_drive.pickle',  # 今回作成予定
        # MacMini2014のパス（アクセス可能になったら）
        # '/home/fujinosuke/google/token_contacts_real.pickle',
        # '/home/fujinosuke/google_contacts/token.pickle'
    ]
    
    for token_path in token_paths:
        if os.path.exists(token_path):
            print(f"✓ トークンファイル発見: {token_path}")
            try:
                with open(token_path, 'rb') as f:
                    creds = pickle.load(f)
                
                # スコープを確認
                if hasattr(creds, 'scopes'):
                    print(f"  現在のスコープ: {creds.scopes}")
                
                # トークンを更新
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    print("  トークンを更新しました")
                
                # Drive APIテスト
                headers = {'Authorization': f'Bearer {creds.token}'}
                response = requests.get(
                    'https://www.googleapis.com/drive/v3/files?pageSize=5',
                    headers=headers
                )
                
                if response.status_code == 200:
                    files_data = response.json()
                    files = files_data.get('files', [])
                    print(f"✓ Google Driveアクセス成功！ファイル数: {len(files)}")
                    
                    for file in files[:5]:
                        print(f"  📄 {file.get('name', 'Unknown')}")
                    
                    return True
                else:
                    print(f"  ✗ Drive APIアクセス失敗: {response.status_code}")
                    if response.status_code == 403:
                        error_data = response.json()
                        print(f"     エラー: {error_data.get('error', {}).get('message', 'Unknown')}")
                        if 'insufficient permissions' in str(error_data):
                            print("     → スコープが不足しています")
                        
            except Exception as e:
                print(f"  ✗ エラー: {e}")
    
    return False

def create_manual_drive_request():
    """手動でDriveアクセスリクエストを作成"""
    
    print("\n=== 手動Google Drive APIアクセス ===")
    
    # 公開Drive APIを使用（認証なし）
    public_test_url = "https://www.googleapis.com/drive/v3/about?fields=user"
    
    print("パブリックAPI テスト:")
    response = requests.get(public_test_url)
    print(f"レスポンス: {response.status_code}")
    
    if response.status_code == 401:
        print("✓ 正常（認証が必要なAPIです）")
    
    # 新しいOAuth設定の提案
    print("\n=== 新しいアプローチ ===")
    print("1. 個人Googleアカウントで新しいプロジェクトを作成")
    print("2. そのプロジェクトでDrive APIを有効化")
    print("3. 新しいOAuth認証情報を作成")
    
    # 代替案: rcloneの再設定
    print("\n=== rclone 再設定案 ===")
    print("MacMini2014でrclone config を実行して新しい認証を設定する方法:")
    print("1. rclone config")
    print("2. n (new remote)")
    print("3. name: mydrive")
    print("4. storage: drive")
    print("5. client_id, client_secret: 空白（デフォルト使用）")
    print("6. ブラウザで認証")

def create_simple_drive_test():
    """シンプルなDriveテストスクリプトを作成"""
    
    script_content = '''#!/usr/bin/env python3
"""
MacMini2014用 Google Driveアクセステスト
"""

import subprocess
import json

def test_rclone_drive():
    """rcloneでDriveアクセスをテスト"""
    try:
        # 設定済みリモートを確認
        result = subprocess.run(['rclone', 'listremotes'], 
                              capture_output=True, text=True)
        print("設定済みリモート:")
        print(result.stdout)
        
        # Driveアクセスを試行
        for remote in ['googledrive:', 'e:']:
            print(f"\\n{remote} をテスト中...")
            
            # ファイル数確認
            result = subprocess.run(['rclone', 'size', remote], 
                                  capture_output=True, text=True, 
                                  timeout=30)
            
            if result.returncode == 0:
                print(f"✓ {remote} アクセス成功")
                print(result.stdout)
                
                # ファイル一覧
                list_result = subprocess.run(['rclone', 'ls', remote], 
                                           capture_output=True, text=True,
                                           timeout=30)
                if list_result.returncode == 0:
                    lines = list_result.stdout.split('\\n')[:10]
                    print("\\nファイル一覧（最初の10件）:")
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
                
                return True
            else:
                print(f"✗ {remote} アクセス失敗")
                if "Failed to create file system" in result.stderr:
                    print("  → 認証が必要です")
                    
    except Exception as e:
        print(f"エラー: {e}")
    
    return False

if __name__ == "__main__":
    print("=== MacMini2014 Google Drive テスト ===")
    test_rclone_drive()
'''
    
    with open('/home/rootmax/macmini_drive_test.py', 'w') as f:
        f.write(script_content)
    
    print("\n✓ MacMini2014用テストスクリプトを作成: macmini_drive_test.py")

def main():
    print("=== Google Drive アクセス 既存認証利用 ===\n")
    
    # 既存トークンを試す
    if not try_existing_tokens():
        print("\n既存トークンでのアクセスに失敗しました")
        
        # 代替案を提示
        create_manual_drive_request()
        create_simple_drive_test()
        
        print("\n=== 推奨対応 ===")
        print("1. MacMini2014接続復旧後、rclone config で再設定")
        print("2. または個人Googleアカウントで新プロジェクト作成")
        print("3. MacMini2014用テストスクリプト実行")

if __name__ == "__main__":
    main()