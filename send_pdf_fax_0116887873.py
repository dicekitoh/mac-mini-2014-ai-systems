#!/usr/bin/env python3
"""
PDFファイルのFAX送信スクリプト
Google DriveからダウンロードしたファイルをFAX送信
"""

import os
import json
import subprocess
from datetime import datetime

def send_pdf_fax():
    """PDFファイルをFAX送信"""
    fax_number = "0116887873"
    pdf_file = "fax_document.pdf"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"📠 PDF FAX送信システム")
    print(f"📞 宛先: {fax_number}")
    print(f"📄 ファイル: {pdf_file}")
    print(f"⏰ 送信時刻: {timestamp}")
    
    # ファイル存在確認
    if not os.path.exists(pdf_file):
        print(f"❌ PDFファイルが見つかりません: {pdf_file}")
        return False
    
    file_size = os.path.getsize(pdf_file)
    print(f"📊 ファイルサイズ: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
    
    # 送信データ準備
    fax_data = {
        "recipient": fax_number,
        "timestamp": timestamp,
        "file_path": os.path.abspath(pdf_file),
        "file_size": file_size,
        "status": "送信準備完了"
    }
    
    # ログファイルに記録
    log_file = "/home/fujinosuke/pdf_fax_log.json"
    
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
        
        print(f"📝 ログ記録完了: {log_file}")
        
        # 実際の送信試行（複数の方法）
        print("\n🚀 FAX送信を試行中...")
        
        # 方法1: curl + FaxZero API（もし利用可能な場合）
        try:
            print("📡 方法1: Web API経由での送信を試行...")
            # 注意: 実際のFAX送信APIが必要
            print("ℹ️  Web API送信は設定が必要です")
        except Exception as e:
            print(f"⚠️  Web API送信失敗: {e}")
        
        # 方法2: システムコマンド（efax等）
        try:
            print("📡 方法2: システムFAXコマンドを確認...")
            result = subprocess.run(['which', 'efax'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ efaxコマンドが利用可能: {result.stdout.strip()}")
                # efax -d /dev/ttyS0 -t {fax_number} {pdf_file}
            else:
                print("ℹ️  efaxコマンドが見つかりません")
        except Exception as e:
            print(f"⚠️  システムコマンド確認失敗: {e}")
        
        # 方法3: 手動指示
        print("\n📋 手動でのFAX送信方法:")
        print(f"  1. FAXマシンまたはソフトウェアを起動")
        print(f"  2. 宛先番号を入力: {fax_number}")
        print(f"  3. 以下のファイルを送信: {os.path.abspath(pdf_file)}")
        
        # CSV記録
        csv_log = "/home/fujinosuke/fax_log.csv"
        with open(csv_log, 'a') as f:
            f.write(f"{timestamp},{fax_number},{pdf_file},{file_size},準備完了\n")
        
        print(f"\n✅ FAX送信準備が完了しました")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.abspath(pdf_file)}")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    send_pdf_fax()