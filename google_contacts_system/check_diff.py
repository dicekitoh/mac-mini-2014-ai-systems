#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts API vs ローカルDB 差分チェック
"""

import json
import pickle
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def authenticate():
    """OAuth認証"""
    try:
        token_path = '/home/fujinosuke/unified_oauth_token_new.pickle'
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('people', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f'認証エラー: {e}')
        return None

def get_api_contacts():
    """Google API から連絡先取得"""
    service = authenticate()
    if not service:
        return None
    
    try:
        print('Google API から連絡先数を取得中...')
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1,
            personFields='names'
        ).execute()
        
        total_size = results.get('totalSize', 0)
        return total_size
        
    except Exception as e:
        print(f'API取得エラー: {e}')
        return None

def get_local_db():
    """ローカルDB読み込み"""
    db_path = '/home/fujinosuke/projects/google_contacts_system/contacts_local_db.json'
    
    try:
        if not os.path.exists(db_path):
            return None
            
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        print(f'ローカルDB読み込みエラー: {e}')
        return None

def check_difference():
    """差分チェック実行"""
    print('=' * 60)
    print('📊 Google Contacts API vs ローカルDB 差分チェック')
    print('=' * 60)
    
    # API連絡先数取得
    api_count = get_api_contacts()
    if api_count is None:
        print('❌ API接続失敗')
        return
    
    # ローカルDB読み込み
    local_db = get_local_db()
    if local_db is None:
        print('❌ ローカルDB読み込み失敗')
        return
    
    local_count = local_db.get('contact_count', 0)
    last_sync = local_db.get('last_sync', '不明')
    
    print(f'🌐 Google API 連絡先数: {api_count} 件')
    print(f'💾 ローカルDB 連絡先数: {local_count} 件')
    print(f'📅 最終同期日時: {last_sync}')
    print('')
    
    # 差分計算
    diff = api_count - local_count
    
    if diff == 0:
        print('✅ 差分なし - 完全同期済み')
        print('   データは最新状態です')
    elif diff > 0:
        print(f'⚠️  差分検出: +{diff} 件')
        print(f'   Google API に {diff} 件多く連絡先があります')
        print('   推奨: 同期実行して最新化')
    else:
        print(f'⚠️  差分検出: {diff} 件')
        print(f'   ローカルDB に {abs(diff)} 件多く連絡先があります')
        print('   推奨: 同期実行してクリーンアップ')
    
    print('')
    print('=' * 60)
    
    # 同期推奨判定
    if diff != 0:
        print('🔄 同期推奨コマンド:')
        print('   ./sync_contacts.sh sync')
        print('   または')
        print('   python3 contacts_sync_system.py sync')
    
    return diff

if __name__ == '__main__':
    check_difference()
