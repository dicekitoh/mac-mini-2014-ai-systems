#!/usr/bin/env python3
"""
LINEWORKS連絡先登録システム
Google連絡先から取得した情報をLINEWORKS連絡先に登録
"""

import requests
import json
import time
import jwt
from datetime import datetime, timedelta

class LINEWORKSContactManager:
    def __init__(self):
        # LINEWORKS API設定（CLAUDE.mdから取得）
        self.CLIENT_ID = '***REMOVED***'
        self.CLIENT_SECRET = '***REMOVED***'
        self.SERVICE_ACCOUNT = '***REMOVED***'
        self.PRIVATE_KEY_PATH = '/home/fujinosuke/lineworks/private_20250529134836.key'
        self.DOMAIN_ID = '608300'
        
        # API エンドポイント
        self.TOKEN_URL = 'https://auth.worksmobile.com/oauth2/v2.0/token'
        self.CONTACT_API_BASE = 'https://www.worksapis.com/v1.0'
        
        self.access_token = None

    def load_private_key(self):
        """秘密鍵を読み込み"""
        try:
            with open(self.PRIVATE_KEY_PATH, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"❌ 秘密鍵読み込みエラー: {e}")
            return None

    def create_jwt_assertion(self):
        """JWT認証用のassertionを作成"""
        private_key = self.load_private_key()
        if not private_key:
            return None
        
        # JWT ヘッダー
        header = {
            'alg': 'RS256',
            'typ': 'JWT'
        }
        
        # JWT ペイロード
        now = datetime.utcnow()
        payload = {
            'iss': self.SERVICE_ACCOUNT,  # Issuer
            'sub': self.CLIENT_ID,        # Subject  
            'aud': self.TOKEN_URL,        # Audience
            'iat': int(now.timestamp()),  # Issued At
            'exp': int((now + timedelta(minutes=30)).timestamp())  # Expiration
        }
        
        try:
            # JWT トークン生成
            token = jwt.encode(payload, private_key, algorithm='RS256', headers=header)
            return token
        except Exception as e:
            print(f"❌ JWT作成エラー: {e}")
            return None

    def get_access_token(self):
        """アクセストークンを取得"""
        jwt_assertion = self.create_jwt_assertion()
        if not jwt_assertion:
            return False
            
        # トークン取得リクエスト
        token_data = {
            'assertion': jwt_assertion,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'scope': 'contact'
        }
        
        try:
            response = requests.post(self.TOKEN_URL, data=token_data)
            
            if response.status_code == 200:
                token_info = response.json()
                self.access_token = token_info.get('access_token')
                print("✅ LINEWORKS API認証成功")
                return True
            else:
                print(f"❌ トークン取得失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ トークン取得エラー: {e}")
            return False

    def add_contact(self, name, phone, email):
        """LINEWORKS連絡先に追加"""
        if not self.access_token:
            if not self.get_access_token():
                return False
        
        # 連絡先データ作成
        contact_data = {
            'userExternalKey': f'google_import_{int(time.time())}',
            'userName': name,
            'displayName': name,
            'phoneNumber': phone,
            'email': email,
            'orgUnitId': self.DOMAIN_ID
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # 連絡先追加API呼び出し
        contact_url = f'{self.CONTACT_API_BASE}/contacts'
        
        try:
            response = requests.post(contact_url, 
                                   headers=headers, 
                                   json=contact_data)
            
            if response.status_code in [200, 201]:
                print("✅ LINEWORKS連絡先登録成功")
                print(f"登録情報: {name} / {phone} / {email}")
                return True
            else:
                print(f"❌ 連絡先登録失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 連絡先登録エラー: {e}")
            return False

    def register_contact_from_google(self, name, phone, email):
        """Google連絡先からLINEWORKS連絡先に登録"""
        print("🔄 LINEWORKS連絡先登録システム")
        print("=" * 50)
        print(f"登録対象: {name}")
        print(f"電話番号: {phone}")
        print(f"メール: {email}")
        print("=" * 50)
        
        # LINEWORKS連絡先に登録
        if self.add_contact(name, phone, email):
            print(f"✅ {name} の連絡先をLINEWORKSに登録完了")
            return True
        else:
            print(f"❌ {name} の連絡先登録に失敗")
            return False

def main():
    """メイン関数"""
    # Google連絡先から取得した情報
    contact_name = "高橋進"
    contact_phone = "011-851-2181"
    contact_email = "ns-tsukisamu@st-g.co.jp"
    
    # LINEWORKS連絡先マネージャー初期化
    manager = LINEWORKSContactManager()
    
    # 連絡先登録実行
    success = manager.register_contact_from_google(
        contact_name, 
        contact_phone, 
        contact_email
    )
    
    if success:
        print("\n🎉 連絡先の代理登録が完了しました！")
        print("LINEWORKS連絡先で確認できます:")
        print("https://contact.worksmobile.com/v2/p/shared/contact")
    else:
        print("\n❌ 連絡先の代理登録に失敗しました")

if __name__ == "__main__":
    main()