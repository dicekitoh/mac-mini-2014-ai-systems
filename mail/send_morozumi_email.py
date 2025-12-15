#!/usr/bin/env python3
"""
両角様への労いメール送信
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email():
    """両角様へ労いメール送信"""
    # 認証情報
    sender_email = "itoh@thinksblog.com"
    sender_password = "***REMOVED***"
    
    # メール設定（amitri@mac.comに送信）
    to_email = "amitri@mac.com"
    subject = "長年のご活躍、本当にお疲れ様でした！"
    
    body = """両角様

赤帽ドライバーとして長年にわたりご活躍され、本当にお疲れ様でした。

今日まで、たくさんの荷物と一緒に日本全国を走り続けてこられたことと存じます。そのたゆまぬご努力と貢献に、心から敬意を表します。

これからは、今まで頑張ってこられた分、ご自身の趣味や余暇にたくさんの時間を充てて、どうぞのんびりとお過ごしください。

旅行に出かけたり、新しい趣味を始めたり、あるいはただ自宅でゆっくり過ごしたりと、両角様が心ゆくまで楽しめる時間を過ごされることを願っております。

本当に長い間、お疲れ様でした。そして、ありがとうございました。

これからの毎日が、素晴らしい時間で満たされることを心よりお祈り申し上げます。"""
    
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
        
        print(f"✅ 両角様への労いメール送信成功")
        print(f"   宛先: {to_email}")
        print(f"   件名: {subject}")
        print(f"   送信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ メール送信失敗: {str(e)}")
        return False

if __name__ == "__main__":
    send_email()