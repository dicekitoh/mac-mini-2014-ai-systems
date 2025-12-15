#!/usr/bin/env python3
"""
Google Contacts API手動認証スクリプト
ブラウザが利用できない環境用
"""

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Contacts API設定
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']
CREDENTIALS_FILE = '/home/fujinosuke/google/credentials.json'
TOKEN_FILE = '/home/fujinosuke/google/token_contacts_real.pickle'

def authenticate_google_contacts_manual():
    """Google Contacts API手動認証"""
    creds = None
    
    # トークンファイルが存在する場合はロード
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
            print(f"✅ 既存のトークンをロード: {TOKEN_FILE}")
    
    # 認証が無効または存在しない場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ トークンを更新しました")
            except Exception as e:
                print(f"❌ トークン更新エラー: {e}")
                creds = None
        
        if not creds:
            # 手動認証フロー
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ 認証ファイルが見つかりません: {CREDENTIALS_FILE}")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            
            # 手動認証用URL生成
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("=" * 60)
            print("🔑 Google Contacts API手動認証")
            print("=" * 60)
            print("以下のURLにアクセスして認証コードを取得してください:")
            print()
            print(auth_url)
            print()
            print("=" * 60)
            
            # 認証コード入力待ち
            auth_code = input("認証コードを入力してください: ").strip()
            
            try:
                # 認証コードで認証実行
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                print("✅ 手動認証を完了しました")
            except Exception as e:
                print(f"❌ 認証コード処理エラー: {e}")
                return None
        
        # トークンを保存
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print(f"✅ トークンを保存しました: {TOKEN_FILE}")
    
    return creds

def get_all_contacts(service):
    """全連絡先取得"""
    try:
        print("🔍 全連絡先を取得中...")
        
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,
            personFields='names,phoneNumbers,emailAddresses'
        ).execute()
        
        connections = results.get('connections', [])
        print(f"📋 総連絡先数: {len(connections)}件")
        
        return connections
        
    except Exception as e:
        print(f"❌ 連絡先取得エラー: {e}")
        return []

def search_contacts_detail(connections, query):
    """詳細連絡先検索"""
    matches = []
    query_lower = query.lower()
    
    print(f"\n🔍 '{query}' での検索実行中...")
    
    for person in connections:
        names = person.get('names', [])
        for name in names:
            display_name = name.get('displayName', '')
            given_name = name.get('givenName', '')
            family_name = name.get('familyName', '')
            
            # デバッグ: 「小野寺」を含む連絡先を全て表示
            if '小野寺' in display_name:
                print(f"  🔎 発見: {display_name} (given: {given_name}, family: {family_name})")
                
                # 詳細情報を取得
                contact_info = {
                    'display_name': display_name,
                    'given_name': given_name,
                    'family_name': family_name,
                    'phones': [],
                    'emails': []
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
                
                matches.append(contact_info)
                break
    
    return matches

def display_results(matches, query):
    """検索結果表示"""
    if not matches:
        print(f"\n❌ '{query}' に一致する連絡先が見つかりませんでした")
        return
    
    print(f"\n✅ '{query}' の検索結果: {len(matches)}件")
    print("=" * 50)
    
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
        
        # メールアドレス
        if contact['emails']:
            print("   📧 メールアドレス:")
            for email in contact['emails']:
                type_str = f"({email['type']})" if email['type'] else ""
                print(f"      {email['value']} {type_str}")
        
        print("-" * 30)

def main():
    """メイン関数"""
    print("🔑 Google Contacts手動認証・検索システム")
    print("=" * 50)
    
    # 手動認証実行
    creds = authenticate_google_contacts_manual()
    if not creds:
        print("❌ 認証に失敗しました")
        return
    
    try:
        # Google Contacts サービス構築
        service = build('people', 'v1', credentials=creds)
        print("✅ Google Contacts API接続成功")
        
        # 全連絡先取得
        connections = get_all_contacts(service)
        if not connections:
            print("❌ 連絡先の取得に失敗しました")
            return
        
        # 「小野寺」検索実行
        matches = search_contacts_detail(connections, "小野寺")
        
        # 結果表示
        display_results(matches, "小野寺")
        
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()