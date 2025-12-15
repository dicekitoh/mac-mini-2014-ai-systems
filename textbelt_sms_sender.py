#!/usr/bin/env python3
"""
TextBelt API SMS送信スクリプト
TextBelt APIを使用してSMSを送信
"""

import sys
import json
import requests
from datetime import datetime

# TextBelt API エンドポイント
TEXTBELT_API_URL = "https://textbelt.com/text"

class TextBeltSMSSender:
    """TextBelt API SMS送信クラス"""
    
    def __init__(self, api_key=None):
        # api_keyが指定されていない場合は無料版を使用
        self.api_key = api_key if api_key else "textbelt"
        self.sent_log = []
    
    def normalize_phone_number(self, phone_number):
        """電話番号を国際形式に正規化"""
        import re
        
        # 各種記号を除去
        phone = re.sub(r'[-\s\(\)]', '', phone_number)
        
        # +81が既についている場合はそのまま
        if phone.startswith('+81'):
            return phone
        
        # 0から始まる場合は+81に変換
        if phone.startswith('0'):
            return '+81' + phone[1:]
        
        # 81から始まる場合は+を追加
        if phone.startswith('81'):
            return '+' + phone
        
        # それ以外はそのまま返す
        return phone
    
    def send_sms(self, phone_number, message):
        """SMS送信"""
        try:
            normalized_phone = self.normalize_phone_number(phone_number)
            
            # リクエストペイロード
            payload = {
                'phone': normalized_phone,
                'message': message,
                'key': self.api_key
            }
            
            # API呼び出し
            response = requests.post(TEXTBELT_API_URL, data=payload)
            result = response.json()
            
            # ログ記録
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'phone': normalized_phone,
                'message': message[:50] + "..." if len(message) > 50 else message,
                'success': result.get('success', False),
                'quota_remaining': result.get('quotaRemaining', 'N/A'),
                'textId': result.get('textId', 'N/A'),
                'error': result.get('error', None)
            }
            self.sent_log.append(log_entry)
            
            return {
                'success': result.get('success', False),
                'phone': normalized_phone,
                'message': message,
                'quota_remaining': result.get('quotaRemaining', 'N/A'),
                'textId': result.get('textId', 'N/A'),
                'error': result.get('error', None),
                'raw_response': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'phone': phone_number,
                'message': message
            }
    
    def get_send_log(self):
        """送信ログを取得"""
        return self.sent_log

def main():
    """メイン処理"""
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python3 textbelt_sms_sender.py <電話番号> <メッセージ> [APIキー]")
        print("\n例:")
        print("  python3 textbelt_sms_sender.py 090-1234-5678 'テストメッセージ'")
        print("  python3 textbelt_sms_sender.py +819012345678 'Hello' your_api_key")
        print("\n注意:")
        print("  - APIキーを指定しない場合は無料版（1日1通まで）")
        print("  - 日本の番号は+81形式に自動変換されます")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2]
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    
    # SMS送信
    sender = TextBeltSMSSender(api_key)
    
    print(f"SMS送信中...")
    print(f"宛先: {phone_number}")
    print(f"メッセージ: {message}")
    print(f"APIキー: {'指定あり' if api_key else '無料版'}")
    
    result = sender.send_sms(phone_number, message)
    
    print(f"\n=== 送信結果 ===")
    if result['success']:
        print("✓ 送信成功")
        print(f"Text ID: {result['textId']}")
        print(f"残りクォータ: {result['quota_remaining']}")
    else:
        print("✗ 送信失敗")
        print(f"エラー: {result.get('error', 'Unknown error')}")
    
    # 送信ログ表示
    if '--log' in sys.argv:
        print(f"\n=== 送信ログ ===")
        for log in sender.get_send_log():
            print(f"{log['timestamp']}: {log['phone']} - {'成功' if log['success'] else '失敗'}")
            if log.get('error'):
                print(f"  エラー: {log['error']}")

if __name__ == "__main__":
    main()