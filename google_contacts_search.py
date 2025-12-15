#!/usr/bin/env python3
"""
Google Contacts API検索スクリプト
任意の名前で連絡先を検索
"""

import pickle
import os.path
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'

def authenticate_google_contacts():
    """Google Contacts API認証"""
    creds = None
    
    # トークンファイルが存在する場合はロード
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"トークン更新エラー: {e}")
                creds = None
        
        if not creds:
            print("❌ Google Contacts認証が必要です")
            print(f"認証トークンファイル: {TOKEN_FILE}")
            print("認証を実行するには以下のコマンドを使用してください:")
            print("python3 /home/fujinosuke/projects/google_auth/google_contacts_auth.py")
            return None
    
    return creds

def search_contacts(service, query):
    """連絡先検索"""
    try:
        print(f"🔍 Google Contactsで '{query}' を検索中...")
        
        # Google Contacts から全連絡先を取得
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,  # 多めに取得
            personFields='names,phoneNumbers,emailAddresses,organizations,addresses'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"📋 総連絡先数: {len(connections)}件")
        
        matches = []
        query_lower = query.lower()
        
        # 検索実行
        for person in connections:
            names = person.get('names', [])
            for name in names:
                display_name = name.get('displayName', '')
                given_name = name.get('givenName', '')
                family_name = name.get('familyName', '')
                
                # 名前での検索（部分一致）
                if (query_lower in display_name.lower() or
                    query_lower in given_name.lower() or
                    query_lower in family_name.lower() or
                    query in display_name or
                    query in given_name or
                    query in family_name):
                    
                    # 連絡先情報を整理
                    contact_info = {
                        'display_name': display_name,
                        'given_name': given_name,
                        'family_name': family_name,
                        'phones': [],
                        'emails': [],
                        'companies': [],
                        'addresses': []
                    }
                    
                    # 電話番号取得
                    phones = person.get('phoneNumbers', [])
                    for phone in phones:
                        contact_info['phones'].append({
                            'value': phone.get('value', ''),
                            'type': phone.get('type', '')
                        })
                    
                    # メールアドレス取得
                    emails = person.get('emailAddresses', [])
                    for email in emails:
                        contact_info['emails'].append({
                            'value': email.get('value', ''),
                            'type': email.get('type', '')
                        })
                    
                    # 会社情報取得
                    orgs = person.get('organizations', [])
                    for org in orgs:
                        contact_info['companies'].append({
                            'name': org.get('name', ''),
                            'title': org.get('title', ''),
                            'department': org.get('department', '')
                        })
                    
                    # 住所取得
                    addresses = person.get('addresses', [])
                    for addr in addresses:
                        contact_info['addresses'].append({
                            'value': addr.get('formattedValue', ''),
                            'type': addr.get('type', '')
                        })
                    
                    matches.append(contact_info)
                    break
        
        return matches
        
    except Exception as e:
        print(f"❌ 検索エラー: {e}")
        return []

def display_results(matches, query):
    """検索結果表示"""
    if not matches:
        print(f"\n❌ '{query}' に一致する連絡先が見つかりませんでした")
        return []
    
    print(f"\n✅ '{query}' の検索結果: {len(matches)}件")
    print("=" * 50)
    
    phone_numbers = []
    
    for i, contact in enumerate(matches, 1):
        print(f"\n👤 【{i}】 {contact['display_name']}")
        
        if contact['given_name'] or contact['family_name']:
            print(f"   姓名: {contact['family_name']} {contact['given_name']}")
        
        # 電話番号
        if contact['phones']:
            print("   📱 電話番号:")
            for phone in contact['phones']:
                type_str = f"({phone['type']})" if phone['type'] else ""
                print(f"      {phone['value']} {type_str}")
                phone_numbers.append(phone['value'])
        
        # メールアドレス
        if contact['emails']:
            print("   📧 メールアドレス:")
            for email in contact['emails']:
                type_str = f"({email['type']})" if email['type'] else ""
                print(f"      {email['value']} {type_str}")
        
        # 会社情報
        if contact['companies']:
            print("   🏢 会社情報:")
            for company in contact['companies']:
                company_info = company['name']
                if company['department']:
                    company_info += f" {company['department']}"
                if company['title']:
                    company_info += f" {company['title']}"
                print(f"      {company_info}")
        
        # 住所
        if contact['addresses']:
            print("   🏠 住所:")
            for addr in contact['addresses']:
                type_str = f"({addr['type']})" if addr['type'] else ""
                print(f"      {addr['value']} {type_str}")
        
        print("-" * 30)
    
    return phone_numbers

def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法: python3 google_contacts_search.py <検索名>")
        print("例: python3 google_contacts_search.py 竹松陽子")
        sys.exit(1)
    
    search_query = ' '.join(sys.argv[1:])
    
    print("🔍 Google Contacts検索システム")
    print("=" * 40)
    
    # Google Contacts認証
    creds = authenticate_google_contacts()
    if not creds:
        return
    
    try:
        # Google Contacts サービス構築
        service = build('people', 'v1', credentials=creds)
        print("✅ Google Contacts API接続成功")
        
        # 連絡先検索実行
        matches = search_contacts(service, search_query)
        
        # 結果表示
        phone_numbers = display_results(matches, search_query)
        
        # 電話番号を返す（SMS送信用）
        if phone_numbers:
            print(f"\n見つかった電話番号: {', '.join(phone_numbers)}")
        
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()