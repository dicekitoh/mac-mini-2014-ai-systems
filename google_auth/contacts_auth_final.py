#!/usr/bin/env python3
"""
Google Contacts最終認証 
手動取得した認証コードで本格実装
"""

import pickle
import json
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'

def complete_final_auth():
    """最終認証コードで完了"""
    
    # 手動で取得した認証コード（実際に取得後に更新）
    auth_code = "4/0AeanS0T2Vj8MQSmnN3xKzHV3tUKzJZ2kLhqzlPLLsG6RrpP8DCfpR2m9TQn-FV-B6I7gAQ"
    
    try:
        # 正しいスコープで新しいフロー作成
        scopes = ['https://www.googleapis.com/auth/contacts.readonly']
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # 認証コードでトークン取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークン保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ Google Contacts最終認証完了！")
        
        # 実際の連絡先取得テスト
        service = build('people', 'v1', credentials=creds)
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=100,
            personFields='names,phoneNumbers,emailAddresses,organizations'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"🎉 実際のGoogle Contacts取得成功: {len(connections)}件")
        
        # 実際の連絡先から「木村」「伊藤」を検索
        kimura_contacts = []
        ito_contacts = []
        
        for person in connections:
            names = person.get('names', [])
            for name in names:
                display_name = name.get('displayName', '')
                if '木村' in display_name:
                    kimura_contacts.append(display_name)
                elif '伊藤' in display_name:
                    ito_contacts.append(display_name)
        
        print(f"\\n📞 実際の連絡先検索結果:")
        print(f"木村さん: {len(kimura_contacts)}件 - {kimura_contacts}")
        print(f"伊藤さん: {len(ito_contacts)}件 - {ito_contacts}")
        
        return True
        
    except Exception as e:
        print(f"❌ 最終認証エラー: {e}")
        return False

if __name__ == '__main__':
    complete_final_auth()