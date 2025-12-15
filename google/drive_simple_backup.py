#!/usr/bin/env python3
"""
Google Drive全ファイル一括バックアップ（シンプル版）
Rから始まるソフト不使用・Python標準ライブラリのみ
"""
import pickle
import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import time
import io

class SimpleDriveBackup:
    def __init__(self):
        self.token_file = '/home/fujinosuke/token_drive.pickle'
        self.backup_dir = '/home/fujinosuke/drive_simple_backup'
        self.service = None
        self.stats = {
            'downloaded': 0,
            'skipped': 0,
            'errors': 0,
            'total_size': 0
        }
        
        # バックアップディレクトリ作成
        os.makedirs(self.backup_dir, exist_ok=True)
        print(f'📁 バックアップ先: {self.backup_dir}')
        
        self.authenticate()
    
    def authenticate(self):
        """Google Drive認証"""
        try:
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            print('✅ Google Drive認証成功')
            
        except Exception as e:
            print(f'❌ 認証エラー: {e}')
            raise
    
    def get_all_files_recursive(self, folder_id='root', path_prefix=''):
        """フォルダを再帰的に探索して全ファイルを取得"""
        all_files = []
        
        try:
            # 現在のフォルダ内のアイテムを取得
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                pageSize=1000,
                fields="files(id, name, mimeType, size, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            for item in items:
                item_name = item['name']
                
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    # フォルダの場合は再帰的に探索
                    print(f'📁 フォルダ探索: {path_prefix}{item_name}/')
                    subfolder_files = self.get_all_files_recursive(
                        item['id'], 
                        f"{path_prefix}{item_name}/"
                    )
                    all_files.extend(subfolder_files)
                else:
                    # ファイルの場合はリストに追加
                    item['flat_name'] = f"{path_prefix}{item_name}"
                    all_files.append(item)
            
        except Exception as e:
            print(f'❌ フォルダ探索エラー: {e}')
        
        return all_files
    
    def safe_filename(self, original_name):
        """安全なファイル名を生成"""
        # 危険な文字を除去・置換
        safe_name = "".join(c for c in original_name if c.isalnum() or c in (' ', '-', '_', '.', '(', ')'))
        
        # 重複防止用タイムスタンプ
        timestamp = str(int(time.time()))[-6:]
        name, ext = os.path.splitext(safe_name)
        
        return f"{name}_{timestamp}{ext}"
    
    def download_regular_file(self, file_info):
        """通常ファイルのダウンロード"""
        file_id = file_info['id']
        original_name = file_info['name']
        file_size = int(file_info.get('size', 0))
        
        safe_name = self.safe_filename(original_name)
        local_path = os.path.join(self.backup_dir, safe_name)
        
        try:
            print(f'📥 ダウンロード: {original_name} ({file_size:,} bytes)')
            
            # ファイルダウンロード実行
            request = self.service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        percent = int(status.progress() * 100)
                        if percent % 25 == 0:  # 25%刻みで進捗表示
                            print(f'  進捗: {percent}%')
            
            # 実際のファイルサイズ確認
            actual_size = os.path.getsize(local_path)
            print(f'  ✅ 完了: {safe_name} ({actual_size:,} bytes)')
            
            self.stats['downloaded'] += 1
            self.stats['total_size'] += actual_size
            return True
            
        except Exception as e:
            print(f'  ❌ エラー: {e}')
            self.stats['errors'] += 1
            return False
    
    def export_google_apps_file(self, file_info):
        """Google Apps形式ファイルのエクスポート"""
        file_id = file_info['id']
        original_name = file_info['name']
        mime_type = file_info['mimeType']
        
        # エクスポート形式マッピング
        export_formats = {
            'application/vnd.google-apps.document': ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx'),
            'application/vnd.google-apps.spreadsheet': ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),
            'application/vnd.google-apps.presentation': ('application/vnd.openxmlformats-officedocument.presentationml.presentation', '.pptx'),
            'application/vnd.google-apps.drawing': ('application/pdf', '.pdf'),
        }
        
        if mime_type not in export_formats:
            print(f'  ⚠️  スキップ（エクスポート不可）: {mime_type}')
            self.stats['skipped'] += 1
            return False
        
        export_mime, ext = export_formats[mime_type]
        safe_name = self.safe_filename(original_name) + ext
        local_path = os.path.join(self.backup_dir, safe_name)
        
        try:
            print(f'📤 エクスポート: {original_name} → {ext}形式')
            
            request = self.service.files().export_media(fileId=file_id, mimeType=export_mime)
            
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            file_size = os.path.getsize(local_path)
            print(f'  ✅ 完了: {safe_name} ({file_size:,} bytes)')
            
            self.stats['downloaded'] += 1
            self.stats['total_size'] += file_size
            return True
            
        except Exception as e:
            print(f'  ❌ エラー: {e}')
            self.stats['errors'] += 1
            return False
    
    def backup_all_files(self):
        """全ファイルバックアップメイン処理"""
        print('🚀 Google Drive全ファイルバックアップ開始')
        print('📋 全フォルダを探索してファイル一覧を作成中...')
        
        # 全ファイルを再帰的に取得
        all_files = self.get_all_files_recursive()
        
        if not all_files:
            print('❌ ダウンロード可能なファイルが見つかりません')
            return
        
        print(f'\n📊 発見されたファイル: {len(all_files)}件')
        
        # ファイルタイプ別に分類
        regular_files = []
        google_apps_files = []
        
        for file_info in all_files:
            mime_type = file_info.get('mimeType', '')
            if mime_type.startswith('application/vnd.google-apps.'):
                google_apps_files.append(file_info)
            else:
                regular_files.append(file_info)
        
        print(f'  📄 通常ファイル: {len(regular_files)}件')
        print(f'  📋 Google Apps: {len(google_apps_files)}件')
        
        # バックアップ実行
        print(f'\n📥 ダウンロード開始...')
        
        # 通常ファイルをダウンロード
        for i, file_info in enumerate(regular_files):
            print(f'\n[{i+1}/{len(regular_files)}] 通常ファイル:')
            self.download_regular_file(file_info)
        
        # Google Appsファイルをエクスポート
        for i, file_info in enumerate(google_apps_files):
            print(f'\n[{i+1}/{len(google_apps_files)}] Google Apps:')
            self.export_google_apps_file(file_info)
        
        # 結果表示
        self.show_summary()
    
    def show_summary(self):
        """バックアップ結果サマリー表示"""
        print(f'\n🎉 バックアップ完了!')
        print(f'📊 結果サマリー:')
        print(f'  ✅ ダウンロード成功: {self.stats["downloaded"]}件')
        print(f'  ⚠️  スキップ: {self.stats["skipped"]}件')
        print(f'  ❌ エラー: {self.stats["errors"]}件')
        
        # 合計サイズを人間が読みやすい形式で表示
        total_mb = self.stats['total_size'] / (1024 * 1024)
        if total_mb > 1024:
            print(f'  💾 合計サイズ: {total_mb/1024:.2f} GB')
        else:
            print(f'  💾 合計サイズ: {total_mb:.2f} MB')
        
        print(f'📁 保存先: {self.backup_dir}')
        
        # ディレクトリ内容確認
        try:
            files = os.listdir(self.backup_dir)
            print(f'📄 保存ファイル数: {len(files)}件')
        except:
            pass

def main():
    """メイン実行"""
    try:
        backup = SimpleDriveBackup()
        backup.backup_all_files()
        
        print('\n✅ Google Drive全ファイルバックアップ完了！')
        print('フォルダ構造を無視して全ファイルを1箇所にコピーしました。')
        
    except KeyboardInterrupt:
        print('\n⚠️  ユーザーによって中断されました')
    except Exception as e:
        print(f'\n❌ 致命的エラー: {e}')

if __name__ == '__main__':
    main()