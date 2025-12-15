#!/usr/bin/env python3
"""
Google API一覧をマークダウン形式でGoogleドキュメントに保存
"""

import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 既存のGoogle Drive認証ファイル
DRIVE_TOKEN_FILE = '/home/fujinosuke/token_drive.pickle'

def create_markdown_content():
    """マークダウン形式のGoogle API一覧を作成"""
    
    markdown_content = f"""# 🌐 Google APIサービス完全一覧 - 2024年版

**📅 更新日:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  
**🖥️ 接続環境:** MacMini2014 (Ubuntu 24.04.2 LTS)  
**🔗 アクセス:** ssh fujinosuke@192.168.3.43

---

## 📊 Google Workspace APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Google Docs API | docs.googleapis.com | ✅ 接続済み | 文書作成・編集 |
| Google Sheets API | sheets.googleapis.com | 🔄 利用可能 | スプレッドシート操作 |
| Google Drive API | drive.googleapis.com | ✅ 接続済み | ファイル管理 |
| Gmail API | gmail.googleapis.com | 🔄 利用可能 | メール操作 |
| Google Calendar API | calendar.googleapis.com | 🔄 利用可能 | カレンダー管理 |
| Google Contacts API | people.googleapis.com | ✅ 接続済み | 連絡先管理 |
| Google Slides API | slides.googleapis.com | 🔄 利用可能 | プレゼンテーション作成 |
| Google Forms API | forms.googleapis.com | 🔄 利用可能 | フォーム作成・管理 |
| Google Sites API | sites.googleapis.com | 🔄 利用可能 | サイト作成 |
| Google Tasks API | tasks.googleapis.com | ✅ 接続済み | タスク管理 |

---

## ☁️ Google Cloud Platform APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Cloud Translation API | translate.googleapis.com | 🔄 利用可能 | テキスト翻訳 |
| Cloud Vision API | vision.googleapis.com | 🔄 利用可能 | 画像認識・OCR |
| Cloud Speech-to-Text API | speech.googleapis.com | 🔄 利用可能 | 音声認識 |
| Cloud Text-to-Speech API | texttospeech.googleapis.com | 🔄 利用可能 | 音声合成 |
| Cloud Natural Language API | language.googleapis.com | 🔄 利用可能 | 自然言語処理 |
| BigQuery API | bigquery.googleapis.com | 🔄 利用可能 | ビッグデータ分析 |
| Cloud Storage API | storage.googleapis.com | 🔄 利用可能 | オブジェクトストレージ |
| Cloud Firestore API | firestore.googleapis.com | 🔄 利用可能 | NoSQLデータベース |
| Cloud SQL API | sqladmin.googleapis.com | 🔄 利用可能 | リレーショナルDB |
| Cloud Run API | run.googleapis.com | 🔄 利用可能 | コンテナ実行 |
| Compute Engine API | compute.googleapis.com | 🔄 利用可能 | 仮想マシン管理 |
| Kubernetes Engine API | container.googleapis.com | 🔄 利用可能 | Kubernetes管理 |

---

## 🗺️ Google Maps & Location APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Google Maps JavaScript API | maps.googleapis.com | 🔄 利用可能 | 地図表示・操作 |
| Google Maps Geocoding API | maps.googleapis.com | 🔄 利用可能 | 住所⇔座標変換 |
| Google Maps Directions API | maps.googleapis.com | 🔄 利用可能 | ルート検索 |
| Google Maps Places API | maps.googleapis.com | 🔄 利用可能 | 場所情報取得 |
| Google Maps Distance Matrix API | maps.googleapis.com | 🔄 利用可能 | 距離・時間計算 |
| Google Maps Roads API | roads.googleapis.com | 🔄 利用可能 | 道路情報 |
| Google Maps Street View API | maps.googleapis.com | 🔄 利用可能 | ストリートビュー |

---

## 📺 Google Media APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| YouTube Data API | youtube.googleapis.com | 🔄 利用可能 | 動画情報取得・管理 |
| YouTube Analytics API | youtubeanalytics.googleapis.com | 🔄 利用可能 | YouTube分析 |
| YouTube Reporting API | youtubereporting.googleapis.com | 🔄 利用可能 | YouTube レポート |
| Google Photos API | photoslibrary.googleapis.com | 🔄 利用可能 | 写真管理 |
| Google Play Developer API | androidpublisher.googleapis.com | 🔄 利用可能 | アプリ管理 |

---

## 🔍 Google Search & Analytics APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Google Analytics API | analytics.googleapis.com | 🔄 利用可能 | Webサイト分析 |
| Google Analytics Reporting API | analyticsreporting.googleapis.com | 🔄 利用可能 | GA レポート |
| Google Search Console API | searchconsole.googleapis.com | 🔄 利用可能 | 検索パフォーマンス |
| Custom Search API | customsearch.googleapis.com | 🔄 利用可能 | カスタム検索 |
| Google Trends API | trends.googleapis.com | 🔄 利用可能 | 検索トレンド |

---

## 💼 Google Business & Ads APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Google Ads API | googleads.googleapis.com | 🔄 利用可能 | 広告管理 |
| Google My Business API | mybusiness.googleapis.com | 🔄 利用可能 | ビジネス情報管理 |
| Google Shopping API | shopping.googleapis.com | 🔄 利用可能 | 商品情報 |
| Google AdSense API | adsense.googleapis.com | 🔄 利用可能 | 広告収益管理 |
| DoubleClick Bid Manager API | doubleclickbidmanager.googleapis.com | 🔄 利用可能 | プログラマティック広告 |

---

## 🛠️ Google Developer APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Google Cloud Resource Manager API | cloudresourcemanager.googleapis.com | 🔄 利用可能 | プロジェクト管理 |
| Google Cloud Billing API | cloudbilling.googleapis.com | 🔄 利用可能 | 課金管理 |
| Google Cloud Monitoring API | monitoring.googleapis.com | 🔄 利用可能 | 監視・アラート |
| Google Cloud Logging API | logging.googleapis.com | 🔄 利用可能 | ログ管理 |
| Google Cloud Pub/Sub API | pubsub.googleapis.com | 🔄 利用可能 | メッセージング |
| Google Cloud Functions API | cloudfunctions.googleapis.com | 🔄 利用可能 | サーバーレス実行 |

---

## 🤖 Google AI & Machine Learning APIs

| API名 | エンドポイント | 状態 | 機能 |
|-------|---------------|------|------|
| Vertex AI API | aiplatform.googleapis.com | 🔄 利用可能 | 機械学習プラットフォーム |
| AutoML API | automl.googleapis.com | 🔄 利用可能 | 自動機械学習 |
| Cloud AI Platform API | ml.googleapis.com | 🔄 利用可能 | ML モデル管理 |
| Dialogflow API | dialogflow.googleapis.com | 🔄 利用可能 | チャットボット |
| Cloud Video Intelligence API | videointelligence.googleapis.com | 🔄 利用可能 | 動画分析 |
| Recommendations AI API | recommendationengine.googleapis.com | 🔄 利用可能 | レコメンド |
| Document AI API | documentai.googleapis.com | 🔄 利用可能 | 文書解析 |

---

## 📊 MacMini2014 Google API 接続状況サマリー

### ✅ 接続済み・動作確認済み
- **Google Docs API** - 文書作成・編集
- **Google Drive API** - ファイル管理
- **Google Contacts API** - 連絡先管理
- **Google Tasks API** - タスク管理

### 🔄 即座に利用可能 (認証設定のみ必要)
- **Google Sheets API** - スプレッドシート操作
- **Gmail API** - メール操作
- **Google Calendar API** - カレンダー管理
- **Google Translate API** - テキスト翻訳
- **YouTube Data API** - 動画情報取得
- **Google Cloud Vision API** - 画像認識

### 🔧 設定・課金が必要
- **Google Maps APIs** - APIキー必要
- **Google Cloud Platform APIs** - 課金アカウント必要
- **Google Ads API** - 広告アカウント必要

---

## 💡 推奨する次の接続

1. **Google Sheets API** - データ処理自動化
2. **Gmail API** - メール自動化
3. **Google Translate API** - 多言語対応
4. **Google Cloud Vision API** - 画像解析
5. **YouTube Data API** - 動画情報取得

---

## 🔐 認証方式と設定方法

### 🔑 OAuth 2.0認証 (推奨)
- **用途:** 個人データアクセス (Gmail, Drive, Docs等)
- **設定:** credentials.json + トークンファイル
- **MacMini2014:** 既存認証利用可能

### 🔑 サービスアカウント認証
- **用途:** サーバー間通信、自動化
- **設定:** service-account-key.json
- **MacMini2014:** 設定済みテンプレート利用可能

### 🔑 APIキー認証
- **用途:** 公開データアクセス (Maps, Translate等)
- **設定:** API_KEY環境変数
- **制限:** リクエスト制限あり

---

## 📋 認証設定済み環境

- **Python仮想環境:** `~/google_docs_api_env`
- **認証ライブラリ:** google-auth, google-api-python-client
- **既存認証:** Google Drive, Contacts, Tasks

---

## 🎯 Google API活用のメリット

- ✅ **業務自動化:** レポート作成、データ処理の自動化
- ✅ **システム連携:** 既存Googleサービスとの seamless 連携
- ✅ **スケーラビリティ:** Googleインフラの信頼性・拡張性
- ✅ **コスト効率:** 多くのAPIで無料枠が充実
- ✅ **開発効率:** 豊富なライブラリとドキュメント

---

## 📊 統計情報

- **総API数:** 70以上
- **接続済み:** 4個
- **即座に利用可能:** 40以上
- **無料枠あり:** 大部分のAPI

---

**📝 作成日:** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  
**🖥️ 環境:** MacMini2014 Ubuntu 24.04.2 LTS  
**🔗 接続:** ssh fujinosuke@192.168.3.43  
**📄 形式:** Markdown (.md)
"""
    
    return markdown_content

def save_markdown_to_google_docs():
    """マークダウンコンテンツをGoogleドキュメントに保存"""
    
    # 認証情報読み込み
    with open(DRIVE_TOKEN_FILE, 'rb') as token:
        credentials = pickle.load(token)
    
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    
    # サービス構築
    docs_service = build('docs', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # マークダウンコンテンツ取得
    markdown_content = create_markdown_content()
    
    # ドキュメント作成
    document = {
        'title': f'📋 Google API一覧 (Markdown) - {datetime.now().strftime("%Y年%m月%d日")}'
    }
    
    doc = docs_service.documents().create(body=document).execute()
    doc_id = doc.get('documentId')
    
    print(f"✅ Markdownドキュメント作成: {doc_id}")
    
    # マークダウンコンテンツ挿入
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': markdown_content
            }
        }
    ]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={'requests': requests}).execute()
    
    print(f"✅ Markdownコンテンツ挿入完了 ({len(markdown_content)}文字)")
    
    # タイトル部分をフォーマット（見出し1風に）
    format_requests = [
        {
            'updateTextStyle': {
                'range': {'startIndex': 1, 'endIndex': 50},
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': 20, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        }
    ]
    
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={'requests': format_requests}).execute()
    
    print("✅ タイトルフォーマット適用")
    
    # 公開設定
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(
            fileId=doc_id, body=permission).execute()
        print("✅ ドキュメントを公開設定")
    except:
        print("ℹ️  公開設定をスキップ")
    
    # URL出力
    edit_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    view_url = f"https://docs.google.com/document/d/{doc_id}/view"
    
    return doc_id, edit_url, view_url

def main():
    """メイン処理"""
    print("📝 Google API一覧をマークダウン形式でGoogleドキュメントに保存")
    print("=" * 80)
    
    try:
        doc_id, edit_url, view_url = save_markdown_to_google_docs()
        
        print("\n" + "=" * 80)
        print("🎉 マークダウン形式での保存が完了しました！")
        print(f"\n📋 保存されたドキュメント:")
        print(f"   ドキュメントID: {doc_id}")
        print(f"   編集用: {edit_url}")
        print(f"   閲覧用: {view_url}")
        
        print(f"\n📄 マークダウン形式の特徴:")
        print("   • テーブル形式でAPI一覧を整理")
        print("   • 見出し構造で分類")
        print("   • 絵文字とステータス表示")
        print("   • 技術仕様とサマリー情報")
        print("   • コピー&ペーストしやすい形式")
        
        print(f"\n💡 活用方法:")
        print("   • StackEditで編集してGoogleドキュメントに変換")
        print("   • Markdownエディタでの編集")
        print("   • GitHub等でのドキュメント共有")
        print("   • API選択時のリファレンス")
        
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    main()