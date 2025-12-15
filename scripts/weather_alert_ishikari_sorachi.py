#!/usr/bin/env python3
"""
石狩・空知地方の気象警報取得・メール送信スクリプト
毎朝5時30分に実行
"""
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import os
import sys

# ログ設定
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'weather_alert.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# メール設定
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "itoh@thinksblog.com"
SMTP_PASSWORD = "***REMOVED***"  # アプリパスワード
TO_EMAIL = "itoh@thinksblog.com"  # 送信先メールアドレス

# 気象庁API設定
# 石狩地方: 016000, 空知地方: 015000
AREA_CODES = {
    "石狩地方": "016000",
    "空知地方": "015000"
}

def get_weather_warnings():
    """気象庁APIから警報・注意報情報を取得"""
    warnings_data = {}
    
    for area_name, area_code in AREA_CODES.items():
        try:
            # 気象庁の警報・注意報API
            url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            warnings_data[area_name] = data
            
            logging.info(f"{area_name}の警報情報を取得しました")
            
        except Exception as e:
            logging.error(f"{area_name}の警報情報取得エラー: {str(e)}")
            warnings_data[area_name] = None
    
    return warnings_data

def parse_warnings(warnings_data):
    """警報データを解析して整形"""
    result = []
    current_time = datetime.now().strftime("%Y年%m月%d日 %H時%M分")
    
    result.append(f"【石狩・空知地方 気象警報情報】")
    result.append(f"取得時刻: {current_time}")
    result.append("")
    
    has_warnings = False
    
    for area_name, data in warnings_data.items():
        result.append(f"■ {area_name}")
        
        if data is None:
            result.append("  ※データ取得エラー")
            result.append("")
            continue
        
        try:
            # 最新の警報・注意報情報を取得
            if "areaTypes" in data and len(data["areaTypes"]) > 0:
                area_warnings = []
                
                for area_type in data["areaTypes"]:
                    if "areas" in area_type:
                        for area in area_type["areas"]:
                            area_name_detail = area.get("name", "不明")
                            warnings = area.get("warnings", [])
                            
                            active_warnings = []
                            for warning in warnings:
                                status = warning.get("status", "")
                                kind = warning.get("name", "")
                                
                                if status in ["発表", "継続"]:
                                    active_warnings.append(f"{kind}")
                                    has_warnings = True
                            
                            if active_warnings:
                                area_warnings.append(f"  {area_name_detail}: {'、'.join(active_warnings)}")
                
                if area_warnings:
                    result.extend(area_warnings)
                else:
                    result.append("  現在、発表されている警報・注意報はありません")
            else:
                result.append("  データ形式が不正です")
            
        except Exception as e:
            result.append(f"  解析エラー: {str(e)}")
        
        result.append("")
    
    if not has_warnings:
        result.append("【まとめ】")
        result.append("現在、石狩・空知地方に発表されている警報・注意報はありません。")
    else:
        result.append("【まとめ】")
        result.append("上記の警報・注意報が発表されています。最新情報にご注意ください。")
    
    return "\n".join(result)

def send_email(subject, body):
    """メール送信"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logging.info(f"メール送信成功: {TO_EMAIL}")
        return True
        
    except Exception as e:
        logging.error(f"メール送信エラー: {str(e)}")
        return False

def main():
    """メイン処理"""
    logging.info("=== 気象警報取得処理開始 ===")
    
    try:
        # 警報情報取得
        warnings_data = get_weather_warnings()
        
        # データ解析
        report = parse_warnings(warnings_data)
        
        # メール送信
        current_date = datetime.now().strftime("%Y年%m月%d日")
        subject = f"石狩・空知地方 気象警報情報 - {current_date} 5:30"
        
        if send_email(subject, report):
            logging.info("処理完了")
        else:
            logging.error("メール送信に失敗しました")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"処理エラー: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()