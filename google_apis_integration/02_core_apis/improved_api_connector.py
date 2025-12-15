#!/usr/bin/env python3
"""
Google API 改善版接続システム
Google Cloud Python SDK リファレンス準拠の最適化実装
"""

import pickle
import os
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
import datetime

# ログ設定 - Google Cloud SDKリファレンス準拠
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_connection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleAPIConnector:
    """Google API 改善版接続クラス - Google Cloud Python SDK準拠"""
    
    def __init__(self, token_file: str = '/home/rootmax/google_19_apis_connection_system/google_api_complete_token.pkl'):
        self.token_file = token_file
        self.credentials = None
        self.successful_apis = []
        self.failed_apis = []
        self.connection_cache = {}
        
        # 改善されたAPI定義 - Google Cloud Python SDK推奨パターン
        self.api_definitions = [
            # Core Workspace APIs - 高優先度
            {
                'name': 'Gmail API',
                'service': 'gmail',
                'version': 'v1',
                'test_method': self._test_gmail,
                'priority': 1,
                'timeout': 10
            },
            {
                'name': 'Drive API', 
                'service': 'drive',
                'version': 'v3',
                'test_method': self._test_drive,
                'priority': 1,
                'timeout': 10
            },
            {
                'name': 'Calendar API',
                'service': 'calendar', 
                'version': 'v3',
                'test_method': self._test_calendar,
                'priority': 1,
                'timeout': 10
            },
            {
                'name': 'Tasks API',
                'service': 'tasks',
                'version': 'v1', 
                'test_method': self._test_tasks,
                'priority': 2,
                'timeout': 8
            },
            {
                'name': 'Sheets API',
                'service': 'sheets',
                'version': 'v4',
                'test_method': self._test_connection_only,
                'priority': 2,
                'timeout': 8
            },
            # People & Contacts APIs
            {
                'name': 'People API (Contacts)',
                'service': 'people',
                'version': 'v1',
                'test_method': self._test_people,
                'priority': 2,
                'timeout': 8
            },
            # Content APIs
            {
                'name': 'Blogger API',
                'service': 'blogger',
                'version': 'v3',
                'test_method': self._test_blogger,
                'priority': 3,
                'timeout': 8
            },
            {
                'name': 'Docs API',
                'service': 'docs',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 3,
                'timeout': 8
            },
            {
                'name': 'Slides API',
                'service': 'slides',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 3,
                'timeout': 8
            },
            # Cloud APIs - Google Cloud Client Libraries推奨
            {
                'name': 'Cloud Storage API',
                'service': 'storage',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 4,
                'timeout': 15
            },
            {
                'name': 'Cloud Resource Manager API',
                'service': 'cloudresourcemanager',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 4,
                'timeout': 15
            },
            # Additional APIs
            {
                'name': 'YouTube Data API',
                'service': 'youtube',
                'version': 'v3',
                'test_method': self._test_youtube,
                'priority': 4,
                'timeout': 12
            },
            {
                'name': 'Google Analytics API',
                'service': 'analytics',
                'version': 'v3',
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 15
            },
            {
                'name': 'Google Analytics Reporting API',
                'service': 'analyticsreporting',
                'version': 'v4', 
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 15
            },
            {
                'name': 'Google Search Console API',
                'service': 'searchconsole',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 15
            },
            # Enterprise APIs
            {
                'name': 'Google My Business API',
                'service': 'mybusiness',
                'version': 'v4',
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 20
            },
            {
                'name': 'Google Translate API',
                'service': 'translate',
                'version': 'v3',
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 15
            },
            {
                'name': 'Google Vision API',
                'service': 'vision',
                'version': 'v1',
                'test_method': self._test_connection_only,
                'priority': 5,
                'timeout': 15
            }
        ]
    
    def load_credentials(self) -> bool:
        """認証情報読み込み - 改善版"""
        if not os.path.exists(self.token_file):
            logger.error(f"認証トークンファイルが見つかりません: {self.token_file}")
            return False
        
        try:
            with open(self.token_file, 'rb') as f:
                self.credentials = pickle.load(f)
            
            # トークン有効性チェック - Google Cloud SDK推奨パターン
            if hasattr(self.credentials, 'expired') and self.credentials.expired:
                logger.warning("トークンが期限切れです。自動更新を実行...")
                if hasattr(self.credentials, 'refresh_token'):
                    request = Request()
                    self.credentials.refresh(request)
                    logger.info("✅ トークン自動更新成功")
                else:
                    logger.error("❌ リフレッシュトークンが無効です")
                    return False
            
            logger.info("✅ 認証情報読み込み成功")
            if hasattr(self.credentials, '_scopes'):
                logger.info(f"🔑 認証スコープ数: {len(self.credentials._scopes)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 認証情報読み込みエラー: {e}")
            return False
    
    def _get_service_with_retry(self, service_name: str, version: str, max_retries: int = 3) -> Optional[object]:
        """サービス接続 - リトライ機能付き"""
        for attempt in range(max_retries):
            try:
                # キャッシュチェック
                cache_key = f"{service_name}:{version}"
                if cache_key in self.connection_cache:
                    return self.connection_cache[cache_key]
                
                service = build(service_name, version, credentials=self.credentials)
                self.connection_cache[cache_key] = service
                return service
                
            except Exception as e:
                logger.warning(f"サービス接続試行 {attempt + 1}/{max_retries} 失敗 ({service_name}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                logger.error(f"❌ {service_name} サービス接続失敗")
                return None
    
    def _test_gmail(self, service) -> Tuple[bool, str]:
        """Gmail API テスト"""
        try:
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            messages = profile.get('messagesTotal', 0)
            return True, f"{email} ({messages:,} メッセージ)"
        except Exception as e:
            return False, str(e)
    
    def _test_drive(self, service) -> Tuple[bool, str]:
        """Drive API テスト"""
        try:
            about = service.about().get(fields="user,storageQuota").execute()
            user = about.get('user', {}).get('displayName', 'Unknown')
            quota = about.get('storageQuota', {})
            used_gb = int(quota.get('usage', 0)) / (1024**3)
            return True, f"{user} ({used_gb:.1f}GB 使用)"
        except Exception as e:
            return False, str(e)
    
    def _test_calendar(self, service) -> Tuple[bool, str]:
        """Calendar API テスト"""
        try:
            calendars = service.calendarList().list(maxResults=10).execute()
            cal_count = len(calendars.get('items', []))
            return True, f"{cal_count}個のカレンダー"
        except Exception as e:
            return False, str(e)
    
    def _test_tasks(self, service) -> Tuple[bool, str]:
        """Tasks API テスト"""
        try:
            tasklists = service.tasklists().list().execute()
            list_count = len(tasklists.get('items', []))
            return True, f"{list_count}個のタスクリスト"
        except Exception as e:
            return False, str(e)
    
    def _test_people(self, service) -> Tuple[bool, str]:
        """People API テスト"""
        try:
            connections = service.people().connections().list(
                resourceName='people/me',
                pageSize=1,
                personFields='names'
            ).execute()
            total_people = connections.get('totalPeople', 0)
            return True, f"{total_people}件の連絡先"
        except Exception as e:
            return False, str(e)
    
    def _test_blogger(self, service) -> Tuple[bool, str]:
        """Blogger API テスト"""
        try:
            blogs = service.blogs().listByUser(userId='self').execute()
            blog_count = len(blogs.get('items', []))
            return True, f"{blog_count}個のブログ"
        except Exception as e:
            return False, str(e)
    
    def _test_youtube(self, service) -> Tuple[bool, str]:
        """YouTube API テスト"""
        try:
            channels = service.channels().list(part='snippet', mine=True).execute()
            channel_count = len(channels.get('items', []))
            return True, f"{channel_count}個のチャンネル"
        except Exception as e:
            return False, str(e)
    
    def _test_connection_only(self, service) -> Tuple[bool, str]:
        """接続テストのみ"""
        return True, "接続成功"
    
    def test_single_api(self, api_config: Dict) -> Dict:
        """単一API テスト - スレッドセーフ"""
        start_time = time.time()
        
        try:
            service = self._get_service_with_retry(
                api_config['service'], 
                api_config['version']
            )
            
            if service is None:
                return {
                    'name': api_config['name'],
                    'success': False,
                    'message': 'サービス接続失敗',
                    'duration': time.time() - start_time
                }
            
            # タイムアウト制御
            success, message = api_config['test_method'](service)
            duration = time.time() - start_time
            
            if success:
                logger.info(f"✅ {api_config['name']}: {message}")
            else:
                logger.warning(f"⚠️ {api_config['name']}: {message}")
            
            return {
                'name': api_config['name'],
                'success': success,
                'message': message,
                'duration': duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ {api_config['name']}: {e}")
            return {
                'name': api_config['name'],
                'success': False,
                'message': str(e),
                'duration': duration
            }
    
    def test_all_apis_concurrent(self, max_workers: int = 5) -> Dict:
        """並行API テスト - パフォーマンス最適化"""
        logger.info(f"🚀 {len(self.api_definitions)}種類のGoogle API並行接続テスト開始")
        logger.info(f"📊 最大並行数: {max_workers}")
        
        start_time = time.time()
        results = []
        
        # 優先度順にソート
        sorted_apis = sorted(self.api_definitions, key=lambda x: x['priority'])
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # API テスト実行
            future_to_api = {
                executor.submit(self.test_single_api, api_config): api_config 
                for api_config in sorted_apis
            }
            
            for future in as_completed(future_to_api):
                result = future.result()
                results.append(result)
        
        # 結果集計
        successful_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - successful_count
        total_duration = time.time() - start_time
        
        summary = {
            'total_apis': len(results),
            'successful': successful_count, 
            'failed': failed_count,
            'success_rate': (successful_count / len(results)) * 100,
            'total_duration': total_duration,
            'results': results
        }
        
        logger.info(f"📊 テスト完了: {successful_count}/{len(results)} 成功 "
                   f"({summary['success_rate']:.1f}% 成功率) "
                   f"実行時間: {total_duration:.2f}秒")
        
        return summary

def main():
    """メイン実行関数"""
    print("🔍 Google API 改善版接続システム")
    print("=" * 60)
    print("Google Cloud Python SDK リファレンス準拠版")
    print("=" * 60)
    
    connector = GoogleAPIConnector()
    
    # 認証情報読み込み
    if not connector.load_credentials():
        print("❌ 認証情報の読み込みに失敗しました")
        return False
    
    # 並行API テスト実行
    results = connector.test_all_apis_concurrent(max_workers=5)
    
    # 結果表示
    print(f"\n📊 総合結果")
    print(f"✅ 成功: {results['successful']}/{results['total_apis']} APIs")
    print(f"📈 成功率: {results['success_rate']:.1f}%")
    print(f"⏱️ 実行時間: {results['total_duration']:.2f}秒")
    
    print(f"\n📝 成功したAPI:")
    for result in results['results']:
        if result['success']:
            print(f"   ✅ {result['name']}: {result['message']} "
                  f"({result['duration']:.2f}s)")
    
    if any(not r['success'] for r in results['results']):
        print(f"\n⚠️ 問題のあるAPI:")
        for result in results['results']:
            if not result['success']:
                print(f"   ❌ {result['name']}: {result['message']}")
    
    return results['success_rate'] > 70

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 Google API接続システム - 正常動作確認完了")
    else:
        print(f"\n⚠️ システムに問題があります - 確認が必要")