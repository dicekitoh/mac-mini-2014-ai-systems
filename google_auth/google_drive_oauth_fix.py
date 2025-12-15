#!/usr/bin/env python3
"""
Google Drive API OAuth認証修正スクリプト
Client ID: 136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com
"""

import json
import os

# OAuth2.0設定テンプレート
oauth_config = {
    "installed": {
        "client_id": "136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com",
        "project_id": "civil-authority-462513-a9",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "***REMOVED***",  # 既存の設定から
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
    }
}

# 認証URL生成
def generate_auth_url():
    client_id = oauth_config["installed"]["client_id"]
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    scope = "https://www.googleapis.com/auth/drive.readonly"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return auth_url

def main():
    print("=== Google Drive API 認証修正版 ===\n")
    print(f"Client ID: {oauth_config['installed']['client_id']}")
    print(f"Project: {oauth_config['installed']['project_id']}\n")
    
    # 認証URL表示
    auth_url = generate_auth_url()
    print("認証URL（修正版）:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print("\n手順:")
    print("1. 上記URLをブラウザで開く")
    print("2. Googleアカウントでログイン")
    print("3. アプリを許可")
    print("4. 表示される認証コードをコピー")
    print("\n注意: redirect_uri=urn:ietf:wg:oauth:2.0:oob を使用しています")
    
    # credentials.json作成
    cred_file = "credentials_drive.json"
    with open(cred_file, 'w') as f:
        json.dump(oauth_config, f, indent=2)
    print(f"\n認証設定ファイルを作成しました: {cred_file}")

if __name__ == "__main__":
    main()