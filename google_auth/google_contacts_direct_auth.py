#!/usr/bin/env python3
"""
Google Contacts 直接認証・検索システム
実際のGoogle Contactsから「伊藤」を検索
"""

import pickle
import os.path
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_verified.pickle'

def authenticate_google_contacts():
    """Google Contacts認証"""
    creds = None
    
    # 既存のトークンをチェック
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 認証が無効な場合は新規認証
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ 既存トークンをリフレッシュしました")
            except Exception as e:
                print(f"トークンリフレッシュ失敗: {e}")
                creds = None
        
        if not creds:
            print("=== 新しいGoogle Contacts認証が必要です ===")
            print("手動認証URLを生成します...")
            
            # 手動認証フロー
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                access_type='offline'
            )
            
            print(f"\\n認証URL: {auth_url}")
            print("\\n上記URLにアクセスして認証コードを取得してください")
            
            # 認証情報を保存
            auth_info = {
                'auth_url': auth_url,
                'message': '認証コードを取得後、manual_complete_auth.py を実行してください'
            }
            
            with open('/home/fujinosuke/google/pending_auth.json', 'w') as f:
                json.dump(auth_info, f, indent=2)
            
            return None
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def search_ito_contacts(creds):
    """実際のGoogle Contactsから「伊藤」を検索"""
    try:
        service = build('people', 'v1', credentials=creds)
        
        print("🔍 Google Contactsから連絡先を取得中...")
        
        # 全連絡先を取得
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,  # 最大取得数
            personFields='names,phoneNumbers,emailAddresses,organizations,addresses,birthdays,biographies'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"📞 総連絡先数: {len(connections)}件")
        
        # 「伊藤」を検索
        ito_contacts = []
        search_terms = ['伊藤', 'いとう', 'イトウ', 'ito', 'itoh', 'itou']
        
        for person in connections:
            names = person.get('names', [])
            found_match = False
            
            for name in names:
                display_name = name.get('displayName', '')
                given_name = name.get('givenName', '')
                family_name = name.get('familyName', '')
                
                # 名前で検索
                for term in search_terms:
                    if (term.lower() in display_name.lower() or 
                        term.lower() in given_name.lower() or 
                        term.lower() in family_name.lower()):
                        
                        contact_info = extract_contact_details(person)
                        if contact_info not in ito_contacts:
                            ito_contacts.append(contact_info)
                        found_match = True
                        break
                
                if found_match:
                    break
        
        print(f"\\n🎯 「伊藤」の検索結果: {len(ito_contacts)}件")
        
        # 結果を表示
        for i, contact in enumerate(ito_contacts, 1):
            print(f"\\n--- {i}. {contact['name']} ---")
            if contact['phone']:
                print(f"📱 電話: {contact['phone']}")
            if contact['email']:
                print(f"📧 メール: {contact['email']}")
            if contact['company']:
                print(f"🏢 会社: {contact['company']}")
            if contact['address']:
                print(f"🏠 住所: {contact['address']}")
        
        # 結果をJSONファイルに保存
        with open('/home/fujinosuke/google/ito_contacts_real.json', 'w', encoding='utf-8') as f:
            json.dump(ito_contacts, f, ensure_ascii=False, indent=2)
        
        print(f"\\n💾 検索結果を保存しました: /home/fujinosuke/google/ito_contacts_real.json")
        return ito_contacts
        
    except Exception as e:
        print(f"❌ Google Contacts検索エラー: {e}")
        return []

def extract_contact_details(person):
    """連絡先詳細情報を抽出"""
    contact = {
        'name': '',
        'phone': '',
        'email': '',
        'company': '',
        'address': '',
        'notes': ''
    }
    
    # 名前
    names = person.get('names', [])
    if names:
        contact['name'] = names[0].get('displayName', '')
    
    # 電話番号
    phones = person.get('phoneNumbers', [])
    if phones:
        contact['phone'] = phones[0].get('value', '')
    
    # メールアドレス
    emails = person.get('emailAddresses', [])
    if emails:
        contact['email'] = emails[0].get('value', '')
    
    # 会社情報
    orgs = person.get('organizations', [])
    if orgs:
        org = orgs[0]
        company_parts = []
        if org.get('name'):
            company_parts.append(org.get('name'))
        if org.get('department'):
            company_parts.append(org.get('department'))
        if org.get('title'):
            company_parts.append(org.get('title'))
        contact['company'] = ' / '.join(company_parts)
    
    # 住所
    addresses = person.get('addresses', [])
    if addresses:
        contact['address'] = addresses[0].get('formattedValue', '')
    
    # メモ
    bios = person.get('biographies', [])
    if bios:
        contact['notes'] = bios[0].get('value', '')
    
    return contact

def main():
    """メイン実行"""
    print("=== Google Contacts「伊藤」検索システム ===")
    
    # 認証
    creds = authenticate_google_contacts()
    
    if creds:
        print("✅ Google Contacts認証成功")
        
        # 「伊藤」を検索
        ito_contacts = search_ito_contacts(creds)
        
        if ito_contacts:
            print(f"\\n🎉 実際のGoogle Contactsから「伊藤」{len(ito_contacts)}件を抽出しました！")
            print("これらの実データでContact Manager BOTを再構築します。")
        else:
            print("\\n⚠️ 「伊藤」に該当する連絡先が見つかりませんでした")
    else:
        print("❌ 認証が必要です。認証URLにアクセスしてください。")

if __name__ == '__main__':
    main()