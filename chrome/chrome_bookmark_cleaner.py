#!/usr/bin/env python3
"""
Chrome ブックマーククリーナー
・リンク切れブックマークの削除
・1年以上未アクセスのブックマークの検出・削除
・クリーンなブックマークファイルの生成
"""

import json
import urllib.request
import shutil
from datetime import datetime, timedelta
from collections import defaultdict
import os

class ChromeBookmarkCleaner:
    def __init__(self, json_file=None):
        if json_file is None:
            # Windows Chrome のデフォルトパス（WSL経由）
            self.json_file = "/mnt/c/Users/itoh/AppData/Local/Google/Chrome/User Data/Default/Bookmarks"
        else:
            self.json_file = json_file
            
        self.backup_file = f"{self.json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bookmarks = []
        self.broken_links = []
        self.old_bookmarks = []
        self.removed_count = 0
        
        # Chrome時刻の基準（1601年1月1日からのマイクロ秒）
        self.chrome_epoch = datetime(1601, 1, 1)
        
    def chrome_time_to_datetime(self, chrome_time):
        """Chrome時刻をdatetimeに変換"""
        if not chrome_time or chrome_time == '0':
            return None
        try:
            # マイクロ秒を秒に変換してdatetimeに加算
            microseconds = int(chrome_time)
            return self.chrome_epoch + timedelta(microseconds=microseconds)
        except (ValueError, OverflowError):
            return None
    
    def parse_bookmarks(self):
        """Chromeブックマークファイルを解析"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.bookmark_data = json.load(f)
        except Exception as e:
            print(f"❌ ファイル読み込みエラー: {e}")
            return False
            
        self._extract_bookmarks(self.bookmark_data['roots'], "")
        print(f"📊 総ブックマーク数: {len(self.bookmarks)}")
        return True
        
    def _extract_bookmarks(self, node, folder_path):
        """再帰的にブックマークを抽出"""
        if isinstance(node, dict):
            if node.get('type') == 'url':
                # 最終アクセス日時を計算
                last_used = node.get('date_last_used', '0')
                last_used_dt = self.chrome_time_to_datetime(last_used)
                
                bookmark = {
                    'url': node.get('url', ''),
                    'name': node.get('name', ''),
                    'folder': folder_path,
                    'date_added': node.get('date_added', ''),
                    'date_last_used': last_used,
                    'last_used_datetime': last_used_dt,
                    'guid': node.get('guid', ''),
                    'node_ref': node  # 削除用の参照
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
    
    def find_broken_links(self, max_check=100, timeout=3):
        """リンク切れを検出"""
        print(f"🔍 リンク切れチェック中（最大{max_check}件）...")
        
        http_bookmarks = [(i, b) for i, b in enumerate(self.bookmarks) 
                         if b['url'].startswith(('http://', 'https://'))]
        
        check_count = min(len(http_bookmarks), max_check)
        
        for idx, (i, bookmark) in enumerate(http_bookmarks[:check_count]):
            if idx % 20 == 0:
                print(f"  進行状況: {idx}/{check_count}")
                
            try:
                request = urllib.request.Request(bookmark['url'])
                request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    if response.getcode() >= 400:
                        self.broken_links.append({
                            'index': i,
                            'bookmark': bookmark,
                            'error': f"HTTP {response.getcode()}"
                        })
                        
            except Exception as e:
                self.broken_links.append({
                    'index': i,
                    'bookmark': bookmark,
                    'error': str(e)[:100]
                })
                
        print(f"❌ リンク切れ発見: {len(self.broken_links)}件")
    
    def find_old_bookmarks(self, months=12):
        """指定期間以上未アクセスのブックマークを検出"""
        print(f"📅 {months}ヶ月以上未アクセスのブックマーク検出中...")
        
        cutoff_date = datetime.now() - timedelta(days=months*30)
        
        for i, bookmark in enumerate(self.bookmarks):
            last_used = bookmark['last_used_datetime']
            
            # 一度もアクセスしていない、または指定期間以上前
            if last_used is None or last_used < cutoff_date:
                self.old_bookmarks.append({
                    'index': i,
                    'bookmark': bookmark,
                    'last_used': last_used,
                    'reason': '未アクセス' if last_used is None else f'{months}ヶ月以上前'
                })
                
        print(f"⏰ {months}ヶ月以上未アクセス: {len(self.old_bookmarks)}件")
    
    def display_cleanup_targets(self):
        """削除対象の詳細表示"""
        print("\n" + "="*80)
        print("🗑️  削除対象ブックマーク一覧")
        print("="*80)
        
        # リンク切れ
        if self.broken_links:
            print(f"\n❌ リンク切れ ({len(self.broken_links)}件):")
            print("-" * 60)
            for idx, item in enumerate(self.broken_links[:10], 1):  # 最大10件表示
                bookmark = item['bookmark']
                print(f"{idx:2d}. 【{bookmark['name']}】")
                print(f"     📂 {bookmark['folder']}")
                print(f"     🔗 {bookmark['url'][:80]}...")
                print(f"     ❌ {item['error']}")
                print()
            
            if len(self.broken_links) > 10:
                print(f"     ... 他{len(self.broken_links)-10}件")
                
        # 古いブックマーク
        if self.old_bookmarks:
            print(f"\n⏰ 1年以上未アクセス ({len(self.old_bookmarks)}件):")
            print("-" * 60)
            
            # 最終アクセス日でソート
            sorted_old = sorted(self.old_bookmarks, 
                              key=lambda x: x['last_used'] or datetime.min)
            
            for idx, item in enumerate(sorted_old[:15], 1):  # 最大15件表示
                bookmark = item['bookmark']
                last_used = item['last_used']
                last_used_str = last_used.strftime('%Y-%m-%d') if last_used else '未アクセス'
                
                print(f"{idx:2d}. 【{bookmark['name']}】")
                print(f"     📂 {bookmark['folder']}")
                print(f"     🔗 {bookmark['url'][:80]}...")
                print(f"     📅 最終アクセス: {last_used_str}")
                print()
                
            if len(self.old_bookmarks) > 15:
                print(f"     ... 他{len(self.old_bookmarks)-15}件")
    
    def create_backup(self):
        """バックアップファイル作成"""
        try:
            shutil.copy2(self.json_file, self.backup_file)
            print(f"💾 バックアップ作成: {self.backup_file}")
            return True
        except Exception as e:
            print(f"❌ バックアップ作成失敗: {e}")
            return False
    
    def remove_bookmarks(self, remove_broken=True, remove_old=True):
        """ブックマーク削除実行"""
        if not remove_broken and not remove_old:
            print("削除オプションが指定されていません")
            return False
            
        # バックアップ作成
        if not self.create_backup():
            return False
            
        print("\n🗑️  ブックマーク削除実行中...")
        
        # 削除対象のGUIDを収集
        guids_to_remove = set()
        
        if remove_broken:
            for item in self.broken_links:
                guids_to_remove.add(item['bookmark']['guid'])
                
        if remove_old:
            for item in self.old_bookmarks:
                guids_to_remove.add(item['bookmark']['guid'])
        
        # 削除実行
        self.removed_count = self._remove_bookmarks_recursive(self.bookmark_data['roots'], guids_to_remove)
        
        # ファイル保存
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmark_data, f, ensure_ascii=False, indent=3)
            
            print(f"✅ 削除完了: {self.removed_count}件のブックマークを削除")
            print(f"💾 更新されたファイル: {self.json_file}")
            print(f"🔄 バックアップ: {self.backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
            return False
    
    def _remove_bookmarks_recursive(self, node, guids_to_remove):
        """再帰的にブックマークを削除"""
        removed_count = 0
        
        if isinstance(node, dict):
            if 'children' in node:
                # 子要素のリストから削除対象を除外
                original_children = node['children'][:]
                node['children'] = []
                
                for child in original_children:
                    if child.get('type') == 'url' and child.get('guid') in guids_to_remove:
                        removed_count += 1
                        continue  # 削除対象はスキップ
                    else:
                        node['children'].append(child)
                        # フォルダの場合は再帰的に処理
                        if child.get('type') == 'folder':
                            removed_count += self._remove_bookmarks_recursive(child, guids_to_remove)
        
        # 特別なキー処理
        for key in ['bookmark_bar', 'other', 'synced']:
            if key in node:
                removed_count += self._remove_bookmarks_recursive(node[key], guids_to_remove)
                
        return removed_count
    
    def generate_summary(self):
        """削除サマリー生成"""
        summary = {
            'cleanup_date': datetime.now().isoformat(),
            'original_count': len(self.bookmarks),
            'broken_links': len(self.broken_links),
            'old_bookmarks': len(self.old_bookmarks),
            'total_removed': self.removed_count,
            'remaining_count': len(self.bookmarks) - self.removed_count,
            'backup_file': self.backup_file
        }
        
        summary_file = f"bookmark_cleanup_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        print(f"📄 サマリー保存: {summary_file}")
        return summary_file

def main():
    print("🧹 Chrome ブックマーククリーナー")
    print("=" * 60)
    
    cleaner = ChromeBookmarkCleaner()
    
    # ブックマーク解析
    if not cleaner.parse_bookmarks():
        return
    
    # リンク切れ検出
    cleaner.find_broken_links()
    
    # 古いブックマーク検出
    cleaner.find_old_bookmarks(months=12)
    
    # 削除対象表示
    cleaner.display_cleanup_targets()
    
    # 削除確認
    total_targets = len(cleaner.broken_links) + len(cleaner.old_bookmarks)
    if total_targets == 0:
        print("\n✨ 削除対象のブックマークはありません！")
        return
    
    print(f"\n📊 削除対象合計: {total_targets}件")
    print("   • リンク切れ:", len(cleaner.broken_links), "件")
    print("   • 1年以上未アクセス:", len(cleaner.old_bookmarks), "件")
    
    # 自動実行（確認なし）
    print(f"\n🗑️  削除を実行します...")
    
    # 削除実行
    if cleaner.remove_bookmarks(remove_broken=True, remove_old=True):
        cleaner.generate_summary()
        print(f"\n✅ クリーンアップ完了！")
        print(f"📈 削除前: {len(cleaner.bookmarks)}件")
        print(f"📉 削除後: {len(cleaner.bookmarks) - cleaner.removed_count}件")
        print(f"\n🔄 Chromeを再起動してブックマークを確認してください")
    else:
        print(f"\n❌ クリーンアップに失敗しました")

if __name__ == "__main__":
    main()