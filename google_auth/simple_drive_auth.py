#!/usr/bin/env python3
import pickle
import requests
import json
from google.oauth2.credentials import Credentials

def create_drive_token_manually():
    """手動でDriveトークンを作成"""
    
    # クライアント情報（credentials.jsonから）
    client_id = "136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com"
    client_secret = "***REMOVED***"
    
    # 認証コード
    auth_code = "4/1AUJR-x7kktGJ7SOiF2W2eA9IBmWUta4S2bN8eEIrPeNVR43Zg_jB4D94CXQ"
    
    # トークン交換リクエスト
    token_url = "https://oauth2.googleapis.com/token"
    
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        print(f"HTTP Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Credentialsオブジェクトを作成
            creds = Credentials(
                token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # トークンを保存
            with open('/home/fujinosuke/token_drive.pickle', 'wb') as f:
                pickle.dump(creds, f)
            
            print("✅ Drive認証完了!")
            return True
        else:
            print("❌ トークン取得失敗")
            return False
            
    except Exception as e:
        print(f"エラー: {e}")
        return False

if __name__ == '__main__':
    create_drive_token_manually()