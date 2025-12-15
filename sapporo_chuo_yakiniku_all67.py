#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
札幌市中央区 焼肉店 全67件 口コミ件数順表示システム
Google Places API を使用して焼肉店情報を取得し、口コミ件数でランキング
"""

import json
import time
import googlemaps
from datetime import datetime

class SapporoChuoYakinikuAll67Finder:
    def __init__(self):
        """初期化 - Google Maps API キーを設定"""
        self.api_key = self.load_api_key()
        if not self.api_key:
            raise ValueError("Google Maps API キーが見つかりません")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.yakiniku_shops = []
        
    def load_api_key(self):
        """API キーを設定ファイルから読み込み"""
        config_path = "/home/fujinosuke/google_maps_config.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('google_maps_api_key')
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return None
    
    def search_yakiniku_shops(self):
        """札幌市中央区の焼肉店を検索"""
        print("🥩 札幌市中央区の焼肉店を検索中...")
        
        # 札幌市中央区の主要エリア
        search_locations = [
            {"name": "すすきの", "location": "43.0546,141.3533"},
            {"name": "大通", "location": "43.0568,141.3533"},
            {"name": "札幌駅周辺", "location": "43.0683,141.3507"},
            {"name": "円山", "location": "43.0510,141.3160"},
            {"name": "中島公園", "location": "43.0465,141.3538"},
            {"name": "西18丁目", "location": "43.0631,141.3206"},
            {"name": "西28丁目", "location": "43.0717,141.2905"},
        ]
        
        # 検索キーワード
        keywords = [
            "焼肉 札幌市中央区",
            "焼き肉 札幌市中央区", 
            "やきにく 札幌市中央区",
            "BBQ 札幌市中央区",
            "韓国料理 焼肉 札幌市中央区",
            "カルビ 札幌市中央区",
            "ホルモン 札幌市中央区"
        ]
        
        all_shops = {}  # 重複除去用辞書
        
        # キーワード検索
        for keyword in keywords:
            print(f"  検索キーワード: {keyword}")
            try:
                places_result = self.gmaps.places(
                    query=keyword,
                    location="43.0568,141.3533",  # 中央区中心
                    radius=8000,  # 8km範囲
                    type="restaurant",
                    language="ja"
                )
                
                for place in places_result.get('results', []):
                    place_id = place.get('place_id')
                    if place_id and place_id not in all_shops:
                        if self.is_in_chuo_ku(place) and self.is_yakiniku_shop(place):
                            shop_info = self.extract_shop_info(place)
                            if shop_info and shop_info.get('review_count', 0) > 0:
                                all_shops[place_id] = shop_info
                
                time.sleep(0.5)
            except Exception as e:
                print(f"検索エラー ({keyword}): {e}")
                continue
        
        # エリア別検索
        for location in search_locations:
            print(f"  検索エリア: {location['name']}")
            try:
                places_result = self.gmaps.places(
                    query="焼肉",
                    location=location['location'],
                    radius=2000,  # 2km範囲
                    type="restaurant",
                    language="ja"
                )
                
                for place in places_result.get('results', []):
                    place_id = place.get('place_id')
                    if place_id and place_id not in all_shops:
                        if self.is_in_chuo_ku(place) and self.is_yakiniku_shop(place):
                            shop_info = self.extract_shop_info(place)
                            if shop_info and shop_info.get('review_count', 0) > 0:
                                all_shops[place_id] = shop_info
                
                time.sleep(0.5)
            except Exception as e:
                print(f"検索エラー ({location['name']}): {e}")
                continue
        
        self.yakiniku_shops = list(all_shops.values())
        print(f"✅ {len(self.yakiniku_shops)}件の焼肉店を発見")
        return self.yakiniku_shops
    
    def is_in_chuo_ku(self, place):
        """札幌市中央区内かチェック"""
        address = place.get('formatted_address', '')
        return '中央区' in address and '札幌' in address
    
    def is_yakiniku_shop(self, place):
        """焼肉店かどうかを判定"""
        name = place.get('name', '').lower()
        yakiniku_keywords = [
            '焼肉', '焼き肉', 'やきにく', 'yakiniku', 'bbq',
            'カルビ', 'ホルモン', '韓国', 'サムギョプサル',
            'プルコギ', '炭火', '和牛', '牛角', '叙々苑'
        ]
        
        return any(keyword in name for keyword in yakiniku_keywords)
    
    def extract_shop_info(self, place):
        """店舗情報を抽出・整理"""
        try:
            place_id = place.get('place_id')
            details = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'website', 'rating', 'user_ratings_total',
                    'opening_hours', 'geometry', 'reviews', 'price_level'
                ],
                language='ja'
            )
            
            place_details = details.get('result', {})
            
            shop_info = {
                'name': place_details.get('name', '不明'),
                'address': place_details.get('formatted_address', ''),
                'phone': place_details.get('formatted_phone_number', ''),
                'website': place_details.get('website', ''),
                'rating': place_details.get('rating', 0),
                'review_count': place_details.get('user_ratings_total', 0),
                'price_level': place_details.get('price_level', 0),
                'place_id': place_id
            }
            
            # 座標情報
            geometry = place_details.get('geometry', {})
            location = geometry.get('location', {})
            shop_info['latitude'] = location.get('lat', 0)
            shop_info['longitude'] = location.get('lng', 0)
            
            # 営業時間
            opening_hours = place_details.get('opening_hours', {})
            if opening_hours.get('weekday_text'):
                shop_info['opening_hours'] = '\n'.join(opening_hours['weekday_text'])
            else:
                shop_info['opening_hours'] = '営業時間不明'
            
            return shop_info
            
        except Exception as e:
            print(f"詳細情報取得エラー: {e}")
            return None
    
    def get_all_by_reviews(self):
        """口コミ件数で全件ソート"""
        if not self.yakiniku_shops:
            return []
        
        # 口コミ件数でソート（降順）
        sorted_shops = sorted(
            self.yakiniku_shops, 
            key=lambda x: x.get('review_count', 0), 
            reverse=True
        )
        
        return sorted_shops
    
    def display_all(self):
        """全件を見やすく表示"""
        all_shops = self.get_all_by_reviews()
        
        if not all_shops:
            print("❌ 焼肉店が見つかりませんでした")
            return
        
        print("\n" + "="*100)
        print(f"🏆 札幌市中央区 焼肉店 全{len(all_shops)}件 口コミ件数順")
        print("="*100)
        
        for i, shop in enumerate(all_shops, 1):
            price_text = "¥" * shop.get('price_level', 0) if shop.get('price_level', 0) > 0 else "価格不明"
            
            # 住所を短縮表示
            address_short = shop['address'].replace('日本、〒', '').replace('北海道札幌市中央区', '')
            
            print(f"{i:2d}. {shop['name']}")
            print(f"    📍 {address_short}")
            print(f"    📞 {shop['phone']}")
            print(f"    ⭐ ★{shop['rating']:.1f} ({shop['review_count']:,}件) 💰{price_text}")
            if shop['website']:
                print(f"    🌐 {shop['website']}")
            print()
        
        print("="*100)
        print(f"検索日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print("対象エリア: 札幌市中央区")
        print("データ提供: Google Maps API")
        
        # 統計情報
        total_reviews = sum(shop['review_count'] for shop in all_shops)
        avg_rating = sum(shop['rating'] for shop in all_shops if shop['rating'] > 0) / len([s for s in all_shops if s['rating'] > 0])
        print(f"\n📊 統計情報:")
        print(f"   総口コミ数: {total_reviews:,}件")
        print(f"   平均評価: ★{avg_rating:.2f}")
        print(f"   最高口コミ数: {all_shops[0]['review_count']:,}件 ({all_shops[0]['name']})")

def main():
    """メイン実行関数"""
    try:
        # 検索システム初期化
        finder = SapporoChuoYakinikuAll67Finder()
        
        # 焼肉店検索
        shops = finder.search_yakiniku_shops()
        
        if shops:
            # 全件表示
            finder.display_all()
        else:
            print("❌ 焼肉店が見つかりませんでした")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("Google Maps API設定を確認してください")

if __name__ == '__main__':
    main()