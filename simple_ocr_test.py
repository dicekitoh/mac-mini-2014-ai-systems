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

def create_test_image():
    """テスト用の画像を作成 (ImageMagickを使用)"""
    try:
        # ImageMagickでテスト画像を作成
        test_image = "test_ocr_simple.png"
        text_content = [
            "Google OCR Test",
            "こんにちは世界",
            "Hello World!",
            "2025年6月15日",
            "Sample Text OCR",
            "ABC123 xyz789"
        ]
        
        # ImageMagickコマンドを構築
        cmd = [
            'convert',
            '-size', '800x600',
            'xc:white',
            '-font', 'DejaVu-Sans',
            '-pointsize', '24',
            '-fill', 'black'
        ]
        
        # テキストを追加
        y_pos = 80
        for text in text_content:
            cmd.extend(['-annotate', f'+50+{y_pos}', text])
            y_pos += 60
        
        cmd.append(test_image)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(test_image):
            print(f"✅ テスト画像を作成しました: {test_image}")
            return test_image
        else:
            print("❌ ImageMagickでの画像作成に失敗")
            print("インストール方法: sudo apt install imagemagick")
            return None
            
    except FileNotFoundError:
        print("❌ ImageMagick (convert) が見つかりません")
        return None

def ocr_with_tesseract(image_path, language='eng+jpn'):
    """TesseractでOCRを実行"""
    if not os.path.exists(image_path):
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return None
    
    try:
        # Tesseract OCRを実行
        cmd = ['tesseract', image_path, 'stdout', '-l', language]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            text = result.stdout.strip()
            if text:
                print(f"✅ OCR処理が完了しました")
                return text
            else:
                print("⚠️  テキストが検出されませんでした")
                return ""
        else:
            print(f"❌ OCR処理に失敗: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ OCR実行エラー: {e}")
        return None

def display_results(text, image_path):
    """結果を表示"""
    print("\n" + "="*60)
    print("📝 OCR結果")
    print("="*60)
    print(f"画像ファイル: {image_path}")
    print("-" * 40)
    print(text)
    print("\n" + "="*60)
    
    # 結果をファイルに保存
    result_file = f"ocr_result_{Path(image_path).stem}.txt"
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"OCR結果 - {image_path}\n")
            f.write("="*40 + "\n")
            f.write(text)
        print(f"✅ 結果を保存しました: {result_file}")
    except Exception as e:
        print(f"⚠️  結果の保存に失敗: {e}")

def main():
    """メイン処理"""
    print("🔍 シンプルOCRテスト (Tesseract)")
    print("="*50)
    
    # Tesseractの確認
    if not check_tesseract():
        return False
    
    # テスト画像パスを取得
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if not os.path.exists(image_path):
            print(f"❌ 指定された画像ファイルが見つかりません: {image_path}")
            return False
    else:
        print("テスト画像を作成しますか？ (y/n): ", end="")
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
            print("使用方法: python3 simple_ocr_test.py <画像ファイルパス>")
            return False
    
    print(f"📷 画像を処理中: {image_path}")
    
    # OCR実行
    text = ocr_with_tesseract(image_path)
    if text is not None:
        display_results(text, image_path)
        return True
    else:
        print("❌ OCR処理に失敗しました")
        return False

if __name__ == "__main__":
    main()