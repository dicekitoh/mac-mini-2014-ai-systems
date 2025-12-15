#!/usr/bin/env python3
"""
Chrome ブックマーク自動インポートツール
分類済みHTMLファイルを自動でインポート
"""

import subprocess
import time
import os

def main():
    print("📚 Chrome ブックマーク自動インポートツール")
    print("=" * 50)
    
    # HTMLファイルの確認
    html_file = "/mnt/c/Users/itoh/Downloads/bookmarks_categorized.html"
    if not os.path.exists(html_file):
        print(f"❌ HTMLファイルが見つかりません: {html_file}")
        return False
    
    print(f"✅ HTMLファイル確認済み: {html_file}")
    
    try:
        # Chrome起動（ブックマークマネージャー）
        print("🌐 Chromeでブックマークマネージャーを開いています...")
        subprocess.Popen([
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
            "chrome://bookmarks/"
        ])
        
        time.sleep(3)  # Chrome起動待ち
        
        # HTMLファイルをエクスプローラーで開く
        print("📁 分類済みHTMLファイルをエクスプローラーで開いています...")
        subprocess.Popen([
            "/mnt/c/Windows/explorer.exe",
            "/select,C:\\Users\\itoh\\Downloads\\bookmarks_categorized.html"
        ])
        
        print("\n🔄 手動でインポートを完了してください:")
        print("1. Chromeのブックマークマネージャーで右上の「⋮」メニューをクリック")
        print("2. 「ブックマークをインポート」を選択")
        print("3. ファイル選択ダイアログで「bookmarks_categorized.html」を選択")
        print("4. 「開く」をクリックしてインポート実行")
        print("\n✅ インポート完了後、古いブックマークフォルダを削除してください")
        
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    main()