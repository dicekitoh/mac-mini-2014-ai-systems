#!/usr/bin/env python3
"""
Gmail送信システム
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class GmailSender:
    def __init__(self):
        # 環境変数から認証情報を取得
        self.email = os.getenv('GMAIL_EMAIL')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not self.email or not self.app_password:
            raise ValueError("Gmail認証情報が設定されていません。環境変数 GMAIL_EMAIL と GMAIL_APP_PASSWORD を設定してください。")
    
    def send_email(self, to_email, subject, body):
        """メール送信"""
        try:
            # MIMEメッセージを作成
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 本文を追加
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTPサーバーに接続
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.app_password)
            
            # メール送信
            server.send_message(msg)
            server.quit()
            
            print(f"✅ メール送信成功")
            print(f"   宛先: {to_email}")
            print(f"   件名: {subject}")
            print(f"   送信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ メール送信失敗: {str(e)}")
            return False

def main():
    """テストメール送信"""
    sender = GmailSender()
    
    # 暑中お見舞いメール送信
    to_email = "amitri@mac.com"
    subject = "暑中お見舞い申し上げます"
    body = """いつもお世話になっております。

暑い日が続いておりますが、いかがお過ごしでしょうか。

暑中お見舞い申し上げます。
これからも暑さが厳しくなりますが、どうぞお体にお気をつけてお過ごしください。

今後ともよろしくお願いいたします。

送信日時: {}
    """.format(datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    
    sender.send_email(to_email, subject, body)

if __name__ == "__main__":
    main()