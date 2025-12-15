#!/usr/bin/env python3
"""
両角さんへのHTMLページをメールで送信
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class HTMLMailSender:
    def __init__(self):
        # 既存の認証情報を使用
        self.email = "itoh@thinksblog.com"
        self.app_password = "***REMOVED***"
    
    def send_html_email(self, to_email, subject, body, html_file_path):
        """HTMLファイルを添付してメール送信"""
        try:
            # MIMEメッセージを作成
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 本文を追加
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # HTMLファイルを添付
            with open(html_file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(html_file_path)}'
                )
                msg.attach(part)
            
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
            print(f"   添付ファイル: {os.path.basename(html_file_path)}")
            print(f"   送信時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"❌ メール送信失敗: {str(e)}")
            return False

def main():
    """両角さんへのHTMLページを送信"""
    sender = HTMLMailSender()
    
    # メール内容
    to_email = "amitri@mac.com"  # 送信先メールアドレス
    subject = "長年のご活躍、本当にお疲れ様でした！【感謝ページ付き】"
    body = """両角様

赤帽ドライバーとして長年にわたりご活躍され、本当にお疲れ様でした。

今日まで、たくさんの荷物と一緒に日本全国を走り続けてこられたことと存じます。そのたゆまぬご努力と貢献に、心から敬意を表します。

これからは、今まで頑張ってこられた分、ご自身の趣味や余暇にたくさんの時間を充てて、どうぞのんびりとお過ごしください。

旅行に出かけたり、新しい趣味を始めたり、あるいはただ自宅でゆっくり過ごしたりと、両角様が心ゆくまで楽しめる時間を過ごされることを願っております。

本当に長い間、お疲れ様でした。そして、ありがとうございました。

これからの毎日が、素晴らしい時間で満たされることを心よりお祈り申し上げます。

※添付のHTMLファイルをブラウザで開くと、感謝のメッセージがホームページ風に表示されます。

送信日時: {}""".format(datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    
    # HTMLファイルのパス
    html_file_path = "/home/fujinosuke/projects/morozumi_thanks_page.html"
    
    # メール送信
    sender.send_html_email(to_email, subject, body, html_file_path)

if __name__ == "__main__":
    main()