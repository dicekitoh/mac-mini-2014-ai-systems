#!/usr/bin/env python3
"""
動作確認済みGoogle APIを使用した実用デモ
過去の実績に基づく確実に動作するAPI接続
"""

import pickle
import os
from googleapiclient.discovery import build
from datetime import datetime
import json

def test_available_tokens():
    """利用可能なトークンファイルをテスト"""
    
    token_candidates = [
        '/home/rootmax/data/03_backups/google_api_success_tokens.pkl',
        '/home/rootmax/data/03_backups/macmini_working_token.pickle',
        '/home/rootmax/data/03_backups/macmini_success_token.pickle',
        '/home/rootmax/data/03_backups/blogger_working_token.pickle',
        '/home/rootmax/macmini_contacts_complete_token_20251129_111044.pkl'
    ]
    
    working_credentials = None
    working_file = None
    
    for token_file in token_candidates:
        if os.path.exists(token_file):
            try:
                print(f"🔍 テスト中: {token_file}")
                with open(token_file, 'rb') as f:
                    creds = pickle.load(f)
                
                # Gmail API接続テスト
                try:
                    service = build('gmail', 'v1', credentials=creds)
                    profile = service.users().getProfile(userId='me').execute()
                    email = profile.get('emailAddress', 'Unknown')
                    
                    print(f"✅ 認証成功! {email}")
                    working_credentials = creds
                    working_file = token_file
                    break
                    
                except Exception as e:
                    print(f"❌ Gmail API テスト失敗: {e}")
                    
                # Calendar API接続テスト（Gmail失敗時）
                try:
                    service = build('calendar', 'v3', credentials=creds)
                    calendars = service.calendarList().list().execute()
                    cal_count = len(calendars.get('items', []))
                    
                    print(f"✅ Calendar API成功! {cal_count}個のカレンダー")
                    working_credentials = creds
                    working_file = token_file
                    break
                    
                except Exception as e:
                    print(f"❌ Calendar API テスト失敗: {e}")
                    continue
                    
            except Exception as e:
                print(f"❌ トークン読み込み失敗: {e}")
                continue
    
    return working_credentials, working_file

def comprehensive_api_test(creds):
    """包括的なGoogle API接続テスト"""
    print("\n🚀 包括的Google API接続テスト")
    print("=" * 60)
    
    apis_to_test = [
        ('Gmail', 'gmail', 'v1'),
        ('Calendar', 'calendar', 'v3'),
        ('Drive', 'drive', 'v3'),
        ('Tasks', 'tasks', 'v1'),
        ('Sheets', 'sheets', 'v4'),
        ('People (Contacts)', 'people', 'v1'),
        ('Blogger', 'blogger', 'v3')
    ]
    
    successful_apis = []
    failed_apis = []
    
    for api_name, service_name, version in apis_to_test:
        print(f"\n📡 {api_name} API テスト中...")
        try:
            service = build(service_name, version, credentials=creds)
            
            # 各APIに応じた簡単なテスト
            if service_name == 'gmail':
                result = service.users().getProfile(userId='me').execute()
                email = result.get('emailAddress', 'Unknown')
                messages = result.get('messagesTotal', 0)
                print(f"✅ {api_name}: {email} ({messages}件のメッセージ)")
                successful_apis.append((api_name, f"Email: {email}, Messages: {messages}"))
                
            elif service_name == 'calendar':
                result = service.calendarList().list().execute()
                cal_count = len(result.get('items', []))
                primary = next((c for c in result.get('items', []) if c.get('primary')), {})
                primary_name = primary.get('summary', 'Unknown')
                print(f"✅ {api_name}: {cal_count}個のカレンダー (メイン: {primary_name})")
                successful_apis.append((api_name, f"{cal_count} calendars, Primary: {primary_name}"))
                
            elif service_name == 'drive':
                result = service.about().get(fields='user, storageQuota').execute()
                user = result.get('user', {}).get('displayName', 'Unknown')
                quota = result.get('storageQuota', {})
                used_gb = int(quota.get('usage', 0)) / (1024**3)
                print(f"✅ {api_name}: ユーザー {user} (使用容量: {used_gb:.2f} GB)")
                successful_apis.append((api_name, f"User: {user}, Storage: {used_gb:.2f} GB"))
                
            elif service_name == 'tasks':
                result = service.tasklists().list().execute()
                list_count = len(result.get('items', []))
                list_names = [tl['title'] for tl in result.get('items', [])]
                print(f"✅ {api_name}: {list_count}個のタスクリスト ({', '.join(list_names)})")
                successful_apis.append((api_name, f"{list_count} task lists: {', '.join(list_names)}"))
                
            elif service_name == 'sheets':
                # Drive経由でスプレッドシートを確認
                drive_service = build('drive', 'v3', credentials=creds)
                sheets = drive_service.files().list(
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageSize=5,
                    fields="files(id, name)"
                ).execute()
                sheet_count = len(sheets.get('files', []))
                print(f"✅ {api_name}: {sheet_count}個のスプレッドシート利用可能")
                successful_apis.append((api_name, f"{sheet_count} spreadsheets available"))
                
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
                blog_names = [blog['name'] for blog in result.get('items', [])]
                print(f"✅ {api_name}: {blog_count}個のブログ ({', '.join(blog_names)})")
                successful_apis.append((api_name, f"{blog_count} blogs: {', '.join(blog_names)}"))
                
        except Exception as e:
            print(f"❌ {api_name} API: {e}")
            failed_apis.append((api_name, str(e)))
    
    return successful_apis, failed_apis

def gmail_practical_demo(creds):
    """実用的なGmail機能のデモ"""
    print("\n📧 Gmail実用機能デモ")
    print("=" * 40)
    
    try:
        gmail = build('gmail', 'v1', credentials=creds)
        
        # ラベル情報取得
        labels_result = gmail.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        user_labels = [l for l in labels if l['type'] == 'user']
        system_labels = [l for l in labels if l['type'] == 'system']
        
        print(f"🏷️ ラベル分析:")
        print(f"   カスタムラベル: {len(user_labels)}個")
        print(f"   システムラベル: {len(system_labels)}個")
        
        # 受信トレイ情報
        inbox = next((l for l in labels if l['name'] == 'INBOX'), None)
        if inbox:
            messages_total = inbox.get('messagesTotal', 0)
            messages_unread = inbox.get('messagesUnread', 0)
            print(f"📬 受信トレイ: 全{messages_total}件, 未読{messages_unread}件")
        
        # 最新メール5件の分析
        messages = gmail.users().messages().list(
            userId='me',
            maxResults=5,
            labelIds=['INBOX']
        ).execute()
        
        print(f"\n📮 最新メール{len(messages.get('messages', []))}件:")
        
        for i, msg in enumerate(messages.get('messages', [])[:3], 1):
            msg_detail = gmail.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = msg_detail.get('payload', {}).get('headers', [])
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '差出人不明')[:50]
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '件名なし')[:40]
            
            print(f"   {i}. {subject}...")
            print(f"      差出人: {sender}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail デモエラー: {e}")
        return False

def generate_summary_report(successful_apis, failed_apis, working_file):
    """結果サマリーレポートを生成"""
    print("\n" + "=" * 60)
    print("🎯 Google API接続テスト結果サマリー")
    print("=" * 60)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📅 テスト実行時刻: {current_time}")
    print(f"🔑 使用認証ファイル: {working_file}")
    
    print(f"\n📊 接続結果:")
    print(f"   ✅ 成功: {len(successful_apis)}/{len(successful_apis) + len(failed_apis)} APIs")
    print(f"   ❌ 失敗: {len(failed_apis)}/{len(successful_apis) + len(failed_apis)} APIs")
    print(f"   📈 成功率: {len(successful_apis)/(len(successful_apis) + len(failed_apis))*100:.1f}%")
    
    if successful_apis:
        print(f"\n✅ 動作中のGoogle APIs:")
        for api_name, details in successful_apis:
            print(f"   • {api_name}: {details}")
    
    if failed_apis:
        print(f"\n❌ 接続失敗APIs:")
        for api_name, error in failed_apis:
            print(f"   • {api_name}: {error}")
    
    print(f"\n🚀 実用可能な機能:")
    if any('Gmail' in api[0] for api in successful_apis):
        print("   📧 メール送受信・管理・検索・ラベル操作")
    if any('Calendar' in api[0] for api in successful_apis):
        print("   📅 カレンダー管理・予定作成・通知")
    if any('Drive' in api[0] for api in successful_apis):
        print("   💾 ファイル管理・共有・ダウンロード")
    if any('Tasks' in api[0] for api in successful_apis):
        print("   ✅ タスク管理・TODO作成")
    if any('People' in api[0] for api in successful_apis):
        print("   👥 連絡先管理・アドレス帳操作")
    if any('Blogger' in api[0] for api in successful_apis):
        print("   📝 ブログ投稿・記事管理")

def main():
    """メイン実行関数"""
    print("🚀 Google API実績検証・実用デモシステム")
    print("=" * 60)
    
    # 利用可能な認証情報をテスト
    print("📝 Step 1: 認証ファイルの検証")
    creds, working_file = test_available_tokens()
    
    if not creds:
        print("❌ 利用可能な認証情報が見つかりませんでした")
        return
    
    print(f"✅ 動作する認証ファイル: {working_file}")
    print("=" * 60)
    
    # 包括的API接続テスト
    print("📝 Step 2: 全Google API接続テスト")
    successful_apis, failed_apis = comprehensive_api_test(creds)
    
    print("=" * 60)
    
    # Gmail実用デモ（Gmail APIが動作する場合）
    if any('Gmail' in api[0] for api in successful_apis):
        print("📝 Step 3: Gmail実用機能デモ")
        gmail_practical_demo(creds)
        print("=" * 60)
    
    # 最終サマリーレポート
    generate_summary_report(successful_apis, failed_apis, working_file)
    
    print("\n✨ Google API実績検証・デモ完了!")

if __name__ == '__main__':
    main()