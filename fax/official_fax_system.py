#!/usr/bin/env python3
"""
公式SDK利用 無料FAXシステム (FAX.PLUS Official Python SDK)
Alohi公式ライブラリ使用・月10枚まで無料

MacMini2014サーバー用 - Claude経由操作専用
2025年6月10日作成 (公式SDK版)
"""

import sys
import os
import json
import base64
from datetime import datetime
from pathlib import Path

# 仮想環境のパスを追加
sys.path.insert(0, '/home/fujinosuke/fax_venv/lib/python3.12/site-packages')

try:
    import faxplus
    from faxplus.rest import ApiException
    from faxplus import Configuration, ApiClient, OutboxApi
    from faxplus.models import PayloadOutboxModification, OutboxFileChanges
except ImportError as e:
    print(f"❌ FAX.PLUS SDK未インストール: {e}")
    print("仮想環境でインストール: python3 -m venv ~/fax_venv && source ~/fax_venv/bin/activate && pip install faxplus-api")
    sys.exit(1)

class OfficialFaxSystem:
    def __init__(self):
        self.service_name = "FAX.PLUS (Official SDK)"
        self.monthly_limit = 10  # 無料プランの月間上限
        
        # ファイルパス設定
        self.log_file = "/home/fujinosuke/official_fax_log.csv"
        self.config_file = "/home/fujinosuke/official_fax_config.json"
        
        # 設定読み込み
        self.load_config()
        
        # API設定
        self.configuration = None
        self.api_client = None
        self.setup_api_client()
        
    def load_config(self):
        """設定ファイルの読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "access_token": "",
                    "monthly_count": 0,
                    "last_reset": datetime.now().strftime("%Y-%m")
                }
                self.save_config()
        except Exception as e:
            print(f"❌ 設定ファイル読み込みエラー: {e}")
            self.config = {"access_token": "", "monthly_count": 0, "last_reset": datetime.now().strftime("%Y-%m")}
    
    def save_config(self):
        """設定ファイルの保存"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"❌ 設定ファイル保存エラー: {e}")
    
    def setup_api_client(self):
        """FAX.PLUS API クライアント設定"""
        if self.config["access_token"]:
            try:
                self.configuration = Configuration()
                self.configuration.access_token = self.config["access_token"]
                self.api_client = ApiClient(self.configuration)
                return True
            except Exception as e:
                print(f"❌ API設定エラー: {e}")
                return False
        return False
    
    def setup_access_token(self, token):
        """アクセストークンの設定"""
        self.config["access_token"] = token
        self.save_config()
        self.setup_api_client()
        print(f"✅ アクセストークンを設定しました")
    
    def reset_monthly_count(self):
        """月次カウントのリセット"""
        current_month = datetime.now().strftime("%Y-%m")
        if self.config["last_reset"] != current_month:
            self.config["monthly_count"] = 0
            self.config["last_reset"] = current_month
            self.save_config()
            print(f"📅 月次カウントをリセット ({current_month})")
    
    def check_monthly_limit(self):
        """月間送信制限の確認"""
        self.reset_monthly_count()
        if self.config["monthly_count"] >= self.monthly_limit:
            return False, f"❌ 月間送信上限到達 ({self.config['monthly_count']}/{self.monthly_limit})"
        return True, f"✅ 送信可能 ({self.config['monthly_count']}/{self.monthly_limit})"
    
    def prepare_file(self, file_path):
        """ファイル準備（PDF変換・Base64エンコード）"""
        try:
            # PDFでない場合は簡易変換
            if not file_path.lower().endswith('.pdf'):
                if file_path.lower().endswith('.txt'):
                    # テキストファイル→PDF変換 (簡易版)
                    return self.convert_text_to_pdf(file_path)
            
            # Base64エンコード
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ ファイル準備エラー: {e}")
            return None
    
    def convert_text_to_pdf(self, txt_path):
        """簡易テキスト→PDF変換"""
        try:
            # fpdf2を使用してPDF作成
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', size=12)
            
            with open(txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    # 日本語文字は□で表示される可能性あり（制限）
                    line_clean = line.strip().encode('latin-1', 'ignore').decode('latin-1')
                    pdf.cell(0, 10, line_clean, ln=True)
            
            pdf_path = txt_path.replace('.txt', '_converted.pdf')
            pdf.output(pdf_path)
            
            # Base64エンコード
            with open(pdf_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
                
        except Exception as e:
            print(f"❌ PDF変換エラー: {e}")
            # 変換失敗時はテキストファイルをそのままBase64エンコード
            with open(txt_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    
    def send_fax_official(self, fax_number, file_path, comment="MacMini2014 Official SDK"):
        """公式SDK経由でFAX送信"""
        
        # 事前チェック
        can_send, limit_msg = self.check_monthly_limit()
        if not can_send:
            return False, limit_msg
        
        if not self.config["access_token"]:
            return False, "❌ アクセストークンが未設定"
        
        if not os.path.exists(file_path):
            return False, f"❌ ファイルが見つかりません: {file_path}"
        
        try:
            print(f"📤 公式SDK FAX送信開始...")
            print(f"📞 宛先: {fax_number}")
            print(f"📄 ファイル: {os.path.basename(file_path)}")
            print(f"🔧 SDK: {self.service_name}")
            
            # ファイル準備
            file_content = self.prepare_file(file_path)
            if not file_content:
                return False, "❌ ファイル準備失敗"
            
            # API実行
            outbox_api = OutboxApi(self.api_client)
            
            # ファイル変更オブジェクト作成
            file_changes = OutboxFileChanges(
                name=os.path.basename(file_path),
                content=file_content
            )
            
            # ペイロード作成
            payload = PayloadOutboxModification(
                to=fax_number,
                files=[file_changes],
                comment=comment
            )
            
            # FAX送信実行
            result = outbox_api.send_fax("self", payload)
            
            # 成功処理
            self.config["monthly_count"] += 1
            self.save_config()
            
            # ログ記録
            self.log_transmission(fax_number, file_path, "成功", f"ID: {result.id}")
            
            return True, f"✅ FAX送信成功! ID: {result.id}"
            
        except ApiException as e:
            error_msg = f"API Exception: {e.status} - {e.reason}"
            self.log_transmission(fax_number, file_path, "API Error", error_msg)
            return False, f"❌ {error_msg}"
        except Exception as e:
            error_msg = f"System Error: {str(e)}"
            self.log_transmission(fax_number, file_path, "System Error", error_msg)
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
    
    def get_account_info(self):
        """アカウント情報取得"""
        if not self.api_client:
            return "❌ API未設定"
        
        try:
            from faxplus import AccountsApi
            accounts_api = AccountsApi(self.api_client)
            account = accounts_api.get_account("self")
            return f"✅ アカウント: {account.email} (プラン: {account.plan})"
        except Exception as e:
            return f"❌ アカウント情報取得エラー: {e}"
    
    def get_status(self):
        """システム状況表示"""
        can_send, limit_msg = self.check_monthly_limit()
        account_info = self.get_account_info()
        
        status = f"""
📠 公式SDK無料FAXシステム ({self.service_name})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 サービス: FAX.PLUS (Alohi公式SDK)
🆓 料金: 月10枚まで完全無料
🔑 アクセストークン: {"設定済み" if self.config["access_token"] else "未設定"}
📊 {limit_msg}
📅 対象月: {self.config["last_reset"]}
👤 {account_info}

📋 使用方法:
1. トークン設定: setup YOUR_ACCESS_TOKEN
2. FAX送信: send FAX番号 ファイルパス
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return status

def main():
    """メイン関数 - コマンドライン実行用"""
    fax_system = OfficialFaxSystem()
    
    if len(sys.argv) == 1:
        print(fax_system.get_status())
        return
    
    if len(sys.argv) == 3 and sys.argv[1] == "setup":
        # アクセストークン設定
        fax_system.setup_access_token(sys.argv[2])
        return
    
    if len(sys.argv) == 4 and sys.argv[1] == "send":
        # FAX送信
        fax_number = sys.argv[2]
        file_path = sys.argv[3]
        
        success, message = fax_system.send_fax_official(fax_number, file_path)
        print(message)
        return
    
    # ヘルプ表示
    print("""
📠 公式SDK無料FAXシステム使用方法:

アクセストークン設定:
~/fax_venv/bin/python3 official_fax_system.py setup YOUR_ACCESS_TOKEN

FAX送信:
~/fax_venv/bin/python3 official_fax_system.py send 0116887873 document.txt

システム状況確認:
~/fax_venv/bin/python3 official_fax_system.py
""")

if __name__ == "__main__":
    main()