#!/usr/bin/env python3
"""
MacMini2014 Notifier BOT 画像受信 → 自動OCR処理システム
横向き画像の自動回転機能付き
"""

import os
import time
import shutil
from datetime import datetime
from PIL import Image, ImageOps
import subprocess

class OCRFileReceiver:
    def __init__(self):
        self.watch_directory = "/tmp/received_images"  # 受信画像フォルダ
        self.processed_directory = "/tmp/processed_images"  # 処理済みフォルダ
        self.ocr_script_path = "/home/fujinosuke/projects/google_vision_ocr_test.py"
        self.api_key = "***REMOVED***"
        
        # ディレクトリを作成
        os.makedirs(self.watch_directory, exist_ok=True)
        os.makedirs(self.processed_directory, exist_ok=True)
        
        print(f"🔍 OCRファイル受信システム起動")
        print(f"📁 監視フォルダ: {self.watch_directory}")
        print(f"📁 処理済みフォルダ: {self.processed_directory}")
    
    def detect_and_correct_orientation(self, image_path):
        """画像の向きを自動検出して正しい向きに回転"""
        try:
            print(f"📐 画像の向きを確認中: {os.path.basename(image_path)}")
            
            with Image.open(image_path) as img:
                # EXIFデータから回転情報を取得
                img_with_exif = ImageOps.exif_transpose(img)
                
                # 画像の縦横比から向きを判定
                width, height = img_with_exif.size
                aspect_ratio = width / height
                
                print(f"  📊 サイズ: {width}x{height}, 縦横比: {aspect_ratio:.2f}")
                
                # 横向きの可能性が高い場合（縦横比が1.3以上）
                if aspect_ratio > 1.3:
                    print(f"  🔄 横向き画像を検出、90度回転を試行")
                    
                    # 90度ずつ回転して最適な向きを見つける
                    rotations = [0, 90, 180, 270]
                    best_rotation = 0
                    best_ratio = aspect_ratio
                    
                    # 文書の場合、通常は縦長が正しい向き
                    for rotation in rotations:
                        rotated = img_with_exif.rotate(rotation, expand=True)
                        w, h = rotated.size
                        ratio = h / w  # 縦横比（縦÷横）
                        
                        print(f"    {rotation}度回転: {w}x{h}, 縦横比={ratio:.2f}")
                        
                        # 縦長になる回転角度を選択（縦横比1.2以上）
                        if ratio > 1.2 and ratio > best_ratio:
                            best_rotation = rotation
                            best_ratio = ratio
                    
                    if best_rotation != 0:
                        corrected_img = img_with_exif.rotate(best_rotation, expand=True)
                        
                        # 回転後の画像を保存
                        base_name = os.path.splitext(os.path.basename(image_path))[0]
                        corrected_path = os.path.join(
                            os.path.dirname(image_path), 
                            f"rotated_{best_rotation}deg_{base_name}.png"
                        )
                        
                        corrected_img.save(corrected_path, quality=95, optimize=True)
                        print(f"  ✅ 向き修正完了: {best_rotation}度回転 → {corrected_path}")
                        return corrected_path
                    else:
                        print(f"  ℹ️ 回転不要と判定")
                        return image_path
                else:
                    print(f"  ℹ️ 縦向き画像、回転不要")
                    return image_path
                    
        except Exception as e:
            print(f"  ❌ 向き修正エラー: {e}")
            return image_path
    
    def run_ocr_on_image(self, image_path):
        """指定された画像でOCR処理を実行"""
        try:
            print(f"\n🔍 OCR処理開始: {os.path.basename(image_path)}")
            
            # 環境変数を設定
            env = os.environ.copy()
            env['GOOGLE_CLOUD_API_KEY'] = self.api_key
            
            # OCRスクリプトを実行
            result = subprocess.run([
                'python3', self.ocr_script_path, image_path
            ], env=env, capture_output=True, text=True, cwd='/home/fujinosuke/projects')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if result.returncode == 0:
                print(f"✅ OCR処理完了")
                
                # OCR結果を保存
                result_file = f"/tmp/ocr_result_{timestamp}.txt"
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(f"OCR結果 - {image_path}\n")
                    f.write("="*50 + "\n")
                    f.write(f"処理時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*50 + "\n\n")
                    f.write(result.stdout)
                
                print(f"💾 OCR結果保存: {result_file}")
                
                # 成功時の簡潔な結果表示
                if "📄 文書全体テキスト" in result.stdout:
                    lines = result.stdout.split('\n')
                    for i, line in enumerate(lines):
                        if "📄 文書全体テキスト" in line:
                            # 次の数行を表示
                            print(f"\n📋 OCR結果プレビュー:")
                            for j in range(i+2, min(i+10, len(lines))):
                                if lines[j].strip() and not lines[j].startswith('📏'):
                                    print(f"  {lines[j]}")
                            break
                
                return True
            else:
                print(f"❌ OCR処理失敗")
                print(f"エラー: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ OCR実行エラー: {e}")
            return False
    
    def process_new_files(self):
        """新しいファイルを処理"""
        try:
            files = os.listdir(self.watch_directory)
            image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
            
            for image_file in image_files:
                image_path = os.path.join(self.watch_directory, image_file)
                
                print(f"\n📥 新しい画像を発見: {image_file}")
                
                # 画像の向きを自動修正
                corrected_path = self.detect_and_correct_orientation(image_path)
                
                # OCR処理を実行
                success = self.run_ocr_on_image(corrected_path)
                
                # 処理済みフォルダに移動
                processed_path = os.path.join(self.processed_directory, image_file)
                shutil.move(image_path, processed_path)
                
                # 回転画像も移動（元画像と異なる場合）
                if corrected_path != image_path and os.path.exists(corrected_path):
                    corrected_name = os.path.basename(corrected_path)
                    corrected_processed_path = os.path.join(self.processed_directory, corrected_name)
                    shutil.move(corrected_path, corrected_processed_path)
                    print(f"📁 回転画像も移動: {corrected_processed_path}")
                
                print(f"📁 元画像を処理済みフォルダに移動: {processed_path}")
                
                if success:
                    print(f"🎉 {image_file} の処理が完了しました！")
                else:
                    print(f"⚠️ {image_file} の処理に失敗しました")
                
        except Exception as e:
            print(f"❌ ファイル処理エラー: {e}")
    
    def watch_for_files(self, interval=5):
        """ファイル監視ループ"""
        print(f"\n👀 ファイル監視開始（{interval}秒間隔）")
        print(f"画像ファイルを {self.watch_directory} に配置してください")
        
        try:
            while True:
                self.process_new_files()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n⏹️ ファイル監視を停止しました")

def main():
    """メイン処理"""
    print("🔍 MacMini2014 OCR File Receiver")
    print("="*50)
    
    receiver = OCRFileReceiver()
    
    # 使用方法を表示
    print(f"\n📋 使用方法:")
    print(f"1. 画像ファイルを {receiver.watch_directory} に配置")
    print(f"2. 自動的にOCR処理が開始されます")
    print(f"3. 横向きの画像は自動的に回転されます")
    print(f"4. 処理済みファイルは {receiver.processed_directory} に移動")
    
    # ファイル監視開始
    receiver.watch_for_files()

if __name__ == "__main__":
    main()