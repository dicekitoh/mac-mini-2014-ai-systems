#!/usr/bin/env python3
"""
気象庁WebサイトからHTML内の発表時刻と警報詳細を抽出
"""

import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

class JMAWebDetailExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.area_codes = {
            '016000': '石狩地方',
            '015000': '空知地方'
        }
    
    def extract_web_details(self, area_code):
        """WebページからHTML詳細を抽出"""
        area_name = self.area_codes[area_code]
        url = f"https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code={area_code}"
        
        print(f"\n🔍 {area_name} Web詳細抽出中...")
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text()
            
            # 時刻パターンを詳細検索
            time_patterns = [
                (r'(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分発表', '年月日時分発表'),
                (r'(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分発表', '月日時分発表'),
                (r'(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分', '月日時分'),
                (r'(\d{1,2})日(\d{1,2})時(\d{1,2})分発表', '日時分発表'),
                (r'(\d{1,2})時(\d{1,2})分発表', '時分発表'),
                (r'令和(\d+)年(\d{1,2})月(\d{1,2})日(\d{1,2})時(\d{1,2})分', '令和年月日時分')
            ]
            
            found_times = []
            for pattern, description in time_patterns:
                matches = re.finditer(pattern, full_text)
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(full_text), match.end() + 100)
                    context = full_text[start:end].strip()
                    
                    found_times.append({
                        'time_text': match.group(),
                        'pattern_type': description,
                        'context': context,
                        'position': match.start()
                    })
            
            # 警報・注意報の詳細検索
            warning_patterns = [
                (r'([^。\n]*)(濃霧|暴風|大雨|洪水|大雪|暴風雪|雷|強風|乾燥|なだれ|着氷|着雪|融雪|霜|低温)(警報|注意報)([^。\n]*)', '警報注意報詳細'),
                (r'([^。\n]*)(石狩|空知)([^。\n]*)(警報|注意報)([^。\n]*)', '地域別警報'),
                (r'(発表|継続|解除|警戒|注意)([^。\n]*)', '状況キーワード')
            ]
            
            found_warnings = []
            for pattern, description in warning_patterns:
                matches = re.finditer(pattern, full_text)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(full_text), match.end() + 50)
                    context = full_text[start:end].strip()
                    
                    found_warnings.append({
                        'warning_text': match.group(),
                        'pattern_type': description,
                        'context': context,
                        'position': match.start()
                    })
            
            # HTMLタグから構造的情報を抽出
            structural_info = self.extract_structural_info(soup)
            
            return {
                'area_name': area_name,
                'area_code': area_code,
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': url,
                'found_times': found_times,
                'found_warnings': found_warnings,
                'structural_info': structural_info,
                'total_time_matches': len(found_times),
                'total_warning_matches': len(found_warnings),
                'page_title': soup.title.get_text(strip=True) if soup.title else '不明'
            }
            
        except Exception as e:
            return {
                'area_name': area_name,
                'area_code': area_code,
                'error': str(e),
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def extract_structural_info(self, soup):
        """HTMLの構造的情報を抽出"""
        structural = {
            'meta_tags': [],
            'script_content': [],
            'data_attributes': []
        }
        
        # metaタグから情報抽出
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') or meta.get('property'):
                content = meta.get('content', '')
                if any(keyword in content.lower() for keyword in ['weather', 'warning', 'alert', 'meteorological']):
                    structural['meta_tags'].append({
                        'name': meta.get('name') or meta.get('property'),
                        'content': content
                    })
        
        # data-*属性を持つ要素
        data_elements = soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
        for element in data_elements[:10]:  # 最初の10個
            data_attrs = {k: v for k, v in element.attrs.items() if k.startswith('data-')}
            if data_attrs:
                structural['data_attributes'].append({
                    'tag': element.name,
                    'data_attrs': data_attrs,
                    'text': element.get_text(strip=True)[:100]  # 最初の100文字
                })
        
        return structural
    
    def run_detailed_analysis(self):
        """詳細分析実行"""
        print("🌤️  気象庁Web詳細抽出システム")
        print("=" * 40)
        
        results = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'areas': {}
        }
        
        for area_code, area_name in self.area_codes.items():
            result = self.extract_web_details(area_code)
            results['areas'][area_code] = result
            
            # 結果表示
            self.display_result(result)
        
        return results
    
    def display_result(self, result):
        """結果表示"""
        if 'error' in result:
            print(f"❌ {result['area_name']}: エラー - {result['error']}")
            return
        
        area_name = result['area_name']
        print(f"\n📊 {area_name} Web詳細結果:")
        
        # 発表時刻情報
        times = result.get('found_times', [])
        print(f"  🕐 発表時刻: {len(times)}件検出")
        for i, time_info in enumerate(times[:5]):  # 最初の5件
            print(f"    {i+1}. {time_info['time_text']} ({time_info['pattern_type']})")
            print(f"       前後文脈: {time_info['context'][:80]}...")
        
        # 警報情報
        warnings = result.get('found_warnings', [])
        print(f"  ⚠️  警報詳細: {len(warnings)}件検出")
        for i, warning_info in enumerate(warnings[:3]):  # 最初の3件
            print(f"    {i+1}. {warning_info['pattern_type']}")
            print(f"       内容: {warning_info['warning_text'][:100]}...")
        
        # 構造情報
        structural = result.get('structural_info', {})
        meta_count = len(structural.get('meta_tags', []))
        data_count = len(structural.get('data_attributes', []))
        print(f"  🏗️  構造情報: meta {meta_count}件, data属性 {data_count}件")

if __name__ == "__main__":
    extractor = JMAWebDetailExtractor()
    result = extractor.run_detailed_analysis()