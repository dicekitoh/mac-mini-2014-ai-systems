#!/usr/bin/env python3
"""
Google Cloud Vision API セットアップ支援スクリプト
"""

import os
import json

def setup_vision_api():
    """Vision API の設定を行う"""
    print("🔧 Google Cloud Vision API セットアップ")
    print("="*50)
    
    # Google Cloud プロジェクト情報
    print("\n📋 Google Cloud プロジェクト情報:")
    print("プロジェクト名: thinksblog")
    print("プロジェクトID: thinksblog-439301")
    
    # API KEY設定
    print("\n🔑 API KEY設定:")
    print("Google Cloud ConsoleからVision APIのAPI KEYを取得してください")
    print("https://console.cloud.google.com/apis/credentials")
    
    api_key = input("\nAPI KEYを入力してください (またはEnterでスキップ): ").strip()
    
    if api_key:
        # API KEYをファイルに保存
        api_key_file = "/home/fujinosuke/projects/google_auth/api_key.txt"
        try:
            with open(api_key_file, 'w') as f:
                f.write(api_key)
            print(f"✅ API KEYを保存しました: {api_key_file}")
            
            # 環境変数設定用のスクリプトも作成
            env_script = "/home/fujinosuke/projects/google_auth/set_vision_api_key.sh"
            with open(env_script, 'w') as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"export GOOGLE_CLOUD_API_KEY='{api_key}'\n")
                f.write(f"echo 'Google Cloud Vision API KEY設定完了'\n")
            
            os.chmod(env_script, 0o755)
            print(f"✅ 環境変数設定スクリプトを作成: {env_script}")
            print(f"   使用方法: source {env_script}")
            
            return True
            
        except Exception as e:
            print(f"❌ API KEYの保存に失敗: {e}")
            return False
    else:
        print("⚠️  API KEYが設定されていません")
        print("💡 後で設定する場合:")
        print("   1. echo 'YOUR_API_KEY' > /home/fujinosuke/projects/google_auth/api_key.txt")
        print("   2. export GOOGLE_CLOUD_API_KEY='YOUR_API_KEY'")
        return False

def test_vision_api():
    """Vision API の接続テスト"""
    import requests
    
    # API KEYを取得
    api_key = None
    
    # ファイルから取得
    api_key_file = "/home/fujinosuke/projects/google_auth/api_key.txt"
    if os.path.exists(api_key_file):
        try:
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
        except:
            pass
    
    # 環境変数から取得
    if not api_key:
        api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
    
    if not api_key:
        print("❌ API KEYが設定されていません")
        return False
    
    print("\n🔍 Vision API 接続テスト中...")
    
    # シンプルなAPI呼び出しテスト
    url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
    
    # 小さなテスト画像（1x1 白いピクセル）
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    request_body = {
        'requests': [
            {
                'image': {
                    'content': test_image_b64
                },
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=request_body, timeout=10)
        
        if response.status_code == 200:
            print("✅ Vision API 接続成功")
            return True
        elif response.status_code == 403:
            print("❌ API KEYが無効または権限がありません")
            print(f"   詳細: {response.text}")
            return False
        else:
            print(f"❌ API呼び出しエラー: {response.status_code}")
            print(f"   詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 接続テストに失敗: {e}")
        return False

def main():
    """メイン処理"""
    setup_success = setup_vision_api()
    
    if setup_success:
        print("\n" + "="*50)
        test_vision_api()
    
    print("\n📝 次のステップ:")
    print("1. python3 google_vision_ocr_test.py でOCRテストを実行")
    print("2. 画像ファイルを指定してOCR処理を試す")
    print("3. テスト用画像の自動生成も利用可能")

if __name__ == "__main__":
    main()