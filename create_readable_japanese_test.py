#!/usr/bin/env python3
"""
より読みやすい日本語OCRテスト画像作成
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_readable_japanese_test():
    """読みやすい日本語テスト画像を作成"""
    
    # より大きなサイズで高解像度
    width, height = 1200, 900
    
    # 白い背景
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # シンプルで読みやすいテキスト
    test_texts = [
        "スザンヌ ヘキサゴン やらせ 告白",
        "上沼恵美子 今やったら アウトやな",
        "",
        "日本語OCRテスト",
        "ひらがな: あいうえお かきくけこ",
        "カタカナ: アイウエオ カキクケコ", 
        "漢字: 日本語 文字認識 技術",
        "",
        "English: Hello World 123",
        "数字: 2025年6月15日",
        "記号: !@#$%^&*()",
        "",
        "固有名詞テスト:",
        "・スザンヌ",
        "・ヘキサゴン",
        "・上沼恵美子",
        "・バラエティ番組",
        "",
        "複雑な文:",
        "「実は台本があったんです」",
        "『でも楽しくやってました』",
        "※今やったらアウトやな※"
    ]
    
    # より大きく明確なフォント
    try:
        # システムフォントを使用
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        print("✅ システムフォントを使用")
    except:
        # デフォルトフォント
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        print("⚠️ デフォルトフォントを使用")
    
    # テキストを描画（行間を広く）
    y_position = 40
    
    for i, text in enumerate(test_texts):
        if text.strip():
            if i < 2:  # 最初の2行はタイトル
                draw.text((50, y_position), text, fill='darkblue', font=font_title)
                y_position += 40
            elif text.startswith("・"):
                # リスト項目
                draw.text((80, y_position), text, fill='darkgreen', font=font_normal)
                y_position += 35
            elif text.startswith("「") or text.startswith("『") or text.startswith("※"):
                # 特殊な文
                draw.text((50, y_position), text, fill='purple', font=font_normal)
                y_position += 35
            else:
                # 通常テキスト
                draw.text((50, y_position), text, fill='black', font=font_normal)
                y_position += 35
        else:
            y_position += 20  # 空行
    
    # 見やすい枠線
    draw.rectangle([20, 20, width-20, height-20], outline='darkgray', width=3)
    
    # 画像を保存
    output_file = "readable_japanese_test.png"
    image.save(output_file)
    
    print(f"✅ 読みやすい日本語テスト画像を作成: {output_file}")
    print("📋 特徴:")
    print("- 大きく明確なフォント")
    print("- 高解像度 (1200x900)")
    print("- 十分な行間")
    print("- 様々な日本語文字種")
    print("- 固有名詞（スザンヌ、ヘキサゴン等）")
    
    return output_file

def main():
    """メイン処理"""
    print("🔍 読みやすい日本語OCRテスト画像作成")
    print("="*60)
    
    try:
        image_file = create_readable_japanese_test()
        
        print(f"\n🚀 OCRテスト実行:")
        print(f"export GOOGLE_CLOUD_API_KEY='***REMOVED***'")
        print(f"python3 google_vision_ocr_test.py {image_file}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()