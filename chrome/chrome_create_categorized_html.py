#!/usr/bin/env python3
"""
Chrome ブックマーク分類済みHTML生成ツール
同期問題を回避してHTMLインポートで確実に分類
"""

import json
import html
from datetime import datetime
from collections import defaultdict

class BookmarkHTMLGenerator:
    def __init__(self):
        self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        self.html_file = "/mnt/c/Users/itoh/Downloads/bookmarks_categorized.html"
        self.bookmarks = []
        self.categorized_bookmarks = defaultdict(list)
        
        # 改良されたカテゴリ定義
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
            ],
            '🏥 医療・健康': [
                'hospital', 'clinic', '病院', '診療', '予約', 'mfmb.jp', 
                '村形耳鼻咽喉科', '医療'
            ]
        }

    def parse_bookmarks(self):
        """ブックマーク解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(self.bookmark_data['roots'])
        print(f"📊 ブックマーク数: {len(self.bookmarks)}")
        return True

    def _extract_bookmarks(self, node):
        """ブックマーク抽出（再帰）"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                self.bookmarks.append({
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'date_added': node.get('date_added', '')
                })
            elif node.get('type') == 'folder' and 'children' in node:
                for child in node['children']:
                    self._extract_bookmarks(child)
        
        # 各ルートフォルダを処理
        for key in ['bookmark_bar', 'other', 'synced']:
            if isinstance(node, dict) and key in node:
                self._extract_bookmarks(node[key])

    def categorize_bookmarks(self):
        """ブックマーク分類"""
        print("⚡ ブックマーク分類中...")
        
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
                self.categorized_bookmarks['📂 その他・未分類'].append(bookmark)

        # 結果表示
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  {category}: {len(bookmarks)}件")

    def generate_html(self):
        """分類済みHTMLファイル生成"""
        print("📄 HTMLファイル生成中...")
        
        html_content = f'''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>ブックマーク分類済み - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</TITLE>
<H1>ブックマーク分類済み</H1>
<DL><p>
'''

        # カテゴリ別にHTMLを生成
        for category, bookmarks in sorted(self.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
            if not bookmarks:
                continue
                
            html_content += f'    <DT><H3>{html.escape(category)} ({len(bookmarks)}件)</H3>\n'
            html_content += '    <DL><p>\n'
            
            for bookmark in bookmarks[:50]:  # 1カテゴリ最大50件
                name = html.escape(bookmark['name'])
                url = html.escape(bookmark['url'])
                html_content += f'        <DT><A HREF="{url}">{name}</A>\n'
            
            if len(bookmarks) > 50:
                html_content += f'        <DT><A HREF="">... 他{len(bookmarks)-50}件</A>\n'
            
            html_content += '    </DL><p>\n'

        html_content += '</DL><p>\n'

        # ファイル書き込み
        try:
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTMLファイル生成完了: {self.html_file}")
            return True
        except Exception as e:
            print(f"❌ HTML生成エラー: {e}")
            return False

def main():
    print("📚 Chrome ブックマーク分類済みHTML生成ツール")
    print("=" * 60)
    
    generator = BookmarkHTMLGenerator()
    
    if generator.parse_bookmarks():
        generator.categorize_bookmarks()
        
        if generator.generate_html():
            print(f"\n🎉 HTML生成完了！")
            print(f"📁 ファイル場所: {generator.html_file}")
            print(f"\n📋 生成されたカテゴリ:")
            
            for category, bookmarks in sorted(generator.categorized_bookmarks.items(), key=lambda x: len(x[1]), reverse=True):
                if bookmarks:
                    print(f"  {category}: {len(bookmarks)}件")
            
            print(f"\n🔄 次の手順:")
            print(f"1. Chromeでブックマークマネージャーを開く (Ctrl+Shift+O)")
            print(f"2. 右上メニュー → 「ブックマークをインポート」")
            print(f"3. ファイル選択: bookmarks_categorized.html")
            print(f"4. インポート完了後、古いブックマークを削除")
        else:
            print(f"\n❌ HTML生成失敗")
    else:
        print(f"\n❌ ブックマーク解析失敗")

if __name__ == "__main__":
    main()