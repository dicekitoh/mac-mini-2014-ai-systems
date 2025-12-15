#!/usr/bin/env python3
"""
@icloud.com/@me.com/@mac.comからのメールを専用フォルダに移動するスクリプト
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
            print(f"フォルダ '{folder_name}' を作成しました")
        else:
            print(f"フォルダ '{folder_name}' は既に存在します")
            
    except Exception as e:
        print(f"フォルダ作成エラー: {e}")

def move_icloud_emails(mail, target_folder):
    """@icloud.com/@me.com/@mac.comからのメールを移動"""
    try:
        # INBOXを選択
        mail.select('INBOX')
        
        # iCloud関連ドメインからのメールを検索
        domains = ['@icloud.com', '@me.com', '@mac.com']
        all_email_ids = []
        
        print("\n検索中...")
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
            print("iCloudからのメールは見つかりませんでした")
            return 0
        
        print(f"\n合計 {total_emails} 件のメールが見つかりました")
        
        moved_count = 0
        for i, email_id in enumerate(all_email_ids, 1):
            try:
                # メールを取得
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # 件名を取得
                subject_header = msg['Subject']
                if subject_header:
                    subject = decode_header(subject_header)[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode('utf-8', errors='ignore')
                else:
                    subject = "（件名なし）"
                
                # 送信者を取得
                from_addr = msg['From'] or "（送信者不明）"
                
                # 日付を取得
                date = msg['Date'] or "（日付不明）"
                
                print(f"\n[{i}/{total_emails}] 移動中...")
                print(f"  送信者: {from_addr}")
                print(f"  件名: {subject}")
                print(f"  日付: {date}")
                
                # メールをコピー
                mail.copy(email_id, target_folder)
                
                # 元のメールを削除フラグを立てる
                mail.store(email_id, '+FLAGS', '\\Deleted')
                
                moved_count += 1
                print(f"  → 移動完了")
                
            except Exception as e:
                print(f"  → エラー: {e}")
                continue
        
        # 削除フラグが立てられたメールを実際に削除
        mail.expunge()
        
        return moved_count
        
    except Exception as e:
        print(f"メール移動エラー: {e}")
        return 0

def main():
    """メイン処理"""
    print("=== iCloudメール移動ツール ===\n")
    
    # 設定を読み込む
    config = load_config()
    
    # Gmailに接続
    print("Gmailに接続中...")
    mail = connect_to_gmail(config)
    
    # フォルダ名を設定
    target_folder = "@icloud"
    
    # フォルダを作成
    print(f"\nフォルダ '{target_folder}' を確認中...")
    create_folder_if_not_exists(mail, target_folder)
    
    # メールを移動
    moved_count = move_icloud_emails(mail, target_folder)
    
    # 接続を閉じる
    mail.close()
    mail.logout()
    
    # 結果を表示
    print(f"\n=== 処理完了 ===")
    print(f"移動したメール数: {moved_count} 件")
    print(f"移動先フォルダ: {target_folder}")
    
    if moved_count > 0:
        print(f"\n※ Gmailの '{target_folder}' ラベルで確認できます")

if __name__ == "__main__":
    main()