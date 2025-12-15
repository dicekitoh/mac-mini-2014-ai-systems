#!/usr/bin/env python3
"""
PDF対応Google Vision OCRスクリプト
PDFファイルを画像に変換してOCR処理を実行
"""

import os
import sys
import base64
import requests
from datetime import datetime
from pathlib import Path
import tempfile
from pdf2image import convert_from_path

class PDFVisionOCR:
    def __init__(self):
        self.api_key = self.get_api_key()
        
    def get_api_key(self):
        """API KEYを取得"""
        api_key_file = '/home/fujinosuke/projects/google_auth/api_key.txt'
        if os.path.exists(api_key_file):
            try:
                with open(api_key_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        print("❌ API KEYが見つかりません")
        return None
    
    def is_pdf_file(self, file_path):
        """PDFファイルかどうか判定"""
        return file_path.lower().endswith('.pdf')
    
    def convert_pdf_to_images(self, pdf_path, dpi=300):
        """PDFを画像に変換"""
        try:
            print(f"📄 PDFを画像に変換中: {pdf_path}")
            
            # PDFを画像に変換（高解像度で）
            images = convert_from_path(pdf_path, dpi=dpi)
            
            print(f"✅ {len(images)}ページの画像に変換完了")
            return images
            
        except Exception as e:
            print(f"❌ PDF変換に失敗: {e}")
            return None
    
    def ocr_from_image(self, image_data, is_pil_image=False):
        """画像からOCRを実行"""
        if not self.api_key:
            print("❌ API KEYが設定されていません")
            return None
        
        try:
            # PIL画像の場合はbase64エンコード
            if is_pil_image:
                import io
                img_byte_arr = io.BytesIO()
                image_data.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')
                file_size = len(img_byte_arr)
            else:
                # ファイルパスの場合
                with open(image_data, 'rb') as image_file:
                    content = image_file.read()
                    encoded_image = base64.b64encode(content).decode('utf-8')
                    file_size = len(content)
            
            print(f"📷 画像を処理中 ({file_size} bytes)")
            
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
    
    def process_file(self, file_path):
        """ファイルを処理（PDF/画像対応）"""
        if not os.path.exists(file_path):
            print(f"❌ ファイルが見つかりません: {file_path}")
            return None
        
        all_results = []
        
        if self.is_pdf_file(file_path):
            # PDFファイルの処理
            images = self.convert_pdf_to_images(file_path)
            if not images:
                return None
            
            print(f"\n📋 {len(images)}ページのPDFを処理中...")
            
            for i, image in enumerate(images, 1):
                print(f"\n--- ページ {i}/{len(images)} ---")
                response = self.ocr_from_image(image, is_pil_image=True)
                
                if response:
                    texts = self.extract_text(response)
                    if texts:
                        all_results.append((f"ページ {i}", texts))
                        
                        # 各ページの結果を表示
                        for title, text in texts:
                            if "テキスト" in title:
                                print(f"📄 ページ {i} テキスト:")
                                print(text[:200] + "..." if len(text) > 200 else text)
                                print(f"📏 文字数: {len(text)} 文字")
                                break
                    else:
                        print(f"⚠️ ページ {i}: テキストが検出されませんでした")
                else:
                    print(f"❌ ページ {i}: OCR処理に失敗")
        
        else:
            # 画像ファイルの処理
            response = self.ocr_from_image(file_path)
            if response:
                texts = self.extract_text(response)
                if texts:
                    all_results.append(("画像", texts))
        
        return all_results
    
    def save_results(self, results, file_path):
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"ocr_result_{Path(file_path).stem}_{timestamp}.txt"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"Google Vision OCR結果\n")
                f.write("="*50 + "\n")
                f.write(f"ファイル: {file_path}\n")
                f.write(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                for page_title, texts in results:
                    f.write(f"{page_title}\n")
                    f.write("-" * 30 + "\n")
                    
                    for title, text in texts:
                        f.write(f"{title}:\n")
                        f.write(text + "\n\n")
                    
                    f.write("-" * 50 + "\n\n")
            
            print(f"💾 結果を保存しました: {result_file}")
            return result_file
            
        except Exception as e:
            print(f"⚠️ 結果の保存に失敗: {e}")
            return None
    
    def display_summary(self, results, file_path):
        """結果のサマリーを表示"""
        print("\n" + "="*60)
        print("🔍 Google Vision OCR処理完了")
        print("="*60)
        print(f"📁 ファイル: {file_path}")
        print(f"⏰ 処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_chars = 0
        total_pages = len(results)
        
        for page_title, texts in results:
            for title, text in texts:
                if "テキスト" in title:
                    total_chars += len(text)
        
        print(f"📄 処理ページ数: {total_pages}")
        print(f"📏 総文字数: {total_chars} 文字")
        print("="*60)

def main():
    """メイン処理"""
    print("🔍 PDF対応Google Vision OCRシステム")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 pdf_ocr_vision.py <PDFファイル名>")
        print("  python3 pdf_ocr_vision.py <画像ファイル名>")
        return False
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return False
    
    # ファイルタイプを表示
    if file_path.lower().endswith('.pdf'):
        print(f"📄 PDFファイルを処理します: {file_path}")
    else:
        print(f"🖼️ 画像ファイルを処理します: {file_path}")
    
    ocr = PDFVisionOCR()
    results = ocr.process_file(file_path)
    
    if results:
        ocr.display_summary(results, file_path)
        result_file = ocr.save_results(results, file_path)
        print("✅ OCR処理が完了しました")
        return True
    else:
        print("❌ OCR処理に失敗しました")
        return False

if __name__ == "__main__":
    main()