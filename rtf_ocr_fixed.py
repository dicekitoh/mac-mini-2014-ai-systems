#!/usr/bin/env python3
"""
文字化け対応RTF OCRスクリプト
エンコーディング検出と日本語フォント対応
"""

import os
import sys
import base64
import requests
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont
from striprtf.striprtf import rtf_to_text
import chardet

class RTFVisionOCRFixed:
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
    
    def detect_encoding(self, file_path):
        """ファイルのエンコーディングを検出"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                print(f"🔍 検出されたエンコーディング: {encoding} (信頼度: {confidence:.2%})")
                return encoding
        except Exception as e:
            print(f"⚠️ エンコーディング検出エラー: {e}")
            return 'utf-8'
    
    def read_rtf_file(self, rtf_path):
        """RTFファイルを複数エンコーディングで試行読み込み"""
        encodings = ['utf-8', 'shift_jis', 'cp932', 'euc-jp', 'iso-2022-jp']
        
        # まず自動検出を試行
        detected_encoding = self.detect_encoding(rtf_path)
        if detected_encoding and detected_encoding not in encodings:
            encodings.insert(0, detected_encoding)
        
        for encoding in encodings:
            try:
                print(f"📄 エンコーディング {encoding} で読み込み試行中...")
                with open(rtf_path, 'r', encoding=encoding) as f:
                    rtf_content = f.read()
                
                # RTFからプレーンテキストに変換
                plain_text = rtf_to_text(rtf_content)
                
                if plain_text.strip():
                    print(f"✅ {encoding} で読み込み成功 ({len(plain_text)} 文字)")
                    return plain_text
                    
            except Exception as e:
                print(f"❌ {encoding} での読み込み失敗: {e}")
                continue
        
        print("❌ すべてのエンコーディングで読み込みに失敗しました")
        return None
    
    def get_japanese_font(self):
        """日本語対応フォントを取得"""
        japanese_fonts = [
            '/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/Windows/Fonts/msgothic.ttc'
        ]
        
        for font_path in japanese_fonts:
            if os.path.exists(font_path):
                print(f"✅ 日本語フォント使用: {font_path}")
                return font_path
        
        print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用")
        return None
    
    def text_to_image_improved(self, text, width=1400, font_size=20):
        """改良されたテキスト→画像変換（日本語対応）"""
        try:
            # フォント設定
            font_path = self.get_japanese_font()
            if font_path:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"✅ フォント読み込み成功: {font_size}px")
                except Exception as e:
                    print(f"⚠️ フォント読み込み失敗: {e}")
                    font = ImageFont.load_default()
            else:
                font = ImageFont.load_default()
            
            # テキストを行に分割
            lines = text.split('\n')
            
            # 画像サイズを計算
            line_height = font_size + 6
            height = max(800, len(lines) * line_height + 100)
            
            # 白い背景の画像を作成
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # テキストを描画
            y_position = 30
            for line in lines:
                if line.strip():  # 空行でない場合
                    # 長い行を文字数で折り返し
                    max_chars = 60  # 1行の最大文字数
                    
                    if len(line) <= max_chars:
                        draw.text((30, y_position), line, fill='black', font=font)
                        y_position += line_height
                    else:
                        # 長い行を分割
                        for i in range(0, len(line), max_chars):
                            chunk = line[i:i+max_chars]
                            draw.text((30, y_position), chunk, fill='black', font=font)
                            y_position += line_height
                else:
                    # 空行
                    y_position += line_height // 2
            
            print(f"✅ テキストを画像に変換完了 ({width}x{height})")
            return image
            
        except Exception as e:
            print(f"❌ テキスト→画像変換に失敗: {e}")
            return None
    
    def rtf_to_image_fixed(self, rtf_path):
        """修正版RTF→画像変換"""
        try:
            print(f"📄 RTFファイルを読み込み中: {rtf_path}")
            
            # エンコーディング対応でRTFを読み込み
            plain_text = self.read_rtf_file(rtf_path)
            
            if not plain_text:
                return None
            
            # 改良された画像変換
            image = self.text_to_image_improved(plain_text)
            return [image] if image else None
            
        except Exception as e:
            print(f"❌ RTF変換に失敗: {e}")
            return None
    
    def ocr_from_image(self, image_data, is_pil_image=False):
        """画像からOCRを実行"""
        if not self.api_key:
            print("❌ API KEYが設定されていません")
            return None
        
        try:
            if is_pil_image:
                import io
                img_byte_arr = io.BytesIO()
                image_data.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')
                file_size = len(img_byte_arr)
            else:
                with open(image_data, 'rb') as image_file:
                    content = image_file.read()
                    encoded_image = base64.b64encode(content).decode('utf-8')
                    file_size = len(content)
            
            print(f"📷 画像を処理中 ({file_size} bytes)")
            
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
            
            if 'pages' in response['fullTextAnnotation']:
                for page in response['fullTextAnnotation']['pages']:
                    if 'confidence' in page:
                        confidence = page['confidence'] * 100
                        texts.append(("📊 信頼度", f"{confidence:.2f}%"))
        
        return texts
    
    def process_file(self, file_path):
        """ファイルを処理"""
        if not os.path.exists(file_path):
            print(f"❌ ファイルが見つかりません: {file_path}")
            return None
        
        all_results = []
        
        if file_path.lower().endswith('.rtf'):
            images = self.rtf_to_image_fixed(file_path)
            if not images:
                return None
            
            print(f"\n📋 RTFファイルを処理中...")
            
            for i, image in enumerate(images, 1):
                print(f"\n--- ページ {i}/{len(images)} ---")
                response = self.ocr_from_image(image, is_pil_image=True)
                
                if response:
                    texts = self.extract_text(response)
                    if texts:
                        all_results.append((f"RTF変換画像 {i}", texts))
                        
                        for title, text in texts:
                            if "テキスト" in title:
                                print(f"📄 OCR結果（最初の500文字）:")
                                print(text[:500] + "..." if len(text) > 500 else text)
                                print(f"📏 文字数: {len(text)} 文字")
                                break
                    else:
                        print(f"⚠️ テキストが検出されませんでした")
                else:
                    print(f"❌ OCR処理に失敗")
        else:
            print("❌ RTFファイルではありません")
            return None
        
        return all_results
    
    def save_results(self, results, file_path):
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"rtf_ocr_fixed_result_{Path(file_path).stem}_{timestamp}.txt"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"RTF Google Vision OCR結果（文字化け修正版）\n")
                f.write("="*60 + "\n")
                f.write(f"ファイル: {file_path}\n")
                f.write(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
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

def main():
    """メイン処理"""
    print("🔍 文字化け対応RTF OCRシステム")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 rtf_ocr_fixed.py <RTFファイル名>")
        return False
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return False
    
    print(f"📄 RTFファイルを処理します: {file_path}")
    
    ocr = RTFVisionOCRFixed()
    results = ocr.process_file(file_path)
    
    if results:
        result_file = ocr.save_results(results, file_path)
        print("✅ 文字化け対応RTF OCR処理が完了しました")
        return True
    else:
        print("❌ RTF OCR処理に失敗しました")
        return False

if __name__ == "__main__":
    main()