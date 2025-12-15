#!/usr/bin/env python3
"""
毎朝のSMSとEメールテスト送信
"""

import smtplib
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# ログ設定
LOG_DIR = '/home/fujinosuke/logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=f'{LOG_DIR}/daily_test_mail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_email_test():
    """Eメールテスト送信"""
    # 認証情報
    sender_email = "itoh@thinksblog.com"
    sender_password = "***REMOVED***"
    
    # メール設定
    to_email = "amitri@mac.com"
    subject = f"毎朝のテストメール - {datetime.now().strftime('%Y年%m月%d日')}"
    
    body = f"""
おはようございます。

これは毎朝の自動テストメールです。

送信日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
送信元: Macmini2014 (ターミナウス経由)

メールシステムは正常に動作しています。

今日も良い一日をお過ごしください。
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
        
        logging.info(f"Eメール送信成功: {to_email}")
        print(f"✅ Eメール送信成功: {to_email}")
        return True
        
    except Exception as e:
        logging.error(f"Eメール送信失敗: {str(e)}")
        print(f"❌ Eメール送信失敗: {str(e)}")
        return False

def send_sms_test():
    """SMSテスト送信（キャリアメール経由）"""
    # SMSシステムのパスを追加
    sys.path.append('/home/fujinosuke/projects/mail')
    
    try:
        # 設定ファイルのパスを一時的に変更
        import sms_via_carrier_email
        sms_via_carrier_email.CONFIG_PATH = '/home/fujinosuke/projects/mail/sms_config.json'
        
        # SMS設定を作成
        sms_config = {
            "gmail": {
                "email": "itoh@thinksblog.com",
                "app_password": "***REMOVED***"
            }
        }
        
        # 設定ファイルを作成
        import json
        with open('/home/fujinosuke/projects/mail/sms_config.json', 'w', encoding='utf-8') as f:
            json.dump(sms_config, f, ensure_ascii=False, indent=2)
        
        # SMS送信
        from sms_via_carrier_email import CarrierSMSSender
        sender = CarrierSMSSender()
        
        # テストメッセージ（短め）
        message = f"毎朝のテストSMS {datetime.now().strftime('%m/%d %H:%M')} システム正常"
        
        # 090-1234-5678形式の電話番号（実際の番号に変更してください）
        phone_number = "090-1234-5678"  # TODO: 実際の電話番号に変更
        
        result = sender.send_sms(phone_number, message)
        
        if result['success']:
            logging.info(f"SMS送信成功: {phone_number}")
            print(f"✅ SMS送信成功: {phone_number}")
            return True
        else:
            logging.error(f"SMS送信失敗: {result}")
            print(f"❌ SMS送信失敗: {result}")
            return False
            
    except Exception as e:
        logging.error(f"SMS送信エラー: {str(e)}")
        print(f"❌ SMS送信エラー: {str(e)}")
        # SMS送信は失敗してもメールが送れればOKとする
        return True

def main():
    """メイン処理"""
    print(f"\n=== 毎朝のテストメール送信 ===")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Eメール送信
    email_result = send_email_test()
    
    # SMS送信（オプション）
    # 注意: 実際の電話番号を設定する必要があります
    # sms_result = send_sms_test()
    
    if email_result:
        logging.info("毎朝のテストメール送信完了")
        print("\n✅ テストメール送信完了")
    else:
        logging.error("毎朝のテストメール送信失敗")
        print("\n❌ テストメール送信失敗")

if __name__ == "__main__":
    main()