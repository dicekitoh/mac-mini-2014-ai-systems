#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts 詳細検索システム（メモ欄対応）
APIから直接詳細情報（メモ、誕生日、住所等）を取得
"""

import pickle
import sys
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ContactsDetailedSearch:
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
    
    def search_contacts_with_details(self, keyword):
        """詳細情報付きで連絡先検索"""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            print(f'🔍 "{keyword}" の詳細検索実行中...')
            
            # 全連絡先を取得（詳細フィールド付き）
            contacts = []
            page_token = None
            
            while True:
                if page_token:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=1000,
                        pageToken=page_token,
                        personFields='names,phoneNumbers,emailAddresses,organizations,biographies,birthdays,addresses,urls,relations,events,memberships,metadata'
                    ).execute()
                else:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=1000,
                        personFields='names,phoneNumbers,emailAddresses,organizations,biographies,birthdays,addresses,urls,relations,events,memberships,metadata'
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
                match_found = False
                search_texts = []
                
                # 名前検索
                if 'names' in contact:
                    for name in contact['names']:
                        display_name = name.get('displayName', '')
                        given_name = name.get('givenName', '')
                        family_name = name.get('familyName', '')
                        search_texts.extend([display_name, given_name, family_name])
                
                # 電話番号検索
                if 'phoneNumbers' in contact:
                    for phone in contact['phoneNumbers']:
                        search_texts.append(phone.get('value', ''))
                
                # メールアドレス検索
                if 'emailAddresses' in contact:
                    for email in contact['emailAddresses']:
                        search_texts.append(email.get('value', ''))
                
                # メモ欄検索
                if 'biographies' in contact:
                    for bio in contact['biographies']:
                        search_texts.append(bio.get('value', ''))
                
                # 組織検索
                if 'organizations' in contact:
                    for org in contact['organizations']:
                        search_texts.extend([org.get('name', ''), org.get('title', '')])
                
                # キーワードマッチング
                all_text = ' '.join(filter(None, search_texts)).lower()
                if keyword_lower in all_text:
                    matches.append(contact)
            
            print(f'✅ {len(matches)} 件の連絡先が見つかりました')
            return matches
            
        except Exception as e:
            print(f'❌ 検索エラー: {e}')
            return []
    
    def format_detailed_contact(self, contact):
        """詳細連絡先情報の整形表示"""
        lines = []
        lines.append('=' * 60)
        
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
        
        # メールアドレス
        if 'emailAddresses' in contact:
            for i, email in enumerate(contact['emailAddresses']):
                type_info = email.get('formattedType', email.get('type', ''))
                lines.append(f'📧 メール{i+1}: {email.get("value", "")} ({type_info})')
        
        # 組織
        if 'organizations' in contact:
            for org in contact['organizations']:
                org_name = org.get('name', '')
                title = org.get('title', '')
                if org_name or title:
                    lines.append(f'🏢 組織: {org_name} {title}'.strip())
        
        # 📝 メモ（重要！）
        if 'biographies' in contact:
            for bio in contact['biographies']:
                note = bio.get('value', '')
                if note:
                    lines.append(f'📝 メモ: {note}')
        
        # 誕生日
        if 'birthdays' in contact:
            for birthday in contact['birthdays']:
                date = birthday.get('date', {})
                if date:
                    year = date.get('year', '')
                    month = date.get('month', '')
                    day = date.get('day', '')
                    if month and day:
                        birthday_str = f'{month}/{day}'
                        if year:
                            birthday_str += f'/{year}'
                        lines.append(f'🎂 誕生日: {birthday_str}')
        
        # 住所
        if 'addresses' in contact:
            for addr in contact['addresses']:
                formatted_value = addr.get('formattedValue', '')
                type_info = addr.get('formattedType', addr.get('type', ''))
                if formatted_value:
                    lines.append(f'🏠 住所 ({type_info}): {formatted_value}')
        
        # URL
        if 'urls' in contact:
            for url in contact['urls']:
                value = url.get('value', '')
                type_info = url.get('formattedType', url.get('type', ''))
                if value:
                    lines.append(f'🌐 URL ({type_info}): {value}')
        
        # 関係
        if 'relations' in contact:
            for relation in contact['relations']:
                person = relation.get('person', '')
                type_info = relation.get('formattedType', relation.get('type', ''))
                if person:
                    lines.append(f'👥 関係 ({type_info}): {person}')
        
        # イベント
        if 'events' in contact:
            for event in contact['events']:
                date = event.get('date', {})
                type_info = event.get('formattedType', event.get('type', ''))
                if date:
                    year = date.get('year', '')
                    month = date.get('month', '')
                    day = date.get('day', '')
                    if month and day:
                        event_str = f'{month}/{day}'
                        if year:
                            event_str += f'/{year}'
                        lines.append(f'📅 イベント ({type_info}): {event_str}')
        
        return '\n'.join(lines)
    
    def search_and_display_detailed(self, keyword):
        """詳細検索・表示統合"""
        from datetime import datetime
        start_time = datetime.now()
        
        results = self.search_contacts_with_details(keyword)
        
        if not results:
            print('該当する連絡先が見つかりませんでした')
            return
        
        print('\n' + '='*60)
        print(f'🔍 詳細検索結果: {len(results)} 件')
        print('='*60)
        
        for i, contact in enumerate(results, 1):
            print(f'\n[{i}]')
            print(self.format_detailed_contact(contact))
        
        search_time = (datetime.now() - start_time).total_seconds()
        print(f'\n🕐 検索時間: {search_time:.3f}秒')
        print('='*60)

def main():
    if len(sys.argv) < 2:
        print('使用方法:')
        print('  python3 contacts_detailed_search.py "検索キーワード"')
        print('\n例:')
        print('  python3 contacts_detailed_search.py "佐々木奈々"')
        print('  python3 contacts_detailed_search.py "菜那"')
        return
    
    keyword = sys.argv[1]
    search_system = ContactsDetailedSearch()
    search_system.search_and_display_detailed(keyword)

if __name__ == '__main__':
    main()
