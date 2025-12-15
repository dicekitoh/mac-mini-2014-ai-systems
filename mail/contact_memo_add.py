#!/usr/bin/env python3
"""
コンタクトメモ追加システム
"""

import json
from datetime import datetime

def add_memo_to_contact(contact_file, phone_number, memo):
    """指定された電話番号のコンタクトにメモを追加"""
    try:
        # ファイルを読み込み
        with open(contact_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 指定された電話番号のコンタクトを検索
        for contact in data['contacts']:
            for phone in contact.get('phones', []):
                if phone_number in phone['value']:
                    # メモフィールドを追加または更新
                    if 'notes' not in contact:
                        contact['notes'] = []
                    
                    memo_entry = {
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'content': memo
                    }
                    contact['notes'].append(memo_entry)
                    
                    # ファイルに保存
                    with open(contact_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ メモを追加しました")
                    print(f"   連絡先: {contact['names'][0]['display_name'] if contact.get('names') else '名前なし'}")
                    print(f"   電話番号: {phone['value']}")
                    print(f"   メモ: {memo}")
                    return True
        
        print(f"❌ 電話番号 {phone_number} が見つかりませんでした")
        return False
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False

if __name__ == "__main__":
    # 菜那さんにSMS送信結果のメモを追加
    contact_file = "/home/fujinosuke/projects/google_contacts_system/contacts_local_db.json"
    phone_number = "+818045097709"
    memo = "2025-07-12: 暑中お見舞いSMS送信成功 - 有料APIキー使用。Text ID: 89371752288353179。大輔より"
    
    add_memo_to_contact(contact_file, phone_number, memo)