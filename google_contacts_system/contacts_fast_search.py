#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Contacts 高速検索システム
ローカルDB使用で0.1秒未満の検索を実現
"""

import json
import os
import sys
import re
from datetime import datetime

class ContactsFastSearch:
    def __init__(self):
        self.db_path = '/home/fujinosuke/projects/google_contacts_system/contacts_local_db.json'
        self.contacts_db = None
        self.last_loaded = None
        
    def load_db(self):
        """ローカルDB読み込み（必要時のみ）"""
        try:
            if not os.path.exists(self.db_path):
                print('❌ ローカルDBが見つかりません')
                print('   先に同期を実行してください: python3 contacts_sync_system.py sync')
                return False
            
            # ファイル更新時刻確認
            file_mtime = os.path.getmtime(self.db_path)
            if self.last_loaded and file_mtime <= self.last_loaded:
                return True  # 既に最新版読み込み済み
            
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            
            self.contacts_db = db_data
            self.last_loaded = file_mtime
            
            print(f'✅ ローカルDB読み込み完了: {db_data.get("contact_count", 0)} 件')
            print(f'   最終同期: {db_data.get("last_sync", "不明")}')
            return True
            
        except Exception as e:
            print(f'❌ DB読み込みエラー: {e}')
            return False
    
    def search(self, keyword, limit=10):
        """高速検索実行"""
        if not self.load_db():
            return []
        
        if not keyword or not keyword.strip():
            print('検索キーワードを入力してください')
            return []
        
        keyword = keyword.lower().strip()
        contacts = self.contacts_db.get('contacts', [])
        
        # 検索実行
        matches = []
        for contact in contacts:
            search_text = contact.get('search_text', '')
            
            # キーワードマッチング（部分一致）
            if keyword in search_text:
                # スコア計算（完全一致を優先）
                score = 0
                if keyword in search_text:
                    score += 1
                
                # 名前での完全一致は高スコア
                for name in contact.get('names', []):
                    display_name = name.get('display_name', '').lower()
                    if keyword == display_name:
                        score += 10
                    elif keyword in display_name:
                        score += 5
                
                matches.append((score, contact))
        
        # スコア順でソート
        matches.sort(key=lambda x: x[0], reverse=True)
        
        # 結果制限
        results = [match[1] for match in matches[:limit]]
        
        print(f'検索結果: {len(results)} 件 （キーワード: "{keyword}"）')
        return results
    
    def format_contact(self, contact):
        """連絡先情報の整形表示"""
        lines = []
        
        # 名前
        names = contact.get('names', [])
        if names:
            name = names[0].get('display_name', '')
            lines.append(f'👤 名前: {name}')
        
        # 電話番号
        phones = contact.get('phones', [])
        for i, phone in enumerate(phones[:3]):  # 最大3件
            type_info = phone.get('formatted_type', phone.get('type', ''))
            lines.append(f'📞 電話{i+1}: {phone.get("value", "")} ({type_info})')
        
        # メールアドレス
        emails = contact.get('emails', [])
        for i, email in enumerate(emails[:2]):  # 最大2件
            type_info = email.get('formatted_type', email.get('type', ''))
            lines.append(f'📧 メール{i+1}: {email.get("value", "")} ({type_info})')
        
        # 組織
        organizations = contact.get('organizations', [])
        if organizations:
            org = organizations[0]
            org_name = org.get('name', '')
            title = org.get('title', '')
            if org_name or title:
                lines.append(f'🏢 組織: {org_name} {title}'.strip())
        
        return '\n'.join(lines)
    
    def search_and_display(self, keyword, limit=10):
        """検索・表示統合"""
        start_time = datetime.now()
        
        results = self.search(keyword, limit)
        
        if not results:
            print('該当する連絡先が見つかりませんでした')
            return
        
        print('\n' + '='*50)
        for i, contact in enumerate(results, 1):
            print(f'\n[{i}] {self.format_contact(contact)}')
        
        search_time = (datetime.now() - start_time).total_seconds()
        print(f'\n検索時間: {search_time:.3f}秒')
        print('='*50)
    
    def get_db_status(self):
        """DB状況確認"""
        if not self.load_db():
            return
        
        db = self.contacts_db
        print(f'📊 ローカルDB状況:')
        print(f'   最終同期: {db.get("last_sync", "不明")}')
        print(f'   連絡先数: {db.get("contact_count", 0)} 件')
        print(f'   DBバージョン: {db.get("version", "不明")}')
        print(f'   DBファイル: {self.db_path}')

def main():
    search_system = ContactsFastSearch()
    
    if len(sys.argv) < 2:
        print('使用方法:')
        print('  python3 contacts_fast_search.py "検索キーワード"')
        print('  python3 contacts_fast_search.py status')
        print('\n例:')
        print('  python3 contacts_fast_search.py "伊藤"')
        print('  python3 contacts_fast_search.py "090"')
        return
    
    command = sys.argv[1]
    
    if command == 'status':
        search_system.get_db_status()
    else:
        # 検索実行
        keyword = command
        limit = 10
        
        # オプション: 件数制限
        if len(sys.argv) > 2:
            try:
                limit = int(sys.argv[2])
            except ValueError:
                pass
        
        search_system.search_and_display(keyword, limit)

if __name__ == '__main__':
    main()
