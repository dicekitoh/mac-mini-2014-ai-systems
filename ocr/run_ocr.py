#!/usr/bin/env python3
"""
OCR実行用スクリプト
ocr_inboxフォルダ内のファイルを処理する簡単なコマンド
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """メイン処理"""
    ocr_inbox = "/home/fujinosuke/ocr_inbox"
    ocr_script = "/home/fujinosuke/projects/pdf_ocr_vision.py"
    venv_path = "/home/fujinosuke/projects/ocr_env/bin/activate"
    
    print("🔍 OCR処理システム")
    print("="*40)
    
    if len(sys.argv) > 1:
        # ファイル名指定
        filename = sys.argv[1]
        file_path = os.path.join(ocr_inbox, filename)
    else:
        # ocr_inboxフォルダ内のファイル一覧表示
        if not os.path.exists(ocr_inbox):
            print(f"❌ フォルダが存在しません: {ocr_inbox}")
            return False
        
        files = [f for f in os.listdir(ocr_inbox) 
                if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.gif', '.rtf'))]
        
        if not files:
            print(f"📁 {ocr_inbox} フォルダにOCR対象ファイルがありません")
            print("対応形式: PDF, PNG, JPG, JPEG, TIFF, GIF, RTF")
            return False
        
        print(f"📁 {ocr_inbox} フォルダ内のファイル:")
        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")
        
        print(f"\n使用方法:")
        print(f"  python3 run_ocr.py <ファイル名>")
        print(f"例: python3 run_ocr.py document.pdf")
        return True
    
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return False
    
    print(f"📄 処理ファイル: {filename}")
    
    # ファイルタイプに応じてスクリプトを選択
    if filename.lower().endswith('.rtf'):
        ocr_script = "/home/fujinosuke/projects/rtf_ocr_vision.py"
    
    # OCRスクリプトを実行
    try:
        cmd = f"cd /home/fujinosuke/projects && source {venv_path} && python3 {ocr_script} {file_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')
        
        print(result.stdout)
        if result.stderr:
            print("エラー出力:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ OCR実行エラー: {e}")
        return False

if __name__ == "__main__":
    main()