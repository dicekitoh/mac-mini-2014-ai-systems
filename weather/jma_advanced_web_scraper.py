#!/usr/bin/env python3
"""
気象庁警報・注意報サイト 高度WebスクレイピングシステムV2
JavaScriptで動的に読み込まれるデータも含めて取得
"""

import requests
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class JMAAdvancedWebScraper:
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
    
    def setup_selenium_driver(self):
        """Seleniumドライバーを設定"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"⚠️ Seleniumドライバー初期化失敗: {e}")
            return None
    
    def scrape_with_selenium(self, area_code):
        """Seleniumを使用してJavaScript実行後のページをスクレイピング"""
        area_name = self.area_codes[area_code]
        print(f"🔍 {area_name} Selenium高度スクレイピング実行中...")
        
        driver = self.setup_selenium_driver()
        if not driver:
            return None
        
        try:
            # 地域別ページにアクセス
            url = f"https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code={area_code}"
            driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 追加で動的コンテンツ読み込み待機
            time.sleep(3)
            
            # ページソースを取得
            page_source = driver.page_source
            
            # BeautifulSoupでパース
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 警報・注意報要素を詳細検索
            warning_data = self.extract_warnings_from_html(soup, area_name)
            
            # 発表時刻を詳細検索
            time_data = self.extract_time_info_from_html(soup)
            
            result = {
                'area_name': area_name,
                'area_code': area_code,
                'method': 'selenium',
                'url': url,
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'page_title': soup.title.get_text(strip=True) if soup.title else 'タイトル不明',
                'warnings': warning_data,
                'time_info': time_data,
                'full_text_keywords': self.search_keywords_in_text(page_source)
            }
            
            driver.quit()
            return result
            
        except Exception as e:
            print(f"❌ {area_name} Seleniumエラー: {str(e)}")
            if driver:
                driver.quit()
            return {
                'area_name': area_name,
                'area_code': area_code,
                'method': 'selenium',
                'error': str(e),
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def extract_warnings_from_html(self, soup, area_name):
        """HTMLから警報・注意報を詳細抽出"""
        warnings = []
        
        # 各種警報・注意報キーワードを検索
        warning_keywords = [
            '暴風警報', '大雨警報', '洪水警報', '大雪警報', '暴風雪警報',
            '濃霧注意報', '雷注意報', '乾燥注意報', 'なだれ注意報', '着氷注意報',
            '着雪注意報', '融雪注意報', '霜注意報', '低温注意報', '強風注意報',
            '大雨注意報', '洪水注意報', '大雪注意報', '風雪注意報'
        ]
        
        # 警報・注意報関連のクラス名やID
        warning_selectors = [
            '[class*="warning"]', '[class*="alert"]', '[class*="caution"]',
            '[id*="warning"]', '[id*="alert"]', '[class*="weather"]',
            '[class*="meteorological"]'
        ]
        
        # 各セレクターで要素を検索
        for selector in warning_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 0:
                    # 警報キーワードが含まれているかチェック
                    for keyword in warning_keywords:
                        if keyword in text:
                            warnings.append({
                                'type': 'detected_warning',
                                'keyword': keyword,
                                'text': text,
                                'selector': selector,
                                'element_tag': element.name
                            })
        
        # テキスト全体からも警報を検索
        full_text = soup.get_text()
        for keyword in warning_keywords:
            if keyword in full_text:
                # キーワード前後のコンテキストを取得
                matches = re.finditer(re.escape(keyword), full_text)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(full_text), match.end() + 50)
                    context = full_text[start:end].strip()
                    
                    warnings.append({
                        'type': 'text_search',
                        'keyword': keyword,
                        'context': context,
                        'position': match.start()
                    })
        
        return warnings
    
    def extract_time_info_from_html(self, soup):
        """HTMLから時刻情報を詳細抽出"""
        time_info = []
        
        # 時刻パターンを検索
        time_patterns = [
            r'\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分',
            r'\d{4}年\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分',
            r'\d{1,2}日\d{1,2}時\d{1,2}分',
            r'令和\d+年\d{1,2}月\d{1,2}日\d{1,2}時\d{1,2}分'
        ]
        
        full_text = soup.get_text()
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(full_text), match.end() + 30)
                context = full_text[start:end].strip()
                
                time_info.append({
                    'time_text': match.group(),
                    'pattern': pattern,
                    'context': context,
                    'position': match.start()
                })
        
        return time_info
    
    def search_keywords_in_text(self, text):
        """ページ全体から関連キーワードを検索"""
        keywords = {
            '石狩': text.count('石狩'),
            '空知': text.count('空知'),
            '警報': text.count('警報'),
            '注意報': text.count('注意報'),
            '発表': text.count('発表'),
            '解除': text.count('解除'),
            '継続': text.count('継続'),
            '濃霧': text.count('濃霧'),
            '強風': text.count('強風'),
            '大雨': text.count('大雨')
        }
        
        return {k: v for k, v in keywords.items() if v > 0}
    
    def get_api_data_detailed(self, area_code):
        """APIデータの詳細取得"""
        area_name = self.area_codes[area_code]
        api_url = f"https://www.jma.go.jp/bosai/warning/data/warning/{area_code}.json"
        
        try:
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            raw_data = response.json()
            
            # APIデータの詳細解析
            parsed_warnings = []
            report_time = raw_data.get('reportDatetime', 'unknown')
            
            for area_type in raw_data.get('areaTypes', []):
                for area in area_type.get('areas', []):
                    area_info = {
                        'area_name': area.get('name', 'unknown'),
                        'area_code': area.get('code', 'unknown'),
                        'warnings': []
                    }
                    
                    for warning in area.get('warnings', []):
                        warning_info = {
                            'name': warning.get('name', 'unknown'),
                            'code': warning.get('code', 'unknown'),
                            'status': warning.get('status', 'unknown')
                        }
                        area_info['warnings'].append(warning_info)
                    
                    if area_info['warnings']:  # 警報がある場合のみ追加
                        parsed_warnings.append(area_info)
            
            return {
                'area_name': area_name,
                'area_code': area_code,
                'method': 'api',
                'api_url': api_url,
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'report_datetime': report_time,
                'warnings': parsed_warnings,
                'raw_data': raw_data
            }
            
        except Exception as e:
            return {
                'area_name': area_name,
                'area_code': area_code,
                'method': 'api',
                'error': str(e),
                'access_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def run_comprehensive_analysis(self):
        """包括的な警報データ分析"""
        print("🌤️  気象庁警報・注意報 高度分析システム V2")
        print("=" * 60)
        
        results = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': 'comprehensive',
            'areas': {}
        }
        
        for area_code, area_name in self.area_codes.items():
            print(f"\n📍 {area_name} ({area_code}) 分析開始")
            
            area_result = {
                'area_name': area_name,
                'area_code': area_code,
                'web_data': None,
                'api_data': None,
                'final_recommendation': None
            }
            
            # Seleniumによる高度Webスクレイピング
            print(f"  🔍 Web高度スクレイピング実行...")
            web_data = self.scrape_with_selenium(area_code)
            area_result['web_data'] = web_data
            
            # API詳細データ取得
            print(f"  🔧 API詳細データ取得...")
            api_data = self.get_api_data_detailed(area_code)
            area_result['api_data'] = api_data
            
            # 結果比較・分析
            final_rec = self.analyze_and_recommend(web_data, api_data)
            area_result['final_recommendation'] = final_rec
            
            results['areas'][area_code] = area_result
            
            print(f"  ✅ {area_name} 分析完了")
        
        # 結果を保存
        filename = f"jma_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細結果を保存: {filename}")
        
        # サマリー表示
        self.display_summary(results)
        
        return results
    
    def analyze_and_recommend(self, web_data, api_data):
        """WebとAPIデータを分析して最終推奨を決定"""
        recommendation = {
            'priority_source': 'unknown',
            'summary': 'no_data',
            'warnings_detected': False,
            'time_info': 'unknown'
        }
        
        web_warnings = 0
        api_warnings = 0
        
        # Web警報カウント
        if web_data and 'warnings' in web_data:
            web_warnings = len(web_data['warnings'])
        
        # API警報カウント
        if api_data and 'warnings' in api_data:
            api_warnings = len(api_data['warnings'])
        
        # 優先順位決定
        if web_warnings > 0 and api_warnings > 0:
            recommendation.update({
                'priority_source': 'web_priority',
                'summary': f'Web: {web_warnings}件, API: {api_warnings}件 → Web優先',
                'warnings_detected': True,
                'recommended_data': web_data
            })
        elif web_warnings > 0:
            recommendation.update({
                'priority_source': 'web_only',
                'summary': f'Webのみ警報検出: {web_warnings}件',
                'warnings_detected': True,
                'recommended_data': web_data
            })
        elif api_warnings > 0:
            recommendation.update({
                'priority_source': 'api_only',
                'summary': f'APIのみ警報検出: {api_warnings}件',
                'warnings_detected': True,
                'recommended_data': api_data
            })
        else:
            recommendation.update({
                'priority_source': 'no_warnings',
                'summary': '警報・注意報なし',
                'warnings_detected': False
            })
        
        # 時刻情報
        if api_data and 'report_datetime' in api_data:
            recommendation['time_info'] = api_data['report_datetime']
        
        return recommendation
    
    def display_summary(self, results):
        """結果サマリーを表示"""
        print(f"\n📊 === 分析結果サマリー ===")
        
        for area_code, area_result in results['areas'].items():
            area_name = area_result['area_name']
            final_rec = area_result['final_recommendation']
            
            print(f"\n🏮 {area_name}")
            print(f"   優先ソース: {final_rec.get('priority_source', 'unknown')}")
            print(f"   サマリー: {final_rec.get('summary', 'unknown')}")
            print(f"   警報検出: {'あり' if final_rec.get('warnings_detected') else 'なし'}")
            print(f"   発表時刻: {final_rec.get('time_info', 'unknown')}")

if __name__ == "__main__":
    scraper = JMAAdvancedWebScraper()
    result = scraper.run_comprehensive_analysis()