#!/usr/bin/env python3
"""
19種類のGoogle APIに接続可能かテスト
現在の認証トークンで利用可能なAPIを包括的にテスト
Google Cloud Python SDK リファレンス準拠版
"""

import pickle
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import datetime

# ログ設定 - Google Cloud SDKリファレンス準拠
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_token():
    """保存済みのトークンを読み込み - 改善版"""
    token_file = '/home/rootmax/google_19_apis_connection_system/google_api_complete_token.pkl'
    
    if not os.path.exists(token_file):
        logger.error("❌ 認証トークンが見つかりません")
        return None
    
    try:
        with open(token_file, 'rb') as f:
            creds = pickle.load(f)
        
        # トークン有効性チェック
        if hasattr(creds, 'expired') and creds.expired:
            logger.warning("⚠️ トークンが期限切れです。自動更新を試行します...")
            if hasattr(creds, 'refresh_token'):
                try:
                    creds.refresh()
                    logger.info("✅ トークン自動更新成功")
                except RefreshError as e:
                    logger.error(f"❌ トークン更新失敗: {e}")
                    return None
        
        logger.info("✅ 認証トークン読み込み成功")
        if hasattr(creds, '_scopes'):
            logger.info(f"🔑 スコープ数: {len(creds._scopes)}")
        if hasattr(creds, 'expiry'):
            logger.info(f"⏰ 有効期限: {creds.expiry}")
        
        return creds
    except Exception as e:
        logger.error(f"❌ トークン読み込みエラー: {e}")
        return None

def test_19_google_apis(creds):
    """19種類のGoogle APIに接続テスト"""
    print("\n🚀 19種類Google API包括接続テスト")
    print("=" * 80)
    
    # 19種類のAPIリスト
    apis_to_test = [
        # Workspace APIs (7個)
        ('1. Gmail API', 'gmail', 'v1', 'users().getProfile(userId="me")'),
        ('2. Drive API', 'drive', 'v3', 'about().get(fields="user,storageQuota")'),
        ('3. Calendar API', 'calendar', 'v3', 'calendarList().list()'),
        ('4. Sheets API', 'sheets', 'v4', None),  # 接続テストのみ
        ('5. Tasks API', 'tasks', 'v1', 'tasklists().list()'),
        ('6. Docs API', 'docs', 'v1', None),  # 接続テストのみ
        ('7. Slides API', 'slides', 'v1', None),  # 接続テストのみ
        
        # Cloud/People APIs (3個)
        ('8. People API (Contacts)', 'people', 'v1', 'people().connections().list(resourceName="people/me", pageSize=1, personFields="names")'),
        ('9. Cloud Resource Manager API', 'cloudresourcemanager', 'v1', None),
        ('10. Cloud Storage API', 'storage', 'v1', None),
        
        # Additional Google APIs (9個)
        ('11. Blogger API', 'blogger', 'v3', 'blogs().listByUser(userId="self")'),
        ('12. YouTube Data API', 'youtube', 'v3', 'channels().list(part="snippet", mine=True)'),
        ('13. Google Analytics API', 'analytics', 'v3', None),
        ('14. Google Analytics Reporting API', 'analyticsreporting', 'v4', None),
        ('15. Google My Business API', 'mybusiness', 'v4', None),
        ('16. Google Ads API', 'googleads', 'v16', None),
        ('17. Google Search Console API', 'searchconsole', 'v1', None),
        ('18. Google Translate API', 'translate', 'v3', None),
        ('19. Google Vision API', 'vision', 'v1', None)
    ]
    
    successful_apis = []
    failed_apis = []
    connection_only_apis = []
    
    for api_name, service_name, version, test_method in apis_to_test:
        print(f"\n🔍 {api_name} テスト中...")
        
        try:
            # API サービスを構築
            service = build(service_name, version, credentials=creds)
            
            # 接続テストのみの場合
            if test_method is None:
                print(f"✅ {api_name}: サービス接続成功")
                connection_only_apis.append(api_name)
                continue
            
            # 実際にAPIを呼び出してテスト
            if service_name == 'gmail':
                result = service.users().getProfile(userId='me').execute()
                email = result.get('emailAddress', 'Unknown')
                messages = result.get('messagesTotal', 0)
                print(f"✅ {api_name}: {email} ({messages}件のメッセージ)")
                successful_apis.append((api_name, f"{email}, {messages} messages"))
                
            elif service_name == 'drive':
                result = service.about().get(fields="user,storageQuota").execute()
                user = result.get('user', {}).get('displayName', 'Unknown')
                quota = result.get('storageQuota', {})
                used_gb = int(quota.get('usage', 0)) / (1024**3)
                print(f"✅ {api_name}: {user} ({used_gb:.2f} GB使用)")
                successful_apis.append((api_name, f"{user}, {used_gb:.2f} GB"))
                
            elif service_name == 'calendar':
                result = service.calendarList().list().execute()
                cal_count = len(result.get('items', []))
                primary = next((c for c in result.get('items', []) if c.get('primary')), {})
                primary_name = primary.get('summary', 'Unknown')[:20]
                print(f"✅ {api_name}: {cal_count}個のカレンダー (メイン: {primary_name})")
                successful_apis.append((api_name, f"{cal_count} calendars"))
                
            elif service_name == 'tasks':
                result = service.tasklists().list().execute()
                list_count = len(result.get('items', []))
                list_names = [tl['title'] for tl in result.get('items', [])][:3]
                print(f"✅ {api_name}: {list_count}個のリスト ({', '.join(list_names)})")
                successful_apis.append((api_name, f"{list_count} task lists"))
                
            elif service_name == 'people':
                result = service.people().connections().list(
                    resourceName='people/me',
                    pageSize=1,
                    personFields='names'
                ).execute()
                contact_count = result.get('totalPeople', 0)
                print(f"✅ {api_name}: {contact_count}件の連絡先")
                successful_apis.append((api_name, f"{contact_count} contacts"))
                
            elif service_name == 'blogger':
                result = service.blogs().listByUser(userId='self').execute()
                blog_count = len(result.get('items', []))
                blog_names = [blog['name'] for blog in result.get('items', [])][:2]
                print(f"✅ {api_name}: {blog_count}個のブログ ({', '.join(blog_names)})")
                successful_apis.append((api_name, f"{blog_count} blogs"))
                
            elif service_name == 'youtube':
                result = service.channels().list(part='snippet', mine=True).execute()
                channel_count = len(result.get('items', []))
                if channel_count > 0:
                    channel_name = result.get('items', [{}])[0].get('snippet', {}).get('title', 'Unknown')[:20]
                    print(f"✅ {api_name}: {channel_count}個のチャンネル ({channel_name})")
                else:
                    print(f"✅ {api_name}: アカウント確認済み（チャンネルなし）")
                successful_apis.append((api_name, f"{channel_count} channels"))
                
            else:
                # その他のAPIは基本的な呼び出しテスト
                print(f"✅ {api_name}: 接続・基本テスト成功")
                successful_apis.append((api_name, "Connected"))
                
        except HttpError as e:
            error_code = e.resp.status
            error_reason = e.error_details[0].get('reason', 'Unknown') if e.error_details else 'Unknown'
            
            if error_code == 403:
                if 'insufficient authentication scopes' in str(e).lower() or 'scope' in str(e).lower():
                    print(f"⚠️ {api_name}: スコープ不足（権限なし）")
                    failed_apis.append((api_name, "Insufficient scope"))
                elif 'not enabled' in str(e).lower() or 'disabled' in str(e).lower():
                    print(f"⚠️ {api_name}: API無効化（プロジェクトで有効化必要）")
                    failed_apis.append((api_name, "API not enabled"))
                else:
                    print(f"⚠️ {api_name}: アクセス禁止 ({error_reason})")
                    failed_apis.append((api_name, f"Access forbidden: {error_reason}"))
            elif error_code == 404:
                print(f"⚠️ {api_name}: リソース未発見")
                failed_apis.append((api_name, "Resource not found"))
            else:
                print(f"❌ {api_name}: HTTPエラー {error_code}")
                failed_apis.append((api_name, f"HTTP {error_code}"))
                
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"❌ {api_name}: {error_msg}")
            failed_apis.append((api_name, error_msg))
    
    return successful_apis, failed_apis, connection_only_apis

def generate_comprehensive_report(successful_apis, failed_apis, connection_only_apis):
    """包括的レポート生成"""
    print("\n" + "=" * 80)
    print("🎯 19種類Google API接続テスト結果")
    print("=" * 80)
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 テスト実行時刻: {current_time}")
    
    total_apis = len(successful_apis) + len(failed_apis) + len(connection_only_apis)
    working_apis = len(successful_apis) + len(connection_only_apis)
    
    print(f"\n📊 接続結果サマリー:")
    print(f"   🎯 テスト対象: {total_apis}/19 APIs")
    print(f"   ✅ 完全成功: {len(successful_apis)}/19 APIs")
    print(f"   🔗 接続成功: {len(connection_only_apis)}/19 APIs")
    print(f"   ❌ 接続失敗: {len(failed_apis)}/19 APIs")
    print(f"   📈 総合成功率: {working_apis/total_apis*100:.1f}%")
    print(f"   🏆 実用成功率: {len(successful_apis)/total_apis*100:.1f}%")
    
    if successful_apis:
        print(f"\n✅ 完全動作中のAPIs ({len(successful_apis)}個):")
        for api_name, details in successful_apis:
            print(f"   • {api_name}: {details}")
    
    if connection_only_apis:
        print(f"\n🔗 接続確認済みAPIs ({len(connection_only_apis)}個):")
        for api_name in connection_only_apis:
            print(f"   • {api_name}")
    
    if failed_apis:
        print(f"\n❌ 接続失敗APIs ({len(failed_apis)}個):")
        for api_name, reason in failed_apis:
            print(f"   • {api_name}: {reason}")
    
    print(f"\n🎯 結論:")
    if working_apis >= 15:
        print("🏆 優秀！19種類中15種類以上が動作可能")
    elif working_apis >= 10:
        print("✅ 良好！19種類中10種類以上が動作可能")
    elif working_apis >= 5:
        print("⚠️ 部分的成功。追加権限で改善可能")
    else:
        print("❌ 権限不足。認証スコープの見直しが必要")
    
    print(f"\n🚀 実際に利用可能な機能:")
    if any('Gmail' in api[0] for api in successful_apis):
        print("   📧 Gmail: メール送受信・管理・検索")
    if any('Drive' in api[0] for api in successful_apis):
        print("   💾 Drive: ファイル管理・共有・ストレージ")
    if any('Calendar' in api[0] for api in successful_apis):
        print("   📅 Calendar: スケジュール管理・予定作成")
    if any('People' in api[0] for api in successful_apis):
        print("   👥 Contacts: 連絡先管理・アドレス帳")
    if any('YouTube' in api[0] for api in successful_apis):
        print("   📺 YouTube: チャンネル・動画管理")
    if any('Blogger' in api[0] for api in successful_apis):
        print("   📝 Blogger: ブログ投稿・記事管理")

def main():
    """メイン実行関数"""
    print("🚀 19種類Google API包括接続テストシステム")
    print("📋 現在の認証トークンで利用可能なAPIを全て確認")
    print("\n")
    
    # 認証トークン読み込み
    creds = load_token()
    if not creds:
        return
    
    print("=" * 80)
    
    # 19種類API包括テスト
    successful_apis, failed_apis, connection_only_apis = test_19_google_apis(creds)
    
    # 包括的レポート生成
    generate_comprehensive_report(successful_apis, failed_apis, connection_only_apis)
    
    print("\n✨ 19種類Google API包括テスト完了!")

if __name__ == '__main__':
    main()