#!/usr/bin/env python3
import pickle
import os
import sys
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

def download_gdrive_file(file_id, output_filename):
    """Google Driveからファイルをダウンロード"""
    
    # 既存のトークンを確認
    token_path = 'google_auth/token_drive.pickle'
    creds = None
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # トークンが無効または期限切れの場合は再認証が必要
    if not creds or not creds.valid:
        print("❌ 有効な認証情報がありません")
        print("📝 以下のコマンドで認証を行ってください：")
        print("python3 setup_drive_auth_with_code.py")
        return False
    
    try:
        # Drive APIサービスを構築
        service = build('drive', 'v3', credentials=creds)
        
        # ファイル情報を取得
        print(f"📋 ファイル情報を取得中... (ID: {file_id})")
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', 'unknown')
        mime_type = file_metadata.get('mimeType', 'unknown')
        
        print(f"📄 ファイル名: {file_name}")
        print(f"📋 MIMEタイプ: {mime_type}")
        
        # ファイルをダウンロード
        print(f"📥 ダウンロード中...")
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"  進行状況: {int(status.progress() * 100)}%")
        
        # ファイルに保存
        with open(output_filename, 'wb') as f:
            f.write(fh.getvalue())
        
        print(f"✅ ダウンロード完了: {output_filename}")
        return True
        
    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python3 simple_gdrive_download.py <file_id> <output_filename>")
        sys.exit(1)
    
    file_id = sys.argv[1]
    output_filename = sys.argv[2]
    
    download_gdrive_file(file_id, output_filename)