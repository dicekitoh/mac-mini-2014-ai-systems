#!/usr/bin/env python3
"""
Google Contacts APIにメモを追加するスクリプト
"""

import pickle
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class ContactNoteAdder:
    def __init__(self):
        self.token_path = '/home/fujinosuke/unified_oauth_token_write.pickle'
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
    
    def add_note_to_contact(self, resource_name, note_content):
        """指定されたコンタクトにメモを追加"""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            # 現在のコンタクト情報を取得
            contact = self.service.people().get(
                resourceName=resource_name,
                personFields='names,phoneNumbers,emailAddresses,organizations,birthdays,biographies,metadata'
            ).execute()
            
            # 既存のメモを取得
            existing_notes = contact.get('biographies', [])
            
            # 新しいメモを追加
            new_note = {
                'value': note_content,
                'contentType': 'TEXT_PLAIN'
            }
            
            # メモリストを更新
            updated_notes = existing_notes + [new_note]
            
            # コンタクトを更新
            result = self.service.people().updateContact(
                resourceName=resource_name,
                updatePersonFields='biographies',
                body={
                    'etag': contact.get('etag'),
                    'biographies': updated_notes
                }
            ).execute()
            
            print(f"✅ メモ追加成功")
            print(f"   Resource Name: {resource_name}")
            print(f"   追加メモ: {note_content}")
            
            return True
            
        except Exception as e:
            print(f"❌ メモ追加失敗: {str(e)}")
            return False

def main():
    """菜那さんにSMSメモを追加"""
    adder = ContactNoteAdder()
    
    # 菜那さんのresource_name
    resource_name = "people/c6385158792781991852"
    
    # 追加するメモ
    note_content = "2025-07-12: Claude Code経由でメモ追加テスト - mobile_scriptsフォルダから実行成功"
    
    result = adder.add_note_to_contact(resource_name, note_content)
    
    if result:
        print("\n次回同期時にローカルDBにも反映されます。")
    else:
        print("\nメモ追加に失敗しました。")

if __name__ == "__main__":
    main()