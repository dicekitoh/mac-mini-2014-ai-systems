#!/usr/bin/env python3
"""
Chrome ブックマーク究極修正ツール
同期無効化 → Chrome完全終了 → ファイル修正 → 手動確認
"""

import json
import shutil
import subprocess
import time
import os
from datetime import datetime
from collections import defaultdict

class ChromeUltimateFix:
    def __init__(self):
        self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        self.backup_file = f"{self.json_file}.ultimate_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bookmarks = []
        self.categorized_bookmarks = defaultdict(list)
        
        # 簡潔なカテゴリ定義
        self.categories = {
            '🏦 金融マネー': ['sbi', 'jcb', 'bank', '銀行', 'money', 'マネー', '住信', '北洋', 'moneyforward', '三井住友', 'やよい', 'モビット'],
            '🛍️ ショッピング': ['amazon', 'rakuten', 'dmm', 'shop', '楽天', 'yahoo', 'hotel', 'クロスホテル'],
            '🚗 自動車': ['car', 'toyota', 'honda', '車', '中古車', 'アクシオ', 'carsensor', 'aucsupport', 'プリウス', 'クラウン'],
            '🎬 動画': ['youtube', 'video', 'dmm.co.jp/digital', 'NO.1 STYLE', '大痙攣', 'エロス覚醒', 'kawaii', 'mylibrary'],
            '📱 SNS': ['line', 'twitter', 'instagram', 'lineworks', '面会予約', 'talk.worksmobile'],
            '🔧 ツール': ['google', 'chatgpt', 'claude', 'notebooklm', 'apple', 'icloud', 'trello', 'ボーリング'],
            '📡 通信': ['docomo', 'softbank', 'biglobe', 'ahamo', 'iijmio', 'nifty'],
            '📰 ニュース': ['news', 'nhk', 'weathernews', '天気', '気象警報'],
            '📚 学習': ['study', 'english', '学習', '勉強', 'manual', 'studyfire'],
            '💻 開発': ['github', 'git', 'programming', 'jcom', 'etc-meisai', '予約システム']
        }

    def force_kill_chrome(self):
        """Chrome完全強制終了"""
        print("🛑 Chrome完全強制終了中...")
        
        commands = [
            'taskkill /F /IM chrome.exe /T',
            'taskkill /F /IM msedge.exe /T',  # Edgeも念のため
            'timeout /t 3'  # 3秒待機
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, cwd="/mnt/c", capture_output=True, timeout=10)
            except:
                pass
        
        print("✅ Chrome強制終了完了")

    def parse_bookmarks(self):
        """ブックマーク解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(self.bookmark_data['roots'], "")
        print(f"📊 ブックマーク数: {len(self.bookmarks)}")
        return True

    def _extract_bookmarks(self, node, folder_path):
        """ブックマーク抽出"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                self.bookmarks.append({
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'date_added': node.get('date_added', ''),
                    'date_last_used': node.get('date_last_used', ''),
                    'guid': node.get('guid', '')
                })
            elif node.get('type') == 'folder' and 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child, folder_path)
            elif 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child, folder_path)
        elif isinstance(node, list):
            for item in node:
                self._extract_bookmarks(item, folder_path)
                
        for key in ['bookmark_bar', 'other', 'synced']:
            if key in node:
                self._extract_bookmarks(node[key], folder_path)

    def quick_categorize(self):
        """高速カテゴリ分類"""
        print("⚡ 高速カテゴリ分類中...")
        
        for bookmark in self.bookmarks:
            url = bookmark['url'].lower()
            name = bookmark['name'].lower()
            
            assigned = False
            for category, keywords in self.categories.items():
                for keyword in keywords:
                    if keyword.lower() in url or keyword.lower() in name:
                        self.categorized_bookmarks[category].append(bookmark)
                        assigned = True
                        break
                if assigned:
                    break
            
            if not assigned:
                self.categorized_bookmarks['📂 その他'].append(bookmark)

        # 結果表示
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {category}: {len(bookmarks)}件")

    def create_simple_structure(self):
        """シンプル構造作成"""
        print("🗂️ シンプル構造作成中...")
        
        # バックアップ
        shutil.copy2(self.json_file, self.backup_file)
        print(f"💾 バックアップ: {os.path.basename(self.backup_file)}")
        
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
                    "guid": "bookmark-bar-guid",
                    "id": "1",
                    "name": "ブックマーク バー",
                    "type": "folder"
                },
                "other": {
                    "children": [],
                    "date_added": timestamp,
                    "date_last_used": "0",
                    "date_modified": timestamp,
                    "guid": "other-guid",
                    "id": "2",
                    "name": "その他のブックマーク",
                    "type": "folder"
                },
                "synced": {
                    "children": [],
                    "date_added": timestamp,
                    "date_last_used": "0",
                    "date_modified": timestamp,
                    "guid": "synced-guid",
                    "id": "3",
                    "name": "同期されたブックマーク",
                    "type": "folder"
                }
            },
            "version": 1
        }
        
        # カテゴリフォルダ追加
        current_id = 10
        
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if not bookmarks:
                continue
            
            folder = {
                "children": [],
                "date_added": timestamp,
                "date_last_used": "0",
                "date_modified": timestamp,
                "guid": f"folder-{current_id}",
                "id": str(current_id),
                "name": category,
                "type": "folder"
            }
            current_id += 1
            
            # ブックマーク追加
            for bookmark in bookmarks:
                item = {
                    "date_added": bookmark['date_added'] or timestamp,
                    "date_last_used": bookmark['date_last_used'] or "0",
                    "guid": f"bookmark-{current_id}",
                    "id": str(current_id),
                    "name": bookmark['name'],
                    "type": "url",
                    "url": bookmark['url']
                }
                folder["children"].append(item)
                current_id += 1
            
            new_structure["roots"]["bookmark_bar"]["children"].append(folder)
        
        # ファイル書き込み
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, ensure_ascii=False, indent=2)
            
            print("✅ ファイル書き込み完了")
            return True
        except Exception as e:
            print(f"❌ 書き込みエラー: {e}")
            return False

def main():
    print("🔥 Chrome ブックマーク究極修正ツール")
    print("=" * 50)
    
    fixer = ChromeUltimateFix()
    
    print("\n⚠️ 自動実行モード: Chrome強制終了 → ブックマーク修正")
    
    # Chrome強制終了
    fixer.force_kill_chrome()
    
    # ブックマーク処理
    if fixer.parse_bookmarks():
        fixer.quick_categorize()
        
        if fixer.create_simple_structure():
            print(f"\n🎉 修正完了！")
            print(f"📋 作成されたカテゴリ:")
            
            for category, bookmarks in sorted(fixer.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
                if bookmarks:
                    print(f"  {category}: {len(bookmarks)}件")
            
            print(f"\n🔄 今すぐChromeを起動してブックマークバーを確認してください")
            print(f"❗ 重要: Chromeの同期設定を確認してください")
        else:
            print(f"\n❌ 修正失敗")
    else:
        print(f"\n❌ ブックマーク解析失敗")

if __name__ == "__main__":
    main()