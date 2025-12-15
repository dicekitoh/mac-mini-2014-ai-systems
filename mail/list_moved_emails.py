#!/usr/bin/env python3
"""
各フォルダに移動したメールアドレスの一覧を表示するスクリプト
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import json
import os
import sys
from collections import defaultdict

# 設定ファイルのパス
CONFIG_PATH = '/home/rootmax/google/mail_config.json'

# チェックするフォルダ
FOLDERS_TO_CHECK = ['@docomo.ne.jp', '@au', '@softbank', '@icloud']

def load_config():
    """メール設定を読み込む"""
    if not os.path.exists(CONFIG_PATH):
        print(f"エラー: 設定ファイルが見つかりません: {CONFIG_PATH}")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def connect_to_gmail(config):
    """Gmailに接続"""
    try:
        gmail_config = config['gmail']
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(gmail_config['email'], gmail_config['app_password'])
        return mail
    except Exception as e:
        print(f"Gmail接続エラー: {e}")
        sys.exit(1)

def extract_email_address(from_field):
    """From フィールドからメールアドレスを抽出"""
    try:
        # decode_header を試みる
        decoded = decode_header(from_field)
        from_str = ""
        for part, encoding in decoded:
            if isinstance(part, bytes):
                if encoding:
                    from_str += part.decode(encoding, errors='ignore')
                else:
                    from_str += part.decode('utf-8', errors='ignore')
            else:
                from_str += str(part)
        
        # メールアドレスを抽出
        name, email_addr = parseaddr(from_str)
        return email_addr if email_addr else from_field
    except:
        # エラーの場合は元の文字列から抽出を試みる
        import re
        match = re.search(r'<([^>]+)>', from_field)
        if match:
            return match.group(1)
        return from_field

def list_emails_in_folder(mail, folder_name):
    """特定フォルダ内のメールアドレス一覧を取得"""
    email_addresses = set()
    
    try:
        # フォルダを選択
        mail.select(f'"{folder_name}"')
        
        # すべてのメールを検索
        _, message_ids = mail.search(None, 'ALL')
        
        if not message_ids[0]:
            return email_addresses
        
        email_ids = message_ids[0].split()
        
        for email_id in email_ids:
            try:
                # メールヘッダーのみ取得（高速化のため）
                _, msg_data = mail.fetch(email_id, '(BODY[HEADER.FIELDS (FROM)])')
                raw_header = msg_data[0][1]
                msg = email.message_from_bytes(raw_header)
                
                from_field = msg.get('From', '')
                if from_field:
                    email_addr = extract_email_address(from_field)
                    if email_addr:
                        email_addresses.add(email_addr)
                        
            except Exception as e:
                continue
        
    except Exception as e:
        print(f"  エラー: {folder_name} - {e}")
    
    return email_addresses

def main():
    """メイン処理"""
    print("=== 移動済みメールアドレス一覧 ===\n")
    
    # 設定を読み込む
    config = load_config()
    
    # Gmailに接続
    print("Gmailに接続中...")
    mail = connect_to_gmail(config)
    print("接続成功\n")
    
    # 各フォルダのメールアドレスを取得
    all_results = {}
    
    for folder in FOLDERS_TO_CHECK:
        print(f"フォルダ '{folder}' を確認中...")
        email_addresses = list_emails_in_folder(mail, folder)
        all_results[folder] = sorted(list(email_addresses))
        print(f"  → {len(email_addresses)} 個のユニークなアドレスを発見\n")
    
    # 接続を閉じる
    mail.close()
    mail.logout()
    
    # 結果を表示
    print("\n=== 詳細結果 ===\n")
    
    for folder, addresses in all_results.items():
        print(f"【{folder}】({len(addresses)}件)")
        if addresses:
            for addr in addresses:
                print(f"  - {addr}")
        else:
            print(f"  （メールなし）")
        print()
    
    # サマリー表示
    total_addresses = sum(len(addresses) for addresses in all_results.values())
    print(f"\n合計: {total_addresses} 個のユニークなメールアドレス")

if __name__ == "__main__":
    main()