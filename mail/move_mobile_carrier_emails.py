#!/usr/bin/env python3
"""
携帯キャリア（docomo, au, softbank）からのメールを専用フォルダに移動するスクリプト
"""

import imaplib
import email
from email.header import decode_header
import json
import os
import sys
from datetime import datetime

# 設定ファイルのパス
CONFIG_PATH = '/home/rootmax/google/mail_config.json'

# キャリア別の設定
CARRIERS = {
    'docomo': {
        'folder_name': '@docomo.ne.jp',
        'domains': ['@docomo.ne.jp']
    },
    'au': {
        'folder_name': '@au',
        'domains': ['@ezweb.ne.jp', '@au.com', '@auone.jp']
    },
    'softbank': {
        'folder_name': '@softbank',
        'domains': ['@softbank.ne.jp', '@i.softbank.jp', '@vodafone.ne.jp', '@disney.ne.jp', '@y-mobile.ne.jp', '@ymobile.ne.jp', '@emobile.ne.jp', '@willcom.com', '@pdx.ne.jp']
    }
}

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
        # IMAPサーバーに接続
        gmail_config = config['gmail']
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        mail.login(gmail_config['email'], gmail_config['app_password'])
        return mail
    except Exception as e:
        print(f"Gmail接続エラー: {e}")
        sys.exit(1)

def create_folder_if_not_exists(mail, folder_name):
    """フォルダが存在しない場合は作成"""
    try:
        # フォルダ一覧を取得
        _, folders = mail.list()
        folder_exists = False
        
        for folder in folders:
            if folder_name.encode() in folder:
                folder_exists = True
                break
        
        if not folder_exists:
            # フォルダを作成
            mail.create(folder_name)
            print(f"  ✓ フォルダ '{folder_name}' を作成しました")
        else:
            print(f"  ✓ フォルダ '{folder_name}' は既に存在します")
            
    except Exception as e:
        print(f"  ✗ フォルダ作成エラー: {e}")

def move_carrier_emails(mail, carrier_name, carrier_info):
    """特定キャリアからのメールを移動"""
    target_folder = carrier_info['folder_name']
    domains = carrier_info['domains']
    
    print(f"\n【{carrier_name.upper()}】")
    
    # フォルダを作成
    print(f"フォルダ確認中...")
    create_folder_if_not_exists(mail, target_folder)
    
    try:
        # INBOXを選択
        mail.select('INBOX')
        
        # 各ドメインからのメールを検索
        all_email_ids = []
        for domain in domains:
            search_criteria = f'FROM "{domain}"'
            _, message_ids = mail.search(None, search_criteria)
            if message_ids[0]:
                email_ids = message_ids[0].split()
                all_email_ids.extend(email_ids)
                print(f"  - {domain}: {len(email_ids)}件")
        
        # 重複を除去
        all_email_ids = list(set(all_email_ids))
        total_emails = len(all_email_ids)
        
        if total_emails == 0:
            print(f"  → {carrier_name}からのメールは見つかりませんでした")
            return 0
        
        print(f"  → 合計 {total_emails} 件のメールを移動します")
        
        moved_count = 0
        for i, email_id in enumerate(all_email_ids, 1):
            try:
                # メールを取得
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 件名を取得
                subject = decode_header(msg['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode('utf-8', errors='ignore')
                
                # 送信者を取得
                from_addr = msg['From']
                
                print(f"  [{i}/{total_emails}] {from_addr}")
                
                # メールをコピー
                mail.copy(email_id, target_folder)
                
                # 元のメールを削除フラグを立てる
                mail.store(email_id, '+FLAGS', '\\Deleted')
                
                moved_count += 1
                
            except Exception as e:
                print(f"    → エラー: {e}")
                continue
        
        # 削除フラグが立てられたメールを実際に削除
        mail.expunge()
        
        print(f"  ✓ {moved_count}件を移動完了")
        return moved_count
        
    except Exception as e:
        print(f"  ✗ メール移動エラー: {e}")
        return 0

def main():
    """メイン処理"""
    print("=== 携帯キャリアメール整理ツール ===")
    print("対象: docomo, au, softbank\n")
    
    # 設定を読み込む
    config = load_config()
    
    # Gmailに接続
    print("Gmailに接続中...")
    mail = connect_to_gmail(config)
    print("✓ 接続成功")
    
    # 各キャリアのメールを処理
    total_moved = 0
    results = {}
    
    for carrier_name, carrier_info in CARRIERS.items():
        moved_count = move_carrier_emails(mail, carrier_name, carrier_info)
        results[carrier_name] = moved_count
        total_moved += moved_count
    
    # 接続を閉じる
    mail.close()
    mail.logout()
    
    # 結果を表示
    print("\n=== 処理完了 ===")
    print(f"移動したメール総数: {total_moved} 件")
    print("\n内訳:")
    for carrier, count in results.items():
        print(f"  - {carrier}: {count}件 → フォルダ: {CARRIERS[carrier]['folder_name']}")
    
    if total_moved > 0:
        print(f"\n※ Gmailの各キャリアラベルで確認できます")

if __name__ == "__main__":
    main()