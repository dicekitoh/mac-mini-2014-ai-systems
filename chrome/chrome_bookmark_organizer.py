#!/usr/bin/env python3
"""
Chrome ブックマーク整理ツール
Windows11 Chrome ブックマークの解析・整理・重複削除・リンクチェック

使用方法:
1. Chrome設定 → ブックマーク → ブックマークマネージャー → エクスポート
2. python chrome_bookmark_organizer.py bookmarks.html
"""

import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from html.parser import HTMLParser
from collections import defaultdict
import argparse
import sys

class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = []
        self.in_folder = False
        
    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            # フォルダの開始
            self.in_folder = True
        elif tag == 'a':
            # ブックマークリンク
            attrs_dict = dict(attrs)
            if 'href' in attrs_dict:
                bookmark = {
                    'url': attrs_dict['href'],
                    'title': '',
                    'folder': '/'.join(self.current_folder),
                    'add_date': attrs_dict.get('add_date', ''),
                    'last_modified': attrs_dict.get('last_modified', '')
                }
                self.bookmarks.append(bookmark)
        elif tag == 'dl' and self.in_folder:
            # フォルダ内容の開始
            pass
            
    def handle_endtag(self, tag):
        if tag == 'h3':
            self.in_folder = False
        elif tag == 'dl' and self.current_folder:
            # フォルダ終了
            if self.current_folder:
                self.current_folder.pop()
                
    def handle_data(self, data):
        if self.in_folder:
            # フォルダ名
            self.current_folder.append(data.strip())
        elif self.bookmarks and not self.bookmarks[-1]['title']:
            # ブックマークタイトル
            self.bookmarks[-1]['title'] = data.strip()

class ChromeBookmarkOrganizer:
    def __init__(self, html_file):
        self.html_file = html_file
        self.bookmarks = []
        self.duplicates = []
        self.broken_links = []
        
    def parse_bookmarks(self):
        """HTMLファイルからブックマークを解析"""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(self.html_file, 'r', encoding='cp932') as f:
                content = f.read()
                
        parser = BookmarkParser()
        parser.feed(content)
        self.bookmarks = parser.bookmarks
        print(f"総ブックマーク数: {len(self.bookmarks)}")
        
    def find_duplicates(self):
        """重複ブックマークを検出"""
        url_count = defaultdict(list)
        title_count = defaultdict(list)
        
        for i, bookmark in enumerate(self.bookmarks):
            url_count[bookmark['url']].append(i)
            title_count[bookmark['title']].append(i)
            
        # URL重複
        url_duplicates = {url: indices for url, indices in url_count.items() if len(indices) > 1}
        
        # タイトル重複（URLが異なる場合）
        title_duplicates = {}
        for title, indices in title_count.items():
            if len(indices) > 1:
                urls = [self.bookmarks[i]['url'] for i in indices]
                if len(set(urls)) > 1:  # 異なるURLで同じタイトル
                    title_duplicates[title] = indices
                    
        self.duplicates = {
            'url_duplicates': url_duplicates,
            'title_duplicates': title_duplicates
        }
        
        print(f"URL重複: {len(url_duplicates)}組")
        print(f"タイトル重複: {len(title_duplicates)}組")
        
    def check_broken_links(self, timeout=5):
        """リンク切れをチェック"""
        print("リンク切れチェック中...")
        broken_count = 0
        
        for i, bookmark in enumerate(self.bookmarks):
            if i % 10 == 0:
                print(f"進行状況: {i}/{len(self.bookmarks)}")
                
            try:
                request = urllib.request.Request(bookmark['url'])
                request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    if response.getcode() >= 400:
                        self.broken_links.append({
                            'index': i,
                            'url': bookmark['url'],
                            'title': bookmark['title'],
                            'error': f"HTTP {response.getcode()}"
                        })
                        broken_count += 1
                        
            except Exception as e:
                self.broken_links.append({
                    'index': i,
                    'url': bookmark['url'],
                    'title': bookmark['title'],
                    'error': str(e)
                })
                broken_count += 1
                
        print(f"リンク切れ: {broken_count}件")
        
    def generate_report(self):
        """整理レポートを生成"""
        report = {
            'total_bookmarks': len(self.bookmarks),
            'duplicates': self.duplicates,
            'broken_links': self.broken_links,
            'analysis_date': datetime.now().isoformat(),
            'categories': self._categorize_bookmarks()
        }
        
        report_file = f"bookmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        print(f"レポート保存: {report_file}")
        return report_file
        
    def _categorize_bookmarks(self):
        """ブックマークをカテゴリ分け"""
        categories = defaultdict(int)
        
        for bookmark in self.bookmarks:
            url = bookmark['url'].lower()
            title = bookmark['title'].lower()
            
            if any(word in url or word in title for word in ['github', 'git']):
                categories['開発・プログラミング'] += 1
            elif any(word in url or word in title for word in ['youtube', 'video', '動画']):
                categories['動画・エンターテイメント'] += 1
            elif any(word in url or word in title for word in ['news', 'ニュース', '新聞']):
                categories['ニュース・情報'] += 1
            elif any(word in url or word in title for word in ['shop', 'amazon', '楽天', '購入']):
                categories['ショッピング'] += 1
            elif any(word in url or word in title for word in ['twitter', 'facebook', 'instagram', 'social']):
                categories['SNS・ソーシャル'] += 1
            else:
                categories['その他'] += 1
                
        return dict(categories)
        
    def create_clean_bookmarks(self, remove_duplicates=True, remove_broken=True):
        """クリーンなブックマークHTMLを生成"""
        if not remove_duplicates and not remove_broken:
            print("削除オプションが指定されていません")
            return
            
        indices_to_remove = set()
        
        if remove_duplicates:
            # URL重複の古い方を削除
            for url, indices in self.duplicates['url_duplicates'].items():
                # 最新（最後）のものを残す
                indices_to_remove.update(indices[:-1])
                
        if remove_broken:
            # リンク切れを削除
            indices_to_remove.update([item['index'] for item in self.broken_links])
            
        clean_bookmarks = [bookmark for i, bookmark in enumerate(self.bookmarks) 
                          if i not in indices_to_remove]
        
        clean_file = f"bookmarks_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self._generate_html(clean_bookmarks, clean_file)
        
        print(f"クリーンブックマーク作成: {clean_file}")
        print(f"削除数: {len(indices_to_remove)}")
        print(f"残存数: {len(clean_bookmarks)}")
        
    def _generate_html(self, bookmarks, filename):
        """ブックマークHTMLファイルを生成"""
        html_content = '''<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
'''
        
        folders = defaultdict(list)
        for bookmark in bookmarks:
            folder = bookmark['folder'] or 'その他'
            folders[folder].append(bookmark)
            
        for folder_name, folder_bookmarks in folders.items():
            html_content += f'    <DT><H3 FOLDED>{folder_name}</H3>\n'
            html_content += '    <DL><p>\n'
            
            for bookmark in folder_bookmarks:
                add_date = f' ADD_DATE="{bookmark["add_date"]}"' if bookmark['add_date'] else ''
                html_content += f'        <DT><A HREF="{bookmark["url"]}"{add_date}>{bookmark["title"]}</A>\n'
                
            html_content += '    </DL><p>\n'
            
        html_content += '</DL><p>'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='Chrome ブックマーク整理ツール')
    parser.add_argument('html_file', help='エクスポートしたブックマークHTMLファイル')
    parser.add_argument('--check-links', action='store_true', help='リンク切れチェックを実行')
    parser.add_argument('--remove-duplicates', action='store_true', help='重複を削除')
    parser.add_argument('--remove-broken', action='store_true', help='リンク切れを削除')
    parser.add_argument('--timeout', type=int, default=5, help='リンクチェックタイムアウト（秒）')
    
    args = parser.parse_args()
    
    organizer = ChromeBookmarkOrganizer(args.html_file)
    
    print("ブックマーク解析中...")
    organizer.parse_bookmarks()
    
    print("重複検出中...")
    organizer.find_duplicates()
    
    if args.check_links:
        organizer.check_broken_links(args.timeout)
        
    print("レポート生成中...")
    report_file = organizer.generate_report()
    
    if args.remove_duplicates or args.remove_broken:
        organizer.create_clean_bookmarks(args.remove_duplicates, args.remove_broken)
        
    print(f"\n整理完了！レポート: {report_file}")

if __name__ == "__main__":
    main()