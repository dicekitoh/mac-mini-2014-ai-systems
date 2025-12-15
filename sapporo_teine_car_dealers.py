#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
札幌市手稲区 自動車販売店検索・抽出システム
Google Places API を使用して自動車販売店情報を取得
"""

import json
import csv
import os
import time
from datetime import datetime
import googlemaps
from pathlib import Path

class SapporoTeineCarDealerExtractor:
    def __init__(self):
        """初期化 - Google Maps API キーを設定"""
        self.api_key = self.load_api_key()
        if not self.api_key:
            raise ValueError("Google Maps API キーが見つかりません")
        
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.results = []
        
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
    
    def search_car_dealers(self):
        """札幌市手稲区の自動車販売店を検索"""
        print("🚗 札幌市手稲区の自動車販売店を検索中...")
        
        # 検索キーワードリスト
        keywords = [
            "自動車販売 札幌市手稲区",
            "中古車販売 札幌市手稲区", 
            "車屋 札幌市手稲区",
            "オートディーラー 札幌市手稲区",
            "car dealer 札幌市手稲区"
        ]
        
        all_dealers = {}  # 重複除去用辞書
        
        for keyword in keywords:
            print(f"  検索中: {keyword}")
            try:
                # Places APIで検索
                places_result = self.gmaps.places(
                    query=keyword,
                    location="43.1236,141.2469",  # 札幌市手稲区の座標
                    radius=10000,  # 10km範囲
                    type="car_dealer",
                    language="ja"
                )
                
                # 結果を処理
                for place in places_result.get('results', []):
                    place_id = place.get('place_id')
                    if place_id and place_id not in all_dealers:
                        # 手稲区内かチェック
                        if self.is_in_teine(place):
                            dealer_info = self.extract_dealer_info(place)
                            if dealer_info:
                                all_dealers[place_id] = dealer_info
                
                # API制限対策で少し待機
                time.sleep(1)
                
            except Exception as e:
                print(f"検索エラー ({keyword}): {e}")
                continue
        
        self.results = list(all_dealers.values())
        print(f"✅ {len(self.results)}件の自動車販売店を発見")
        return self.results
    
    def is_in_teine(self, place):
        """住所に「手稲」が含まれているかチェック"""
        address = place.get('formatted_address', '')
        name = place.get('name', '')
        return '手稲' in address or 'teine' in address.lower()
    
    def extract_dealer_info(self, place):
        """店舗情報を抽出・整理"""
        try:
            # Place Details APIで詳細情報取得
            place_id = place.get('place_id')
            details = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'website', 'rating', 'user_ratings_total',
                    'opening_hours', 'geometry', 'reviews'
                ],
                language='ja'
            )
            
            place_details = details.get('result', {})
            
            # 基本情報
            dealer_info = {
                'name': place_details.get('name', '不明'),
                'address': place_details.get('formatted_address', ''),
                'phone': place_details.get('formatted_phone_number', ''),
                'website': place_details.get('website', ''),
                'rating': place_details.get('rating', 0),
                'review_count': place_details.get('user_ratings_total', 0),
                'business_type': 'car_dealer',
                'place_id': place_id
            }
            
            # 座標情報
            geometry = place_details.get('geometry', {})
            location = geometry.get('location', {})
            dealer_info['latitude'] = location.get('lat', 0)
            dealer_info['longitude'] = location.get('lng', 0)
            
            # 営業時間
            opening_hours = place_details.get('opening_hours', {})
            if opening_hours.get('weekday_text'):
                dealer_info['opening_hours'] = '\n'.join(opening_hours['weekday_text'])
            else:
                dealer_info['opening_hours'] = '営業時間不明'
            
            # レビュー（最新3件）
            reviews = place_details.get('reviews', [])
            if reviews:
                review_texts = []
                for review in reviews[:3]:
                    text = review.get('text', '')[:100]  # 100文字まで
                    rating = review.get('rating', 0)
                    review_texts.append(f"★{rating}: {text}")
                dealer_info['recent_reviews'] = '\n'.join(review_texts)
            else:
                dealer_info['recent_reviews'] = 'レビューなし'
            
            return dealer_info
            
        except Exception as e:
            print(f"詳細情報取得エラー: {e}")
            return None
    
    def save_to_csv(self, filename=None):
        """結果をCSVファイルに保存"""
        if not self.results:
            print("保存するデータがありません")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/fujinosuke/projects/sapporo_teine_car_dealers_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'name', 'address', 'phone', 'website', 'rating', 
                    'review_count', 'business_type', 'latitude', 'longitude',
                    'opening_hours', 'recent_reviews', 'place_id'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
            
            print(f"✅ CSVファイルに保存: {filename}")
            return filename
            
        except Exception as e:
            print(f"CSV保存エラー: {e}")
            return None
    
    def save_to_json(self, filename=None):
        """結果をJSONファイルに保存"""
        if not self.results:
            print("保存するデータがありません")
            return None
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/fujinosuke/projects/sapporo_teine_car_dealers_{timestamp}.json"
        
        try:
            data = {
                'search_date': datetime.now().isoformat(),
                'search_area': '札幌市手稲区',
                'total_count': len(self.results),
                'dealers': self.results
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, ensure_ascii=False, indent=2)
            
            print(f"✅ JSONファイルに保存: {filename}")
            return filename
            
        except Exception as e:
            print(f"JSON保存エラー: {e}")
            return None
    
    def display_summary(self):
        """検索結果サマリーを表示"""
        if not self.results:
            print("検索結果がありません")
            return
        
        print("\n" + "="*60)
        print(f"📊 札幌市手稲区 自動車販売店検索結果: {len(self.results)}件")
        print("="*60)
        
        for i, dealer in enumerate(self.results, 1):
            print(f"\n{i}. {dealer['name']}")
            print(f"   住所: {dealer['address']}")
            print(f"   電話: {dealer['phone']}")
            print(f"   評価: ★{dealer['rating']} ({dealer['review_count']}件)")
            if dealer['website']:
                print(f"   WEB: {dealer['website']}")
            
        # 評価順でトップ3表示
        top_rated = sorted(
            [d for d in self.results if d['rating'] > 0], 
            key=lambda x: (x['rating'], x['review_count']), 
            reverse=True
        )[:3]
        
        if top_rated:
            print("\n🏆 評価上位3店舗:")
            for i, dealer in enumerate(top_rated, 1):
                print(f"{i}. {dealer['name']} - ★{dealer['rating']} ({dealer['review_count']}件)")

def main():
    """メイン実行関数"""
    try:
        # 抽出システム初期化
        extractor = SapporoTeineCarDealerExtractor()
        
        # 自動車販売店検索
        dealers = extractor.search_car_dealers()
        
        if dealers:
            # 結果表示
            extractor.display_summary()
            
            # ファイル保存
            csv_file = extractor.save_to_csv()
            json_file = extractor.save_to_json()
            
            print(f"\n📁 保存ファイル:")
            if csv_file:
                print(f"  CSV: {csv_file}")
            if json_file:
                print(f"  JSON: {json_file}")
                
        else:
            print("❌ 自動車販売店が見つかりませんでした")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("Google Maps API設定を確認してください")

if __name__ == '__main__':
    main()