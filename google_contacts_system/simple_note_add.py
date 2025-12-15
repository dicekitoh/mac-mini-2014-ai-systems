#!/usr/bin/env python3
"""
シンプルなGoogle Contactsメモ追加
"""

import pickle
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def main():
    print('📝 簡単メモ追加テスト')
    print('=' * 25)
    
    # 認証
    try:
        with open('/home/fujinosuke/unified_oauth_token_write.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('people', 'v1', credentials=creds)
        print('✅ API接続成功')
        
    except Exception as e:
        print(f'❌ 認証エラー: {e}')
        return
    
    # 菜那さんの情報取得
    resource_name = "people/c6385158792781991852"
    
    try:
        # まず現在の情報を取得
        contact = service.people().get(
            resourceName=resource_name,
            personFields='names,biographies,metadata'
        ).execute()
        
        print(f'📞 コンタクト: {contact.get("names", [{}])[0].get("displayName", "不明")}')
        
        # 新しいメモ作成
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_note = f'{timestamp}: Claude Code経由メモ追加成功 - API調整後テスト'
        
        # 既存のメモを取得
        existing_bios = contact.get('biographies', [])
        
        # 新しいメモを追加
        updated_bios = existing_bios + [{
            'value': new_note,
            'contentType': 'TEXT_PLAIN'
        }]
        
        # 更新実行
        result = service.people().updateContact(
            resourceName=resource_name,
            updatePersonFields='biographies',
            body={
                'etag': contact.get('etag'),
                'biographies': updated_bios
            }
        ).execute()
        
        print(f'✅ メモ追加成功!')
        print(f'   内容: {new_note}')
        
    except Exception as e:
        print(f'❌ エラー: {e}')

if __name__ == '__main__':
    main()