#!/usr/bin/env python3
"""Google Drive authenticated download script"""

import pickle
import os
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import re

def extract_file_id(url):
    """Extract file ID from Google Drive URL"""
    patterns = [
        r'/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
        r'/file/d/([a-zA-Z0-9-_]+)/view'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_file(file_id):
    """Download file from Google Drive using authentication"""
    # Load credentials
    token_path = 'google_auth/token_drive.pickle'
    
    if not os.path.exists(token_path):
        print(f"❌ 認証トークンが見つかりません: {token_path}")
        return None
    
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    
    # Build the service
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', f'gdrive_file_{file_id}')
        mime_type = file_metadata.get('mimeType', '')
        
        print(f"📄 ファイル名: {file_name}")
        print(f"📋 MIMEタイプ: {mime_type}")
        
        # Download the file
        request = service.files().get_media(fileId=file_id)
        
        output_file = f"fax_document_{file_id}.pdf"
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"📥 ダウンロード進行中: {int(status.progress() * 100)}%")
        
        # Save to file
        with open(output_file, 'wb') as f:
            f.write(fh.getvalue())
        
        print(f"✅ ダウンロード完了: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 download_gdrive_with_auth.py <Google Drive URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    file_id = extract_file_id(url)
    
    if not file_id:
        print(f"❌ URLからファイルIDを抽出できません: {url}")
        sys.exit(1)
    
    print(f"🔍 ファイルID: {file_id}")
    download_file(file_id)