#!/usr/bin/env python3
"""
Gmail API を使用したメール送信
"""

import pickle
import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from datetime import datetime

def load_credentials():
    """保存されたトークンを読み込む"""
    token_path = "/home/fujinosuke/projects/google_auth/unified_google_token.pickle"
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
        # トークンの有効性確認
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        return creds
    else:
        raise FileNotFoundError(f"認証トークンが見つかりません: {token_path}")

def create_message(sender, to, subject, message_text):
    """メールメッセージを作成"""
    message = MIMEText(message_text, 'plain', 'utf-8')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """メールを送信"""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"✅ メール送信成功: Message Id: {message['id']}")
        return message
    except Exception as error:
        print(f"❌ メール送信エラー: {error}")
        return None

def main():
    """メイン処理"""
    try:
        # 認証情報を読み込む
        creds = load_credentials()
        
        # Gmail APIサービスを構築
        service = build('gmail', 'v1', credentials=creds)
        
        # メール内容
        sender = "itoh@thinksblog.com"
        to = "amitri@mac.com"
        subject = "テストメール - Gmail API"
        body = f"""
Gmail APIを使用したテストメールです。

送信日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

このメールが正常に受信できれば、メール送信システムは正常に動作しています。
"""
        
        # メッセージを作成
        message = create_message(sender, to, subject, body)
        
        # メールを送信
        send_message(service, 'me', message)
        
        print(f"\n📧 メール送信完了")
        print(f"   宛先: {to}")
        print(f"   件名: {subject}")
        
    except Exception as e:
        print(f"エラー: {e}")

if __name__ == '__main__':
    main()