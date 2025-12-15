#\!/usr/bin/env python3
"""
Google Maps API と Notion API の連携システム
地図情報をNotionデータベースに保存・管理
"""

import json
import requests
from datetime import datetime
from notion_client import Client

class GoogleMapsNotionIntegration:
    def __init__(self):
        # Google Maps API設定
        with open("/home/fujinosuke/google_maps_config.json", "r") as f:
            self.maps_config = json.load(f)
        self.maps_api_key = self.maps_config["google_maps_api_key"]
        
        # Notion API設定
        self.notion_api_key = "***REMOVED***"
        self.notion = Client(auth=self.notion_api_key)
        
        # 既存のNotionデータベースID（アイデアDBを使用）
        self.notion_db_id = "21506a5ef87980b9ab82c84e7b631568"
    
    def geocode_address(self, address):
        """住所から緯度経度を取得"""
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.maps_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK" and data["results"]:
                result = data["results"][0]
                location = result["geometry"]["location"]
                return {
                    "formatted_address": result["formatted_address"],
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "place_id": result.get("place_id", ""),
                    "types": result.get("types", [])
                }
        return None
    
    def reverse_geocode(self, lat, lng):
        """緯度経度から住所を取得"""
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.maps_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK" and data["results"]:
                return data["results"][0]["formatted_address"]
        return None
    
    def get_place_details(self, place_id):
        """Place IDから詳細情報を取得"""
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,types,rating,formatted_phone_number,website",
            "key": self.maps_api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                return data["result"]
        return None
    
    def save_to_notion(self, location_data, note=""):
        """位置情報をNotionに保存"""
        try:
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": f"地図情報: {location_data.get(formatted_address, Unknown)}"
                            }
                        }
                    ]
                }
            }
            
            # 詳細情報をコンテンツとして追加
            content_blocks = [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": "地図情報詳細"}
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
                                "text": {"content": f"住所: {location_data.get(formatted_address, N/A)}"}
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
                                "text": {"content": f"緯度: {location_data.get(latitude, N/A)}"}
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
                                "text": {"content": f"経度: {location_data.get(longitude, N/A)}"}
                            }
                        ]
                    }
                }
            ]
            
            if note:
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"メモ: {note}"}
                            }
                        ]
                    }
                })
            
            # Google Mapsリンクを追加
            maps_url = f"https://maps.google.com/maps?q={location_data.get(latitude, 0)},{location_data.get(longitude, 0)}"
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Google Maps: "},
                        },
                        {
                            "type": "text",
                            "text": {"content": maps_url, "link": {"url": maps_url}},
                        }
                    ]
                }
            })
            
            # Notionページを作成
            page = self.notion.pages.create(
                parent={"database_id": self.notion_db_id},
                properties=properties,
                children=content_blocks
            )
            
            return {
                "success": True,
                "page_id": page["id"],
                "url": page["url"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def address_to_notion(self, address, note=""):
        """住所からNotionに地図情報を保存"""
        print(f"住所を検索中: {address}")
        location_data = self.geocode_address(address)
        
        if location_data:
            print(f"✅ 位置情報取得成功: {location_data[formatted_address]}")
            result = self.save_to_notion(location_data, note)
            
            if result["success"]:
                print(f"✅ Notionに保存完了")
                print(f"ページURL: {result[url]}")
                return result
            else:
                print(f"❌ Notion保存エラー: {result[error]}")
                return result
        else:
            print(f"❌ 住所が見つかりません: {address}")
            return {"success": False, "error": "Address not found"}

def main():
    """メイン実行関数"""
    integration = GoogleMapsNotionIntegration()
    
    print("=== Google Maps & Notion API 連携システム ===")
    print("1. 住所検索とNotion保存のテスト")
    
    # テスト実行
    test_address = "東京駅"
    test_note = "テスト実行: Google Maps API → Notion API連携"
    
    result = integration.address_to_notion(test_address, test_note)
    
    if result["success"]:
        print("\n🎉 連携システムテスト成功!")
        print("Google Maps API と Notion API の連携が正常に動作しています。")
    else:
        print(f"\n❌ 連携システムテスト失敗: {result.get(error, Unknown error)}")

if __name__ == "__main__":
    main()
