#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts notesフィールド対応検索
biographies以外にnotesフィールドも取得
"""

import pickle
import sys
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ContactsNotesSearch:
    def __init__(self):
        self.token_path = '/home/fujinosuke/unified_oauth_token_new.pickle'
        self.service = None
        
    def authenticate(self):
        """OAuth認証"""
        try:
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
            
            if creds and creds.expired and creds.refresh_token:
                print('トークンをリフレッシュ中...')
                creds.refresh(Request())
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('people', 'v1', credentials=creds)
            return True
            
        except Exception as e:
            print(f'❌ 認証エラー: {e}')
            return False
    
    def search_with_all_notes_fields(self, keyword):
        """全てのメモ関連フィールドを取得"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            print(f'🔍 "{keyword}" のnotesフィールド検索実行中...')
            
            contacts = []
            page_token = None
            
            # 全フィールドを取得
            all_fields = 'names,phoneNumbers,emailAddresses,organizations,biographies,birthdays,addresses,urls,relations,events,memberships,metadata,userDefined,clientData'
            
            while True:
                if page_token:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=1000,
                        pageToken=page_token,
                        personFields=all_fields
                    ).execute()
                else:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=1000,
                        personFields=all_fields
                    ).execute()
                
                connections = results.get('connections', [])
                contacts.extend(connections)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            print(f'📊 合計 {len(contacts)} 件から検索中...')
            
            # キーワード検索
            matches = []
            keyword_lower = keyword.lower()
            
            for contact in contacts:
                search_texts = []
                
                # 名前検索
                if 'names' in contact:
                    for name in contact['names']:
                        search_texts.extend([
                            name.get('displayName', ''),
                            name.get('givenName', ''),
                            name.get('familyName', '')
                        ])
                
                # キーワードマッチング
                all_text = ' '.join(filter(None, search_texts)).lower()
                if keyword_lower in all_text:
                    matches.append(contact)
            
            print(f'✅ {len(matches)} 件の連絡先が見つかりました')
            return matches
            
        except Exception as e:
            print(f'❌ 検索エラー: {e}')
            return []
    
    def format_all_fields_contact(self, contact):
        """全フィールド表示（デバッグ用）"""
        lines = []
        lines.append('=' * 80)
        
        # 名前
        if 'names' in contact:
            for name in contact['names']:
                display_name = name.get('displayName', '')
                if display_name:
                    lines.append(f'👤 名前: {display_name}')
                    break
        
        # 電話番号
        if 'phoneNumbers' in contact:
            for i, phone in enumerate(contact['phoneNumbers']):
                type_info = phone.get('formattedType', phone.get('type', ''))
                lines.append(f'📞 電話{i+1}: {phone.get("value", "")} ({type_info})')
        
        # 📝 biographies（従来のメモ）
        if 'biographies' in contact:
            for i, bio in enumerate(contact['biographies']):
                note = bio.get('value', '')
                content_type = bio.get('contentType', '')
                if note:
                    lines.append(f'📝 Biography{i+1} ({content_type}): {note}')
        
        # 🔍 userDefined（カスタムフィールド）
        if 'userDefined' in contact:
            for i, user_field in enumerate(contact['userDefined']):
                key = user_field.get('key', '')
                value = user_field.get('value', '')
                if key and value:
                    lines.append(f'🏷️  カスタム{i+1} [{key}]: {value}')
        
        # 📋 clientData（アプリ固有データ）
        if 'clientData' in contact:
            for i, client_data in enumerate(contact['clientData']):
                key = client_data.get('key', '')
                value = client_data.get('value', '')
                if key and value:
                    lines.append(f'💾 ClientData{i+1} [{key}]: {value}')
        
        # 🔍 RAWデータ表示（デバッグ用）
        lines.append('\n📋 全フィールド（RAWデータ）:')
        for field_name, field_data in contact.items():
            if field_name not in ['names', 'phoneNumbers', 'biographies']:
                if field_data:  # 空でない場合のみ表示
                    lines.append(f'  {field_name}: {field_data}')
        
        return '\n'.join(lines)
    
    def search_and_display_all_fields(self, keyword):
        """全フィールド検索・表示"""
        from datetime import datetime
        start_time = datetime.now()
        
        results = self.search_with_all_notes_fields(keyword)
        
        if not results:
            print('該当する連絡先が見つかりませんでした')
            return
        
        print('\n' + '='*80)
        print(f'🔍 全フィールド検索結果: {len(results)} 件')
        print('='*80)
        
        for i, contact in enumerate(results, 1):
            print(f'\n[{i}]')
            print(self.format_all_fields_contact(contact))
        
        search_time = (datetime.now() - start_time).total_seconds()
        print(f'\n🕐 検索時間: {search_time:.3f}秒')
        print('='*80)

def main():
    if len(sys.argv) < 2:
        print('使用方法:')
        print('  python3 contacts_notes_search.py "検索キーワード"')
        return
    
    keyword = sys.argv[1]
    search_system = ContactsNotesSearch()
    search_system.search_and_display_all_fields(keyword)

if __name__ == '__main__':
    main()
