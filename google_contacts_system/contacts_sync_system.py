#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts ローカル同期システム
マスター: Google Contacts API (610件)
ローカル: JSONデータベース + 高速検索
"""

import json
import pickle
import os
import sys
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ContactsSyncSystem:
    def __init__(self):
        self.token_path = '/home/fujinosuke/unified_oauth_token_new.pickle'
        self.db_path = '/home/fujinosuke/projects/google_contacts_system/contacts_local_db.json'
        self.sync_log_path = '/home/fujinosuke/projects/google_contacts_system/sync_log.txt'
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
            print('✅ Google Contacts API認証成功')
            return True
            
        except Exception as e:
            print(f'❌ 認証エラー: {e}')
            return False
    
    def fetch_all_contacts(self):
        """Google APIから全連絡先取得"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            print('Google Contacts API から全連絡先を取得中...')
            
            # 全連絡先を取得（ページネーション対応）
            contacts = []
            page_token = None
            
            while True:
                if page_token:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=2000,
                        pageToken=page_token,
                        personFields='names,phoneNumbers,emailAddresses,organizations,metadata,birthdays,biographies'
                    ).execute()
                else:
                    results = self.service.people().connections().list(
                        resourceName='people/me',
                        pageSize=2000,
                        personFields='names,phoneNumbers,emailAddresses,organizations,metadata,birthdays,biographies'
                    ).execute()
                
                connections = results.get('connections', [])
                contacts.extend(connections)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
                print(f'取得中... 現在 {len(contacts)} 件')
            
            print(f'✅ 合計 {len(contacts)} 件の連絡先を取得')
            return contacts
            
        except Exception as e:
            print(f'❌ API取得エラー: {e}')
            return None
    
    def process_contacts(self, raw_contacts):
        """連絡先データを検索用に最適化"""
        processed = []
        
        for contact in raw_contacts:
            # 基本情報抽出
            entry = {
                'resource_name': contact.get('resourceName', ''),
                'etag': contact.get('etag', ''),
                'names': [],
                'phones': [],
                'emails': [],
                'organizations': [],
                'birthdays': [],
                'notes': [],
                'search_text': ''
            }
            
            # 名前
            if 'names' in contact:
                for name in contact['names']:
                    entry['names'].append({
                        'display_name': name.get('displayName', ''),
                        'given_name': name.get('givenName', ''),
                        'family_name': name.get('familyName', '')
                    })
            
            # 電話番号
            if 'phoneNumbers' in contact:
                for phone in contact['phoneNumbers']:
                    entry['phones'].append({
                        'value': phone.get('value', ''),
                        'type': phone.get('type', ''),
                        'formatted_type': phone.get('formattedType', '')
                    })
            
            # メールアドレス
            if 'emailAddresses' in contact:
                for email in contact['emailAddresses']:
                    entry['emails'].append({
                        'value': email.get('value', ''),
                        'type': email.get('type', ''),
                        'formatted_type': email.get('formattedType', '')
                    })
            
            # 組織
            if 'organizations' in contact:
                for org in contact['organizations']:
                    entry['organizations'].append({
                        'name': org.get('name', ''),
                        'title': org.get('title', '')
                    })
            
            # 誕生日
            if 'birthdays' in contact:
                for birthday in contact['birthdays']:
                    date_info = birthday.get('date', {})
                    entry['birthdays'].append({
                        'year': date_info.get('year'),
                        'month': date_info.get('month'),
                        'day': date_info.get('day'),
                        'text': birthday.get('text', '')
                    })
            
            # メモ/備考
            if 'biographies' in contact:
                for bio in contact['biographies']:
                    entry['notes'].append({
                        'content': bio.get('value', ''),
                        'content_type': bio.get('contentType', '')
                    })
            
            # 検索用テキスト生成
            search_parts = []
            for name in entry['names']:
                search_parts.extend([name['display_name'], name['given_name'], name['family_name']])
            for phone in entry['phones']:
                search_parts.append(phone['value'])
            for email in entry['emails']:
                search_parts.append(email['value'])
            for org in entry['organizations']:
                search_parts.extend([org['name'], org['title']])
            
            entry['search_text'] = ' '.join(filter(None, search_parts)).lower()
            
            if entry['search_text']:  # 検索可能な情報がある場合のみ追加
                processed.append(entry)
        
        return processed
    
    def save_local_db(self, contacts):
        """ローカルデータベースに保存"""
        try:
            db_data = {
                'last_sync': datetime.now(timezone.utc).isoformat(),
                'contact_count': len(contacts),
                'version': '1.0',
                'contacts': contacts
            }
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)
            
            print(f'✅ ローカルDB保存完了: {len(contacts)} 件')
            return True
            
        except Exception as e:
            print(f'❌ ローカルDB保存エラー: {e}')
            return False
    
    def load_local_db(self):
        """ローカルデータベース読み込み"""
        try:
            if not os.path.exists(self.db_path):
                return None
                
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f'❌ ローカルDB読み込みエラー: {e}')
            return None
    
    def log_sync(self, message):
        """同期ログ記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'[{timestamp}] {message}\n'
        
        with open(self.sync_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def full_sync(self):
        """完全同期実行"""
        self.log_sync('=== 完全同期開始 ===')
        
        # Google Contacts API から取得
        raw_contacts = self.fetch_all_contacts()
        if not raw_contacts:
            self.log_sync('❌ 完全同期失敗: API取得エラー')
            return False
        
        # データ処理
        processed_contacts = self.process_contacts(raw_contacts)
        self.log_sync(f'データ処理完了: {len(processed_contacts)} 件')
        
        # ローカル保存
        if self.save_local_db(processed_contacts):
            self.log_sync(f'✅ 完全同期成功: {len(processed_contacts)} 件')
            return True
        else:
            self.log_sync('❌ 完全同期失敗: ローカル保存エラー')
            return False
    
    def get_sync_status(self):
        """同期状況確認"""
        db = self.load_local_db()
        if not db:
            return {
                'status': 'no_db',
                'message': 'ローカルDBなし',
                'last_sync': None,
                'contact_count': 0
            }
        
        return {
            'status': 'ok',
            'message': 'ローカルDB利用可能',
            'last_sync': db.get('last_sync'),
            'contact_count': db.get('contact_count', 0),
            'version': db.get('version', 'unknown')
        }

def main():
    import sys
    
    sync_system = ContactsSyncSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'sync':
            # 完全同期実行
            success = sync_system.full_sync()
            sys.exit(0 if success else 1)
            
        elif command == 'status':
            # 同期状況確認
            status = sync_system.get_sync_status()
            print(f"状態: {status['message']}")
            print(f"最終同期: {status['last_sync']}")
            print(f"連絡先数: {status['contact_count']} 件")
            
        elif command == 'test':
            # 認証テスト
            if sync_system.authenticate():
                print('✅ 認証テスト成功')
            else:
                print('❌ 認証テスト失敗')
                sys.exit(1)
    else:
        print('使用方法:')
        print('  python3 contacts_sync_system.py sync    # 完全同期実行')
        print('  python3 contacts_sync_system.py status  # 同期状況確認')
        print('  python3 contacts_sync_system.py test    # 認証テスト')

if __name__ == '__main__':
    main()
