#!/usr/bin/env python3
"""
石狩・空知地方の気象警報取得・メール送信スクリプト（完成版）
毎朝5時30分に実行
作成日: 2025-06-05
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

# 警報コード定義
WARNING_CODES = {
    "02": "暴風雪警報",
    "03": "大雨警報",
    "04": "洪水警報",
    "05": "暴風警報",
    "06": "大雪警報",
    "07": "波浪警報",
    "08": "高潮警報",
    "10": "大雨注意報",
    "12": "大雪注意報",
    "13": "風雪注意報",
    "14": "雷注意報",
    "15": "強風注意報",
    "16": "波浪注意報",
    "17": "融雪注意報",
    "18": "洪水注意報",
    "19": "高潮注意報",
    "20": "濃霧注意報",
    "21": "乾燥注意報",
    "22": "なだれ注意報",
    "23": "低温注意報",
    "24": "霜注意報",
    "25": "着氷注意報",
    "26": "着雪注意報"
}

# 地域コード定義（石狩・空知地方の細分区域）
AREA_NAME_MAP = {
    "016010": "石狩地方",
    "016020": "空知地方", 
    "016030": "後志地方",
    "015010": "胆振地方",
    "015020": "日高地方"
}

def get_area_info():
    """地域情報を取得"""
    try:
        response = requests.get("https://www.jma.go.jp/bosai/common/const/area.json", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"地域情報取得エラー: {str(e)}")
        return None

def get_weather_warnings():
    """気象庁APIから警報・注意報情報を取得"""
    warnings_data = {}
    area_info = get_area_info()
    
    for area_name, area_code in AREA_CODES.items():
        try:
            # 気象庁の警報・注意報API
            url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            warnings_data[area_name] = {
                "data": data,
                "area_info": area_info
            }
            
            logging.info(f"{area_name}の警報情報を取得しました")
            
        except Exception as e:
            logging.error(f"{area_name}の警報情報取得エラー: {str(e)}")
            warnings_data[area_name] = None
    
    return warnings_data

def get_area_name(area_code, area_info):
    """地域コードから地域名を取得"""
    # まず定義済みマップから取得
    if area_code in AREA_NAME_MAP:
        return AREA_NAME_MAP[area_code]
    
    # 次にAPIデータから取得
    if area_info:
        for key in ["class20s", "class15s", "class10s", "offices"]:
            if key in area_info and area_code in area_info[key]:
                return area_info[key][area_code].get("name", area_code)
    
    return area_code

def parse_warnings(warnings_data):
    """警報データを解析して整形"""
    result = []
    current_time = datetime.now().strftime("%Y年%m月%d日 %H時%M分")
    
    result.append(f"【石狩・空知地方 気象警報情報】")
    result.append(f"取得時刻: {current_time}")
    result.append("")
    
    # ヘッドラインテキストがあれば表示
    for area_name, data_dict in warnings_data.items():
        if data_dict and "data" in data_dict:
            headline = data_dict["data"].get("headlineText", "")
            if headline:
                result.append(f"《気象庁発表》")
                result.append(headline)
                result.append("")
                break
    
    has_warnings = False
    
    for area_name, data_dict in warnings_data.items():
        result.append(f"■ {area_name}")
        
        if data_dict is None:
            result.append("  ※データ取得エラー")
            result.append("")
            continue
        
        try:
            data = data_dict["data"]
            area_info = data_dict["area_info"]
            
            # 最新の警報・注意報情報を取得
            if "areaTypes" in data and len(data["areaTypes"]) > 0:
                area_warnings = []
                
                # 最初のareaTypeを使用（通常は市町村単位）
                area_type = data["areaTypes"][0]
                if "areas" in area_type:
                    for area in area_type["areas"]:
                        area_code = area.get("code", "")
                        area_name_detail = get_area_name(area_code, area_info)
                        warnings = area.get("warnings", [])
                        
                        active_warnings = []
                        for warning in warnings:
                            status = warning.get("status", "")
                            code = warning.get("code", "")
                            
                            if status in ["発表", "継続"]:
                                warning_name = WARNING_CODES.get(code, f"コード{code}")
                                active_warnings.append(warning_name)
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
            logging.error(f"解析エラー詳細: {str(e)}")
        
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