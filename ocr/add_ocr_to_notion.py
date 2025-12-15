#\!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from google.cloud import vision

def setup_google_vision():
    """Google Vision API設定"""
    credentials_path = "/home/fujinosuke/google_vision_credentials.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
    client = vision.ImageAnnotatorClient()
    return client

def ocr_image(image_path, client):
    """画像からOCR実行"""
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.document_text_detection(
        image=image,
        image_context=vision.ImageContext(language_hints=["ja", "en"])
    )
    
    if response.error.message:
        raise Exception(f"Google Vision API エラー: {response.error.message}")
    
    return response.full_text_annotation.text if response.full_text_annotation.text else ""

def add_to_notion(content, source_file):
    """NotionデータベースにOCR結果を追加"""
    
    # Notion API設定
    notion_api_key = "***REMOVED***"
    database_id = "21706a5ef87981e8ba00cae9a8553b7f"
    
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # 現在時刻
    timestamp = datetime.now().isoformat()
    
    # Notion APIペイロード
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "タイトル": {
                "title": [
                    {
                        "text": {
                            "content": f"スキャン文書OCR - {source_file}"
                        }
                    }
                ]
            },
            "内容": {
                "rich_text": [
                    {
                        "text": {
                            "content": content[:2000] if len(content) > 2000 else content
                        }
                    }
                ]
            },
            "作成日時": {
                "date": {
                    "start": timestamp
                }
            },
            "カテゴリー": {
                "select": {
                    "name": "スキャン文書"
                }
            }
        }
    }
    
    # Notion API呼び出し
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    
    return response

def main():
    print("=== スキャン文書OCR→Notion追加 ===")
    
    # 対象ファイル
    target_file = "20250620124933.jpg"
    image_path = f"/home/fujinosuke/scansnap_scans/processed/{target_file}"
    
    if not os.path.exists(image_path):
        print(f"❌ ファイルが見つかりません: {image_path}")
        return
    
    try:
        # Google Vision API設定
        client = setup_google_vision()
        print("✅ Google Vision API接続成功")
        
        # OCR実行
        print(f"🔍 OCR処理中: {target_file}")
        ocr_content = ocr_image(image_path, client)
        
        if not ocr_content:
            print("❌ テキストが検出されませんでした")
            return
            
        print(f"✅ OCR成功: {len(ocr_content)}文字検出")
        print(f"   プレビュー: {ocr_content[:100]}...")
        
        # Notionに追加
        print("📝 Notionデータベースに追加中...")
        response = add_to_notion(ocr_content, target_file)
        
        if response.status_code == 200:
            result = response.json()
            page_id = result["id"]
            print("✅ Notion追加成功!"))
            print(f"   ページID: {page_id}")
            print(f"   URL: https://www.notion.so/{page_id.replace("-", "")}")
        else:
            print(f"❌ Notion追加エラー: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            
    except Exception as e:
        print(f"❌ 処理エラー: {e}")

if __name__ == "__main__":
    main()
