#!/usr/bin/env python3
"""
Chrome ブックマーク自動修正ツール（入力待機なし）
"""

import json
import shutil
import subprocess
import time
import os
from datetime import datetime
from collections import defaultdict

class ChromeAutoFix:
    def __init__(self):
        self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        self.backup_file = f"{self.json_file}.auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bookmarks = []
        self.categorized_bookmarks = defaultdict(list)
        
        # 主要カテゴリのみ
        self.categories = {
            '🏦 金融': ['sbi', 'jcb', 'bank', '銀行', 'money', '住信', '北洋', 'moneyforward', '三井住友', 'やよい'],
            '🛍️ ショッピング': ['amazon', 'rakuten', 'dmm', 'shop', '楽天', 'yahoo', 'hotel'],
            '🚗 自動車': ['car', 'toyota', '車', '中古車', 'carsensor', 'aucsupport'],
            '🎬 動画': ['youtube', 'video', 'dmm.co.jp/digital', 'エロス覚醒'],
            '📱 SNS': ['line', 'lineworks', '面会予約'],
            '🔧 ツール': ['google', 'chatgpt', 'claude', 'apple', 'trello'],
            '📡 通信': ['docomo', 'softbank', 'biglobe', 'ahamo'],
            '📰 ニュース': ['news', 'nhk', 'weathernews', '天気'],
            '📚 学習': ['study', 'english', '学習'],
            '💻 開発': ['github', 'programming', 'jcom']
        }

    def auto_process(self):
        """自動処理実行"""
        print("🔧 Chrome自動修正開始...")
        
        # Chrome強制終了
        print("1️⃣ Chrome強制終了中...")
        try:
            subprocess.run('taskkill /F /IM chrome.exe /T', shell=True, cwd="/mnt/c", capture_output=True, timeout=5)
            time.sleep(2)
        except:
            pass
        
        # ブックマーク解析
        print("2️⃣ ブックマーク解析中...")
        if not self.parse_bookmarks():
            return False
        
        # カテゴリ分類
        print("3️⃣ カテゴリ分類中...")
        self.categorize_bookmarks()
        
        # 構造作成
        print("4️⃣ 新構造作成中...")
        return self.create_new_structure()

    def parse_bookmarks(self):
        """ブックマーク解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
            
            self._extract_bookmarks(self.bookmark_data['roots'])
            print(f"   📊 {len(self.bookmarks)}件のブックマークを解析")
            return True
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            return False

    def _extract_bookmarks(self, node):
        """ブックマーク抽出（簡易版）"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                self.bookmarks.append({
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'date_added': node.get('date_added', ''),
                    'date_last_used': node.get('date_last_used', '')
                })
            elif 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child)
        elif isinstance(node, list):
            for item in node:
                self._extract_bookmarks(item)
        
        # 主要キー処理
        for key in ['bookmark_bar', 'other', 'synced']:
            if isinstance(node, dict) and key in node:
                self._extract_bookmarks(node[key])

    def categorize_bookmarks(self):
        """カテゴリ分類"""
        for bookmark in self.bookmarks:
            url = bookmark['url'].lower()
            name = bookmark['name'].lower()
            
            categorized = False
            for category, keywords in self.categories.items():
                if any(keyword.lower() in url or keyword.lower() in name for keyword in keywords):
                    self.categorized_bookmarks[category].append(bookmark)
                    categorized = True
                    break
            
            if not categorized:
                self.categorized_bookmarks['📂 その他'].append(bookmark)
        
        # 結果表示
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if bookmarks:
                print(f"   {category}: {len(bookmarks)}件")

    def create_new_structure(self):
        """新構造作成"""
        try:
            # バックアップ
            shutil.copy2(self.json_file, self.backup_file)
            print(f"   💾 バックアップ: {os.path.basename(self.backup_file)}")
            
            # 新構造
            timestamp = str(int(datetime.now().timestamp() * 1000000))
            
            new_structure = {
                "checksum": "",
                "roots": {
                    "bookmark_bar": {
                        "children": [],
                        "date_added": timestamp,
                        "date_last_used": "0",
                        "date_modified": timestamp,
                        "guid": "bar-guid-001",
                        "id": "1",
                        "name": "ブックマーク バー",
                        "type": "folder"
                    },
                    "other": {
                        "children": [],
                        "date_added": timestamp,
                        "date_last_used": "0",
                        "date_modified": timestamp,
                        "guid": "other-guid-002",
                        "id": "2",
                        "name": "その他のブックマーク",
                        "type": "folder"
                    },
                    "synced": {
                        "children": [],
                        "date_added": timestamp,
                        "date_last_used": "0",
                        "date_modified": timestamp,
                        "guid": "synced-guid-003",
                        "id": "3",
                        "name": "同期されたブックマーク",
                        "type": "folder"
                    }
                },
                "version": 1
            }
            
            # カテゴリフォルダ作成
            folder_id = 100
            
            for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
                if not bookmarks:
                    continue
                
                folder = {
                    "children": [],
                    "date_added": timestamp,
                    "date_last_used": "0",
                    "date_modified": timestamp,
                    "guid": f"cat-{folder_id}",
                    "id": str(folder_id),
                    "name": category,
                    "type": "folder"
                }
                folder_id += 1
                
                # ブックマーク追加
                for bookmark in bookmarks:
                    item = {
                        "date_added": bookmark['date_added'] or timestamp,
                        "date_last_used": bookmark['date_last_used'] or "0",
                        "guid": f"bm-{folder_id}",
                        "id": str(folder_id),
                        "name": bookmark['name'],
                        "type": "url",
                        "url": bookmark['url']
                    }
                    folder["children"].append(item)
                    folder_id += 1
                
                new_structure["roots"]["bookmark_bar"]["children"].append(folder)
            
            # ファイル書き込み
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ 新構造作成完了")
            return True
            
        except Exception as e:
            print(f"   ❌ 作成エラー: {e}")
            return False

def main():
    print("🚀 Chrome ブックマーク自動修正ツール")
    print("=" * 50)
    
    fixer = ChromeAutoFix()
    
    if fixer.auto_process():
        print(f"\n🎉 自動修正完了！")
        print(f"📋 作成されたカテゴリ:")
        
        for category, bookmarks in sorted(fixer.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if bookmarks:
                print(f"  {category}: {len(bookmarks)}件")
        
        print(f"\n🔄 手順:")
        print(f"1. Chromeの同期設定を確認: chrome://settings/syncSetup")
        print(f"2. 同期を一時停止")
        print(f"3. Chromeを再起動")
        print(f"4. ブックマークバーを確認")
        
        # Chrome自動起動を試行
        try:
            subprocess.Popen(["/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"], cwd="/mnt/c")
            print(f"5. Chrome自動起動完了")
        except:
            print(f"5. Chromeを手動起動してください")
            
    else:
        print(f"\n❌ 自動修正失敗")

if __name__ == "__main__":
    main()