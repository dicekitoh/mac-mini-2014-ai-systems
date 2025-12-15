#\!/usr/bin/env python3
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Gmail設定
GMAIL_EMAIL = "itoh@thinksblog.com"
GMAIL_APP_PASSWORD = "***REMOVED***"

def send_email(to_email, subject, body):
    try:
        # メール作成
        msg = MIMEText(body, plain, utf-8)
        msg[From] = GMAIL_EMAIL
        msg[To] = to_email
        msg[Subject] = subject
        
        # 送信
        server = smtplib.SMTP(smtp.gmail.com, 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("✅ メール送信成功！")
        print("宛先:", to_email)
        print("件名:", subject)
        print("送信時刻:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return True
        
    except Exception as e:
        print("❌ メール送信失敗:", str(e))
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使用方法: python3 gmail_simple.py <宛先> <件名> <本文>")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    send_email(to_email, subject, body)
