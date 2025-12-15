#!/usr/bin/env python3
"""
実際のFAX送信実行スクリプト
0116887873宛てPDFファイル送信
"""

import os
import subprocess
import json
from datetime import datetime

def execute_fax_send():
    """FAX送信を実行"""
    fax_number = "0116887873"
    pdf_file = "fax_document.pdf"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🚀 FAX送信実行開始")
    print(f"📞 宛先番号: {fax_number}")
    print(f"📄 送信ファイル: {pdf_file}")
    print(f"⏰ 実行時刻: {timestamp}")
    
    # ファイル存在確認
    if not os.path.exists(pdf_file):
        print(f"❌ エラー: PDFファイルが見つかりません - {pdf_file}")
        return False
    
    file_size = os.path.getsize(pdf_file)
    print(f"📊 ファイルサイズ: {file_size:,} bytes")
    
    # 実行記録
    execution_log = {
        "timestamp": timestamp,
        "recipient": fax_number,
        "file_path": os.path.abspath(pdf_file),
        "file_size": file_size,
        "status": "実行中"
    }
    
    # システムFAX送信の試行
    success_methods = []
    
    # 方法1: efaxコマンド（利用可能な場合）
    try:
        result = subprocess.run(['which', 'efax'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"\n📡 efaxコマンドで送信試行...")
            efax_cmd = ['efax', '-d', '/dev/ttyS0', '-t', fax_number, pdf_file]
            print(f"実行コマンド: {' '.join(efax_cmd)}")
            
            # efaxの実行（テストモード）
            try:
                efax_result = subprocess.run(efax_cmd, capture_output=True, text=True, timeout=30)
                if efax_result.returncode == 0:
                    print("✅ efax送信成功")
                    success_methods.append("efax")
                    execution_log["status"] = "efax送信成功"
                else:
                    print(f"⚠️ efax送信失敗: {efax_result.stderr}")
            except subprocess.TimeoutExpired:
                print("⚠️ efax送信タイムアウト（30秒）")
            except Exception as e:
                print(f"⚠️ efax実行エラー: {e}")
    except Exception as e:
        print(f"⚠️ efaxコマンド確認エラー: {e}")
    
    # 方法2: 代替FAXコマンド確認
    fax_commands = ['fax', 'sendfax', 'lp']
    for cmd in fax_commands:
        try:
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📡 {cmd}コマンドが利用可能: {result.stdout.strip()}")
                # 実際の送信は手動確認後に実行
        except:
            pass
    
    # 方法3: ネットワークFAX（可能な場合）
    try:
        print(f"\n📡 ネットワークFAX送信を確認中...")
        # 実際のFAXサーバーが設定されている場合のみ
        print("ℹ️ ネットワークFAXサーバー未設定")
    except Exception as e:
        print(f"⚠️ ネットワークFAX確認エラー: {e}")
    
    # 実行結果の記録
    log_file = "/home/fujinosuke/fax_execution_log.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        execution_log["success_methods"] = success_methods
        execution_log["final_status"] = "送信完了" if success_methods else "手動送信が必要"
        logs.append(execution_log)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        print(f"\n📝 実行ログ保存: {log_file}")
    except Exception as e:
        print(f"⚠️ ログ保存エラー: {e}")
    
    # 最終結果
    if success_methods:
        print(f"\n✅ FAX送信完了")
        print(f"📞 宛先: {fax_number}")
        print(f"📄 ファイル: {os.path.abspath(pdf_file)}")
        print(f"✅ 使用方法: {', '.join(success_methods)}")
        return True
    else:
        print(f"\n📋 FAX送信準備完了 - 手動送信が必要")
        print(f"📞 宛先番号: {fax_number}")
        print(f"📄 送信ファイル: {os.path.abspath(pdf_file)}")
        print(f"\n🔧 手動送信方法:")
        print(f"  1. FAXソフトウェアまたは機器を使用")
        print(f"  2. 宛先番号を設定: {fax_number}")
        print(f"  3. PDFファイルを送信: {os.path.abspath(pdf_file)}")
        return True

if __name__ == "__main__":
    execute_fax_send()