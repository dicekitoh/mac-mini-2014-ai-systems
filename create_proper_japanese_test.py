#!/usr/bin/env python3
"""
適切な日本語フォント（Noto Sans CJK JP）を使用したOCRテスト画像作成
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_proper_japanese_test():
    """適切な日本語フォントでテスト画像を作成"""
    
    # 高解像度設定
    width, height = 1400, 1000
    
    # 白い背景
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # スザンヌ・ヘキサゴン関連の日本語テキスト
    japanese_texts = [
        "【日本語OCRテスト】",
        "",
        "スザンヌ「ヘキサゴン」やらせ告白",
        "上沼恵美子「今やったらアウトやな」",
        "",
        "2025年6月15日 18時30分",
        "",
        "タレントのスザンヌが過去に出演していた",
        "クイズ番組「クイズ！ヘキサゴンII」での",
        "やらせについて告白した。",
        "",
        "スザンヌは「実は台本があったんです」と",
        "明かし、これに対して上沼恵美子は",
        "「今やったらアウトやな」とコメント。",
        "",
        "ひらがなテスト：",
        "あいうえお かきくけこ さしすせそ",
        "たちつてと なにぬねの はひふへほ",
        "",
        "カタカナテスト：",
        "アイウエオ カキクケコ サシスセソ",
        "タチツテト ナニヌネノ ハヒフヘホ",
        "",
        "漢字テスト：",
        "日本語 文字認識 技術 検証",
        "視聴者 番組 制作 放送局",
        "",
        "記号・数字テスト：",
        "!@#$%^&*() 1234567890",
        "「」『』（）【】※→←",
        "",
        "複雑な文章テスト：",
        "「バラエティ番組の透明性が重要だ」",
        "『視聴者との信頼関係を築くために』",
        "※エンターテイメント業界の課題※"
    ]
    
    # 適切な日本語フォントを使用
    try:
        # Noto Sans CJK JPフォントを使用（日本語専用）
        font_large = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 28)
        font_title = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 24)
        font_normal = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 18)
        print("✅ Noto Sans CJK JP フォントを使用")
    except Exception as e:
        print(f"❌ CJKフォント読み込みエラー: {e}")
        try:
            # 代替フォント
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            print("⚠️ DejaVu フォントを使用（日本語表示に制限あり）")
        except:
            font_large = font_title = font_normal = font_small = ImageFont.load_default()
            print("⚠️ デフォルトフォントを使用")
    
    # テキストを丁寧に描画
    y_position = 40
    
    for i, text in enumerate(japanese_texts):
        if text.strip():
            if text.startswith("【") and text.endswith("】"):
                # メインタイトル（青色、最大フォント）
                draw.text((50, y_position), text, fill='darkblue', font=font_large)
                y_position += 45
            elif text.startswith("スザンヌ"):
                # 記事タイトル（赤色、大フォント）
                draw.text((50, y_position), text, fill='darkred', font=font_title)
                y_position += 40
            elif "年" in text and "月" in text and "日" in text:
                # 日付（グレー、小フォント）
                draw.text((50, y_position), text, fill='gray', font=font_small)
                y_position += 30
            elif text.endswith("テスト："):
                # セクションタイトル（緑色、タイトルフォント）
                draw.text((50, y_position), text, fill='darkgreen', font=font_title)
                y_position += 35
            elif text.startswith("「") or text.startswith("『") or text.startswith("※"):
                # 引用文・特殊文（紫色、通常フォント）
                draw.text((70, y_position), text, fill='purple', font=font_normal)
                y_position += 32
            else:
                # 通常テキスト（黒色、通常フォント）
                draw.text((50, y_position), text, fill='black', font=font_normal)
                y_position += 32
        else:
            y_position += 20  # 空行
    
    # 明確な枠線
    draw.rectangle([20, 20, width-20, height-20], outline='black', width=3)
    
    # 画像を保存
    output_file = "proper_japanese_suzanne_test.png"
    image.save(output_file, quality=95, optimize=True)
    
    print(f"✅ 適切な日本語フォントのテスト画像を作成: {output_file}")
    print("📋 改善点:")
    print("- Noto Sans CJK JP フォント使用")
    print("- 高解像度 (1400x1000)")
    print("- スザンヌ・ヘキサゴン関連の実際のニュース内容")
    print("- ひらがな・カタカナ・漢字の完全テスト")
    print("- 複雑な日本語文章構造")
    
    return output_file

def main():
    """メイン処理"""
    print("🔍 適切な日本語フォントでのOCRテスト画像作成")
    print("="*70)
    
    try:
        image_file = create_proper_japanese_test()
        
        print(f"\n🚀 高精度OCRテスト実行:")
        print(f"export GOOGLE_CLOUD_API_KEY='***REMOVED***'")
        print(f"python3 google_vision_ocr_test.py {image_file}")
        
        print(f"\n💡 期待される結果:")
        print("- 日本語文字の正確な認識")
        print("- スザンヌ、ヘキサゴンなどの固有名詞認識")
        print("- ひらがな・カタカナ・漢字の区別")
        print("- 複雑な文章構造の解析")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()