#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
札幌市内ラーメン店 口コミ件数トップ5検索システム
Google Places API を使用してラーメン店情報を取得し、口コミ件数でランキング
"""

import json
import time
import googlemaps
from datetime import datetime

class SapporoRamenTop5Finder:
    def __init__(self):
        """初期化 - Google Maps API キーを設定"""
        self.api_key = self.load_api_key()
        if not self.api_key:
            raise ValueError("Google Maps API キーが見つかりません")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.ramen_shops = []
        
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
    
    def search_ramen_shops(self):
        """札幌市内のラーメン店を検索"""
        print("🍜 札幌市内のラーメン店を検索中...")
        
        # 札幌市の主要エリアを定義
        search_areas = [
            {"name": "札幌市中央区", "location": "43.0568,141.3533"},
            {"name": "札幌市北区", "location": "43.0909,141.3400"},
            {"name": "札幌市東区", "location": "43.0766,141.3656"},
            {"name": "札幌市白石区", "location": "43.0472,141.4056"},
            {"name": "札幌市豊平区", "location": "43.0317,141.3806"},
            {"name": "札幌市南区", "location": "42.9897,141.3533"},
            {"name": "札幌市西区", "location": "43.0742,141.3017"},
            {"name": "札幌市厚別区", "location": "43.0378,141.4789"},
            {"name": "札幌市手稲区", "location": "43.1236,141.2469"},
            {"name": "札幌市清田区", "location": "43.0089,141.4328"}
        ]
        
        # 検索キーワード
        keywords = ["ラーメン", "ramen", "らーめん", "味噌ラーメン", "醤油ラーメン"]
        
        all_shops = {}  # 重複除去用辞書
        
        for area in search_areas:
            print(f"  検索エリア: {area['name']}")
            
            for keyword in keywords:
                try:
                    # Places APIで検索
                    places_result = self.gmaps.places(
                        query=f"{keyword} {area['name']}",
                        location=area['location'],
                        radius=5000,  # 5km範囲
                        type="restaurant",
                        language="ja"
                    )
                    
                    # 結果を処理
                    for place in places_result.get('results', []):
                        place_id = place.get('place_id')
                        if place_id and place_id not in all_shops:
                            # ラーメン店かチェック
                            if self.is_ramen_shop(place):
                                shop_info = self.extract_shop_info(place)
                                if shop_info and shop_info.get('review_count', 0) > 0:
                                    all_shops[place_id] = shop_info
                    
                    # API制限対策で少し待機
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"検索エラー ({area['name']}, {keyword}): {e}")
                    continue
        
        self.ramen_shops = list(all_shops.values())
        print(f"✅ {len(self.ramen_shops)}件のラーメン店を発見")
        return self.ramen_shops
    
    def is_ramen_shop(self, place):
        """ラーメン店かどうかを判定"""
        name = place.get('name', '').lower()
        ramen_keywords = ['ラーメン', 'らーめん', 'ramen', '麺', '味噌', '醤油', '豚骨', 'とんこつ', '塩ラーメン']
        
        return any(keyword in name for keyword in ramen_keywords)
    
    def extract_shop_info(self, place):
        """店舗情報を抽出・整理"""
        try:
            # Place Details APIで詳細情報取得
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
            
            # 基本情報
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
            
            # レビュー（最新3件）
            reviews = place_details.get('reviews', [])
            if reviews:
                review_texts = []
                for review in reviews[:3]:
                    text = review.get('text', '')[:100]  # 100文字まで
                    rating = review.get('rating', 0)
                    review_texts.append(f"★{rating}: {text}")
                shop_info['recent_reviews'] = '\n'.join(review_texts)
            else:
                shop_info['recent_reviews'] = 'レビューなし'
            
            return shop_info
            
        except Exception as e:
            print(f"詳細情報取得エラー: {e}")
            return None
    
    def get_top5_by_reviews(self):
        """口コミ件数でトップ5を取得"""
        if not self.ramen_shops:
            return []
        
        # 口コミ件数でソート（降順）
        sorted_shops = sorted(
            self.ramen_shops, 
            key=lambda x: x.get('review_count', 0), 
            reverse=True
        )
        
        return sorted_shops[:5]
    
    def display_top5(self):
        """トップ5を見やすく表示"""
        top5 = self.get_top5_by_reviews()
        
        if not top5:
            print("❌ ラーメン店が見つかりませんでした")
            return
        
        print("\n" + "="*80)
        print("🏆 札幌市内ラーメン店 口コミ件数トップ5")
        print("="*80)
        
        for i, shop in enumerate(top5, 1):
            price_text = "¥" * shop.get('price_level', 0) if shop.get('price_level', 0) > 0 else "価格不明"
            
            print(f"\n🥇 第{i}位: {shop['name']}")
            print(f"   📍 {shop['address']}")
            print(f"   📞 {shop['phone']}")
            print(f"   ⭐ 評価: ★{shop['rating']:.1f} ({shop['review_count']:,}件の口コミ)")
            print(f"   💰 価格帯: {price_text}")
            if shop['website']:
                print(f"   🌐 {shop['website']}")
            print(f"   🕒 営業時間:")
            for line in shop['opening_hours'].split('\n')[:3]:  # 最初の3行のみ表示
                print(f"      {line}")
            
            # 最新レビューを1つ表示
            if shop['recent_reviews'] and shop['recent_reviews'] != 'レビューなし':
                first_review = shop['recent_reviews'].split('\n')[0]
                print(f"   💬 最新レビュー: {first_review}")
        
        print("\n" + "="*80)
        print(f"検索日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        print("データ提供: Google Maps API")

def main():
    """メイン実行関数"""
    try:
        # 検索システム初期化
        finder = SapporoRamenTop5Finder()
        
        # ラーメン店検索
        shops = finder.search_ramen_shops()
        
        if shops:
            # トップ5表示
            finder.display_top5()
        else:
            print("❌ ラーメン店が見つかりませんでした")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("Google Maps API設定を確認してください")

if __name__ == '__main__':
    main()