#\!/usr/bin/env python3
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = "itoh@thinksblog.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("itoh@thinksblog.com", "***REMOVED***")
        server.send_message(msg)
        server.quit()
        
        print("✅ メール送信成功！")
        print("宛先:", to_email)
        print("件名:", subject)
        return True
    except Exception as e:
        print("❌ 送信失敗:", str(e))
        return False

if __name__ == "__main__":
    if len(sys.argv) \!= 4:
        print("使用方法: python3 gmail_working.py <宛先> <件名> <本文>")
        sys.exit(1)
    
    send_email(sys.argv[1], sys.argv[2], sys.argv[3])
