#\!/usr/bin/env python3
import os
import subprocess
import time
from datetime import datetime

def setup_scansnap_folder():
    """ScanSnap共有フォルダを作成・設定"""
    scan_dir = "/home/fujinosuke/scansnap_scans"
    
    # ディレクトリ作成
    os.makedirs(scan_dir, exist_ok=True)
    os.makedirs(f"{scan_dir}/inbox", exist_ok=True)
    os.makedirs(f"{scan_dir}/processed", exist_ok=True)
    
    # 権限設定
    os.chmod(scan_dir, 0o755)
    os.chmod(f"{scan_dir}/inbox", 0o777)
    os.chmod(f"{scan_dir}/processed", 0o755)
    
    print(f"ScanSnap受信フォルダ設定完了: {scan_dir}")
    print(f"  - スキャン受信: {scan_dir}/inbox (書き込み許可)")
    print(f"  - 処理済み: {scan_dir}/processed")
    
    return scan_dir

def check_scansnap_connection():
    """ScanSnap接続確認"""
    ip = "192.168.3.49"
    print(f"ScanSnap iX1600 ({ip}) 接続確認中...")
    
    # Ping確認
    result = subprocess.run(["ping", "-c", "3", ip], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ ScanSnap接続確認: 成功")
        return True
    else:
        print("❌ ScanSnap接続確認: 失敗")
        return False

if __name__ == "__main__":
    print("=== ScanSnap iX1600 連携設定 ===")
    
    # 接続確認
    if check_scansnap_connection():
        # フォルダ設定
        scan_dir = setup_scansnap_folder()
        
        print("\n=== 設定完了 ===")
        print("ScanSnap iX1600の設定手順:")
        print("1. ScanSnap本体の[Scan]ボタン長押し → 設定モード")
        print("2. ネットワーク設定でMacMini2014を検索・追加")
        print(f"3. 保存先: {scan_dir}/inbox")
        print("4. または手動でファイル転送")
        
    else:
        print("ScanSnap接続に問題があります。")
