#!/usr/bin/env python3
"""
気象庁警報・注意報 簡易Web優先システム
実際のWebページの内容とAPIを比較して、相違があればWeb情報を優先表示
"""

import requests
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup

class JMASimpleWebPriority:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.area_codes = {
            '016000': '石狩地方',
            '015000': '空知地方'
        }
    
    def get_web_page_content(self, area_code):
        """Webページの内容を取得"""
        area_name = self.area_codes[area_code]
        url = f"https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code={area_code}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            # ページから警報関連キーワードを検索
            warning_keywords = ['警報', '注意報', '濃霧', '強風', '大雨', '大雪', '暴風', '雷']
            found_keywords = {}
            
            for keyword in warning_keywords:
                count = page_text.count(keyword)
                if count > 0:
                    found_keywords[keyword] = count
            
            # 時刻情報を検索
            time_matches = re.findall(r'\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分', page_text)
            
            return {
                'area_name': area_name,
                'area_code': area_code,
                'source': 'web',
                'url': url,
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'keywords_found': found_keywords,
                'time_matches': time_matches,
                'page_title': soup.title.get_text(strip=True) if soup.title else '不明',
                'total_keywords': sum(found_keywords.values()) if found_keywords else 0
            }
            
        except Exception as e:
            return {
                'area_name': area_name,
                'area_code': area_code,
                'source': 'web',
                'error': str(e),
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_api_data(self, area_code):
        """APIから詳細データを取得"""
        area_name = self.area_codes[area_code]
        api_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
        
        try:
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # APIから警報情報を抽出
            warnings_summary = []
            total_warnings = 0
            
            for area_type in data.get('areaTypes', []):
                for area in area_type.get('areas', []):
                    for warning in area.get('warnings', []):
                        warning_name = warning.get('name', '不明')
                        warnings_summary.append(warning_name)
                        total_warnings += 1
            
            return {
                'area_name': area_name,
                'area_code': area_code,
                'source': 'api',
                'api_url': api_url,
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'report_datetime': data.get('reportDatetime', '不明'),
                'warnings_summary': warnings_summary,
                'total_warnings': total_warnings,
                'raw_data': data
            }
            
        except Exception as e:
            return {
                'area_name': area_name,
                'area_code': area_code,
                'source': 'api',
                'error': str(e),
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def compare_and_prioritize(self, web_data, api_data):
        """WebとAPIを比較してWeb優先で統合"""
        area_name = web_data.get('area_name', api_data.get('area_name', '不明'))
        
        comparison = {
            'area_name': area_name,
            'comparison_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'web_status': 'success' if 'error' not in web_data else 'error',
            'api_status': 'success' if 'error' not in api_data else 'error',
            'priority_source': 'web',
            'final_data': {},
            'differences_detected': False
        }
        
        # Web情報の処理
        if 'error' not in web_data:
            web_keywords = web_data.get('total_keywords', 0)
            web_time = web_data.get('time_matches', [])
            
            comparison['final_data'].update({
                'primary_source': 'web',
                'web_keywords_count': web_keywords,
                'web_time_info': web_time,
                'web_found_keywords': web_data.get('keywords_found', {}),
                'web_access_time': web_data.get('access_time')
            })
        
        # API情報の処理
        if 'error' not in api_data:
            api_warnings = api_data.get('total_warnings', 0)
            api_time = api_data.get('report_datetime', '不明')
            
            comparison['final_data'].update({
                'api_warnings_count': api_warnings,
                'api_report_time': api_time,
                'api_warnings_list': api_data.get('warnings_summary', []),
                'api_access_time': api_data.get('access_time')
            })
            
            # 差異検出
            web_keywords = web_data.get('total_keywords', 0) if 'error' not in web_data else 0
            if web_keywords != api_warnings:
                comparison['differences_detected'] = True
                comparison['difference_details'] = f"Web: {web_keywords}件 vs API: {api_warnings}件"
        
        # Web優先の最終判定
        if comparison['web_status'] == 'success':
            comparison['final_data']['recommended_source'] = 'web'
            comparison['final_data']['reason'] = 'Web情報を優先使用'
        elif comparison['api_status'] == 'success':
            comparison['final_data']['recommended_source'] = 'api'
            comparison['final_data']['reason'] = 'WebエラーのためAPI使用'
        else:
            comparison['final_data']['recommended_source'] = 'none'
            comparison['final_data']['reason'] = '両方ともエラー'
        
        return comparison
    
    def run_analysis(self):
        """メイン分析実行"""
        print("🌤️  気象庁警報・注意報 Web優先分析システム")
        print("=" * 50)
        
        results = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'priority_policy': 'web_first',
            'areas': {}
        }
        
        for area_code, area_name in self.area_codes.items():
            print(f"\n📍 {area_name} 分析中...")
            
            # Webデータ取得
            print(f"  🌐 Webページ解析...")
            web_data = self.get_web_page_content(area_code)
            
            # APIデータ取得
            print(f"  🔧 API取得...")
            api_data = self.get_api_data(area_code)
            
            # 比較・統合
            print(f"  ⚖️  Web優先統合...")
            comparison = self.compare_and_prioritize(web_data, api_data)
            
            results['areas'][area_code] = {
                'web_data': web_data,
                'api_data': api_data,
                'comparison': comparison
            }
            
            # 結果表示
            self.display_area_result(comparison)
        
        # 結果保存
        filename = f"jma_web_priority_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 結果保存: {filename}")
        print(f"🎯 Web優先分析完了")
        
        return results
    
    def display_area_result(self, comparison):
        """地域別結果を表示"""
        area_name = comparison['area_name']
        final_data = comparison['final_data']
        
        print(f"    📊 {area_name} 結果:")
        print(f"       推奨ソース: {final_data.get('recommended_source', 'unknown')}")
        print(f"       理由: {final_data.get('reason', 'unknown')}")
        
        if comparison['differences_detected']:
            print(f"       ⚠️  差異検出: {comparison.get('difference_details', 'unknown')}")
        else:
            print(f"       ✅ Web/API一致")
        
        # Web情報
        if 'web_keywords_count' in final_data:
            web_count = final_data['web_keywords_count']
            web_keywords = final_data.get('web_found_keywords', {})
            print(f"       🌐 Web: {web_count}件 {list(web_keywords.keys())}")
        
        # API情報
        if 'api_warnings_count' in final_data:
            api_count = final_data['api_warnings_count']
            api_time = final_data.get('api_report_time', '不明')
            print(f"       🔧 API: {api_count}件 発表時刻:{api_time}")

if __name__ == "__main__":
    analyzer = JMASimpleWebPriority()
    result = analyzer.run_analysis()