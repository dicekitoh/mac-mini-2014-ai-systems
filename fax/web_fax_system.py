#!/usr/bin/env python3
"""
WEBベース無料FAXシステム (FAX.PLUS API利用)
クレジット登録不要・月10枚まで無料送信

MacMini2014サーバー用
2025年6月10日作成
"""

import requests
import json
import os
import time
from datetime import datetime
import base64
from pathlib import Path

class WebFaxSystem:
    def __init__(self):
        self.api_base_url = "https://restapi.fax.plus/v3"
        self.service_name = "FAX.PLUS"
        self.monthly_limit = 10  # 無料プランの月間上限
        
        # ログファイル設定
        self.log_file = "/home/fujinosuke/web_fax_log.csv"
        self.config_file = "/home/fujinosuke/fax_config.json"
        
        # 設定ファイル読み込み
        self.load_config()
        
    def load_config(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "api_key": "",
                    "monthly_count": 0,
                    "last_reset": datetime.now().strftime("%Y-%m")
                }
                self.save_config()
        except Exception as e:
            print(f"❌ 設定ファイル読み込みエラー: {e}")
            self.config = {"api_key": "", "monthly_count": 0, "last_reset": datetime.now().strftime("%Y-%m")}
    
    def save_config(self):
        """設定ファイルの保存"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"❌ 設定ファイル保存エラー: {e}")
    
    def reset_monthly_count(self):
        """月次カウントのリセット"""
        current_month = datetime.now().strftime("%Y-%m")
        if self.config["last_reset"] != current_month:
            self.config["monthly_count"] = 0
            self.config["last_reset"] = current_month
            self.save_config()
            print(f"📅 月次カウントをリセットしました ({current_month})")
    
    def check_monthly_limit(self):
        """月間送信制限の確認"""
        self.reset_monthly_count()
        if self.config["monthly_count"] >= self.monthly_limit:
            return False, f"❌ 月間送信上限に達しました ({self.config['monthly_count']}/{self.monthly_limit})"
        return True, f"✅ 送信可能 ({self.config['monthly_count']}/{self.monthly_limit})"
    
    def setup_api_key(self, api_key):
        """APIキーの設定"""
        self.config["api_key"] = api_key
        self.save_config()
        print(f"✅ APIキーを設定しました")
    
    def convert_to_pdf(self, file_path):
        """ファイルをPDF形式に変換"""
        try:
            from fpdf import FPDF
            
            if file_path.lower().endswith('.pdf'):
                return file_path
            
            # テキストファイルをPDFに変換
            if file_path.lower().endswith('.txt'):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font('Arial', size=12)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        pdf.cell(0, 10, line.strip(), ln=True)
                
                pdf_path = file_path.replace('.txt', '.pdf')
                pdf.output(pdf_path)
                return pdf_path
            
            return file_path
        except Exception as e:
            print(f"❌ PDF変換エラー: {e}")
            return file_path
    
    def encode_file_base64(self, file_path):
        """ファイルをBase64エンコード"""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ ファイルエンコードエラー: {e}")
            return None
    
    def send_fax_api(self, fax_number, file_path, comment="MacMini2014 Web FAX"):
        """FAX.PLUS API経由でFAX送信"""
        
        # 月間制限確認
        can_send, message = self.check_monthly_limit()
        if not can_send:
            return False, message
        
        if not self.config["api_key"]:
            return False, "❌ APIキーが設定されていません"
        
        try:
            # ファイル準備
            pdf_path = self.convert_to_pdf(file_path)
            file_content = self.encode_file_base64(pdf_path)
            
            if not file_content:
                return False, "❌ ファイル読み込み失敗"
            
            # API リクエスト構築
            headers = {
                'Authorization': f'Bearer {self.config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "to": fax_number,
                "files": [
                    {
                        "name": os.path.basename(pdf_path),
                        "content": file_content,
                        "type": "application/pdf"
                    }
                ],
                "comment": comment
            }
            
            print(f"📤 FAX送信開始...")
            print(f"📞 宛先: {fax_number}")
            print(f"📄 ファイル: {os.path.basename(file_path)}")
            print(f"🌐 サービス: {self.service_name}")
            
            # API リクエスト送信
            response = requests.post(
                f"{self.api_base_url}/accounts/self/outbox",
                headers=headers,
                data=json.dumps(payload),
                timeout=60
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                
                # カウンター更新
                self.config["monthly_count"] += 1
                self.save_config()
                
                # ログ記録
                self.log_transmission(fax_number, file_path, "成功", str(result))
                
                return True, f"✅ FAX送信成功! ID: {result.get('id', 'N/A')}"
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                self.log_transmission(fax_number, file_path, "失敗", error_msg)
                return False, f"❌ FAX送信失敗: {error_msg}"
                
        except Exception as e:
            error_msg = f"システムエラー: {str(e)}"
            self.log_transmission(fax_number, file_path, "エラー", error_msg)
            return False, f"❌ {error_msg}"
    
    def log_transmission(self, fax_number, file_path, status, details):
        """送信ログの記録"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp},{fax_number},{os.path.basename(file_path)},{status},{details}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ ログ記録エラー: {e}")
    
    def get_status(self):
        """システム状況表示"""
        can_send, limit_msg = self.check_monthly_limit()
        
        status = f"""
📠 WEBベース無料FAXシステム ({self.service_name})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: {self.service_name}
🆓 料金: 月10枚まで完全無料
🔑 APIキー: {"設定済み" if self.config["api_key"] else "未設定"}
📊 {limit_msg}
📅 対象月: {self.config["last_reset"]}

📋 使用方法:
1. APIキー設定: setup_api_key("your_api_key")
2. FAX送信: send_fax("FAX番号", "ファイルパス")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return status

def main():
    """メイン関数 - コマンドライン実行用"""
    import sys
    
    fax_system = WebFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 3 and sys.argv[1] == "setup":
        # APIキー設定
        fax_system.setup_api_key(sys.argv[2])
        return
    
    if len(sys.argv) == 3:
        # FAX送信
        fax_number = sys.argv[1]
        file_path = sys.argv[2]
        
        if not os.path.exists(file_path):
            print(f"❌ ファイルが見つかりません: {file_path}")
            return
        
        success, message = fax_system.send_fax_api(fax_number, file_path)
        print(message)
        return
    
    print("""
📠 WEBベース無料FAXシステム使用方法:

APIキー設定:
python3 web_fax_system.py setup YOUR_API_KEY

FAX送信:
python3 web_fax_system.py 0116887873 document.txt

システム状況確認:
python3 web_fax_system.py
""")

if __name__ == "__main__":
    main()