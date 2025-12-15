#!/usr/bin/env python3
"""
RTF対応Google Vision OCRスクリプト
RTFファイルを画像に変換してOCR処理を実行
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

class RTFVisionOCR:
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
    
    def is_rtf_file(self, file_path):
        """RTFファイルかどうか判定"""
        return file_path.lower().endswith('.rtf')
    
    def rtf_to_image(self, rtf_path):
        """RTFファイルを画像に変換"""
        try:
            print(f"📄 RTFファイルを読み込み中: {rtf_path}")
            
            # RTFファイルを読み込みテキストに変換
            with open(rtf_path, 'r', encoding='utf-8') as f:
                rtf_content = f.read()
            
            # RTFからプレーンテキストに変換
            plain_text = rtf_to_text(rtf_content)
            
            if not plain_text.strip():
                print("❌ RTFファイルからテキストが抽出できませんでした")
                return None
            
            print(f"✅ テキスト抽出完了 ({len(plain_text)} 文字)")
            
            # テキストを画像に変換
            image = self.text_to_image(plain_text)
            return [image] if image else None
            
        except Exception as e:
            print(f"❌ RTF変換に失敗: {e}")
            return None
    
    def text_to_image(self, text, width=1200, font_size=16):
        """テキストを画像に変換"""
        try:
            # フォント設定
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # テキストを行に分割
            lines = text.split('\n')
            
            # 画像サイズを計算
            line_height = font_size + 4
            height = max(600, len(lines) * line_height + 100)
            
            # 白い背景の画像を作成
            image = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(image)
            
            # テキストを描画
            y_position = 20
            for line in lines:
                if line.strip():  # 空行でない場合
                    # 長い行を折り返し
                    words = line.split(' ')
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        bbox = draw.textbbox((0, 0), test_line, font=font)
                        text_width = bbox[2] - bbox[0]
                        
                        if text_width <= width - 40:  # マージンを考慮
                            current_line = test_line
                        else:
                            # 現在の行を描画
                            if current_line:
                                draw.text((20, y_position), current_line, fill='black', font=font)
                                y_position += line_height
                            current_line = word
                    
                    # 残りのテキストを描画
                    if current_line:
                        draw.text((20, y_position), current_line, fill='black', font=font)
                        y_position += line_height
                else:
                    # 空行
                    y_position += line_height // 2
            
            print(f"✅ テキストを画像に変換完了 ({width}x{height})")
            return image
            
        except Exception as e:
            print(f"❌ テキスト→画像変換に失敗: {e}")
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
        """ファイルを処理（RTF/PDF/画像対応）"""
        if not os.path.exists(file_path):
            print(f"❌ ファイルが見つかりません: {file_path}")
            return None
        
        all_results = []
        
        if self.is_rtf_file(file_path):
            # RTFファイルの処理
            images = self.rtf_to_image(file_path)
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
                        
                        # 結果を表示
                        for title, text in texts:
                            if "テキスト" in title:
                                print(f"📄 OCR結果:")
                                print(text[:300] + "..." if len(text) > 300 else text)
                                print(f"📏 文字数: {len(text)} 文字")
                                break
                    else:
                        print(f"⚠️ テキストが検出されませんでした")
                else:
                    print(f"❌ OCR処理に失敗")
        
        else:
            print("❌ RTFファイルではありません")
            print("対応形式: .rtf")
            return None
        
        return all_results
    
    def save_results(self, results, file_path):
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f"rtf_ocr_result_{Path(file_path).stem}_{timestamp}.txt"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(f"RTF Google Vision OCR結果\n")
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
        print("🔍 RTF Google Vision OCR処理完了")
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
    print("🔍 RTF対応Google Vision OCRシステム")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 rtf_ocr_vision.py <RTFファイル名>")
        return False
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return False
    
    # ファイルタイプを表示
    if file_path.lower().endswith('.rtf'):
        print(f"📄 RTFファイルを処理します: {file_path}")
    else:
        print(f"❌ RTFファイルではありません: {file_path}")
        return False
    
    ocr = RTFVisionOCR()
    results = ocr.process_file(file_path)
    
    if results:
        ocr.display_summary(results, file_path)
        result_file = ocr.save_results(results, file_path)
        print("✅ RTF OCR処理が完了しました")
        return True
    else:
        print("❌ RTF OCR処理に失敗しました")
        return False

if __name__ == "__main__":
    main()