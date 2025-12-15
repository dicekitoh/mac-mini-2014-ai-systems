#\!/usr/bin/env python3
"""
Textbelt API SMS送信スクリプト（無料枠優先版）
使用方法: python3 send_textbelt_sms_smart.py <電話番号> <メッセージ>
"""

import sys
import requests
import json
import os
from datetime import datetime

# 設定
PAID_API_KEY = "6f2ea521d1fb9012a61b9f79a883b5f77b84f03c2M13h3cAI4I2LHjjBiqdkckwH"  # 有料APIキーをここに設定
LOG_FILE = os.path.expanduser("~/textbelt_usage.log")

def log_usage(status, message):
    """使用履歴をログに記録"""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {status} - {message}\n")

def send_sms(phone_number, message, use_paid=False):
    """Textbelt APIを使用してSMSを送信"""
    
    # 日本の番号形式に変換（0から始まる場合は+81に変換）
    if phone_number.startswith("0"):
        phone_number = "+81" + phone_number[1:]
    
    # Textbelt API エンドポイント
    url = "https://textbelt.com/text"
    
    # APIキーの選択
    api_key = PAID_API_KEY if use_paid else "textbelt"
    key_type = "有料版" if use_paid else "無料版"
    
    # リクエストデータ
    data = {
        "phone": phone_number,
        "message": message,
        "key": api_key
    }
    
    try:
        # APIリクエスト送信
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get("success"):
            print(f"✅ SMS送信成功！({key_type})")
            print(f"📱 宛先: {phone_number}")
            print(f"💬 メッセージ: {message}")
            print(f"🆔 ID: {result.get('textId')}")
            print(f"📊 残りクレジット: {result.get('quotaRemaining', 'N/A')}")
            log_usage(f"SUCCESS_{key_type}", f"{phone_number} - {len(message)}文字")
            return True
        else:
            error_msg = result.get('error', '不明なエラー')
            if not use_paid and "quota" in error_msg.lower():
                print(f"⚠️ 無料枠を使い切りました。有料版で送信を試みます...")
                return False
            else:
                print(f"❌ SMS送信失敗 ({key_type})")
                print(f"エラー: {error_msg}")
                log_usage(f"FAILED_{key_type}", f"{phone_number} - {error_msg}")
                return None
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        log_usage(f"ERROR_{key_type}", str(e))
        return None

def main():
    if len(sys.argv) \!= 3:
        print("使用方法: python3 send_textbelt_sms_smart.py <電話番号> <メッセージ>")
        print("例: python3 send_textbelt_sms_smart.py 09012345678 'こんにちは！'")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    message = sys.argv[2]
    
    # メッセージ長チェック（70文字以内）
    if len(message) > 70:
        print(f"⚠️ メッセージが長すぎます（{len(message)}文字）。70文字以内にしてください。")
        sys.exit(1)
    
    print("📤 SMS送信を開始します...")
    print("1️⃣ まず無料枠で送信を試みます...")
    
    # まず無料版で試す
    result = send_sms(phone_number, message, use_paid=False)
    
    # 無料版が失敗した場合、有料版を試す
    if result is False and PAID_API_KEY \!= "YOUR_API_KEY_HERE":
        print("\n2️⃣ 有料版で送信を試みます...")
        result = send_sms(phone_number, message, use_paid=True)
    elif result is False:
        print("\n❌ 有料APIキーが設定されていません。")
        print("📝 ~/send_textbelt_sms_smart.py を編集してAPIキーを設定してください。")

if __name__ == "__main__":
    main()
