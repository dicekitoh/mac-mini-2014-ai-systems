#!/usr/bin/env python3
"""
Google API認証状況確認システム
各サービスごとの認証状況を詳細チェック
"""

import pickle
import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

print("🔍 Google API認証状況確認システム")
print("=" * 60)

# 主要なトークンファイルの場所
token_locations = {
    "統合認証": "/home/fujinosuke/projects/google_auth/unified_google_token.pickle",
    "Google Contacts": "/home/fujinosuke/google_contacts/token.pickle",
    "Google Drive": "/home/fujinosuke/projects/google_auth/token_drive.pickle",
    "Google Docs": "/home/fujinosuke/projects/google_auth/google_docs_token.pickle",
    "永続認証": "/home/fujinosuke/projects/google_auth/token_persistent.pickle",
    "連絡先リアル": "/home/fujinosuke/google/token_contacts_real.pickle",
    "Bot用連絡先": "/home/fujinosuke/google_contacts/contact_manager_v2_bot_github/token.pickle"
}

valid_tokens = []
all_scopes = set()

print("\n📋 各トークンファイルの状況:")
print("-" * 60)

for service_name, token_path in token_locations.items():
    print(f"\n🔐 {service_name}")
    print(f"   ファイル: {os.path.basename(token_path)}")
    
    if os.path.exists(token_path):
        try:
            # ファイル情報
            stat_info = os.stat(token_path)
            mod_time = datetime.fromtimestamp(stat_info.st_mtime)
            print(f"   サイズ: {stat_info.st_size} bytes")
            print(f"   更新日: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # トークン読み込み
            with open(token_path, "rb") as f:
                creds = pickle.load(f)
            
            # 認証状況確認
            is_valid = creds.valid if hasattr(creds, 'valid') else False
            is_expired = creds.expired if hasattr(creds, 'expired') else True
            
            print(f"   有効性: {'✅ 有効' if is_valid else '❌ 無効'}")
            print(f"   期限切れ: {'❌ 期限切れ' if is_expired else '✅ 有効期限内'}")
            
            # スコープ確認
            if hasattr(creds, "scopes") and creds.scopes:
                scopes = list(creds.scopes)
                print(f"   スコープ数: {len(scopes)}")
                
                # サービス別分類
                services = []
                if any("contacts" in scope for scope in scopes):
                    services.append("📞 Contacts")
                if any("drive" in scope for scope in scopes):
                    services.append("📁 Drive")
                if any("docs" in scope for scope in scopes):
                    services.append("📄 Docs")
                if any("gmail" in scope for scope in scopes):
                    services.append("📧 Gmail")
                if any("calendar" in scope for scope in scopes):
                    services.append("📅 Calendar")
                if any("tasks" in scope for scope in scopes):
                    services.append("✅ Tasks")
                if any("photos" in scope for scope in scopes):
                    services.append("📸 Photos")
                if any("sheets" in scope for scope in scopes):
                    services.append("📊 Sheets")
                
                print(f"   対応サービス: {' '.join(services) if services else '不明'}")
                
                # 全スコープ記録
                all_scopes.update(scopes)
                
                if is_valid:
                    valid_tokens.append((service_name, token_path, len(scopes), creds))
            else:
                print(f"   スコープ: なし")
                
        except Exception as e:
            print(f"   ❌ エラー: {str(e)[:50]}...")
    else:
        print(f"   ❌ ファイルが存在しません")

# 統計情報
print("\n" + "=" * 60)
print("📊 認証状況サマリー")
print("=" * 60)

print(f"📁 総トークンファイル数: {len(token_locations)}")
print(f"✅ 有効なトークン数: {len(valid_tokens)}")
print(f"🔐 総スコープ数: {len(all_scopes)}")

if valid_tokens:
    print(f"\n🎯 最多スコープ認証:")
    best_token = max(valid_tokens, key=lambda x: x[2])
    print(f"   サービス: {best_token[0]}")
    print(f"   スコープ数: {best_token[2]}")
    print(f"   ファイル: {os.path.basename(best_token[1])}")
    
    print(f"\n📋 有効な認証一覧:")
    for name, path, scope_count, creds in sorted(valid_tokens, key=lambda x: x[2], reverse=True):
        print(f"   • {name}: {scope_count}スコープ ({os.path.basename(path)})")

# 利用可能なGoogleサービス
print(f"\n🌐 利用可能なGoogleサービス:")
service_mapping = {
    "contacts": "📞 Google Contacts",
    "drive": "📁 Google Drive", 
    "docs": "📄 Google Docs",
    "gmail": "📧 Gmail",
    "calendar": "📅 Google Calendar",
    "tasks": "✅ Google Tasks",
    "photos": "📸 Google Photos",
    "sheets": "📊 Google Sheets",
    "userinfo": "👤 User Info"
}

available_services = []
for scope in all_scopes:
    for service_key, service_name in service_mapping.items():
        if service_key in scope.lower() and service_name not in available_services:
            available_services.append(service_name)

if available_services:
    for service in sorted(available_services):
        print(f"   ✅ {service}")
else:
    print("   ❌ 利用可能なサービスが見つかりません")

print(f"\n🔄 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")