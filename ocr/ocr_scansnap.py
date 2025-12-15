#\!/usr/bin/env python3
import os
import json
from google.cloud import vision
from datetime import datetime

def setup_google_vision():
    """Google Vision API設定"""
    # 認証ファイルパス設定
    credentials_path = "/home/fujinosuke/google_vision_credentials.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    
    # クライアント初期化
    client = vision.ImageAnnotatorClient()
    return client

def ocr_image(image_path, client):
    """画像からOCR実行"""
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    
    # OCR実行（日本語対応）
    response = client.document_text_detection(
        image=image,
        image_context=vision.ImageContext(language_hints=["ja", "en"])
    )
    
    if response.error.message:
        raise Exception(f"Google Vision API エラー: {response.error.message}")
    
    return response

def save_ocr_result(image_path, response):
    """OCR結果を保存"""
    # ファイル名生成
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # テキストファイル保存
    text_file = f"/home/fujinosuke/scansnap_scans/processed/{base_name}_ocr.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(f"OCR処理結果 - {timestamp}\n")
        f.write(f"元ファイル: {os.path.basename(image_path)}\n")
        f.write("=" * 50 + "\n\n")
        
        if response.full_text_annotation.text:
            f.write(response.full_text_annotation.text)
        else:
            f.write("テキストが検出されませんでした。")
    
    # JSON詳細結果保存
    json_file = f"/home/fujinosuke/scansnap_scans/processed/{base_name}_ocr_detail.json"
    ocr_data = {
        "timestamp": timestamp,
        "source_file": os.path.basename(image_path),
        "full_text": response.full_text_annotation.text if response.full_text_annotation.text else "",
        "pages": []
    }
    
    for page in response.full_text_annotation.pages:
        page_data = {
            "blocks": []
        }
        for block in page.blocks:
            block_text = ""
            for paragraph in block.paragraphs:
                para_text = ""
                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    para_text += word_text + " "
                block_text += para_text.strip() + "\n"
            page_data["blocks"].append(block_text.strip())
        ocr_data["pages"].append(page_data)
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=2)
    
    return text_file, json_file

def main():
    print("=== ScanSnap OCR処理開始 ===")
    
    try:
        # Google Vision API設定
        client = setup_google_vision()
        print("✅ Google Vision API接続成功")
        
        # 処理済みフォルダの画像ファイル検索
        processed_dir = "/home/fujinosuke/scansnap_scans/processed"
        image_files = [f for f in os.listdir(processed_dir) 
                      if f.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp"))]
        
        if not image_files:
            print("❌ 処理対象の画像ファイルが見つかりません")
            return
        
        print(f"📄 {len(image_files)}件の画像ファイルを発見")
        
        for image_file in image_files:
            image_path = os.path.join(processed_dir, image_file)
            print(f"\n🔍 OCR処理中: {image_file}")
            
            try:
                # OCR実行
                response = ocr_image(image_path, client)
                
                # 結果保存
                text_file, json_file = save_ocr_result(image_path, response)
                
                # 結果表示
                if response.full_text_annotation.text:
                    text_preview = response.full_text_annotation.text[:200].replace("\n", " ")
                    print(f"✅ OCR成功: {len(response.full_text_annotation.text)}文字検出")
                    print(f"   プレビュー: {text_preview}...")
                    print(f"   保存先: {os.path.basename(text_file)}")
                else:
                    print("⚠️  テキストが検出されませんでした")
                
            except Exception as e:
                print(f"❌ OCR処理エラー ({image_file}): {e}")
        
        print(f"\n=== OCR処理完了 ===")
        print("結果ファイル:")
        result_files = [f for f in os.listdir(processed_dir) 
                       if f.endswith((_ocr.txt, _ocr_detail.json))]
        for result_file in sorted(result_files):
            print(f"  - {result_file}")
            
    except Exception as e:
        print(f"❌ 処理エラー: {e}")

if __name__ == "__main__":
    main()
