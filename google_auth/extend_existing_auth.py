#!/usr/bin/env python3
"""
既存のGoogle認証を拡張してDriveアクセスを追加
"""

import json
import requests

def test_different_client_secrets():
    """異なるclient_secretを試す"""
    
    # 可能性のあるclient_secret値
    possible_secrets = [
        "***REMOVED***",
        "***REMOVED***",  # 確認用
    ]
    
    client_id = "136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com"
    auth_code = "4/1AUJR-x7Zb1E-uE7tWFzzBujODx4tIyM0Y6zaTfQzeGHPLp94glMKvsIKXko"
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    
    print("=== Google Drive API 認証テスト ===\n")
    
    for i, client_secret in enumerate(possible_secrets, 1):
        print(f"テスト {i}: {client_secret[:20]}...")
        
        data = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post("https://oauth2.googleapis.com/token", data=data)
        
        if response.status_code == 200:
            print("✓ 成功！")
            token_data = response.json()
            
            # アクセストークンをテスト
            headers = {'Authorization': f'Bearer {token_data["access_token"]}'}
            drive_response = requests.get(
                'https://www.googleapis.com/drive/v3/files?pageSize=5',
                headers=headers
            )
            
            if drive_response.status_code == 200:
                files = drive_response.json().get('files', [])
                print(f"✓ Google Driveアクセス成功！ファイル数: {len(files)}")
                
                for file in files:
                    print(f"  - {file.get('name', 'Unknown')}")
                    
                # トークンを保存
                with open('/home/rootmax/drive_tokens.json', 'w') as f:
                    json.dump(token_data, f, indent=2)
                print("\n✓ トークンを保存しました: drive_tokens.json")
                
                return True
            else:
                print(f"✗ Drive APIアクセス失敗: {drive_response.status_code}")
                print(drive_response.text)
        else:
            print(f"✗ 失敗: {response.status_code}")
            error_data = response.json()
            print(f"   エラー: {error_data.get('error', 'Unknown')}")
            print(f"   詳細: {error_data.get('error_description', 'No description')}")
        
        print()
    
    # 新しい認証URLを提案
    print("すべてのテストが失敗した場合の対処法:")
    print("1. Google Cloud Consoleでclient_secretを確認")
    print("2. Drive APIが有効になっているか確認") 
    print("3. 新しい認証コードを取得（期限切れの可能性）")
    
    return False

def check_drive_api_status():
    """Drive APIの有効化状況をチェック"""
    print("Google Drive API有効化確認:")
    print("https://console.cloud.google.com/apis/library/drive.googleapis.com?project=civil-authority-462513-a9")

if __name__ == "__main__":
    if not test_different_client_secrets():
        check_drive_api_status()