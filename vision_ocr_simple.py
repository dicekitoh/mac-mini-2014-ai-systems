#!/usr/bin/env python3
"""
シンプルGoogle Vision OCRテスト (仮想環境対応版)
"""

import os
import sys
import base64
import requests
from datetime import datetime
from pathlib import Path

class SimpleVisionOCR:
    def __init__(self):
        self.api_key = self.get_api_key()
        
    def get_api_key(self):
        """API KEYを取得"""
        # 固定のAPI KEYファイルから読み込み
        api_key_file = '/home/fujinosuke/projects/google_auth/api_key.txt'
        if os.path.exists(api_key_file):
            try:
                with open(api_key_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        print("❌ API KEYが見つかりません")
        return None
    
    def ocr_from_image(self, image_path):
        """画像ファイルからOCRを実行"""
        if not os.path.exists(image_path):
            print(f"❌ 画像ファイルが見つかりません: {image_path}")
            return None
        
        if not self.api_key:
            print("❌ API KEYが設定されていません")
            return None
        
        try:
            # 画像をbase64エンコード
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
                encoded_image = base64.b64encode(content).decode('utf-8')
            
            print(f"📷 画像を処理中: {image_path} ({len(content)} bytes)")
            
            # Vision API呼び出し
            url = f'https://vision.googleapis.com/v1/images:annotate?key={self.api_key}'
            
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
                            'languageHints': ['ja', 'en']
                        }
                    }
                ]
            }
            
            headers = {'Content-Type': 'application/json'}
            
            print("🔍 Google Cloud Vision API でOCR実行中...")
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
    
    def extract_text(self, response):
        """OCRレスポンスからテキストを抽出"""
        texts = []
        
        # 文書全体のテキスト
        if 'fullTextAnnotation' in response:
            full_text = response['fullTextAnnotation']['text']
            texts.append(("📄 検出されたテキスト", full_text))
            
            # 信頼度情報
            if 'pages' in response['fullTextAnnotation']:
                for page in response['fullTextAnnotation']['pages']:
                    if 'confidence' in page:
                        confidence = page['confidence'] * 100
                        texts.append(("📊 信頼度", f"{confidence:.2f}%"))
        
        return texts
    
    def display_and_save_results(self, texts, image_path):
        """結果を表示・保存"""
        print("\n" + "="*50)
        print("🔍 Google Vision OCR結果")
        print("="*50)
        print(f"📁 ファイル: {image_path}")
        print(f"⏰ 処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        for title, text in texts:
            print(f"\n{title}:")
            print(text)
            if "テキスト" in title:
                print(f"📏 文字数: {len(text)} 文字")
        
        print("\n" + "="*50)
        
        # 結果をファイルに保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"vision_ocr_result_{Path(image_path).stem}_{timestamp}.txt"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"Google Vision OCR結果\n")
                f.write("="*30 + "\n")
                f.write(f"ファイル: {image_path}\n")
                f.write(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*30 + "\n\n")
                
                for title, text in texts:
                    f.write(f"{title}:\n")
                    f.write(text + "\n\n")
            
            print(f"💾 結果を保存しました: {result_file}")
        except Exception as e:
            print(f"⚠️ 結果の保存に失敗: {e}")

def main():
    """メイン処理"""
    print("🔍 シンプルGoogle Vision OCRテスト")
    print("="*40)
    
    if len(sys.argv) < 2:
        print("使用方法: python3 vision_ocr_simple.py <画像ファイルパス>")
        return False
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return False
    
    ocr = SimpleVisionOCR()
    response = ocr.ocr_from_image(image_path)
    
    if response:
        texts = ocr.extract_text(response)
        if texts:
            ocr.display_and_save_results(texts, image_path)
            print("✅ OCR処理が完了しました")
            return True
        else:
            print("❌ テキストが検出されませんでした")
            return False
    else:
        print("❌ OCR処理に失敗しました")
        return False

if __name__ == "__main__":
    main()