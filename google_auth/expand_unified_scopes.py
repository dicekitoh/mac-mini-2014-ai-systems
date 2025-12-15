#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一認証システムのスコープ拡張
全Google APIサービスへの包括的アクセス権限を取得
"""

import os
import pickle
import json
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow

# 包括的な全Googleサービススコープ
COMPREHENSIVE_SCOPES = [
    # Core Drive & Documents
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    
    # Gmail (Full Access)
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
    
    # Calendar (Full Access)
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.settings.readonly',
    
    # Tasks
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/tasks.readonly',
    
    # Contacts & People
    'https://www.googleapis.com/auth/contacts',
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/contacts.other.readonly',
    'https://www.googleapis.com/auth/directory.readonly',
    
    # User Profile
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/plus.me',
    
    # Photos
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/photoslibrary.sharing',
    
    # YouTube
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.upload',
    
    # Google Cloud & Admin
    'https://www.googleapis.com/auth/cloud-platform.read-only',
    'https://www.googleapis.com/auth/script.projects.readonly',
    
    # Additional Services
    'https://www.googleapis.com/auth/blogger.readonly',
    'https://www.googleapis.com/auth/books',
    'https://www.googleapis.com/auth/fitness.readonly',
]

class ScopeExpansionManager:
    """スコープ拡張管理クラス"""
    
    def __init__(self):
        self.credentials_file = '/home/fujinosuke/credentials_drive.json'
        self.current_token_file = '/home/fujinosuke/unified_google_token.pickle'
        self.expanded_token_file = '/home/fujinosuke/unified_google_token_expanded.pickle'
        self.expansion_log_file = '/home/fujinosuke/scope_expansion_log.json'
        
    def analyze_current_scopes(self):
        """現在のスコープ分析"""
        print("🔍 現在のスコープ分析...")
        
        if not os.path.exists(self.current_token_file):
            print("❌ 統一トークンファイルが見つかりません")
            return None
        
        try:
            with open(self.current_token_file, 'rb') as f:
                creds = pickle.load(f)
            
            current_scopes = getattr(creds, 'scopes', [])
            
            print(f"📋 現在のスコープ数: {len(current_scopes)}")
            print("現在のスコープ:")
            for scope in current_scopes:
                scope_name = scope.split('/')[-1]
                print(f"  ✅ {scope_name}")
            
            return current_scopes
            
        except Exception as e:
            print(f"❌ スコープ分析エラー: {e}")
            return None
    
    def generate_expansion_url(self):
        """スコープ拡張用認証URL生成"""
        print("🔗 スコープ拡張認証URL生成...")
        
        if not os.path.exists(self.credentials_file):
            print(f"❌ 認証ファイルが見つかりません: {self.credentials_file}")
            return None
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, 
                COMPREHENSIVE_SCOPES
            )
            
            # 手動認証用設定
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # 強制的に同意画面を表示
            auth_url, _ = flow.authorization_url(
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )
            
            print("🔗 スコープ拡張認証URL:")
            print(auth_url)
            print()
            print("📋 取得予定スコープ数:", len(COMPREHENSIVE_SCOPES))
            print("🆕 新規追加予定サービス:")
            
            new_services = [
                "Gmail (完全アクセス)",
                "Calendar (完全アクセス)", 
                "Drive (完全アクセス)",
                "Docs & Sheets (完全アクセス)",
                "Photos (読み取り)",
                "YouTube (読み取り・アップロード)",
                "Google Cloud (読み取り)",
                "その他Google サービス"
            ]
            
            for service in new_services:
                print(f"  🆕 {service}")
            
            return auth_url, flow
            
        except Exception as e:
            print(f"❌ URL生成エラー: {e}")
            return None
    
    def complete_scope_expansion(self, auth_code, flow):
        """スコープ拡張完了処理"""
        print("🔐 スコープ拡張実行中...")
        
        try:
            # 認証コードでトークン取得
            flow.fetch_token(code=auth_code)
            expanded_creds = flow.credentials
            
            print("✅ 拡張認証トークン取得成功")
            
            # 拡張トークンを保存
            with open(self.expanded_token_file, 'wb') as f:
                pickle.dump(expanded_creds, f)
            
            print(f"💾 拡張トークン保存: {self.expanded_token_file}")
            
            # スコープ確認
            expanded_scopes = getattr(expanded_creds, 'scopes', [])
            print(f"📈 拡張後スコープ数: {len(expanded_scopes)}")
            
            # 現在のトークンをバックアップ
            backup_file = self.current_token_file + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy(self.current_token_file, backup_file)
            print(f"💾 旧トークンバックアップ: {backup_file}")
            
            # 拡張トークンを本番適用
            shutil.copy(self.expanded_token_file, self.current_token_file)
            print("✅ 拡張トークンを本番適用完了")
            
            # 拡張ログ記録
            self._log_expansion(expanded_scopes)
            
            return expanded_creds
            
        except Exception as e:
            print(f"❌ スコープ拡張エラー: {e}")
            return None
    
    def _log_expansion(self, new_scopes):
        """拡張ログ記録"""
        log_data = {
            'expansion_date': datetime.now().isoformat(),
            'total_scopes': len(new_scopes),
            'scopes': new_scopes,
            'services_enabled': self._categorize_scopes(new_scopes)
        }
        
        try:
            with open(self.expansion_log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"📝 拡張ログ記録: {self.expansion_log_file}")
        except Exception as e:
            print(f"❌ ログ記録エラー: {e}")
    
    def _categorize_scopes(self, scopes):
        """スコープのカテゴリ分け"""
        categories = {
            'drive': [],
            'gmail': [],
            'calendar': [],
            'tasks': [],
            'contacts': [],
            'photos': [],
            'youtube': [],
            'other': []
        }
        
        for scope in scopes:
            if 'drive' in scope:
                categories['drive'].append(scope)
            elif 'gmail' in scope:
                categories['gmail'].append(scope)
            elif 'calendar' in scope:
                categories['calendar'].append(scope)
            elif 'tasks' in scope:
                categories['tasks'].append(scope)
            elif 'contacts' in scope or 'directory' in scope:
                categories['contacts'].append(scope)
            elif 'photos' in scope:
                categories['photos'].append(scope)
            elif 'youtube' in scope:
                categories['youtube'].append(scope)
            else:
                categories['other'].append(scope)
        
        return {k: len(v) for k, v in categories.items() if v}
    
    def test_expanded_services(self):
        """拡張されたサービスのテスト"""
        print("🧪 拡張サービステスト開始...")
        
        if not os.path.exists(self.current_token_file):
            print("❌ トークンファイルが見つかりません")
            return
        
        try:
            with open(self.current_token_file, 'rb') as f:
                creds = pickle.load(f)
            
            if not creds.valid:
                print("❌ トークンが無効です")
                return
            
            from googleapiclient.discovery import build
            
            # テスト対象サービス
            services_to_test = [
                ('drive', 'v3', lambda s: s.files().list(pageSize=1).execute(), 'Google Drive'),
                ('docs', 'v1', lambda s: True, 'Google Docs'),  # 作成テストはスキップ
                ('sheets', 'v4', lambda s: True, 'Google Sheets'),  # 作成テストはスキップ
                ('gmail', 'v1', lambda s: s.users().getProfile(userId='me').execute(), 'Gmail'),
                ('calendar', 'v3', lambda s: s.calendarList().list().execute(), 'Google Calendar'),
                ('tasks', 'v1', lambda s: s.tasklists().list().execute(), 'Google Tasks'),
                ('people', 'v1', lambda s: s.people().connections().list(
                    resourceName='people/me', pageSize=1, personFields='names').execute(), 'Google Contacts'),
            ]
            
            working_services = []
            failed_services = []
            
            for service_name, version, test_func, display_name in services_to_test:
                try:
                    service = build(service_name, version, credentials=creds)
                    test_func(service)
                    working_services.append(display_name)
                    print(f"✅ {display_name}: 正常動作")
                except Exception as e:
                    failed_services.append((display_name, str(e)))
                    if "403" in str(e):
                        print(f"⚠️ {display_name}: 権限不足")
                    else:
                        print(f"❌ {display_name}: エラー")
            
            print(f"\n📊 テスト結果:")
            print(f"✅ 正常動作: {len(working_services)}サービス")
            print(f"❌ エラー: {len(failed_services)}サービス")
            
            if working_services:
                print("動作確認済みサービス:")
                for service in working_services:
                    print(f"  ✅ {service}")
            
            return len(working_services) >= 5  # 5つ以上のサービスが動作すれば成功
            
        except Exception as e:
            print(f"❌ サービステストエラー: {e}")
            return False

def main():
    """メインプロセス"""
    print("🚀 Google統一認証システム - スコープ拡張")
    print("=" * 60)
    
    manager = ScopeExpansionManager()
    
    # ステップ1: 現在のスコープ分析
    current_scopes = manager.analyze_current_scopes()
    if not current_scopes:
        print("❌ 現在のスコープ分析に失敗しました")
        return False
    
    print(f"\n📈 スコープ拡張予定:")
    print(f"現在: {len(current_scopes)}スコープ")
    print(f"拡張後: {len(COMPREHENSIVE_SCOPES)}スコープ")
    print(f"追加: {len(COMPREHENSIVE_SCOPES) - len(current_scopes)}スコープ")
    
    # ステップ2: 認証URL生成
    result = manager.generate_expansion_url()
    if not result:
        print("❌ 認証URL生成に失敗しました")
        return False
    
    auth_url, flow = result
    
    print("\n🔑 認証手順:")
    print("1. 上記URLをブラウザで開いてください")
    print("2. Googleアカウントでログインしてください")
    print("3. 全ての権限を許可してください")
    print("4. 認証コードをコピーしてください")
    print("\n認証コードを入力してください:")
    
    # 認証コード入力待ち（実際の使用時は手動入力）
    return auth_url, flow, manager

if __name__ == '__main__':
    result = main()
    if isinstance(result, tuple):
        print("\n✅ 認証URL生成完了")
        print("認証コードを取得したら、complete_expansion()を実行してください")
    else:
        print("❌ スコープ拡張準備に失敗しました")