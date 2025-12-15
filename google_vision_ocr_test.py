#!/usr/bin/env python3
"""
Google Cloud Vision API OCRテストスクリプト (高精度版)
既存のGoogle認証システムを使用してVision APIでOCRを実行
"""

import os
import sys
import json
import pickle
import base64
import requests
from pathlib import Path
from datetime import datetime

# Google認証関連
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    print("✅ Google認証ライブラリが利用可能です")
except ImportError as e:
    print(f"❌ Google認証ライブラリが不足: {e}")
    print("必要パッケージ: python3-google-auth python3-googleapi")
    sys.exit(1)

# 必要なスコープ
SCOPES = [
    'https://www.googleapis.com/auth/cloud-vision',
    'https://www.googleapis.com/auth/cloud-platform'
]

class GoogleVisionOCR:
    def __init__(self):
        self.service = None
        self.project_id = "thinksblog-439301"  # プロジェクトIDを設定
        
    def authenticate(self):
        """Google認証を実行"""
        creds = None
        token_path = "/home/fujinosuke/projects/google_auth/unified_google_token.pickle"
        
        # 既存のトークンファイルを確認
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                print(f"✅ 既存の認証トークンを読み込みました: {token_path}")
            except Exception as e:
                print(f"⚠️  既存トークンの読み込みに失敗: {e}")
        
        # トークンが無効または期限切れの場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ トークンを更新しました")
                except Exception as e:
                    print(f"⚠️  トークン更新に失敗: {e}")
                    creds = None
            
            if not creds:
                # 新しい認証が必要
                credentials_path = "/home/fujinosuke/projects/google_auth/credentials.json"
                if not os.path.exists(credentials_path):
                    print(f"❌ 認証情報ファイルが見つかりません: {credentials_path}")
                    print("Google Cloud Consoleからcredentials.jsonをダウンロードしてください")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ 新しい認証を完了しました")
            
            # トークンを保存
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print(f"✅ 認証トークンを保存しました: {token_path}")
            except Exception as e:
                print(f"⚠️  トークン保存に失敗: {e}")
        
        try:
            self.service = build('vision', 'v1', credentials=creds)
            print("✅ Google Cloud Vision API サービスを初期化しました")
            return True
        except Exception as e:
            print(f"❌ Vision APIサービス初期化に失敗: {e}")
            return False
    
    def ocr_from_image(self, image_path):
        """画像ファイルからOCRを実行 (高精度設定)"""
        if not os.path.exists(image_path):
            print(f"❌ 画像ファイルが見つかりません: {image_path}")
            return None
        
        try:
            # 画像をbase64エンコード
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
                encoded_image = base64.b64encode(content).decode('utf-8')
            
            print(f"📷 画像を処理中: {image_path} ({len(content)} bytes)")
            
            # REST API直接呼び出しで高精度OCR
            api_key = self.get_api_key()
            if not api_key:
                print("❌ API KEYが取得できません")
                return None
            
            url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
            
            # 高精度OCRリクエスト
            request_body = {
                'requests': [
                    {
                        'image': {
                            'content': encoded_image
                        },
                        'features': [
                            {
                                'type': 'DOCUMENT_TEXT_DETECTION',
                                'maxResults': 1
                            }
                        ],
                        'imageContext': {
                            'languageHints': ['ja', 'en']  # 日本語・英語の両方をサポート
                        }
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            print("🔍 Google Cloud Vision API で高精度OCR実行中...")
            response = requests.post(url, headers=headers, json=request_body)
            
            if response.status_code == 200:
                result = response.json()
                if 'responses' in result and result['responses']:
                    return result['responses'][0]
                else:
                    print("❌ OCR結果が空です")
                    return None
            else:
                print(f"❌ API呼び出しエラー: {response.status_code}")
                print(f"エラー詳細: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ OCR処理に失敗: {e}")
            return None
    
    def get_api_key(self):
        """API KEYを取得"""
        # 環境変数からAPI KEYを取得
        api_key = os.environ.get('GOOGLE_CLOUD_API_KEY')
        if api_key:
            return api_key
        
        # 既存の認証情報からAPI KEYを取得を試行
        try:
            creds = self.load_credentials()
            if creds and hasattr(creds, 'token'):
                return creds.token
        except:
            pass
        
        # 固定のAPI KEYファイルから読み込み
        api_key_file = '/home/fujinosuke/projects/google_auth/api_key.txt'
        if os.path.exists(api_key_file):
            try:
                with open(api_key_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        print("❌ API KEYが見つかりません")
        print("設定方法:")
        print("1. export GOOGLE_CLOUD_API_KEY='your-api-key'")
        print("2. /home/fujinosuke/projects/google_auth/api_key.txt にAPI KEYを保存")
        return None
    
    def extract_text(self, response):
        """OCRレスポンスからテキストを抽出 (高精度版)"""
        texts = []
        confidence_info = []
        
        # 文書全体のテキスト（最高精度）
        if 'fullTextAnnotation' in response:
            full_text = response['fullTextAnnotation']['text']
            texts.append(("📄 文書全体テキスト (高精度)", full_text))
            
            # 信頼度情報も取得
            if 'pages' in response['fullTextAnnotation']:
                for page in response['fullTextAnnotation']['pages']:
                    if 'confidence' in page:
                        confidence_info.append(f"ページ信頼度: {page['confidence']:.2%}")
        
        # 個別テキスト検出
        if 'textAnnotations' in response:
            main_text = response['textAnnotations'][0]['description'] if response['textAnnotations'] else ""
            if main_text and main_text not in [text[1] for text in texts]:
                texts.append(("🔍 テキスト検出結果", main_text))
        
        # 信頼度情報があれば追加
        if confidence_info:
            texts.append(("📊 信頼度情報", "\n".join(confidence_info)))
        
        return texts
    
    def load_credentials(self):
        """既存の認証情報を読み込み"""
        token_path = "/home/fujinosuke/projects/google_auth/unified_google_token.pickle"
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    return pickle.load(token)
            except:
                pass
        return None
    
    def display_results(self, texts, image_path):
        """結果を表示 (高精度版)"""
        print("\n" + "="*70)
        print("🔍 Google Cloud Vision API - 高精度OCR結果")
        print("="*70)
        print(f"📁 処理ファイル: {image_path}")
        print(f"⏰ 処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        
        for title, text in texts:
            print(f"\n{title}:")
            print("-" * 50)
            print(text)
            if "テキスト" in title:
                print(f"📏 文字数: {len(text)} 文字")
        
        print("\n" + "="*70)
        
        # 結果をファイルに保存（詳細情報付き）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"vision_ocr_result_{Path(image_path).stem}_{timestamp}.txt"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"Google Cloud Vision API - 高精度OCR結果\n")
                f.write("="*50 + "\n")
                f.write(f"処理ファイル: {image_path}\n")
                f.write(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                for title, text in texts:
                    f.write(f"{title}:\n")
                    f.write("-" * 30 + "\n")
                    f.write(text + "\n\n")
            
            print(f"💾 詳細結果を保存しました: {result_file}")
        except Exception as e:
            print(f"⚠️ 結果の保存に失敗: {e}")
            
        return result_file

def main():
    """メイン処理 (高精度版)"""
    print("🔍 Google Cloud Vision API - 高精度OCRシステム")
    print("="*60)
    
    # OCRオブジェクトを作成
    ocr = GoogleVisionOCR()
    
    # テスト画像パスを取得
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if not os.path.exists(image_path):
            print(f"❌ 指定された画像ファイルが見つかりません: {image_path}")
            return False
    else:
        print("使用方法: python3 google_vision_ocr_test.py <画像ファイルパス>")
        print("\n📝 テスト用画像を作成しますか？ (y/n): ", end="")
        try:
            choice = input().lower().strip()
        except:
            choice = 'y'  # デフォルトでy
        
        if choice == 'y':
            image_path = create_test_image()
            if not image_path:
                print("❌ テスト画像の作成に失敗しました")
                return False
        else:
            print("📋 使用例:")
            print("  python3 google_vision_ocr_test.py sample.jpg")
            print("  python3 google_vision_ocr_test.py document.png")
            return False
    
    print(f"\n🚀 高精度OCR処理を開始します...")
    print(f"📁 対象ファイル: {image_path}")
    
    # OCR実行
    response = ocr.ocr_from_image(image_path)
    if response:
        texts = ocr.extract_text(response)
        if texts:
            result_file = ocr.display_results(texts, image_path)
            print(f"\n✅ 高精度OCR処理が完了しました")
            return True
        else:
            print("❌ テキストが検出されませんでした")
            print("💡 ヒント:")
            print("  - 画像の解像度を上げてみてください")
            print("  - テキストが鮮明に見えるか確認してください")
            return False
    else:
        print("❌ OCR処理に失敗しました")
        print("💡 確認事項:")
        print("  - Google Cloud Vision APIのAPI KEYが設定されているか")
        print("  - インターネット接続が正常か")
        print("  - 画像ファイルが破損していないか")
        return False

def create_test_image():
    """テスト用の画像を作成"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # 白い背景の画像を作成
        width, height = 800, 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # テキストを描画
        test_texts = [
            "Google Cloud Vision API OCRテスト",
            "こんにちは世界！",
            "Hello World!",
            "2025年6月15日",
            "テスト用サンプルテキスト",
            "英数字: ABC123 abc456",
            "記号: !@#$%^&*()",
        ]
        
        y_position = 50
        for text in test_texts:
            draw.text((50, y_position), text, fill='black')
            y_position += 60
        
        # 画像を保存
        test_image_path = "test_ocr_image.png"
        image.save(test_image_path)
        print(f"✅ テスト画像を作成しました: {test_image_path}")
        
        # 作成した画像でOCRテスト
        ocr = GoogleVisionOCR()
        if ocr.authenticate():
            response = ocr.ocr_from_image(test_image_path)
            if response:
                texts = ocr.extract_text(response)
                if texts:
                    ocr.display_results(texts)
                    return True
        
        return False
        
    except ImportError:
        print("❌ PIL (Pillow) がインストールされていません")
        print("インストール: pip install pillow")
        return False
    except Exception as e:
        print(f"❌ テスト画像作成に失敗: {e}")
        return False

if __name__ == "__main__":
    main()