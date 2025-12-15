#!/usr/bin/env python3
"""
Google Contacts特定人物ID取得スクリプト
URL: https://contacts.google.com/person/c4961735682218747621
から名前と携帯番号を抽出してOutlook形式で出力
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

def authenticate_google_contacts():
    """Google Contacts API認証"""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"トークン更新エラー: {e}")
                creds = None
        
        if not creds:
            print("❌ Google Contacts認証が必要です")
            return None
    
    return creds

def get_contact_by_id(service, person_id):
    """特定の人物IDで連絡先取得"""
    try:
        print(f"🔍 人物ID: {person_id} の連絡先を取得中...")
        
        # Google Contacts APIで特定の人物を取得
        resource_name = f'people/{person_id}'
        result = service.people().get(
            resourceName=resource_name,
            personFields='names,phoneNumbers,emailAddresses'
        ).execute()
        
        return result
        
    except Exception as e:
        print(f"❌ 取得エラー: {e}")
        return None

def extract_contact_info(person_data):
    """連絡先情報を抽出"""
    if not person_data:
        return None
    
    contact_info = {
        'name': '',
        'mobile': '',
        'email': ''
    }
    
    # 名前取得
    names = person_data.get('names', [])
    if names:
        contact_info['name'] = names[0].get('displayName', '')
    
    # 電話番号取得（携帯優先）
    phones = person_data.get('phoneNumbers', [])
    for phone in phones:
        phone_type = phone.get('type', '').lower()
        phone_value = phone.get('value', '')
        
        # 携帯電話を優先
        if 'mobile' in phone_type or '携帯' in phone_type:
            contact_info['mobile'] = phone_value
            break
        elif not contact_info['mobile']:  # 携帯がない場合は最初の番号
            contact_info['mobile'] = phone_value
    
    # メールアドレス取得
    emails = person_data.get('emailAddresses', [])
    if emails:
        contact_info['email'] = emails[0].get('value', '')
    
    return contact_info

def format_for_outlook(contact_info):
    """Outlook連絡先形式で出力"""
    if not contact_info:
        return None
    
    print("\n" + "="*50)
    print("📱 Outlook連絡先登録用情報")
    print("="*50)
    print(f"名前: {contact_info['name']}")
    print(f"携帯電話: {contact_info['mobile']}")
    if contact_info['email']:
        print(f"メール: {contact_info['email']}")
    print("="*50)
    
    # CSV形式でも出力
    csv_line = f'"{contact_info["name"]}","{contact_info["mobile"]}","{contact_info["email"]}"'
    print(f"\nCSV形式: {csv_line}")
    
    return contact_info

def main():
    """メイン関数"""
    print("🔍 Google Contacts特定人物取得システム")
    print("=" * 50)
    
    # URLから人物IDを抽出
    person_id = "c1832243206309415940"
    
    # Google Contacts認証
    creds = authenticate_google_contacts()
    if not creds:
        print("MacMini2014で認証を完了してください")
        return
    
    try:
        # Google Contacts サービス構築
        service = build('people', 'v1', credentials=creds)
        print("✅ Google Contacts API接続成功")
        
        # 特定人物取得
        person_data = get_contact_by_id(service, person_id)
        
        # 連絡先情報抽出
        contact_info = extract_contact_info(person_data)
        
        # Outlook形式で出力
        result = format_for_outlook(contact_info)
        
        if result:
            print("\n✅ 連絡先情報の抽出が完了しました")
            print("上記の情報をOutlookにコピー&ペーストして登録できます")
        else:
            print("\n❌ 連絡先情報の取得に失敗しました")
        
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()