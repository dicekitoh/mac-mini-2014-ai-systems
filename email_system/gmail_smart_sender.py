#\!/usr/bin/env python3
"""
スマートGmail送信システム（iPhone最適化）
使用方法: python3 gmail_smart_sender.py <宛先> <件名> <本文>
"""

import sys
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Gmail設定
GMAIL_EMAIL = "itoh@thinksblog.com"
GMAIL_APP_PASSWORD = "***REMOVED***"  # Googleアプリパスワード
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def log_email(status, to_email, subject, message_preview):
    """メール送信履歴をログに記録"""
    log_dir = os.path.expanduser("~/projects/email_system/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "email_history.log")
    
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        preview = message_preview[:50] + "..." if len(message_preview) > 50 else message_preview
        f.write(f"{timestamp} - {status} - TO:{to_email} - SUBJECT:{subject} - MSG:{preview}\n")

def send_email(to_email, subject, body, is_html=False):
    """Gmail経由でメール送信"""
    
    try:
        # メール作成
        msg = MIMEMultipart()
        msg[From] = GMAIL_EMAIL
        msg[To] = to_email
        msg[Subject] = subject
        
        # 本文設定
        mime_body = MIMEText(body, html if is_html else plain, utf-8)
        msg.attach(mime_body)
        
        # SMTP接続・送信
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        # 成功表示
        print("✅ メール送信成功！")
        print(f"📧 宛先: {to_email}")
        print(f"📝 件名: {subject}")
        body_preview = body[:50] + "..." if len(body) > 50 else body
        print(f"📄 本文: {body_preview}")
        print(f"🕒 送信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ログ記録
        log_email("SUCCESS", to_email, subject, body)
        return True
        
    except Exception as e:
        print("❌ メール送信失敗")
        print(f"エラー: {str(e)}")
        log_email("FAILED", to_email, subject, str(e))
        return False

def main():
    if len(sys.argv) \!= 4:
        print("使用方法: python3 gmail_smart_sender.py <宛先> <件名> <本文>")
        print("例: python3 gmail_smart_sender.py test@example.com \"テスト件名\" \"テスト本文\"")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    # 基本チェック
    if not to_email or "@" not in to_email:
        print("❌ 有効なメールアドレスを入力してください")
        sys.exit(1)
    
    if not subject.strip():
        print("❌ 件名を入力してください")
        sys.exit(1)
    
    if not body.strip():
        print("❌ 本文を入力してください")
        sys.exit(1)
    
    print("📤 メール送信を開始します...")
    send_email(to_email, subject, body)

if __name__ == "__main__":
    main()
