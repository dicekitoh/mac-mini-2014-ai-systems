#!/usr/bin/env python3
"""
Chrome新規プロファイル作成 + ブックマーク整理
同期問題を完全回避する最終手段
"""

import json
import shutil
import subprocess
import time
import os
from datetime import datetime
from collections import defaultdict

class ChromeFreshProfileSetup:
    def __init__(self):
        self.chrome_user_data = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data"
        self.old_default = f"{self.chrome_user_data}/Profile 2"
        self.new_profile = f"{self.chrome_user_data}/Profile Fresh"
        self.backup_dir = f"/home/rootmax/chrome_fresh_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # カテゴリ定義
        self.categories = {
            '🏦 金融・マネー': [
                'sbi', 'jcb', 'bank', '銀行', 'money', 'マネー', '住信', '北洋', 
                'moneyforward', '三井住友', 'やよい', 'モビット', 'netbk', 'hokuyobank',
                'my.jcb', 'shinkoku.yayoi', 'mobit'
            ],
            '🛍️ ショッピング': [
                'amazon', 'rakuten', 'dmm', 'shop', '楽天', 'yahoo', 'hotel', 
                'クロスホテル', 'mylibrary', 'travel.rakuten', 'carsensor'
            ],
            '🚗 自動車・車関連': [
                'car', 'toyota', 'honda', '車', '中古車', 'アクシオ', 'carsensor', 
                'aucsupport', 'プリウス', 'クラウン', 'gle', '協栄', 'kyouei'
            ],
            '🎬 動画・エンターテイメント': [
                'youtube', 'video', 'dmm.co.jp/digital', 'NO.1 STYLE', '大痙攣', 
                'エロス覚醒', 'kawaii', 'mylibrary', '新人', '大絶頂', '異常なる'
            ],
            '📱 SNS・コミュニケーション': [
                'line', 'twitter', 'instagram', 'lineworks', '面会予約', 
                'talk.worksmobile', 'works-', 'dice1019.xsrv.jp/lineworks'
            ],
            '🔧 ツール・AI': [
                'google', 'chatgpt', 'claude', 'notebooklm', 'apple', 'icloud', 
                'trello', 'secretoffice', 'aqua', 'chrome://', 'gmail'
            ],
            '📡 データ通信・通信': [
                'docomo', 'softbank', 'biglobe', 'ahamo', 'iijmio', 'nifty', 
                'mydocomo', 'jcom', 'mypage.jcom', 'member1.sso.biglobe'
            ],
            '📰 ニュース・天気': [
                'news', 'nhk', 'weathernews', '天気', '気象警報', 'plus.nhk', 
                'dice1019.xsrv.jp/weather', '札幌市清田区'
            ],
            '📚 学習・教育': [
                'study', 'english', '学習', '勉強', 'manual', 'studyfire', 
                'dice1019.xsrv.jp/english', '英単語', '中学1年生'
            ],
            '💻 開発・プログラミング': [
                'github', 'git', 'programming', 'etc-meisai', '予約システム',
                'mfmb.jp', '診療予約', 'village'
            ]
        }

    def force_kill_chrome(self):
        """Chrome完全強制終了"""
        print("🛑 Chrome完全強制終了中...")
        
        commands = [
            'taskkill /F /IM chrome.exe /T',
            'taskkill /F /IM GoogleUpdate.exe /T',
            'timeout /t 5'
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, cwd="/mnt/c", capture_output=True, timeout=15)
            except:
                pass
        
        print("✅ Chrome強制終了完了")

    def backup_current_profile(self):
        """現在のプロファイルをバックアップ"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 重要ファイルのバックアップ
            important_files = [
                "Bookmarks",
                "Preferences", 
                "History",
                "Login Data",
                "Extensions"
            ]
            
            for file_name in important_files:
                src = f"{self.old_default}/{file_name}"
                if os.path.exists(src):
                    if os.path.isdir(src):
                        shutil.copytree(src, f"{self.backup_dir}/{file_name}")
                    else:
                        shutil.copy2(src, f"{self.backup_dir}/{file_name}")
            
            print(f"💾 プロファイルバックアップ完了: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ バックアップエラー: {e}")
            return False

    def create_fresh_profile(self):
        """新規プロファイルを作成"""
        try:
            # 既存の新規プロファイルを削除
            if os.path.exists(self.new_profile):
                shutil.rmtree(self.new_profile)
            
            # 新規プロファイルディレクトリ作成
            os.makedirs(self.new_profile, exist_ok=True)
            
            print("📁 新規プロファイル作成完了")
            return True
        except Exception as e:
            print(f"❌ プロファイル作成エラー: {e}")
            return False

    def extract_and_categorize_bookmarks(self):
        """既存ブックマークを抽出・分類"""
        try:
            bookmarks_file = f"{self.old_default}/Bookmarks"
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmark_data = json.load(f)
            
            bookmarks = []
            self._extract_bookmarks(bookmark_data['roots'], bookmarks)
            
            print(f"📊 抽出したブックマーク数: {len(bookmarks)}")
            
            # カテゴリ分類
            categorized = defaultdict(list)
            for bookmark in bookmarks:
                url = bookmark['url'].lower()
                name = bookmark['name'].lower()
                
                assigned = False
                for category, keywords in self.categories.items():
                    for keyword in keywords:
                        if keyword.lower() in url or keyword.lower() in name:
                            categorized[category].append(bookmark)
                            assigned = True
                            break
                    if assigned:
                        break
                
                if not assigned:
                    categorized['📂 その他・未分類'].append(bookmark)
            
            return categorized
        except Exception as e:
            print(f"❌ ブックマーク抽出エラー: {e}")
            return {}

    def _extract_bookmarks(self, node, bookmarks):
        """ブックマーク抽出（再帰）"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                bookmarks.append({
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'date_added': node.get('date_added', ''),
                    'guid': node.get('guid', '')
                })
            elif node.get('type') == 'folder' and 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child, bookmarks)
        
        # 各ルートフォルダを処理
        for key in ['bookmark_bar', 'other', 'synced']:
            if isinstance(node, dict) and key in node:
                self._extract_bookmarks(node[key], bookmarks)

    def create_fresh_bookmarks(self, categorized_bookmarks):
        """新規プロファイルに分類済みブックマークを作成"""
        try:
            timestamp = str(int(datetime.now().timestamp() * 1000000))
            
            new_bookmarks = {
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
            
            for category, bookmarks in sorted(categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
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
                        "date_last_used": "0",
                        "guid": f"bookmark-{current_id}",
                        "id": str(current_id),
                        "name": bookmark['name'],
                        "type": "url",
                        "url": bookmark['url']
                    }
                    folder["children"].append(item)
                    current_id += 1
                
                new_bookmarks["roots"]["bookmark_bar"]["children"].append(folder)
            
            # 新規プロファイルにブックマークファイル作成
            bookmarks_path = f"{self.new_profile}/Bookmarks"
            with open(bookmarks_path, 'w', encoding='utf-8') as f:
                json.dump(new_bookmarks, f, ensure_ascii=False, indent=2)
            
            print("✅ 新規プロファイルにブックマーク作成完了")
            return True
        except Exception as e:
            print(f"❌ ブックマーク作成エラー: {e}")
            return False

    def create_fresh_preferences(self):
        """新規プロファイル用のPreferences作成（同期無効）"""
        try:
            preferences = {
                "sync": {
                    "suppress_sync_promo": True,
                    "keep_everything_synced": False,
                    "sync_everything": False,
                    "sync_bookmarks": False,
                    "disabled": True
                },
                "signin": {
                    "allowed": False
                },
                "bookmark_bar": {
                    "show_on_all_tabs": True
                },
                "browser": {
                    "enable_spellchecking": False
                },
                "first_run_tabs": ["chrome://newtab/"]
            }
            
            preferences_path = f"{self.new_profile}/Preferences"
            with open(preferences_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
            
            print("✅ 新規プロファイル用Preferences作成完了")
            return True
        except Exception as e:
            print(f"❌ Preferences作成エラー: {e}")
            return False

    def launch_fresh_profile(self):
        """新規プロファイルでChromeを起動"""
        try:
            profile_name = os.path.basename(self.new_profile)
            subprocess.Popen([
                "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
                f"--profile-directory={profile_name}",
                "--new-window"
            ])
            print("🚀 新規プロファイルでChrome起動")
            return True
        except Exception as e:
            print(f"❌ Chrome起動エラー: {e}")
            return False

def main():
    print("🆕 Chrome新規プロファイル + ブックマーク整理")
    print("=" * 60)
    
    setup = ChromeFreshProfileSetup()
    
    # Chrome強制終了
    setup.force_kill_chrome()
    
    # 現在のプロファイルバックアップ
    if not setup.backup_current_profile():
        return
    
    # 新規プロファイル作成
    if not setup.create_fresh_profile():
        return
    
    # ブックマーク抽出・分類
    categorized = setup.extract_and_categorize_bookmarks()
    if not categorized:
        print("❌ ブックマーク抽出失敗")
        return
    
    print("📋 分類結果:")
    for category, bookmarks in sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category}: {len(bookmarks)}件")
    
    # 新規プロファイルにブックマーク・設定作成
    if setup.create_fresh_bookmarks(categorized) and setup.create_fresh_preferences():
        # 新規プロファイルでChrome起動
        setup.launch_fresh_profile()
        
        print(f"\n🎉 新規プロファイル作成完了！")
        print(f"📁 プロファイル場所: {setup.new_profile}")
        print(f"🔄 今後はこの新規プロファイルを使用してください")
        print(f"💡 ヒント: ブックマークバーに分類されたフォルダが表示されます")
    else:
        print(f"\n❌ 新規プロファイル作成失敗")

if __name__ == "__main__":
    main()