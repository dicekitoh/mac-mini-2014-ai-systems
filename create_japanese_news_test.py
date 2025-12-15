#!/usr/bin/env python3
"""
日本語ニュース記事風のOCRテスト画像作成
複雑な日本語テキストでOCR精度をテスト
"""

import os
import subprocess
from datetime import datetime

def create_japanese_news_image():
    """日本語ニュース記事風のテスト画像を作成"""
    
    # ニュース記事風の日本語テキスト
    news_content = [
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
    
    try:
        # ImageMagickで日本語ニュース記事画像を作成
        output_file = "japanese_news_test.png"
        
        # ImageMagickコマンドを構築
        cmd = [
            'convert',
            '-size', '1000x800',
            'xc:white',
            '-font', 'DejaVu-Sans',
            '-pointsize', '18',
            '-fill', 'black'
        ]
        
        # テキストを配置
        y_pos = 40
        for line in news_content:
            if line.strip():  # 空行でない場合
                if line.startswith("【") and line.endswith("】"):
                    # ヘッダー部分は太字風に
                    cmd.extend(['-pointsize', '20', '-fill', 'darkblue'])
                    cmd.extend(['-annotate', f'+50+{y_pos}', line])
                    cmd.extend(['-pointsize', '18', '-fill', 'black'])
                elif line.startswith("スザンヌ"):
                    # タイトル部分
                    cmd.extend(['-pointsize', '22', '-fill', 'darkred'])
                    cmd.extend(['-annotate', f'+50+{y_pos}', line])
                    cmd.extend(['-pointsize', '18', '-fill', 'black'])
                elif "時間配信" in line:
                    # 日時部分
                    cmd.extend(['-pointsize', '14', '-fill', 'gray'])
                    cmd.extend(['-annotate', f'+50+{y_pos}', line])
                    cmd.extend(['-pointsize', '18', '-fill', 'black'])
                else:
                    # 通常のテキスト
                    cmd.extend(['-annotate', f'+50+{y_pos}', line])
                
                y_pos += 30
            else:
                y_pos += 15  # 空行の場合は少し間隔を空ける
        
        # 枠線を追加
        cmd.extend([
            '-stroke', 'lightgray',
            '-strokewidth', '2',
            '-fill', 'none',
            '-draw', 'rectangle 20,20 980,780'
        ])
        
        cmd.append(output_file)
        
        print("📰 日本語ニュース記事風テスト画像を作成中...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_file):
            print(f"✅ テスト画像を作成しました: {output_file}")
            print("📋 内容: 複雑な日本語ニュース記事（スザンヌ・ヘキサゴン関連）")
            return output_file
        else:
            print("❌ ImageMagickでの画像作成に失敗")
            print(f"エラー: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ ImageMagick (convert) が見つかりません")
        print("インストール方法: sudo apt install imagemagick")
        return None
    except Exception as e:
        print(f"❌ 画像作成エラー: {e}")
        return None

def main():
    """メイン処理"""
    print("🔍 日本語ニュース記事OCRテスト画像作成")
    print("="*60)
    
    image_path = create_japanese_news_image()
    
    if image_path:
        print(f"\n🚀 作成された画像でOCRテストを実行しますか？")
        print("実行方法:")
        print(f"export GOOGLE_CLOUD_API_KEY='***REMOVED***'")
        print(f"python3 google_vision_ocr_test.py {image_path}")
        
        return True
    else:
        print("❌ テスト画像の作成に失敗しました")
        return False

if __name__ == "__main__":
    main()