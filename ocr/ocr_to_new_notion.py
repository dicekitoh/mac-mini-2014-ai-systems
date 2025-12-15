#\!/usr/bin/env python3
import requests
import json
from datetime import datetime
import os
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

def add_to_new_notion_table(title, content, category="スキャン文書"):
    """新しいNotionテーブルにOCR結果を追加"""
    
    # 新しいテーブルのID（URLから抽出）
    database_id = "21806a5ef879808abd63e3263cc17568"
    api_key = "***REMOVED***"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # ページ作成データ
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "名前": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"カテゴリ: {category}"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block", 
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"作成日時: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": "OCR抽出内容"
                            }
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    
    return response

def main():
    print("=== 新規NotionテーブルにOCR結果追加 ===")
    
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
        
        # タイトル生成
        title = f"スキャン文書OCR - {target_file} - {datetime.now().strftime("%Y/%m/%d")}"
        
        # Notionに追加
        print("📝 新規Notionテーブルに追加中...")
        response = add_to_new_notion_table(title, ocr_content)
        
        if response.status_code == 200:
            result = response.json()
            page_id = result.get("id", "unknown").replace("-", "")
            print("✅ Notion追加成功\!")
            print(f"   ページID: {result[id]}")
            print(f"   URL: https://www.notion.so/{page_id}")
            print(f"   テーブルURL: https://www.notion.so/21806a5ef879808abd63e3263cc17568")
        else:
            print(f"❌ Notion追加エラー: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            
    except Exception as e:
        print(f"❌ 処理エラー: {e}")

if __name__ == "__main__":
    main()
