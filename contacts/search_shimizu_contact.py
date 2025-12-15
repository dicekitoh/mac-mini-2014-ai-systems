#!/usr/bin/env python3
"""
清水さん検索専用スクリプト（N8N用）
Google Contactsから清水さんを検索して結果をJSON形式で出力
"""

import pickle
import os.path
import json
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
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                return {"error": f"認証エラー: {e}"}
        
        if not creds:
            return {"error": "Google Contacts認証が必要です"}
    
    return creds

def search_shimizu_contacts():
    """清水さんを検索"""
    
    # 認証
    creds = authenticate_google_contacts()
    if isinstance(creds, dict) and "error" in creds:
        return creds
    
    try:
        # Google Contacts サービス構築
        service = build('people', 'v1', credentials=creds)
        
        # 全連絡先取得
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=2000,
            personFields='names,phoneNumbers,emailAddresses,organizations,addresses,photos'
        ).execute()
        
        connections = results.get('connections', [])
        matches = []
        
        # 清水さんを検索
        for person in connections:
            names = person.get('names', [])
            for name in names:
                display_name = name.get('displayName', '')
                given_name = name.get('givenName', '')
                family_name = name.get('familyName', '')
                
                # 清水という文字が含まれているかチェック
                if ('清水' in display_name or 
                    '清水' in given_name or 
                    '清水' in family_name or
                    'shimizu' in display_name.lower() or
                    'Shimizu' in display_name):
                    
                    # 連絡先情報を整理
                    contact_info = {
                        'resource_name': person.get('resourceName', ''),
                        'display_name': display_name,
                        'given_name': given_name,
                        'family_name': family_name,
                        'phones': [],
                        'emails': [],
                        'companies': [],
                        'addresses': []
                    }
                    
                    # 電話番号
                    phones = person.get('phoneNumbers', [])
                    for phone in phones:
                        contact_info['phones'].append({
                            'number': phone.get('value', ''),
                            'type': phone.get('type', 'その他')
                        })
                    
                    # メールアドレス
                    emails = person.get('emailAddresses', [])
                    for email in emails:
                        contact_info['emails'].append({
                            'address': email.get('value', ''),
                            'type': email.get('type', 'その他')
                        })
                    
                    # 会社情報
                    orgs = person.get('organizations', [])
                    for org in orgs:
                        contact_info['companies'].append({
                            'company': org.get('name', ''),
                            'title': org.get('title', ''),
                            'department': org.get('department', '')
                        })
                    
                    # 住所
                    addresses = person.get('addresses', [])
                    for addr in addresses:
                        contact_info['addresses'].append({
                            'address': addr.get('formattedValue', ''),
                            'type': addr.get('type', 'その他')
                        })
                    
                    matches.append(contact_info)
                    break
        
        # 結果をJSON形式で返す
        result = {
            "success": True,
            "search_query": "清水",
            "total_contacts": len(connections),
            "found_count": len(matches),
            "contacts": matches,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"検索エラー: {str(e)}",
            "search_query": "清水"
        }

def main():
    """メイン関数"""
    result = search_shimizu_contacts()
    
    # JSON形式で出力（N8Nで使用）
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # エラーがある場合はexit code 1
    if not result.get("success", False):
        sys.exit(1)

if __name__ == "__main__":
    main()