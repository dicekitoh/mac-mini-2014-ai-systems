#!/usr/bin/env python3
"""
テストFAX送信スクリプト
0116887873へのテスト送信
"""

import os
import json
from datetime import datetime

def prepare_test_fax():
    """テストFAX準備"""
    fax_number = "0116887873"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 送信データ準備
    fax_data = {
        "recipient": fax_number,
        "timestamp": timestamp,
        "content": f"""
=====================================
テストFAX送信
=====================================
送信日時: {timestamp}
宛先番号: {fax_number}
送信元: MacMini2014 System

これはテスト送信です。
正常に受信できたか確認をお願いいたします。

Test FAX transmission
System test from automated sender
=====================================
        """,
        "status": "準備完了"
    }
    
    # ログファイルに記録
    log_file = "/home/fujinosuke/test_fax_log.json"
    
    try:
        # 既存ログ読み込み
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # 新規エントリ追加
        logs.append(fax_data)
        
        # ログ保存
        with open(log_file, 'w') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ テストFAX準備完了")
        print(f"📞 宛先: {fax_number}")
        print(f"⏰ 時刻: {timestamp}")
        print(f"📄 内容:")
        print(fax_data["content"])
        print(f"\n📝 ログ記録: {log_file}")
        
        # 送信可能なサービス情報
        print("\n📠 実際の送信には以下のサービスが利用可能:")
        print("  • FaxZero (https://faxzero.com) - 1日5通まで無料")
        print("  • GotFreeFax (https://www.gotfreefax.com) - 2ページまで無料")
        print("  • HelloFax (https://www.hellofax.com) - 試用版あり")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    prepare_test_fax()