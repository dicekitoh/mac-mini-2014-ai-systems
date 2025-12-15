#!/usr/bin/env python3
"""
Google Driveの全ファイルをフォルダ構造無視でMacMini2014にダウンロード
"""
import pickle
import os
import requests
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
from urllib.parse import urlparse
import mimetypes

class GoogleDriveFullBackup:
    def __init__(self, token_file='/home/fujinosuke/token_drive.pickle'):
        self.token_file = token_file
        self.service = None
        self.backup_dir = '/home/fujinosuke/google_drive_backup'
        self.download_count = 0
        self.skip_count = 0
        self.error_count = 0
        
        # バックアップディレクトリ作成
        os.makedirs(self.backup_dir, exist_ok=True)
        
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
    
    def get_all_files(self):
        """全てのファイルを再帰的に取得（フォルダ構造無視）"""
        print('📋 Google Drive全ファイル取得中...')
        
        all_files = []
        page_token = None
        
        while True:
            try:
                # 全ファイル取得（ゴミ箱除く）
                results = self.service.files().list(
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, size, parents, createdTime, modifiedTime)",
                    q="trashed = false",
                    pageToken=page_token
                ).execute()
                
                files = results.get('files', [])
                all_files.extend(files)
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
                print(f'  取得済み: {len(all_files)}件')
                
            except Exception as e:
                print(f'❌ ファイル一覧取得エラー: {e}')
                break
        
        # Googleフォルダを除外（ダウンロード可能ファイルのみ）
        downloadable_files = []
        for file in all_files:
            if file.get('mimeType') != 'application/vnd.google-apps.folder':
                downloadable_files.append(file)
        
        print(f'📊 取得結果:')
        print(f'  全ファイル: {len(all_files)}件')
        print(f'  ダウンロード可能: {len(downloadable_files)}件')
        print(f'  フォルダ: {len(all_files) - len(downloadable_files)}件')
        
        return downloadable_files
    
    def safe_filename(self, filename):
        """安全なファイル名に変換"""
        # 危険な文字を置換
        safe_chars = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.', '(', ')', '[', ']'))
        # 重複回避のためタイムスタンプ追加
        name, ext = os.path.splitext(safe_chars)
        timestamp = str(int(time.time()))[-6:]  # 末尾6桁
        return f"{name}_{timestamp}{ext}"
    
    def download_file(self, file_info):
        """単一ファイルをダウンロード"""
        file_id = file_info['id']
        file_name = file_info['name']
        mime_type = file_info.get('mimeType', '')
        file_size = file_info.get('size', 'unknown')
        
        # 安全なファイル名生成
        safe_name = self.safe_filename(file_name)
        local_path = os.path.join(self.backup_dir, safe_name)
        
        try:
            print(f'📥 ダウンロード中: {file_name} ({file_size} bytes)')
            
            # Google Apps形式ファイルの場合はエクスポート
            if mime_type.startswith('application/vnd.google-apps.'):
                export_format = self.get_export_format(mime_type)
                if export_format:
                    request = self.service.files().export_media(fileId=file_id, mimeType=export_format)
                    # ファイル名に適切な拡張子を追加
                    if export_format == 'application/pdf':
                        local_path += '.pdf'
                    elif export_format == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                        local_path += '.xlsx'
                    elif export_format == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        local_path += '.docx'
                    elif export_format == 'text/plain':
                        local_path += '.txt'
                else:
                    print(f'  ⚠️  スキップ（エクスポート不可）: {mime_type}')
                    self.skip_count += 1
                    return False
            else:
                # 通常ファイルのダウンロード
                request = self.service.files().get_media(fileId=file_id)
            
            # ファイルダウンロード実行
            with open(local_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            print(f'  ✅ 完了: {safe_name}')
            self.download_count += 1
            return True
            
        except Exception as e:
            print(f'  ❌ エラー: {e}')
            self.error_count += 1
            return False
    
    def get_export_format(self, mime_type):
        """Google Apps形式に応じたエクスポート形式を返す"""
        export_map = {
            'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Word
            'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Excel
            'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PowerPoint
            'application/vnd.google-apps.drawing': 'application/pdf',  # PDF
            'application/vnd.google-apps.script': 'application/vnd.google-apps.script+json',  # JSON
        }
        return export_map.get(mime_type)
    
    def backup_all_files(self):
        """全ファイルバックアップ実行"""
        print('🚀 Google Drive全ファイルバックアップ開始')
        print(f'📁 保存先: {self.backup_dir}')
        
        # 全ファイル取得
        files = self.get_all_files()
        
        if not files:
            print('ダウンロード可能なファイルがありません')
            return
        
        print(f'\n📥 {len(files)}件のダウンロード開始...')
        
        # MediaIoBaseDownloadをインポート
        try:
            from googleapiclient.http import MediaIoBaseDownload
            globals()['MediaIoBaseDownload'] = MediaIoBaseDownload
        except ImportError:
            print('❌ MediaIoBaseDownloadのインポートに失敗')
            return
        
        # 各ファイルをダウンロード
        for i, file_info in enumerate(files):
            print(f'\n[{i+1}/{len(files)}]', end=' ')
            self.download_file(file_info)
            
            # 進捗表示
            if (i + 1) % 10 == 0:
                print(f'\n📊 進捗: {i+1}/{len(files)} 完了')
        
        # 結果サマリー
        print(f'\n🎉 バックアップ完了!')
        print(f'📊 結果:')
        print(f'  ✅ ダウンロード成功: {self.download_count}件')
        print(f'  ⚠️  スキップ: {self.skip_count}件')
        print(f'  ❌ エラー: {self.error_count}件')
        print(f'📁 保存先: {self.backup_dir}')
        
        # ディスク使用量表示
        import subprocess
        try:
            result = subprocess.run(['du', '-sh', self.backup_dir], capture_output=True, text=True)
            if result.returncode == 0:
                size = result.stdout.split()[0]
                print(f'💾 使用容量: {size}')
        except:
            pass

def main():
    """メイン処理"""
    try:
        backup = GoogleDriveFullBackup()
        backup.backup_all_files()
    except Exception as e:
        print(f'❌ 致命的エラー: {e}')

if __name__ == '__main__':
    main()