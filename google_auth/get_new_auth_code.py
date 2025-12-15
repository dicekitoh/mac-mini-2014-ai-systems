#!/usr/bin/env python3
"""
新しい認証コード取得用スクリプト
"""

import webbrowser
import urllib.parse

def generate_new_auth_url():
    """新しい認証URLを生成"""
    
    # OAuth設定
    client_id = "136454082089-vfaralfhuvp92o3lpv47upag621bmv34.apps.googleusercontent.com"
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    scope = "https://www.googleapis.com/auth/drive.readonly"
    
    # パラメータ
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    
    # URLエンコード
    query_string = urllib.parse.urlencode(params)
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    return auth_url

def main():
    print("=== 新しい Google Drive API 認証コード取得 ===\n")
    
    auth_url = generate_new_auth_url()
    
    print("新しい認証URL:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    
    print("\n手順:")
    print("1. 上記URLをブラウザで開く")
    print("2. Googleアカウントでログイン")
    print("3. アプリへのアクセスを許可")
    print("4. 表示される新しい認証コードをコピー")
    print("5. 新しい認証コードで再実行")
    
    print("\n注意:")
    print("- 認証コードは数分で期限切れになります")
    print("- 取得後すぐに使用してください")

if __name__ == "__main__":
    main()