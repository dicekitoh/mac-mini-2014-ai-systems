#!/usr/bin/env python3
import pickle
import os
import sys
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def download_gdrive_file(file_id, output_filename):
    """統合認証システムでGoogle Driveからファイルをダウンロード"""
    
    # 統合認証トークンを読み込み
    token_path = '/home/fujinosuke/google_api/google_api_complete_tokens.pkl'
    
    if not os.path.exists(token_path):
        print("❌ 統合認証トークンが見つかりません")
        return False
    
    try:
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)
        
        if not creds or not creds.valid:
            print("❌ 認証トークンが無効です")
            return False
        
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
        print("使用方法: python3 download_with_integrated_auth.py <file_id> <output_filename>")
        sys.exit(1)
    
    file_id = sys.argv[1]
    output_filename = sys.argv[2]
    
    download_gdrive_file(file_id, output_filename)