#!/usr/bin/env python3
"""
Google Contacts認証完了（認証コード使用）
認証コード: 4/0AeanS0QE7xL6h4Gvmh5-8rJ3qZY2N9WxVkJHgLsE6tRrP9mF3aCbDs5nVc-XtK8zN2mHwQ
"""

import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_verified.pickle'
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def complete_auth_and_search():
    """認証完了後に伊藤を検索"""
    
    # 実際の認証コード（手動取得後に更新）
    auth_code = "4/0AeanS0QE7xL6h4Gvmh5-8rJ3qZY2N9WxVkJHgLsE6tRrP9mF3aCbDs5nVc-XtK8zN2mHwQ"
    
    try:
        # 認証フロー
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # トークン取得
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # トークン保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Google Contacts認証成功！")
        
        # 即座に「伊藤」を検索
        service = build('people', 'v1', credentials=creds)
        
        print("🔍 Google Contactsから「伊藤」を検索中...")
        
        # 全連絡先取得
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,
            personFields='names,phoneNumbers,emailAddresses,organizations,addresses'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"📞 総連絡先数: {len(connections)}件")
        
        # 「伊藤」検索
        ito_contacts = []
        search_terms = ['伊藤', 'いとう', 'イトウ', 'ito', 'itoh', 'itou']
        
        for person in connections:
            names = person.get('names', [])
            
            for name in names:
                display_name = name.get('displayName', '')
                
                for term in search_terms:
                    if term.lower() in display_name.lower():
                        # 連絡先詳細を抽出
                        contact = {
                            'name': display_name,
                            'phone': '',
                            'email': '',
                            'company': ''
                        }
                        
                        # 電話番号
                        phones = person.get('phoneNumbers', [])
                        if phones:
                            contact['phone'] = phones[0].get('value', '')
                        
                        # メール
                        emails = person.get('emailAddresses', [])
                        if emails:
                            contact['email'] = emails[0].get('value', '')
                        
                        # 会社
                        orgs = person.get('organizations', [])
                        if orgs:
                            contact['company'] = orgs[0].get('name', '')
                        
                        ito_contacts.append(contact)
                        break
        
        print(f"\\n🎯 「伊藤」検索結果: {len(ito_contacts)}件")
        
        for i, contact in enumerate(ito_contacts, 1):
            print(f"\\n{i}. {contact['name']}")
            if contact['phone']:
                print(f"   📱 {contact['phone']}")
            if contact['email']:
                print(f"   📧 {contact['email']}")
            if contact['company']:
                print(f"   🏢 {contact['company']}")
        
        # 結果保存
        import json
        with open('/home/fujinosuke/google/real_ito_contacts.json', 'w', encoding='utf-8') as f:
            json.dump(ito_contacts, f, ensure_ascii=False, indent=2)
        
        print(f"\\n💾 実際の「伊藤」データを保存: /home/fujinosuke/google/real_ito_contacts.json")
        return ito_contacts
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

if __name__ == '__main__':
    complete_auth_and_search()