#!/usr/bin/env python3
"""
気象庁警報・注意報サイトから石狩・空知地方の情報を直接取得
WebサイトのリアルタイムHTML表示データを優先
"""

import requests
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time

class JMAWebWarningReader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 地域コードマッピング
        self.area_codes = {
            '016000': '石狩地方',
            '015000': '空知地方'
        }
    
    def get_web_warning_data(self):
        """Webサイトから警報データを直接スクレイピング"""
        print(f"=== 気象庁Webサイトからのデータ取得開始 ===")
        
        web_data = {}
        
        # 石狩・空知それぞれのページを確認
        for area_code, area_name in self.area_codes.items():
            print(f"\n{area_name}のデータ取得中...")
            
            # 地域別警報ページへのアクセス
            web_url = f"https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code={area_code}"
            
            try:
                response = self.session.get(web_url, timeout=10)
                response.raise_for_status()
                
                # HTMLパース
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 警報・注意報の要素を検索
                warning_elements = soup.find_all(['div', 'span', 'p'], 
                    class_=re.compile(r'warning|alert|caution', re.I))
                
                # 発表時刻を検索
                time_elements = soup.find_all(text=re.compile(r'\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分'))
                
                web_data[area_code] = {
                    'area_name': area_name,
                    'web_url': web_url,
                    'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'warning_elements': [elem.get_text(strip=True) for elem in warning_elements],
                    'time_elements': time_elements,
                    'page_title': soup.title.get_text(strip=True) if soup.title else 'タイトル不明'
                }
                
                print(f"✅ {area_name}: Webアクセス成功")
                
            except Exception as e:
                print(f"❌ {area_name}: Webアクセス失敗 - {str(e)}")
                web_data[area_code] = {
                    'area_name': area_name,
                    'error': str(e),
                    'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            time.sleep(1)  # リクエスト間隔調整
        
        return web_data
    
    def get_api_warning_data(self):
        """APIから警報データを取得（比較用）"""
        print(f"\n=== APIからのデータ取得（比較用） ===")
        
        api_data = {}
        
        for area_code, area_name in self.area_codes.items():
            api_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
            
            try:
                response = self.session.get(api_url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                api_data[area_code] = {
                    'area_name': area_name,
                    'api_url': api_url,
                    'data': data,
                    'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f"✅ {area_name}: API取得成功")
                
            except Exception as e:
                print(f"❌ {area_name}: API取得失敗 - {str(e)}")
                api_data[area_code] = {
                    'area_name': area_name,
                    'error': str(e),
                    'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        
        return api_data
    
    def compare_web_api_data(self, web_data, api_data):
        """WebデータとAPIデータを比較"""
        print(f"\n=== WebデータとAPIデータの比較 ===")
        
        comparison_result = {}
        
        for area_code in self.area_codes.keys():
            area_name = self.area_codes[area_code]
            print(f"\n--- {area_name} ---")
            
            web_info = web_data.get(area_code, {})
            api_info = api_data.get(area_code, {})
            
            # Web情報表示
            if 'error' not in web_info:
                print(f"📱 Web情報:")
                print(f"   アクセス時刻: {web_info.get('access_time', '不明')}")
                print(f"   ページタイトル: {web_info.get('page_title', '不明')}")
                print(f"   警報要素数: {len(web_info.get('warning_elements', []))}")
                
                # 警報要素の内容表示
                warning_elements = web_info.get('warning_elements', [])
                if warning_elements:
                    for i, element in enumerate(warning_elements[:5]):  # 最初の5個
                        if element:
                            print(f"   要素{i+1}: {element[:100]}...")
            else:
                print(f"📱 Web情報: エラー - {web_info.get('error')}")
            
            # API情報表示
            if 'error' not in api_info:
                print(f"🔧 API情報:")
                print(f"   アクセス時刻: {api_info.get('access_time', '不明')}")
                
                api_warnings = api_info.get('data', {})
                if api_warnings:
                    # 発表時刻を探す
                    report_datetime = api_warnings.get('reportDatetime', '不明')
                    print(f"   API発表時刻: {report_datetime}")
                    
                    # 警報内容を表示
                    alerts = api_warnings.get('areaTypes', [])
                    for alert_type in alerts:
                        areas = alert_type.get('areas', [])
                        for area in areas:
                            if area.get('warnings'):
                                print(f"   警報あり: {area.get('name', '地域名不明')}")
                                for warning in area.get('warnings', []):
                                    print(f"     - {warning.get('name', '警報名不明')}")
            else:
                print(f"🔧 API情報: エラー - {api_info.get('error')}")
            
            # 比較結果記録
            comparison_result[area_code] = {
                'area_name': area_name,
                'web_status': 'success' if 'error' not in web_info else 'error',
                'api_status': 'success' if 'error' not in api_info else 'error',
                'web_data': web_info,
                'api_data': api_info,
                'priority': 'web'  # Web優先
            }
        
        return comparison_result
    
    def extract_priority_data(self, comparison_result):
        """Web優先でデータを統合"""
        print(f"\n=== Web優先データ統合 ===")
        
        final_data = {
            'extraction_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'priority_source': 'web',
            'areas': {}
        }
        
        for area_code, result in comparison_result.items():
            area_name = result['area_name']
            print(f"\n--- {area_name} 最終データ ---")
            
            area_final = {
                'area_name': area_name,
                'area_code': area_code,
                'priority_source': 'web'
            }
            
            # Web情報を優先使用
            if result['web_status'] == 'success':
                web_data = result['web_data']
                area_final.update({
                    'source': 'web',
                    'access_time': web_data.get('access_time'),
                    'page_title': web_data.get('page_title'),
                    'warning_count': len(web_data.get('warning_elements', [])),
                    'warnings': web_data.get('warning_elements', [])
                })
                print(f"✅ Web情報を採用: 警報要素{len(web_data.get('warning_elements', []))}件")
                
            # WebがエラーならAPIを使用
            elif result['api_status'] == 'success':
                api_data = result['api_data']['data']
                area_final.update({
                    'source': 'api_fallback',
                    'access_time': result['api_data'].get('access_time'),
                    'report_datetime': api_data.get('reportDatetime'),
                    'api_data': api_data
                })
                print(f"⚠️ APIをフォールバック使用")
                
            else:
                area_final.update({
                    'source': 'error',
                    'web_error': result['web_data'].get('error'),
                    'api_error': result['api_data'].get('error')
                })
                print(f"❌ 両方エラー")
            
            final_data['areas'][area_code] = area_final
        
        return final_data
    
    def save_results(self, data, filename_prefix='jma_web_warning'):
        """結果をファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 結果を保存: {filename}")
        return filename
    
    def run(self):
        """メイン実行"""
        print("🌤️  気象庁警報・注意報 Web優先データリーダー")
        print("=" * 50)
        
        # Webデータ取得
        web_data = self.get_web_warning_data()
        
        # APIデータ取得（比較用）
        api_data = self.get_api_warning_data()
        
        # データ比較
        comparison = self.compare_web_api_data(web_data, api_data)
        
        # Web優先データ統合
        final_data = self.extract_priority_data(comparison)
        
        # 結果保存
        self.save_results(final_data)
        self.save_results(comparison, 'jma_comparison')
        
        print(f"\n🎯 処理完了")
        print(f"石狩地方・空知地方の警報情報をWeb優先で取得しました")
        
        return final_data

if __name__ == "__main__":
    reader = JMAWebWarningReader()
    result = reader.run()