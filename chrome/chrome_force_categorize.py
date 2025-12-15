#!/usr/bin/env python3
"""
Chrome ブックマーク強制カテゴリ分類ツール
Chromeプロセス確認 → 強制終了 → カテゴリ分類 → 完全反映
"""

import json
import shutil
import subprocess
import time
import os
from datetime import datetime
from collections import defaultdict

class ChromeForceCategorizer:
    def __init__(self, json_file=None):
        if json_file is None:
            self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        else:
            self.json_file = json_file
            
        self.backup_file = f"{self.json_file}.force_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bookmarks = []
        self.categorized_bookmarks = defaultdict(list)
        
        # より詳細なカテゴリ定義
        self.categories = {
            '🏦 金融・マネー': [
                'sbi', 'jcb', 'mufg', 'bank', 'money', 'finance', 'pay', 'card', 'investment', 'stock',
                '銀行', 'マネー', 'お金', '投資', '株', 'カード', '金融', '住信', '北洋', 'moneyforward',
                'マネーフォワード', '楽天銀行', 'ゆうちょ', '信用金庫', '三井住友', 'みずほ', 'モビット',
                'やよい', '確定申告', 'benefit', 'ベネフィット', '白色申告', 'netbk', 'smbc-card'
            ],
            '🛍️ ショッピング': [
                'amazon', 'rakuten', 'yahoo', 'shop', 'buy', 'cart', 'price', 'sale', 'store',
                '楽天', 'ショップ', '購入', '買い物', '通販', 'ヨドバシ', 'ビックカメラ', 'メルカリ',
                'dmm.co.jp', 'hotel', 'travel', 'クロスホテル', 'booking', 'クロスホテル札幌'
            ],
            '🚗 自動車・車関連': [
                'car', 'auto', 'toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi',
                '車', '自動車', 'カー', 'トヨタ', 'ホンダ', '日産', 'マツダ', 'スバル', '三菱',
                'プリウス', 'クラウン', 'アクア', 'ヴィッツ', '中古車', 'オークション', '査定',
                'アクシオ', 'ランドローバー', 'ディフェンダー', 'carsensor', 'aucsupport',
                'GLE', 'クラウンクロスオーバー', 'M&P', 'kyouei'
            ],
            '📱 SNS・ソーシャル': [
                'twitter', 'facebook', 'instagram', 'linkedin', 'social', 'line', 'tiktok',
                'ツイッター', 'フェイスブック', 'インスタ', 'ライン', 'SNS', 'コミュニティ',
                'lineworks', '面会予約', 'talk.worksmobile', 'works', 'dice1019.xsrv.jp/lineworks'
            ],
            '🎬 動画・エンターテイメント': [
                'youtube', 'video', 'netflix', 'amazon prime', 'niconico', 'tiktok', 'hulu',
                '動画', 'ニコニコ', 'テレビ', 'アニメ', '映画', 'ドラマ', 'VOD', 'streaming',
                'dmm.co.jp/digital/videoa', 'NO.1 STYLE', '大痙攣', '異常なる', 'エロス覚醒',
                'kawaii', 'adult', 'av', 'アダルト', 'digital/videoa', 'mylibrary'
            ],
            '📰 ニュース・情報': [
                'news', 'nikkei', 'asahi', 'mainichi', 'yomiuri', 'nhk', 'cnn', 'bbc',
                'ニュース', '新聞', '朝日', '読売', '毎日', '日経', '情報', 'yahoo news',
                'weathernews', '天気', 'plus.nhk', 'fakenews', 'NHKプラス', '天気予報'
            ],
            '🔧 ツール・ユーティリティ': [
                'google', 'gmail', 'drive', 'docs', 'office', 'microsoft', 'tool', 'utility',
                'ツール', 'オフィス', 'グーグル', 'マイクロソフト', 'dropbox', 'slack',
                'zoom', 'teams', 'notion', 'calendar', 'notebooklm', 'chatgpt', 'claude',
                'openai', 'trello', 'apple', 'icloud', 'brightstar', 'anker', 'osmo',
                'ChatGPT', 'NotebookLM', 'AQUA', 'ボーリング', 'ハンディキャップ', '計算ツール'
            ],
            '💻 開発・プログラミング': [
                'github', 'git', 'stackoverflow', 'qiita', 'zenn', 'tech', 'dev', 'code', 'programming',
                'プログラム', '開発', 'エンジニア', 'コード', 'システム', 'API', 'データベース',
                'jcom', 'etc', 'mypage', 'etc-meisai', '予約システム', 'mfmb.jp'
            ],
            '📚 学習・教育': [
                'study', 'learn', 'education', 'course', 'tutorial', 'wiki', 'doc', 'manual',
                '学習', '勉強', '教育', 'チュートリアル', 'ウィキ', '辞書', '英語', '語学',
                'studyfire', 'english', 'manual.pdf', 'User_Manual', 'mydocomo', '中学1年生'
            ],
            '📡 データ通信・通信': [
                'mobile', 'docomo', 'au', 'softbank', 'rakuten mobile', 'sim', 'data', 'communication',
                'モバイル', 'ドコモ', 'ソフトバンク', '楽天モバイル', 'データ通信', '通信',
                'biglobe', 'ahamo', 'iijmio', 'nifty', 'BIGLOBEモバイル'
            ],
            '☁️ 天気・気象': [
                'weather', 'forecast', 'rain', 'snow', 'temperature', 'climate',
                '天気', '気象', '天候', '予報', '雨', '雪', '気温', 'weathernews', '気象警報',
                '北海道気象警報'
            ]
        }
    
    def check_chrome_processes(self):
        """Chromeプロセスの確認"""
        print("🔍 Chromeプロセスを確認中...")
        
        # Windows側でChromeプロセスをチェック
        try:
            # PowerShellでChromeプロセスを確認
            cmd = 'powershell.exe "Get-Process chrome -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/mnt/c")
            
            if result.returncode == 0:
                count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
                if count > 0:
                    print(f"⚠️  Chrome プロセスが {count} 個動作中です")
                    return True
                else:
                    print("✅ Chrome プロセスは動作していません")
                    return False
            else:
                print("ℹ️  Chrome プロセス確認できませんでした（正常な場合があります）")
                return False
        except Exception as e:
            print(f"ℹ️  プロセス確認エラー: {e}")
            return False
    
    def force_close_chrome(self):
        """Chromeの強制終了"""
        print("🛑 Chromeを強制終了中...")
        
        try:
            # taskkill コマンドでChromeを強制終了
            cmd = 'taskkill /F /IM chrome.exe /T'
            subprocess.run(cmd, shell=True, cwd="/mnt/c", capture_output=True)
            
            # 少し待機
            time.sleep(3)
            
            print("✅ Chrome強制終了完了")
            return True
        except Exception as e:
            print(f"⚠️  Chrome強制終了に失敗: {e}")
            return False
    
    def parse_bookmarks(self):
        """ブックマークファイルを解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(self.bookmark_data['roots'], "")
        print(f"📊 解析したブックマーク数: {len(self.bookmarks)}")
        return True
    
    def _extract_bookmarks(self, node, folder_path):
        """再帰的にブックマークを抽出"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                bookmark = {
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'folder': folder_path,
                    'date_added': node.get('date_added', ''),
                    'date_last_used': node.get('date_last_used', ''),
                    'guid': node.get('guid', ''),
                    'id': node.get('id', '')
                }
                self.bookmarks.append(bookmark)
                
            elif node.get('type') == 'folder' and 'children' in node:
                folder_name = node.get('name', '無題フォルダ')
                new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                
                for child in node['children']:
                    self._extract_bookmarks(child, new_path)
                    
            elif 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child, folder_path)
        
        elif isinstance(node, list):
            for item in node:
                self._extract_bookmarks(item, folder_path)
                
        # 特別なキー処理
        for key in ['bookmark_bar', 'other', 'synced']:
            if key in node:
                folder_name = {
                    'bookmark_bar': 'ブックマークバー',
                    'other': 'その他のブックマーク', 
                    'synced': '同期されたブックマーク'
                }.get(key, key)
                
                new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                self._extract_bookmarks(node[key], new_path)
    
    def smart_categorize(self):
        """スマートカテゴリ分類"""
        print("🎯 スマートカテゴリ分類実行中...")
        
        for bookmark in self.bookmarks:
            url = bookmark['url'].lower()
            name = bookmark['name'].lower()
            
            # カテゴリ判定（より厳密）
            assigned_category = None
            max_matches = 0
            
            for category, keywords in self.categories.items():
                matches = 0
                for keyword in keywords:
                    if keyword.lower() in url or keyword.lower() in name:
                        matches += 1
                
                if matches > max_matches:
                    max_matches = matches
                    assigned_category = category
            
            # カテゴリが見つからない場合は「その他」
            if assigned_category is None or max_matches == 0:
                assigned_category = '📂 その他'
            
            self.categorized_bookmarks[assigned_category].append(bookmark)
        
        # 結果表示
        print(f"\n📊 スマートカテゴリ分類結果:")
        print("=" * 60)
        
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(bookmarks)
            percentage = (count / len(self.bookmarks)) * 100
            print(f"{category}: {count:3d}件 ({percentage:5.1f}%)")
    
    def create_categorized_structure(self):
        """強制的にカテゴリ構造を作成"""
        print(f"\n🗂️  強制カテゴリ構造作成中...")
        
        # バックアップ作成
        try:
            shutil.copy2(self.json_file, self.backup_file)
            print(f"💾 バックアップ作成: {os.path.basename(self.backup_file)}")
        except Exception as e:
            print(f"❌ バックアップ作成失敗: {e}")
            return False
        
        # 新しいタイムスタンプ
        current_timestamp = str(int(datetime.now().timestamp() * 1000000))
        
        # 完全に新しい構造
        new_structure = {
            "checksum": "",
            "roots": {
                "bookmark_bar": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0",
                    "date_modified": current_timestamp,
                    "guid": "00000000-0000-0000-0000-000000000001",
                    "id": "1",
                    "name": "ブックマーク バー",
                    "type": "folder"
                },
                "other": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0", 
                    "date_modified": current_timestamp,
                    "guid": "00000000-0000-0000-0000-000000000002",
                    "id": "2",
                    "name": "その他のブックマーク",
                    "type": "folder"
                },
                "synced": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0",
                    "date_modified": current_timestamp,
                    "guid": "00000000-0000-0000-0000-000000000003",
                    "id": "3",
                    "name": "同期されたブックマーク",
                    "type": "folder"
                }
            },
            "version": 1
        }
        
        # カテゴリフォルダを作成
        current_id = 100  # 安全なID範囲
        
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if not bookmarks:
                continue
                
            print(f"  📁 {category}: {len(bookmarks)}件を配置中...")
                
            # カテゴリフォルダ
            category_folder = {
                "children": [],
                "date_added": current_timestamp,
                "date_last_used": "0",
                "date_modified": current_timestamp,
                "guid": f"category-{current_id:08d}",
                "id": str(current_id),
                "name": category,
                "type": "folder"
            }
            current_id += 1
            
            # ブックマークを追加
            for bookmark in bookmarks:
                bookmark_item = {
                    "date_added": bookmark['date_added'] or current_timestamp,
                    "date_last_used": bookmark['date_last_used'] or "0",
                    "guid": f"bookmark-{current_id:08d}",
                    "id": str(current_id),
                    "name": bookmark['name'],
                    "type": "url",
                    "url": bookmark['url']
                }
                category_folder["children"].append(bookmark_item)
                current_id += 1
            
            # ブックマークバーに追加
            new_structure["roots"]["bookmark_bar"]["children"].append(category_folder)
        
        # ファイル保存（強制上書き）
        try:
            # 一時的にファイルを削除
            if os.path.exists(self.json_file):
                os.remove(self.json_file)
            
            # 新しいファイルを作成
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, ensure_ascii=False, indent=2, separators=(',', ': '))
            
            # ファイル権限設定
            os.chmod(self.json_file, 0o666)
            
            print(f"✅ 強制カテゴリ構造作成完了！")
            print(f"💾 ファイル: {os.path.basename(self.json_file)}")
            
            return True
            
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return False
    
    def verify_categorization(self):
        """カテゴリ分類の検証"""
        print(f"\n🔍 カテゴリ分類を検証中...")
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                verify_data = json.load(f)
            
            bookmark_bar = verify_data['roots']['bookmark_bar']['children']
            
            print(f"✅ 検証結果:")
            print(f"  - ブックマークバー内フォルダ数: {len(bookmark_bar)}")
            
            total_bookmarks = 0
            for folder in bookmark_bar:
                if folder.get('type') == 'folder':
                    count = len(folder.get('children', []))
                    total_bookmarks += count
                    print(f"  - {folder['name']}: {count}件")
            
            print(f"  - 総ブックマーク数: {total_bookmarks}")
            
            return True
        except Exception as e:
            print(f"❌ 検証エラー: {e}")
            return False

def main():
    print("🚀 Chrome ブックマーク強制カテゴリ分類ツール")
    print("=" * 70)
    
    categorizer = ChromeForceCategorizer()
    
    # Step 1: Chromeプロセス確認
    chrome_running = categorizer.check_chrome_processes()
    
    # Step 2: Chrome強制終了（必要に応じて）
    if chrome_running:
        categorizer.force_close_chrome()
        time.sleep(2)  # 待機
    
    # Step 3: ブックマーク解析
    if not categorizer.parse_bookmarks():
        return
    
    # Step 4: スマートカテゴリ分類
    categorizer.smart_categorize()
    
    # Step 5: 強制構造作成
    if categorizer.create_categorized_structure():
        # Step 6: 検証
        categorizer.verify_categorization()
        
        print(f"\n🎉 強制カテゴリ分類完了！")
        print(f"🔄 今すぐChromeを起動してブックマークバーを確認してください")
        print(f"⏰ 5秒後にChromeを自動起動します...")
        
        # Chrome自動起動
        time.sleep(5)
        try:
            subprocess.Popen(["/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"], cwd="/mnt/c")
            print(f"✅ Chrome起動完了")
        except Exception as e:
            print(f"ℹ️  Chrome手動起動してください: {e}")
            
    else:
        print(f"\n❌ カテゴリ分類に失敗しました")

if __name__ == "__main__":
    main()