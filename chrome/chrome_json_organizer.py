#!/usr/bin/env python3
"""
Chrome JSON ブックマーク整理ツール（WSL対応）
Windows11のChromeブックマークJSONファイルを直接解析・整理

使用方法:
python chrome_json_organizer.py
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from collections import defaultdict
import sys
import os

class ChromeJSONBookmarkOrganizer:
    def __init__(self, json_file=None):
        if json_file is None:
            # Windows Chrome のデフォルトパス（WSL経由）
            self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        else:
            self.json_file = json_file
            
        self.bookmarks = []
        self.duplicates = []
        self.broken_links = []
        self.categories = defaultdict(int)
        
    def parse_bookmarks(self):
        """ChromeのJSONブックマークファイルを解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(data['roots'], "")
        print(f"総ブックマーク数: {len(self.bookmarks)}")
        return True
        
    def _extract_bookmarks(self, node, folder_path):
        """再帰的にブックマークを抽出"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                # ブックマークアイテム
                bookmark = {
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'folder': folder_path,
                    'date_added': node.get('date_added', ''),
                    'date_last_used': node.get('date_last_used', ''),
                    'guid': node.get('guid', '')
                }
                self.bookmarks.append(bookmark)
                self._categorize_bookmark(bookmark)
                
            elif node.get('type') == 'folder' and 'children' in node:
                # フォルダ
                folder_name = node.get('name', '無題フォルダ')
                new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                
                for child in node['children']:
                    self._extract_bookmarks(child, new_path)
                    
            elif 'children' in node:
                # ルートレベルのコンテナ
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
                
    def _categorize_bookmark(self, bookmark):
        """ブックマークをカテゴリ分類"""
        url = bookmark['url'].lower()
        name = bookmark['name'].lower()
        
        # 日本語キーワードも含めた分類
        if any(word in url or word in name for word in [
            'github', 'git', 'stackoverflow', 'qiita', 'zenn', 'tech', 'dev', 'code', 'programming',
            'プログラム', '開発', 'エンジニア', 'コード'
        ]):
            self.categories['開発・プログラミング'] += 1
            
        elif any(word in url or word in name for word in [
            'youtube', 'video', 'netflix', 'amazon prime', 'niconico', 'tiktok',
            '動画', 'ニコニコ', 'テレビ', 'アニメ', '映画'
        ]):
            self.categories['動画・エンターテイメント'] += 1
            
        elif any(word in url or word in name for word in [
            'news', 'nikkei', 'asahi', 'mainichi', 'yomiuri', 'nhk', 'cnn', 'bbc',
            'ニュース', '新聞', '朝日', '読売', '毎日', '日経'
        ]):
            self.categories['ニュース・情報'] += 1
            
        elif any(word in url or word in name for word in [
            'amazon', 'rakuten', 'yahoo', 'shop', 'buy', 'cart', 'price', 'sale',
            '楽天', 'ショップ', '購入', '買い物', '通販', 'ヨドバシ', 'ビックカメラ'
        ]):
            self.categories['ショッピング'] += 1
            
        elif any(word in url or word in name for word in [
            'twitter', 'facebook', 'instagram', 'linkedin', 'social', 'line',
            'ツイッター', 'フェイスブック', 'インスタ', 'ライン', 'SNS'
        ]):
            self.categories['SNS・ソーシャル'] += 1
            
        elif any(word in url or word in name for word in [
            'bank', 'money', 'finance', 'pay', 'card', 'investment', 'stock',
            '銀行', 'マネー', 'お金', '投資', '株', 'カード', '金融', 'SBI', 'JCB'
        ]):
            self.categories['金融・マネー'] += 1
            
        elif any(word in url or word in name for word in [
            'google', 'gmail', 'drive', 'docs', 'office', 'microsoft', 'tool', 'utility',
            'ツール', 'オフィス', 'グーグル', 'マイクロソフト'
        ]):
            self.categories['ツール・ユーティリティ'] += 1
            
        elif any(word in url or word in name for word in [
            'study', 'learn', 'education', 'course', 'tutorial', 'wiki', 'doc',
            '学習', '勉強', '教育', 'チュートリアル', 'ウィキ', '辞書'
        ]):
            self.categories['学習・教育'] += 1
            
        else:
            self.categories['その他'] += 1
            
    def find_duplicates(self):
        """重複ブックマークを検出"""
        url_count = defaultdict(list)
        name_count = defaultdict(list)
        
        for i, bookmark in enumerate(self.bookmarks):
            url_count[bookmark['url']].append(i)
            name_count[bookmark['name']].append(i)
            
        # URL重複
        url_duplicates = {url: indices for url, indices in url_count.items() if len(indices) > 1}
        
        # 名前重複（URLが異なる場合）
        name_duplicates = {}
        for name, indices in name_count.items():
            if len(indices) > 1 and name:  # 空の名前は除外
                urls = [self.bookmarks[i]['url'] for i in indices]
                if len(set(urls)) > 1:  # 異なるURLで同じ名前
                    name_duplicates[name] = indices
                    
        self.duplicates = {
            'url_duplicates': url_duplicates,
            'name_duplicates': name_duplicates
        }
        
        print(f"URL重複: {len(url_duplicates)}組")
        print(f"名前重複: {len(name_duplicates)}組")
        
    def check_broken_links(self, max_check=50, timeout=3):
        """リンク切れをチェック（制限付き）"""
        print(f"リンク切れチェック中（最大{max_check}件）...")
        
        # HTTPSリンクのみをチェック
        http_bookmarks = [(i, b) for i, b in enumerate(self.bookmarks) 
                         if b['url'].startswith(('http://', 'https://'))]
        
        check_count = min(len(http_bookmarks), max_check)
        broken_count = 0
        
        for idx, (i, bookmark) in enumerate(http_bookmarks[:check_count]):
            if idx % 10 == 0:
                print(f"進行状況: {idx}/{check_count}")
                
            try:
                request = urllib.request.Request(bookmark['url'])
                request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    if response.getcode() >= 400:
                        self.broken_links.append({
                            'index': i,
                            'url': bookmark['url'],
                            'name': bookmark['name'],
                            'error': f"HTTP {response.getcode()}"
                        })
                        broken_count += 1
                        
            except Exception as e:
                self.broken_links.append({
                    'index': i,
                    'url': bookmark['url'],
                    'name': bookmark['name'],
                    'error': str(e)[:100]  # エラーメッセージを短縮
                })
                broken_count += 1
                
        print(f"リンク切れ: {broken_count}件")
        
    def display_analysis(self):
        """分析結果を表示"""
        print("\n" + "="*60)
        print("📊 ブックマーク分析結果")
        print("="*60)
        
        print(f"\n📌 総ブックマーク数: {len(self.bookmarks)}")
        
        print(f"\n🔄 重複状況:")
        print(f"  • URL重複: {len(self.duplicates.get('url_duplicates', {}))}組")
        print(f"  • 名前重複: {len(self.duplicates.get('name_duplicates', {}))}組")
        
        if self.broken_links:
            print(f"\n❌ リンク切れ: {len(self.broken_links)}件")
            
        print(f"\n📁 カテゴリ別分類:")
        sorted_categories = sorted(self.categories.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_categories:
            percentage = (count / len(self.bookmarks)) * 100
            print(f"  • {category}: {count}件 ({percentage:.1f}%)")
            
        # フォルダ別統計
        folder_count = defaultdict(int)
        for bookmark in self.bookmarks:
            folder = bookmark['folder'] or '未分類'
            folder_count[folder] += 1
            
        print(f"\n📂 フォルダ別統計（上位10個）:")
        sorted_folders = sorted(folder_count.items(), key=lambda x: x[1], reverse=True)[:10]
        for folder, count in sorted_folders:
            print(f"  • {folder}: {count}件")
            
    def display_duplicates_detail(self):
        """重複の詳細表示"""
        if not self.duplicates.get('url_duplicates'):
            return
            
        print(f"\n🔄 URL重複詳細（上位10組）:")
        url_dupes = list(self.duplicates['url_duplicates'].items())[:10]
        
        for url, indices in url_dupes:
            print(f"\n  URL: {url[:80]}...")
            for idx in indices:
                bookmark = self.bookmarks[idx]
                print(f"    • {bookmark['name']} ({bookmark['folder']})")
                
    def generate_report(self):
        """レポートファイル生成"""
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_bookmarks': len(self.bookmarks),
            'categories': dict(self.categories),
            'duplicates_count': {
                'url_duplicates': len(self.duplicates.get('url_duplicates', {})),
                'name_duplicates': len(self.duplicates.get('name_duplicates', {}))
            },
            'broken_links_count': len(self.broken_links),
            'top_folders': {}
        }
        
        # フォルダ統計
        folder_count = defaultdict(int)
        for bookmark in self.bookmarks:
            folder = bookmark['folder'] or '未分類'
            folder_count[folder] += 1
        report['top_folders'] = dict(sorted(folder_count.items(), key=lambda x: x[1], reverse=True)[:20])
        
        report_file = f"chrome_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"\n📄 詳細レポート保存: {report_file}")
        return report_file

def main():
    print("🔍 Windows11 Chrome ブックマーク分析開始")
    print("-" * 60)
    
    organizer = ChromeJSONBookmarkOrganizer()
    
    if not organizer.parse_bookmarks():
        return
        
    print("\n🔄 重複検出中...")
    organizer.find_duplicates()
    
    print("\n❌ リンク切れチェック中...")
    organizer.check_broken_links()
    
    organizer.display_analysis()
    organizer.display_duplicates_detail()
    
    report_file = organizer.generate_report()
    
    print(f"\n✅ 分析完了！")

if __name__ == "__main__":
    main()