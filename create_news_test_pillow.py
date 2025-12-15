#!/usr/bin/env python3
"""
Pillowを使った日本語ニュース記事風OCRテスト画像作成
"""

import os
import sys

def create_japanese_news_with_pillow():
    """Pillowで日本語ニュース記事風のテスト画像を作成"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ Pillowライブラリが利用可能です")
    except ImportError:
        print("❌ Pillowライブラリが必要です")
        print("代替案: シンプルなテキストファイルからOCRテスト画像を作成します")
        return create_simple_text_image()
    
    # 画像サイズ
    width, height = 1000, 800
    
    # 白い背景の画像を作成
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # ニュース記事のテキスト
    news_lines = [
        "【エンターテイメントニュース】",
        "",
        "スザンヌ「ヘキサゴン」での「やらせ」告白",
        "上沼恵美子は「今やったらアウトやな」",
        "",
        "2025年6月15日 18時30分配信",
        "",
        "タレントのスザンヌ（37）が14日放送の",
        "バラエティー番組で、過去に出演していた",
        "クイズ番組「クイズ！ヘキサゴンII」での",
        "「やらせ」について言及した。",
        "",
        "スザンヌは「実は台本があったんです」と",
        "明かし、「でも楽しくやってました」と",
        "振り返った。これに対し、上沼恵美子は",
        "「今やったらアウトやな」とコメント。",
        "",
        "視聴者からは「正直に話してくれて",
        "ありがとう」「時代が変わったんだな」",
        "などの声が上がっている。",
        "",
        "関連記事：",
        "・バラエティ番組の「やらせ」問題について",
        "・テレビ業界の透明性向上への取り組み",
        "",
        "【記者：田中太郎／編集部】"
    ]
    
    # デフォルトフォントを使用
    try:
        # システムフォントを試す
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        # デフォルトフォント
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # テキストを描画
    y_position = 30
    
    for line in news_lines:
        if line.strip():
            if line.startswith("【") and line.endswith("】"):
                # ヘッダー（青色、大きなフォント）
                draw.text((30, y_position), line, fill='darkblue', font=font_large)
                y_position += 35
            elif line.startswith("スザンヌ"):
                # タイトル（赤色、大きなフォント）
                draw.text((30, y_position), line, fill='darkred', font=font_large)
                y_position += 35
            elif "配信" in line:
                # 日時（グレー、小さなフォント）
                draw.text((30, y_position), line, fill='gray', font=font_small)
                y_position += 25
            else:
                # 通常テキスト
                draw.text((30, y_position), line, fill='black', font=font_normal)
                y_position += 25
        else:
            y_position += 15
    
    # 枠線を描画
    draw.rectangle([10, 10, width-10, height-10], outline='lightgray', width=2)
    
    # 画像を保存
    output_file = "japanese_news_complex.png"
    image.save(output_file)
    
    print(f"✅ 複雑な日本語ニュース記事画像を作成: {output_file}")
    return output_file

def create_simple_text_image():
    """Pillowなしでシンプルなテキスト画像を作成"""
    # テキストファイルを作成してImageMagick以外の方法を試す
    text_content = """【エンターテイメントニュース】

スザンヌ「ヘキサゴン」での「やらせ」告白
上沼恵美子は「今やったらアウトやな」

2025年6月15日 18時30分配信

タレントのスザンヌ（37）が14日放送の
バラエティー番組で、過去に出演していた
クイズ番組「クイズ！ヘキサゴンII」での
「やらせ」について言及した。

スザンヌは「実は台本があったんです」と
明かし、「でも楽しくやってました」と
振り返った。これに対し、上沼恵美子は
「今やったらアウトやな」とコメント。

視聴者からは「正直に話してくれて
ありがとう」「時代が変わったんだな」
などの声が上がっている。

関連記事：
・バラエティ番組の「やらせ」問題について
・テレビ業界の透明性向上への取り組み

【記者：田中太郎／編集部】"""
    
    # テキストファイルとして保存
    with open("news_text.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print("📝 日本語ニューステキストファイルを作成: news_text.txt")
    print("💡 このテキスト内容を手動で画像化してOCRテストしてください")
    
    return None

def main():
    """メイン処理"""
    print("🔍 複雑な日本語ニュース記事OCRテスト")
    print("="*60)
    
    image_file = create_japanese_news_with_pillow()
    
    if image_file:
        print(f"\n🚀 OCRテストの実行方法:")
        print(f"export GOOGLE_CLOUD_API_KEY='***REMOVED***'")
        print(f"python3 google_vision_ocr_test.py {image_file}")
        print(f"\n📋 テスト内容:")
        print("- 複雑な日本語テキスト")
        print("- ニュース記事フォーマット") 
        print("- 固有名詞（スザンヌ、ヘキサゴン等）")
        print("- 日付・時刻情報")
        print("- 括弧、記号類")
        
        return image_file
    else:
        return None

if __name__ == "__main__":
    main()