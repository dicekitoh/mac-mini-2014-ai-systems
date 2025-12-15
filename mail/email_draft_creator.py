#!/usr/bin/env python3
"""
シンプルなメール下書き作成システム
連絡先JSONファイルから情報を読み込んでメール下書きを生成
"""

import json
import sys
from datetime import datetime

class EmailDraftCreator:
    def __init__(self, contacts_file='contacts.json'):
        self.contacts_file = contacts_file
        self.contacts = self.load_contacts()
    
    def load_contacts(self):
        """連絡先情報を読み込む"""
        try:
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('contacts', [])
        except FileNotFoundError:
            print(f"連絡先ファイル {self.contacts_file} が見つかりません")
            return []
        except json.JSONDecodeError:
            print(f"連絡先ファイルの形式が正しくありません")
            return []
    
    def find_contact(self, name):
        """名前から連絡先を検索"""
        for contact in self.contacts:
            if name in contact['name']:
                return contact
        return None
    
    def create_thank_you_email(self, name, subject_detail=""):
        """お礼メールの下書きを作成"""
        contact = self.find_contact(name)
        if not contact:
            return f"エラー: {name}さんの連絡先が見つかりません"
        
        # 件名の生成
        if subject_detail:
            subject = f"{subject_detail}のお礼"
        else:
            subject = "お礼"
        
        # 本文の生成
        body = f"""{contact['name']}様

いつもお世話になっております。

{subject_detail if subject_detail else "先日"}は誠にありがとうございました。

今後ともよろしくお願いいたします。

よろしくお願いいたします。
"""
        
        # メール下書きの生成
        draft = f"""
====== メール下書き ======
宛先: {contact['email']}
件名: {subject}

{body}
========================
"""
        return draft
    
    def create_meeting_request_email(self, name, date="", time="", place=""):
        """面談依頼メールの下書きを作成"""
        contact = self.find_contact(name)
        if not contact:
            return f"エラー: {name}さんの連絡先が見つかりません"
        
        body = f"""{contact['name']}様

お世話になっております。

お忙しいところ恐れ入りますが、下記の日程でお打ち合わせのお時間をいただけますでしょうか。

日時: {date if date else '○月○日'} {time if time else '○時○分'}
場所: {place if place else '弊社会議室'}

ご都合はいかがでしょうか。
お返事をお待ちしております。

よろしくお願いいたします。
"""
        
        draft = f"""
====== メール下書き ======
宛先: {contact['email']}
件名: 面談のお願い

{body}
========================
"""
        return draft
    
    def list_contacts(self):
        """登録済み連絡先一覧を表示"""
        if not self.contacts:
            return "連絡先が登録されていません"
        
        result = "=== 登録済み連絡先 ===\\n"
        for i, contact in enumerate(self.contacts, 1):
            result += f"{i}. {contact['name']} ({contact['email']})\\n"
        return result

def main():
    """メイン関数"""
    creator = EmailDraftCreator()
    
    # コマンドライン引数の処理
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python email_draft_creator.py list                     - 連絡先一覧")
        print("  python email_draft_creator.py thank <名前> [詳細]      - お礼メール")
        print("  python email_draft_creator.py meeting <名前> [日付]    - 面談依頼")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print(creator.list_contacts())
    
    elif command == "thank":
        if len(sys.argv) < 3:
            print("エラー: 名前を指定してください")
            return
        name = sys.argv[2]
        detail = sys.argv[3] if len(sys.argv) > 3 else ""
        print(creator.create_thank_you_email(name, detail))
    
    elif command == "meeting":
        if len(sys.argv) < 3:
            print("エラー: 名前を指定してください")
            return
        name = sys.argv[2]
        date = sys.argv[3] if len(sys.argv) > 3 else ""
        print(creator.create_meeting_request_email(name, date))
    
    else:
        print(f"不明なコマンド: {command}")

if __name__ == "__main__":
    main()