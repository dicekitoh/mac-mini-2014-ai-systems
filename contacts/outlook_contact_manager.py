#!/usr/bin/env python3
"""
Microsoft Outlook連絡先自動登録システム
高橋進の連絡先情報をOutlookに登録
"""

import requests
import json
import os
from datetime import datetime

class OutlookContactManager:
    def __init__(self):
        self.client_id = None
        self.client_secret = None
        self.tenant_id = None
        self.access_token = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        
    def authenticate(self):
        """Microsoft Graph API認証（簡易版）"""
        print("🔐 Microsoft Graph API認証")
        print("注意: 本格的な認証にはAzure ADアプリケーション登録が必要です")
        print("現在は代替手段でOutlook連絡先データを作成します")
        return True
        
    def create_contact_data(self, name, mobile, email):
        """Outlook連絡先データ作成"""
        contact_data = {
            "displayName": name,
            "givenName": name.split()[0] if " " in name else name,
            "surname": name.split()[-1] if " " in name else "",
            "mobilePhone": mobile,
            "emailAddresses": [
                {
                    "address": email,
                    "name": name
                }
            ]
        }
        return contact_data
        
    def save_contact_file(self, contact_data, filename):
        """連絡先データをファイルに保存"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(contact_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 連絡先データ保存: {filename}")
            return True
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return False
            
    def create_outlook_import_csv(self, contact_data, filename):
        """Outlookインポート用CSVファイル作成"""
        try:
            csv_content = """名前,姓,名,携帯電話,電子メール アドレス
"""
            name_parts = contact_data['displayName'].split()
            surname = name_parts[-1] if len(name_parts) > 1 else ""
            given_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else contact_data['displayName']
            
            csv_line = f'"{contact_data["displayName"]}","{surname}","{given_name}","{contact_data["mobilePhone"]}","{contact_data["emailAddresses"][0]["address"]}"'
            csv_content += csv_line
            
            with open(filename, 'w', encoding='utf-8-sig') as f:  # BOM付きUTF-8
                f.write(csv_content)
            print(f"✅ Outlook CSV作成: {filename}")
            return True
        except Exception as e:
            print(f"❌ CSV作成エラー: {e}")
            return False
            
    def create_vcard(self, contact_data, filename):
        """VCard形式で連絡先作成"""
        try:
            vcard_content = f"""BEGIN:VCARD
VERSION:3.0
FN:{contact_data['displayName']}
N:{contact_data.get('surname', '')};{contact_data.get('givenName', '')};;;
TEL;TYPE=CELL:{contact_data['mobilePhone']}
EMAIL:{contact_data['emailAddresses'][0]['address']}
END:VCARD"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(vcard_content)
            print(f"✅ VCard作成: {filename}")
            return True
        except Exception as e:
            print(f"❌ VCard作成エラー: {e}")
            return False
            
    def display_manual_instructions(self, contact_data):
        """手動登録手順表示"""
        print("\n" + "="*60)
        print("📝 Outlook手動登録手順")
        print("="*60)
        print("以下の方法でOutlookに連絡先を登録できます：")
        print()
        print("【方法1: 直接入力】")
        print(f"名前: {contact_data['displayName']}")
        print(f"携帯電話: {contact_data['mobilePhone']}")
        print(f"メール: {contact_data['emailAddresses'][0]['address']}")
        print()
        print("【方法2: CSVインポート】")
        print("1. Outlookを開く")
        print("2. ファイル > インポート/エクスポート")
        print("3. 'ファイルからインポート' > CSV")
        print("4. 作成されたCSVファイルを選択")
        print()
        print("【方法3: VCardインポート】")
        print("1. VCFファイルをダブルクリック")
        print("2. Outlookが自動的に開いて連絡先追加")
        print("="*60)
        
    def register_contact(self, name, mobile, email):
        """連絡先登録メイン処理"""
        print(f"🔄 Outlook連絡先登録開始: {name}")
        
        # 認証
        if not self.authenticate():
            return False
            
        # 連絡先データ作成
        contact_data = self.create_contact_data(name, mobile, email)
        
        # 複数形式でファイル出力
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"outlook_contact_{name.replace(' ', '_')}_{timestamp}"
        
        # JSON形式
        json_file = f"/home/rootmax/{base_filename}.json"
        self.save_contact_file(contact_data, json_file)
        
        # CSV形式（Outlookインポート用）
        csv_file = f"/home/rootmax/{base_filename}.csv"
        self.create_outlook_import_csv(contact_data, csv_file)
        
        # VCard形式
        vcf_file = f"/home/rootmax/{base_filename}.vcf"
        self.create_vcard(contact_data, vcf_file)
        
        # 手動登録手順表示
        self.display_manual_instructions(contact_data)
        
        print(f"\n✅ {name} の連絡先登録準備完了")
        print(f"作成ファイル: {json_file}, {csv_file}, {vcf_file}")
        
        return True

def main():
    """メイン関数"""
    print("📱 Microsoft Outlook連絡先自動登録システム")
    print("="*50)
    
    # 高橋進の連絡先情報
    contact_info = {
        'name': '高橋進',
        'mobile': '011-851-2181',
        'email': 'ns-tsukisamu@st-g.co.jp'
    }
    
    # Outlook連絡先管理インスタンス作成
    manager = OutlookContactManager()
    
    # 連絡先登録実行
    result = manager.register_contact(
        contact_info['name'],
        contact_info['mobile'], 
        contact_info['email']
    )
    
    if result:
        print("\n🎉 連絡先登録処理が完了しました！")
        print("上記の手順に従ってOutlookに登録してください。")
    else:
        print("\n❌ 連絡先登録処理に失敗しました。")

if __name__ == "__main__":
    main()