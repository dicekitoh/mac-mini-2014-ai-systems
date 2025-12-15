#!/usr/bin/env python3
"""
SMTP経由でテストメール送信
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email():
    """SMTPでメール送信"""
    # 認証情報（google_auth_config.jsonから取得）
    sender_email = "itoh@thinksblog.com"
    sender_password = "***REMOVED***"
    
    # メール設定
    to_email = "amitri@mac.com"
    subject = "暑中お見舞い申し上げます"
    body = f"""
いつもお世話になっております。

暑い日が続いておりますが、いかがお過ごしでしょうか。

暑中お見舞い申し上げます。
これからも暑さが厳しくなりますが、どうぞお体にお気をつけてお過ごしください。

今後ともよろしくお願いいたします。

送信日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
    
    try:
        # MIMEメッセージを作成
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 本文を追加
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # SMTPサーバーに接続
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
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

if __name__ == "__main__":
    send_email()