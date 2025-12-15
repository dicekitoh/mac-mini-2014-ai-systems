#!/usr/bin/env python3
"""
Google Driveファイルダウンロード＋自動回転OCRシステム
横向き書類を自動で正しい向きに直してからOCR処理
"""

import os
import requests
import re
from PIL import Image, ImageOps
import sys
from urllib.parse import urlparse, parse_qs

def extract_file_id_from_url(drive_url):
    """Google Drive URLからファイルIDを抽出"""
    patterns = [
        r'/file/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
        r'/d/([a-zA-Z0-9-_]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, drive_url)
        if match:
            return match.group(1)
    
    return None

def download_gdrive_file(file_id, output_filename):
    """Google Driveファイルをダウンロード"""
    try:
        # Google Driveダウンロード用URL
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        print(f"📥 Google Driveからファイルをダウンロード中...")
        print(f"ファイルID: {file_id}")
        
        # セッションを使用してダウンロード
        session = requests.Session()
        
        response = session.get(download_url, stream=True)
        
        # 大きなファイルの場合の確認ページをスキップ
        if "download_warning" in response.text:
            # 確認トークンを取得
            for line in response.text.split('\n'):
                if 'confirm=' in line:
                    confirm_token = line.split('confirm=')[1].split('&')[0].split('"')[0]
                    download_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                    response = session.get(download_url, stream=True)
                    break
        
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(output_filename)
            print(f"✅ ダウンロード完了: {output_filename} ({file_size} bytes)")
            return True
        else:
            print(f"❌ ダウンロード失敗: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ダウンロードエラー: {e}")
        return False

def detect_and_correct_orientation(image_path):
    """画像の向きを自動検出して正しい向きに回転"""
    try:
        with Image.open(image_path) as img:
            print(f"📐 元画像サイズ: {img.size}")
            
            # EXIFデータから回転情報を取得
            img_with_exif = ImageOps.exif_transpose(img)
            
            # 画像の縦横比から向きを判定
            width, height = img_with_exif.size
            aspect_ratio = width / height
            
            print(f"📊 縦横比: {aspect_ratio:.2f}")
            
            # 横向きの可能性が高い場合（縦横比が1.3以上）
            if aspect_ratio > 1.3:
                print("🔄 横向き画像を検出、90度回転を試行")
                
                # 90度ずつ回転して最適な向きを見つける
                rotations = [0, 90, 180, 270]
                best_rotation = 0
                
                # 文書の場合、通常は縦長が正しい向き
                for rotation in rotations:
                    rotated = img_with_exif.rotate(rotation, expand=True)
                    w, h = rotated.size
                    ratio = h / w  # 縦横比（縦÷横）
                    
                    print(f"  {rotation}度回転: {w}x{h}, 縦横比={ratio:.2f}")
                    
                    # 縦長になる回転角度を選択
                    if ratio > 1.2:  # 縦長
                        best_rotation = rotation
                        break
                
                if best_rotation != 0:
                    corrected_img = img_with_exif.rotate(best_rotation, expand=True)
                    corrected_path = f"corrected_{os.path.basename(image_path)}"
                    corrected_img.save(corrected_path, quality=95, optimize=True)
                    print(f"✅ 向き修正完了: {best_rotation}度回転 → {corrected_path}")
                    return corrected_path
                else:
                    print("ℹ️ 回転不要と判定")
                    return image_path
            else:
                print("ℹ️ 縦向き画像、回転不要")
                return image_path
                
    except Exception as e:
        print(f"❌ 向き修正エラー: {e}")
        return image_path

def run_ocr_on_file(image_path):
    """OCR処理を実行"""
    try:
        print(f"\n🔍 OCR処理を開始: {image_path}")
        
        # 環境変数でAPI KEYを設定してOCR実行
        import subprocess
        
        env = os.environ.copy()
        env['GOOGLE_CLOUD_API_KEY'] = '***REMOVED***'
        
        result = subprocess.run([
            'python3', 'google_vision_ocr_test.py', image_path
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ OCR処理完了")
            print(result.stdout)
            return True
        else:
            print("❌ OCR処理失敗")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ OCR実行エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🔍 Google Drive OCR + 自動回転システム")
    print("="*60)
    
    # Google Drive URLを取得
    if len(sys.argv) > 1:
        drive_url = sys.argv[1]
    else:
        drive_url = "https://drive.google.com/file/d/1kwUhjNDk3hxV1N7vRbAEgtbvx6BZoTxi/view?usp=drive_link"
        print(f"デフォルトURL使用: {drive_url}")
    
    # ファイルIDを抽出
    file_id = extract_file_id_from_url(drive_url)
    if not file_id:
        print("❌ 有効なGoogle Drive URLではありません")
        return False
    
    # ファイルをダウンロード
    output_filename = f"gdrive_document_{file_id}.jpg"
    if not download_gdrive_file(file_id, output_filename):
        return False
    
    # 画像の向きを自動修正
    corrected_path = detect_and_correct_orientation(output_filename)
    
    # OCR処理を実行
    success = run_ocr_on_file(corrected_path)
    
    if success:
        print(f"\n🎉 処理完了!")
        print(f"📁 元ファイル: {output_filename}")
        if corrected_path != output_filename:
            print(f"📁 修正ファイル: {corrected_path}")
        print(f"📄 OCR結果: vision_ocr_result_*.txt")
    
    return success

if __name__ == "__main__":
    main()