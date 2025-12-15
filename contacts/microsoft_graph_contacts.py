#!/usr/bin/env python3
"""
Microsoft Graph API 連絡先アクセスシステム
Microsoft 365/Outlookの連絡先を取得・管理
"""

import os
import json
import requests
from datetime import datetime, timedelta
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse
import pickle

# 設定
CONFIG_FILE = '/home/rootmax/microsoft_graph_config.json'
TOKEN_FILE = '/home/rootmax/microsoft_graph_token.pickle'

# Microsoft Graph APIエンドポイント
GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'
AUTH_BASE_URL = 'https://login.microsoftonline.com'

class MicrosoftGraphContacts:
    def __init__(self):
        self.config = self.load_config()
        self.access_token = None
        self.refresh_token = None
        self.token_expires = None
        
    def load_config(self):
        """設定ファイルの読み込み"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            # デフォルト設定を作成
            default_config = {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "tenant_id": "common",
                "redirect_uri": "http://localhost:8080",
                "scopes": ["Contacts.Read", "Contacts.ReadWrite", "User.Read"]
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"設定ファイルを作成しました: {CONFIG_FILE}")
            print("Microsoft Azure ADでアプリを登録し、設定を更新してください。")
            return default_config
    
    def get_auth_url(self):
        """認証URLの生成"""
        params = {
            'client_id': self.config['client_id'],
            'response_type': 'code',
            'redirect_uri': self.config['redirect_uri'],
            'response_mode': 'query',
            'scope': ' '.join(self.config['scopes']),
            'state': '12345'
        }
        auth_url = f"{AUTH_BASE_URL}/{self.config['tenant_id']}/oauth2/v2.0/authorize?" + urlencode(params)
        return auth_url
    
    def exchange_code_for_token(self, code):
        """認証コードをアクセストークンに交換"""
        token_url = f"{AUTH_BASE_URL}/{self.config['tenant_id']}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': code,
            'redirect_uri': self.config['redirect_uri'],
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens.get('refresh_token')
            expires_in = tokens.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            # トークンを保存
            self.save_tokens()
            return True
        else:
            print(f"トークン取得エラー: {response.status_code}")
            print(response.json())
            return False
    
    def save_tokens(self):
        """トークンの保存"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires': self.token_expires
        }
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(token_data, f)
        print("トークンを保存しました")
    
    def load_tokens(self):
        """保存されたトークンの読み込み"""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as f:
                token_data = pickle.load(f)
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                self.token_expires = token_data.get('token_expires')
                return True
        return False
    
    def refresh_access_token(self):
        """アクセストークンの更新"""
        if not self.refresh_token:
            print("リフレッシュトークンがありません")
            return False
            
        token_url = f"{AUTH_BASE_URL}/{self.config['tenant_id']}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access_token']
            if 'refresh_token' in tokens:
                self.refresh_token = tokens['refresh_token']
            expires_in = tokens.get('expires_in', 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            self.save_tokens()
            return True
        else:
            print(f"トークン更新エラー: {response.status_code}")
            return False
    
    def ensure_valid_token(self):
        """有効なトークンの確保"""
        if not self.access_token:
            if not self.load_tokens():
                return False
        
        if self.token_expires and datetime.now() >= self.token_expires:
            print("トークンが期限切れです。更新中...")
            return self.refresh_access_token()
        
        return True
    
    def get_user_info(self):
        """ユーザー情報の取得"""
        if not self.ensure_valid_token():
            print("有効なトークンがありません")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{GRAPH_BASE_URL}/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"ユーザー情報取得エラー: {response.status_code}")
            return None
    
    def get_contacts(self, limit=100, search_query=None):
        """連絡先の取得"""
        if not self.ensure_valid_token():
            print("有効なトークンがありません")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'$top': limit}
        
        if search_query:
            params['$search'] = f'"{search_query}"'
        
        response = requests.get(f"{GRAPH_BASE_URL}/me/contacts", headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"連絡先取得エラー: {response.status_code}")
            print(response.json())
            return None
    
    def search_contacts(self, name):
        """名前で連絡先を検索"""
        if not self.ensure_valid_token():
            print("有効なトークンがありません")
            return None
            
        headers = {'Authorization': f'Bearer {self.access_token}'}
        # フィルター条件を使用
        params = {
            '$filter': f"startswith(displayName, '{name}') or startswith(givenName, '{name}') or startswith(surname, '{name}')"
        }
        
        response = requests.get(f"{GRAPH_BASE_URL}/me/contacts", headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"検索エラー: {response.status_code}")
            return None
    
    def display_contacts(self, contacts_data):
        """連絡先の表示"""
        if not contacts_data or 'value' not in contacts_data:
            print("連絡先が見つかりません")
            return
            
        contacts = contacts_data['value']
        print(f"\n=== 連絡先一覧 ({len(contacts)}件) ===")
        
        for i, contact in enumerate(contacts, 1):
            print(f"\n{i}. {contact.get('displayName', '名前なし')}")
            
            # メールアドレス
            emails = contact.get('emailAddresses', [])
            if emails:
                for email in emails:
                    print(f"   📧 {email.get('address', '')}")
            
            # 電話番号
            phones = contact.get('mobilePhone') or contact.get('businessPhones', [])
            if phones:
                if isinstance(phones, str):
                    print(f"   📱 {phones}")
                else:
                    for phone in phones:
                        print(f"   📱 {phone}")
            
            # 会社
            company = contact.get('companyName')
            if company:
                print(f"   🏢 {company}")

def main():
    """メイン処理"""
    print("=== Microsoft Graph 連絡先アクセスシステム ===")
    
    graph = MicrosoftGraphContacts()
    
    # 既存のトークンを確認
    if graph.load_tokens() and graph.ensure_valid_token():
        print("✅ 既存の認証情報を使用します")
    else:
        print("\n新しい認証が必要です")
        print("\n1. 以下のURLにアクセスしてください:")
        auth_url = graph.get_auth_url()
        print(auth_url)
        print("\n2. Microsoftアカウントでログインし、権限を許可してください")
        print("3. リダイレクトされたURLから'code='の後の値をコピーしてください")
        
        code = input("\n認証コード: ").strip()
        
        if graph.exchange_code_for_token(code):
            print("✅ 認証成功！")
        else:
            print("❌ 認証失敗")
            return
    
    # ユーザー情報の表示
    user_info = graph.get_user_info()
    if user_info:
        print(f"\nログインユーザー: {user_info.get('displayName', 'Unknown')}")
        print(f"メール: {user_info.get('mail', user_info.get('userPrincipalName', 'Unknown'))}")
    
    while True:
        print("\n=== メニュー ===")
        print("1. すべての連絡先を表示")
        print("2. 連絡先を検索")
        print("3. 終了")
        
        choice = input("\n選択してください (1-3): ").strip()
        
        if choice == '1':
            contacts = graph.get_contacts()
            graph.display_contacts(contacts)
        
        elif choice == '2':
            name = input("検索する名前: ").strip()
            contacts = graph.search_contacts(name)
            graph.display_contacts(contacts)
        
        elif choice == '3':
            print("終了します")
            break
        
        else:
            print("無効な選択です")

if __name__ == '__main__':
    main()