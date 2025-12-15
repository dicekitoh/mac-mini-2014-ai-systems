#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Google Drive Manager - Google Drive API連携システム

import logging
import pickle
import os
import io
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Google Drive APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/drive']

class GoogleDriveManager:
    def __init__(self, credentials_file='/home/rootmax/macmini2014_mount/new_credentials.json',
                 token_file='/home/fujinosuke/google_drive.pickle'):
        """Google Drive API管理クラス"""
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._init_google_service()
    
    def _init_google_service(self):
        """Google Drive APIサービスを初期化"""
        creds = None
        
        # トークンファイルが存在する場合は読み込む
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 有効な認証情報がない場合は新規取得
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("トークンの有効期限切れ。リフレッシュ中...")
                creds.refresh(Request())
            else:
                logger.info("新規認証フロー開始...")
                if not os.path.exists(self.credentials_file):
                    logger.error(f"認証ファイルが見つかりません: {self.credentials_file}")
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                
                # ブラウザを使わない認証
                creds = flow.run_local_server(port=0)
                
            # トークンを保存
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("認証成功。トークンを保存しました。")
        
        try:
            service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive API初期化成功")
            return service
        except Exception as e:
            logger.error(f"Google Drive API初期化エラー: {e}")
            return None
    
    def list_files(self, query=None, page_size=10):
        """ファイル一覧を取得"""
        try:
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, createdTime, modifiedTime, size)"
            ).execute()
            
            items = results.get('files', [])
            
            if not items:
                logger.info('ファイルが見つかりませんでした。')
                return []
            else:
                logger.info(f'{len(items)}個のファイルが見つかりました:')
                for item in items:
                    logger.info(f"  {item['name']} ({item['id']})")
                return items
                
        except HttpError as error:
            logger.error(f'エラーが発生しました: {error}')
            return []
    
    def search_files(self, name):
        """ファイル名で検索"""
        query = f"name contains '{name}'"
        return self.list_files(query=query)
    
    def download_file(self, file_id, file_name=None):
        """ファイルをダウンロード"""
        try:
            # ファイル情報を取得
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            if not file_name:
                file_name = file_metadata['name']
            
            # ファイルをダウンロード
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.info(f"ダウンロード進行状況: {int(status.progress() * 100)}%")
            
            # ファイルを保存
            with open(file_name, 'wb') as f:
                f.write(file.getvalue())
            
            logger.info(f"ファイル '{file_name}' のダウンロードが完了しました。")
            return True
            
        except HttpError as error:
            logger.error(f'ダウンロードエラー: {error}')
            return False
    
    def upload_file(self, file_path, folder_id=None):
        """ファイルをアップロード"""
        try:
            file_name = os.path.basename(file_path)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"ファイル '{file_name}' のアップロードが完了しました。ID: {file.get('id')}")
            return file.get('id')
            
        except HttpError as error:
            logger.error(f'アップロードエラー: {error}')
            return None
    
    def create_folder(self, folder_name, parent_id=None):
        """フォルダを作成"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"フォルダ '{folder_name}' を作成しました。ID: {folder.get('id')}")
            return folder.get('id')
            
        except HttpError as error:
            logger.error(f'フォルダ作成エラー: {error}')
            return None

def main():
    """メイン関数"""
    import sys
    
    manager = GoogleDriveManager()
    
    if not manager.service:
        logger.error("Google Drive APIの初期化に失敗しました。")
        return
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python google_drive_manager.py list                    - ファイル一覧")
        print("  python google_drive_manager.py search <name>           - ファイル検索")
        print("  python google_drive_manager.py download <file_id>      - ダウンロード")
        print("  python google_drive_manager.py upload <file_path>      - アップロード")
        print("  python google_drive_manager.py create_folder <name>    - フォルダ作成")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        manager.list_files()
    
    elif command == "search" and len(sys.argv) > 2:
        manager.search_files(sys.argv[2])
    
    elif command == "download" and len(sys.argv) > 2:
        file_id = sys.argv[2]
        file_name = sys.argv[3] if len(sys.argv) > 3 else None
        manager.download_file(file_id, file_name)
    
    elif command == "upload" and len(sys.argv) > 2:
        manager.upload_file(sys.argv[2])
    
    elif command == "create_folder" and len(sys.argv) > 2:
        manager.create_folder(sys.argv[2])
    
    else:
        print("無効なコマンドです。")

if __name__ == "__main__":
    main()