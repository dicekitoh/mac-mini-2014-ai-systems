#!/usr/bin/env python3
"""
Google Drive直接ダウンロード（改良版）
共有設定の問題を回避して画像ファイルを取得
"""

import requests
import os
import sys
from urllib.parse import parse_qs, urlparse

def download_gdrive_direct(file_id):
    """Google Driveから直接ダウンロード（複数手法を試行）"""
    
    methods = [
        f"https://drive.google.com/uc?export=download&id={file_id}",
        f"https://drive.google.com/uc?id={file_id}&export=download",
        f"https://docs.google.com/uc?export=download&id={file_id}",
    ]
    
    for i, url in enumerate(methods, 1):
        print(f"📥 方法{i}: {url[:50]}...")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            
            # レスポンスヘッダーを確認
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            if response.status_code == 200:
                # 画像データかどうか確認
                if 'image' in content_type.lower():
                    output_file = f"gdrive_image_{file_id}.jpg"
                    with open(output_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size = os.path.getsize(output_file)
                    print(f"✅ 画像ダウンロード成功: {output_file} ({file_size} bytes)")
                    return output_file
                    
                elif 'html' in content_type.lower():
                    # HTMLページの場合、共有設定を確認
                    content = response.text[:500]
                    print(f"⚠️ HTMLページを受信。共有設定の確認が必要です。")
                    print(f"内容の一部: {content[:100]}...")
                    
                    # 大きなファイルの場合の確認処理
                    if 'confirm=' in content or 'download_warning' in content:
                        print("📄 大きなファイル用の確認処理を試行中...")
                        # 確認トークンを探す
                        import re
                        confirm_match = re.search(r'confirm=([^&"]+)', content)
                        if confirm_match:
                            confirm_token = confirm_match.group(1)
                            confirm_url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                            confirm_response = requests.get(confirm_url, stream=True)
                            
                            if 'image' in confirm_response.headers.get('content-type', ''):
                                output_file = f"gdrive_confirmed_{file_id}.jpg"
                                with open(output_file, 'wb') as f:
                                    for chunk in confirm_response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                file_size = os.path.getsize(output_file)
                                print(f"✅ 確認後ダウンロード成功: {output_file} ({file_size} bytes)")
                                return output_file
                else:
                    print(f"⚠️ 未知のコンテンツタイプ: {content_type}")
                    
        except Exception as e:
            print(f"❌ 方法{i}失敗: {e}")
            continue
    
    print("❌ 全ての方法でダウンロードに失敗しました")
    return None

def check_file_sharing_status(file_id):
    """ファイルの共有状態を確認"""
    print(f"\n🔍 ファイル共有状態の確認...")
    print(f"ファイルID: {file_id}")
    print(f"共有URL: https://drive.google.com/file/d/{file_id}/view")
    
    # 共有状態確認のリクエスト
    check_url = f"https://drive.google.com/file/d/{file_id}/view"
    try:
        response = requests.get(check_url, timeout=10)
        
        if "Sorry, the file you have requested does not exist" in response.text:
            print("❌ ファイルが存在しません")
            return False
        elif "access denied" in response.text.lower():
            print("❌ アクセス拒否 - 共有設定を確認してください")
            return False
        elif "Request access" in response.text:
            print("❌ アクセス許可が必要です")
            return False
        else:
            print("✅ ファイルにアクセス可能")
            return True
            
    except Exception as e:
        print(f"❌ 共有状態確認エラー: {e}")
        return False

def main():
    """メイン処理"""
    print("🔍 Google Drive 直接ダウンロード（改良版）")
    print("="*60)
    
    file_id = "1kwUhjNDk3hxV1N7vRbAEgtbvx6BZoTxi"
    
    # 共有状態を確認
    if not check_file_sharing_status(file_id):
        print("\n💡 解決方法:")
        print("1. Google Driveでファイルを右クリック")
        print("2. '共有' を選択")
        print("3. '制限付き' を 'リンクを知っている全員' に変更")
        print("4. 'コピー' でリンクを取得")
        return False
    
    # ダウンロードを試行
    downloaded_file = download_gdrive_direct(file_id)
    
    if downloaded_file:
        print(f"\n🎉 ダウンロード成功!")
        print(f"📁 ファイル: {downloaded_file}")
        
        # ファイル種類を確認
        import subprocess
        result = subprocess.run(['file', downloaded_file], capture_output=True, text=True)
        print(f"📋 ファイル種類: {result.stdout.strip()}")
        
        return downloaded_file
    else:
        print("\n❌ ダウンロードに失敗しました")
        print("💡 手動でファイルをダウンロードして、以下のコマンドでOCRテストしてください:")
        print("export GOOGLE_CLOUD_API_KEY='***REMOVED***'")
        print("python3 google_vision_ocr_test.py <ダウンロードしたファイル>")
        return None

if __name__ == "__main__":
    main()