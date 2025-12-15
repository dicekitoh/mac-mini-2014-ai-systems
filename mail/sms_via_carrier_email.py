#!/usr/bin/env python3
"""
キャリアメール経由でSMS送信するシステム
電話番号からキャリアを自動判定してSMSとして送信
"""

import sys
import smtplib
import json
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 設定ファイルのパス
CONFIG_PATH = '/home/rootmax/google/mail_config.json'

# キャリア別のSMSメールアドレス設定
CARRIER_SMS_DOMAINS = {
    'docomo': '@docomo.ne.jp',
    'au': '@ezweb.ne.jp',
    'softbank': '@softbank.ne.jp',
    'ymobile': '@ymobile.ne.jp',
    'rakuten': '@sms.rakuten-mobile.jp'
}

# 電話番号プレフィックスによるキャリア自動判定
CARRIER_PREFIXES = {
    # docomo
    '090': ['docomo', 'au', 'softbank', 'ymobile', 'rakuten'],  # 共通プレフィックス
    '080': ['docomo', 'au', 'softbank', 'ymobile', 'rakuten'],  # 共通プレフィックス
    '070': ['docomo', 'au', 'softbank', 'ymobile', 'rakuten'],  # 共通プレフィックス
    
    # より具体的な判定が必要な場合のための拡張用
    # 実際の運用では、ユーザーにキャリアを指定してもらうか
    # データベースで管理する方が確実
}

class CarrierSMSSender:
    """キャリアメール経由SMS送信クラス"""
    
    def __init__(self):
        self.config = self.load_config()
        self.sent_log = []
    
    def load_config(self):
        """Gmail設定を読み込む"""
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"設定ファイルが見つかりません: {CONFIG_PATH}")
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config['gmail']
    
    def normalize_phone_number(self, phone_number):
        """電話番号を正規化（ハイフンや国番号を除去）"""
        # 国番号+81を090等に変換
        phone = re.sub(r'^\+81', '0', phone_number)
        # ハイフンや空白を除去
        phone = re.sub(r'[-\s\(\)]', '', phone)
        
        # 11桁の携帯電話番号チェック
        if re.match(r'^0[7-9]0\d{8}$', phone):
            return phone
        else:
            raise ValueError(f"無効な電話番号形式: {phone_number}")
    
    def detect_carrier(self, phone_number):
        """電話番号からキャリアを推定（基本的には手動指定を推奨）"""
        normalized = self.normalize_phone_number(phone_number)
        prefix = normalized[:3]
        
        # 基本的にはキャリア判定は困難なので、全キャリアに対応
        return list(CARRIER_SMS_DOMAINS.keys())
    
    def create_sms_email(self, phone_number, message, carrier):
        """SMS用のメールを作成"""
        normalized_phone = self.normalize_phone_number(phone_number)
        sms_address = normalized_phone + CARRIER_SMS_DOMAINS[carrier]
        
        # MIMEメッセージを作成
        msg = MIMEMultipart()
        msg['From'] = self.config['email']
        msg['To'] = sms_address
        msg['Subject'] = ""  # SMSでは件名は表示されない場合が多い
        
        # メッセージ本文（プレーンテキストのみ、70文字制限推奨）
        if len(message) > 70:
            message = message[:67] + "..."
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        return msg, sms_address
    
    def send_sms(self, phone_number, message, carrier=None):
        """SMS送信"""
        try:
            normalized_phone = self.normalize_phone_number(phone_number)
            
            if carrier:
                # 指定されたキャリアで送信
                carriers_to_try = [carrier]
            else:
                # 全キャリアを試行（確実な配信のため）
                carriers_to_try = list(CARRIER_SMS_DOMAINS.keys())
            
            sent_addresses = []
            errors = []
            
            for carrier_name in carriers_to_try:
                try:
                    # SMTPサーバーに接続
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(self.config['email'], self.config['app_password'])
                    
                    # メール作成
                    msg, sms_address = self.create_sms_email(phone_number, message, carrier_name)
                    
                    # 送信
                    server.send_message(msg)
                    server.quit()
                    
                    sent_addresses.append(sms_address)
                    
                    # ログ記録
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'phone': normalized_phone,
                        'carrier': carrier_name,
                        'sms_address': sms_address,
                        'message': message[:50] + "..." if len(message) > 50 else message,
                        'status': 'sent'
                    }
                    self.sent_log.append(log_entry)
                    
                    if carrier:  # 指定キャリアなら1回で終了
                        break
                        
                except Exception as e:
                    error_msg = f"{carrier_name}: {str(e)}"
                    errors.append(error_msg)
                    continue
            
            return {
                'success': len(sent_addresses) > 0,
                'sent_to': sent_addresses,
                'errors': errors,
                'message': message
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': message
            }
    
    def send_to_multiple(self, phone_numbers, message, carrier=None):
        """複数の電話番号にSMS送信"""
        results = []
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message, carrier)
            result['phone'] = phone
            results.append(result)
        
        return results
    
    def get_send_log(self):
        """送信ログを取得"""
        return self.sent_log

def main():
    """メイン処理"""
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python3 sms_via_carrier_email.py <電話番号> <メッセージ> [キャリア]")
        print("\n例:")
        print("  python3 sms_via_carrier_email.py 090-1234-5678 'テストメッセージ'")
        print("  python3 sms_via_carrier_email.py 09012345678 'Hello' docomo")
        print("\nキャリア指定:")
        print("  docomo, au, softbank, ymobile, rakuten")
        print("  ※指定しない場合は全キャリアに送信（確実な配信）")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2]
    carrier = sys.argv[3] if len(sys.argv) > 3 else None
    
    # キャリア名の検証
    if carrier and carrier not in CARRIER_SMS_DOMAINS:
        print(f"エラー: 無効なキャリア名 '{carrier}'")
        print(f"有効なキャリア: {', '.join(CARRIER_SMS_DOMAINS.keys())}")
        sys.exit(1)
    
    # SMS送信
    sender = CarrierSMSSender()
    
    print(f"SMS送信中...")
    print(f"宛先: {phone_number}")
    print(f"メッセージ: {message}")
    if carrier:
        print(f"キャリア: {carrier}")
    else:
        print("キャリア: 自動判定（全キャリア試行）")
    
    result = sender.send_sms(phone_number, message, carrier)
    
    print(f"\n=== 送信結果 ===")
    if result['success']:
        print("✓ 送信成功")
        print(f"送信先アドレス: {', '.join(result['sent_to'])}")
    else:
        print("✗ 送信失敗")
        if 'error' in result:
            print(f"エラー: {result['error']}")
        if 'errors' in result:
            for error in result['errors']:
                print(f"  - {error}")
    
    # 送信ログ表示
    if '--log' in sys.argv:
        print(f"\n=== 送信ログ ===")
        for log in sender.get_send_log():
            print(f"{log['timestamp']}: {log['phone']} ({log['carrier']}) - {log['status']}")

if __name__ == "__main__":
    main()