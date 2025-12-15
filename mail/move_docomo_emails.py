#!/usr/bin/env python3
"""
@docomo.ne.jpからのメールを専用フォルダに移動するスクリプト
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

def move_docomo_emails(mail, target_folder):
    """@docomo.ne.jpからのメールを移動"""
    try:
        # INBOXを選択
        mail.select('INBOX')
        
        # @docomo.ne.jpからのメールを検索
        search_criteria = 'FROM "@docomo.ne.jp"'
        _, message_ids = mail.search(None, search_criteria)
        
        if not message_ids[0]:
            print("@docomo.ne.jpからのメールは見つかりませんでした")
            return 0
        
        # メッセージIDのリストを取得
        email_ids = message_ids[0].split()
        total_emails = len(email_ids)
        print(f"\n@docomo.ne.jpからのメールが {total_emails} 件見つかりました")
        
        moved_count = 0
        for i, email_id in enumerate(email_ids, 1):
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
                
                # 日付を取得
                date = msg['Date']
                
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
    print("=== @docomo.ne.jpメール移動ツール ===\n")
    
    # 設定を読み込む
    config = load_config()
    
    # Gmailに接続
    print("Gmailに接続中...")
    mail = connect_to_gmail(config)
    
    # フォルダ名を設定
    target_folder = "@docomo.ne.jp"
    
    # フォルダを作成
    print(f"\nフォルダ '{target_folder}' を確認中...")
    create_folder_if_not_exists(mail, target_folder)
    
    # メールを移動
    print(f"\n@docomo.ne.jpからのメールを検索・移動中...")
    moved_count = move_docomo_emails(mail, target_folder)
    
    # 接続を閉じる
    mail.close()
    mail.logout()
    
    # 結果を表示
    print(f"\n=== 処理完了 ===")
    print(f"移動したメール数: {moved_count} 件")
    print(f"移動先フォルダ: {target_folder}")
    
    if moved_count > 0:
        print(f"\n※ Gmailの '@docomo.ne.jp' ラベルで確認できます")

if __name__ == "__main__":
    main()