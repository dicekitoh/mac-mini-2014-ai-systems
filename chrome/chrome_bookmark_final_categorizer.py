#!/usr/bin/env python3
"""
Chrome ブックマーク最終カテゴリ分類ツール
現在のブックマークを確実にカテゴリ別フォルダに整理
"""

import json
import shutil
from datetime import datetime
from collections import defaultdict

class FinalChromeBookmarkCategorizer:
    def __init__(self, json_file=None):
        if json_file is None:
            self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        else:
            self.json_file = json_file
            
        self.backup_file = f"{self.json_file}.final_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bookmarks = []
        self.categorized_bookmarks = defaultdict(list)
        
        # カテゴリ定義（詳細）
        self.categories = {
            '🏦 金融・マネー': [
                'sbi', 'jcb', 'mufg', 'bank', 'money', 'finance', 'pay', 'card', 'investment', 'stock',
                '銀行', 'マネー', 'お金', '投資', '株', 'カード', '金融', '住信', '北洋', 'moneyforward',
                'マネーフォワード', '楽天銀行', 'ゆうちょ', '信用金庫', '三井住友', 'みずほ', 'モビット',
                'やよい', '確定申告', 'benefit', 'ベネフィット'
            ],
            '🛍️ ショッピング': [
                'amazon', 'rakuten', 'yahoo', 'shop', 'buy', 'cart', 'price', 'sale', 'store',
                '楽天', 'ショップ', '購入', '買い物', '通販', 'ヨドバシ', 'ビックカメラ', 'メルカリ',
                'dmm', 'hotel', 'travel', 'クロスホテル', 'booking'
            ],
            '🚗 自動車・車関連': [
                'car', 'auto', 'toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi',
                '車', '自動車', 'カー', 'トヨタ', 'ホンダ', '日産', 'マツダ', 'スバル', '三菱',
                'プリウス', 'クラウン', 'アクア', 'ヴィッツ', '中古車', 'オークション', '査定',
                'アクシオ', 'ランドローバー', 'ディフェンダー', 'carsensor', 'aucsupport'
            ],
            '📱 SNS・ソーシャル': [
                'twitter', 'facebook', 'instagram', 'linkedin', 'social', 'line', 'tiktok',
                'ツイッター', 'フェイスブック', 'インスタ', 'ライン', 'SNS', 'コミュニティ',
                'lineworks', '面会予約', 'talk.worksmobile'
            ],
            '🎬 動画・エンターテイメント': [
                'youtube', 'video', 'netflix', 'amazon prime', 'niconico', 'tiktok', 'hulu',
                '動画', 'ニコニコ', 'テレビ', 'アニメ', '映画', 'ドラマ', 'VOD', 'streaming',
                'dmm.co.jp/digital/videoa', 'NO.1 STYLE', '大痙攣', '異常なる', 'エロス覚醒',
                'kawaii', 'adult', 'av', 'アダルト'
            ],
            '📰 ニュース・情報': [
                'news', 'nikkei', 'asahi', 'mainichi', 'yomiuri', 'nhk', 'cnn', 'bbc',
                'ニュース', '新聞', '朝日', '読売', '毎日', '日経', '情報', 'yahoo news',
                'weathernews', '天気', 'plus.nhk', 'fakenews'
            ],
            '🔧 ツール・ユーティリティ': [
                'google', 'gmail', 'drive', 'docs', 'office', 'microsoft', 'tool', 'utility',
                'ツール', 'オフィス', 'グーグル', 'マイクロソフト', 'dropbox', 'slack',
                'zoom', 'teams', 'notion', 'calendar', 'notebooklm', 'chatgpt', 'claude',
                'openai', 'trello', 'apple', 'icloud', 'brightstar', 'anker', 'osmo'
            ],
            '💻 開発・プログラミング': [
                'github', 'git', 'stackoverflow', 'qiita', 'zenn', 'tech', 'dev', 'code', 'programming',
                'プログラム', '開発', 'エンジニア', 'コード', 'システム', 'API', 'データベース',
                'jcom', 'etc', 'mypage'
            ],
            '📚 学習・教育': [
                'study', 'learn', 'education', 'course', 'tutorial', 'wiki', 'doc', 'manual',
                '学習', '勉強', '教育', 'チュートリアル', 'ウィキ', '辞書', '英語', '語学',
                'studyfire', 'english', 'manual.pdf', 'User_Manual'
            ],
            '📡 データ通信・通信': [
                'mobile', 'docomo', 'au', 'softbank', 'rakuten mobile', 'sim', 'data', 'communication',
                'モバイル', 'ドコモ', 'ソフトバンク', '楽天モバイル', 'データ通信', '通信',
                'biglobe', 'ahamo', 'iijmio', 'nifty'
            ],
            '☁️ 天気・気象': [
                'weather', 'forecast', 'rain', 'snow', 'temperature', 'climate',
                '天気', '気象', '天候', '予報', '雨', '雪', '気温', 'weathernews', '気象警報'
            ],
            '🎯 エンターテイメント・ゲーム': [
                'game', 'bowling', 'ボーリング', 'ハンディキャップ', 'ゲーム', '計算ツール',
                'handincap', 'calculation'
            ]
        }
    
    def parse_current_bookmarks(self):
        """現在のブックマークファイルを解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(self.bookmark_data['roots'], "")
        print(f"📊 現在のブックマーク数: {len(self.bookmarks)}")
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
    
    def categorize_all_bookmarks(self):
        """全ブックマークをカテゴリ分類"""
        print("🔍 ブックマークをカテゴリ別に分類中...")
        
        for bookmark in self.bookmarks:
            url = bookmark['url'].lower()
            name = bookmark['name'].lower()
            
            # カテゴリ判定
            assigned_category = None
            
            for category, keywords in self.categories.items():
                if any(keyword.lower() in url or keyword.lower() in name for keyword in keywords):
                    assigned_category = category
                    break
            
            # カテゴリが見つからない場合は「その他」
            if assigned_category is None:
                assigned_category = '📂 その他'
            
            self.categorized_bookmarks[assigned_category].append(bookmark)
        
        # 結果表示
        print(f"\n📊 カテゴリ別分類結果:")
        print("=" * 60)
        
        total_categorized = 0
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(bookmarks)
            total_categorized += count
            percentage = (count / len(self.bookmarks)) * 100
            print(f"{category}: {count:3d}件 ({percentage:5.1f}%)")
        
        print(f"\n合計: {total_categorized}件")
    
    def create_backup_and_reorganize(self):
        """バックアップ作成と完全再構築"""
        print(f"\n🗂️  完全なカテゴリ別フォルダ構造を作成中...")
        
        # バックアップ作成
        try:
            shutil.copy2(self.json_file, self.backup_file)
            print(f"💾 バックアップ作成: {self.backup_file}")
        except Exception as e:
            print(f"❌ バックアップ作成失敗: {e}")
            return False
        
        # 完全に新しいブックマーク構造を作成
        current_timestamp = str(int(datetime.now().timestamp() * 1000000))
        
        new_structure = {
            "checksum": "",
            "roots": {
                "bookmark_bar": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0",
                    "date_modified": current_timestamp,
                    "guid": "0bc5d13f-2cba-5d74-951f-3f233fe6c908",
                    "id": "1",
                    "name": "ブックマーク バー",
                    "type": "folder"
                },
                "other": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0", 
                    "date_modified": current_timestamp,
                    "guid": "82b081ec-3dd3-529c-8475-ab6c344590dd",
                    "id": "2",
                    "name": "その他のブックマーク",
                    "type": "folder"
                },
                "synced": {
                    "children": [],
                    "date_added": current_timestamp,
                    "date_last_used": "0",
                    "date_modified": current_timestamp,
                    "guid": "4cf2e351-0e85-532b-bb37-df045d8f8d0f",
                    "id": "3",
                    "name": "同期されたブックマーク",
                    "type": "folder"
                }
            },
            "version": 1
        }
        
        # カテゴリフォルダをブックマークバーに追加
        current_id = 10  # 安全なID範囲から開始
        
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if not bookmarks:
                continue
                
            print(f"  📁 {category}: {len(bookmarks)}件を追加中...")
                
            # カテゴリフォルダ作成
            category_folder = {
                "children": [],
                "date_added": current_timestamp,
                "date_last_used": "0",
                "date_modified": current_timestamp,
                "guid": f"category-{current_id:08d}-{hash(category) % 100000:05d}",
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
                    "guid": bookmark['guid'] or f"bookmark-{current_id:08d}-{hash(bookmark['url']) % 100000:05d}",
                    "id": str(current_id),
                    "name": bookmark['name'],
                    "type": "url",
                    "url": bookmark['url']
                }
                category_folder["children"].append(bookmark_item)
                current_id += 1
            
            # ブックマークバーに追加
            new_structure["roots"]["bookmark_bar"]["children"].append(category_folder)
        
        # ファイル保存
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, ensure_ascii=False, indent=2)
            
            print(f"✅ カテゴリ別整理完了！")
            print(f"💾 更新されたファイル: {self.json_file}")
            print(f"🔄 バックアップ: {self.backup_file}")
            
            # 詳細サマリー
            print(f"\n📋 作成されたカテゴリフォルダ:")
            for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
                if bookmarks:
                    print(f"  {category}: {len(bookmarks)}件")
            
            return True
            
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return False

def main():
    print("🗂️  Chrome ブックマーク最終カテゴリ分類ツール")
    print("=" * 70)
    
    categorizer = FinalChromeBookmarkCategorizer()
    
    # 現在のブックマーク解析
    if not categorizer.parse_current_bookmarks():
        return
    
    # カテゴリ分類実行
    categorizer.categorize_all_bookmarks()
    
    # 完全再構築実行
    if categorizer.create_backup_and_reorganize():
        print(f"\n🎉 カテゴリ別整理完了！")
        print(f"🔄 Chromeを完全に終了してから再起動し、ブックマークバーを確認してください")
        print(f"\n⚠️  注意: Chromeが開いている場合は、設定が反映されない可能性があります")
    else:
        print(f"\n❌ カテゴリ分類に失敗しました")

if __name__ == "__main__":
    main()