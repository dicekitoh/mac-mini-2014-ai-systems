#\!/usr/bin/env python3

import json
import requests
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
    
    def geocode_address(self, address):
        """住所から緯度経度を取得"""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
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
                    "place_id": result.get("place_id", "")
                }
        return None
    
    def test_apis(self):
        """両方のAPIの接続テスト"""
        print("=== API接続テスト ===")
        
        # Google Maps API テスト
        print("1. Google Maps API テスト...")
        location_data = self.geocode_address("東京駅")
        if location_data:
            print("✅ Google Maps API接続成功")
            print("   住所:", location_data["formatted_address"])
            print("   緯度:", location_data["latitude"])
            print("   経度:", location_data["longitude"])
        else:
            print("❌ Google Maps API接続失敗")
            return False
        
        # Notion API テスト
        print("\n2. Notion API テスト...")
        try:
            user = self.notion.users.me()
            print("✅ Notion API接続成功")
            print("   ユーザー:", user.get("name", "Unknown"))
        except Exception as e:
            print("❌ Notion API接続失敗:", str(e))
            return False
        
        print("\n🎉 両方のAPIが正常に動作しています\!")
        return True

def main():
    integration = GoogleMapsNotionIntegration()
    
    print("=== Google Maps & Notion API 連携システム ===")
    
    if integration.test_apis():
        print("\n✅ 連携システムの基盤が正常に動作しています。")
        print("次のステップ: Notionデータベースの作成と連携機能の実装")
    else:
        print("\n❌ API接続に問題があります。")

if __name__ == "__main__":
    main()
