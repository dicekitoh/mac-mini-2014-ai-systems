#\!/usr/bin/env python3
import requests
import json
from datetime import datetime

def add_to_notion_simple():
    # Notion API設定
    api_key = "***REMOVED***"
    database_id = "21706a5ef87981e8ba00cae9a8553b7f"  # 音声メモDB
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # OCR結果テキスト
    ocr_content = """郵便はがき
料金別納郵便
こくみん共済 coop
〒006-0024
札幌市手稲区手稲本町4条2丁目2-2千代ヶ丘西団地2-204
伊藤 大輔 様

マイカー共済 自動車総合補償共済
商品改定のお知らせ
より安心のカーライフをお送りいただけるよう商品改定を行いました。

主な改定内容:
- 等級別割引率改定（最大65%割引）  
- 運転者本人限定特約新設（9%割引）
- 基本補償範囲拡充（あて逃げ補償等）

差出人: こくみん共済 北海道推進本部
札幌市白石区菊水3条4-1-3"""
    
    # Notionページ作成
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "タイトル": {
                "title": [
                    {
                        "text": {
                            "content": "スキャン文書OCR - こくみん共済マイカー共済案内"
                        }
                    }
                ]
            },
            "内容": {
                "rich_text": [
                    {
                        "text": {
                            "content": ocr_content
                        }
                    }
                ]
            },
            "作成日時": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "タグ": {
                "multi_select": [
                    {"name": "スキャン文書"},
                    {"name": "OCR"}
                ]
            }
        }
    }
    
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    
    return response

# 実行
result = add_to_notion_simple()
if result.status_code == 200:
    page_data = result.json()
    page_id = page_data["id"].replace("-", "")
    print("✅ Notion追加成功\!")
    print(f"URL: https://www.notion.so/{page_id}")
else:
    print(f"❌ エラー: {result.status_code}")
    print(result.text)
