#!/usr/bin/env python3
"""
Google Docs API テストスクリプト
サービスアカウントキーファイルが必要です
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 設定
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# サービスアカウントキーファイルのパス
# 実際のファイルパスに変更してください
KEY_FILE = '/home/fujinosuke/google_docs_service_key.json'

def setup_credentials():
    """認証情報を設定"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            KEY_FILE, scopes=SCOPES)
        return credentials
    except FileNotFoundError:
        print(f"エラー: サービスアカウントキーファイルが見つかりません: {KEY_FILE}")
        print("Google Cloud Consoleからサービスアカウントキーをダウンロードして配置してください。")
        return None
    except Exception as e:
        print(f"認証エラー: {e}")
        return None

def create_services(credentials):
    """Google API サービスを作成"""
    try:
        docs_service = build('docs', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        return docs_service, drive_service
    except Exception as e:
        print(f"サービス作成エラー: {e}")
        return None, None

def create_document(docs_service, title):
    """新しいドキュメントを作成"""
    try:
        document = {'title': title}
        doc = docs_service.documents().create(body=document).execute()
        doc_id = doc.get('documentId')
        print(f"✅ ドキュメント作成成功")
        print(f"   タイトル: {title}")
        print(f"   ドキュメントID: {doc_id}")
        print(f"   URL: https://docs.google.com/document/d/{doc_id}/edit")
        return doc_id
    except HttpError as error:
        print(f"❌ ドキュメント作成エラー: {error}")
        return None

def insert_text(docs_service, document_id, text):
    """ドキュメントにテキストを挿入"""
    try:
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': text
                }
            }
        ]
        
        result = docs_service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}).execute()
        
        print(f"✅ テキスト挿入成功: {len(text)}文字")
        return result
    except HttpError as error:
        print(f"❌ テキスト挿入エラー: {error}")
        return None

def format_text(docs_service, document_id, start_index, end_index, bold=False, italic=False):
    """テキストをフォーマット"""
    try:
        requests = []
        
        if bold:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })
        
        if italic:
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start_index,
                        'endIndex': end_index
                    },
                    'textStyle': {'italic': True},
                    'fields': 'italic'
                }
            })
        
        if requests:
            result = docs_service.documents().batchUpdate(
                documentId=document_id, body={'requests': requests}).execute()
            print(f"✅ テキストフォーマット成功")
            return result
    except HttpError as error:
        print(f"❌ フォーマットエラー: {error}")
        return None

def read_document(docs_service, document_id):
    """ドキュメントを読み取り"""
    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        
        print(f"✅ ドキュメント読み取り成功")
        print(f"   タイトル: {document.get('title')}")
        
        # コンテンツの取得
        content = document.get('body', {}).get('content', [])
        text_content = ""
        
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for run in paragraph.get('elements', []):
                    if 'textRun' in run:
                        text_content += run['textRun'].get('content', '')
        
        print(f"   内容: {text_content.strip()}")
        return document
    except HttpError as error:
        print(f"❌ ドキュメント読み取りエラー: {error}")
        return None

def share_document(drive_service, document_id, email, role='reader'):
    """ドキュメントを共有"""
    try:
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        result = drive_service.permissions().create(
            fileId=document_id, body=permission).execute()
        
        print(f"✅ ドキュメント共有成功: {email} ({role})")
        return result
    except HttpError as error:
        print(f"❌ 共有エラー: {error}")
        return None

def main():
    """メイン処理"""
    print("🚀 Google Docs API テスト開始")
    print("=" * 50)
    
    # 認証情報の設定
    credentials = setup_credentials()
    if not credentials:
        return
    
    # サービスの作成
    docs_service, drive_service = create_services(credentials)
    if not docs_service or not drive_service:
        return
    
    # テストドキュメントの作成
    title = "Google Docs API テストドキュメント"
    doc_id = create_document(docs_service, title)
    if not doc_id:
        return
    
    # テキストの挿入
    sample_text = """Google Docs API テスト

このドキュメントはGoogle Docs APIを使用して作成されました。

主な機能:
• ドキュメントの作成
• テキストの挿入・編集
• フォーマットの適用
• ドキュメントの共有

作成日時: 2025年6月14日
作成者: Google Docs API テストスクリプト
"""
    
    insert_text(docs_service, doc_id, sample_text)
    
    # タイトルを太字にフォーマット
    format_text(docs_service, doc_id, 1, 18, bold=True)
    
    # ドキュメントの読み取り
    read_document(docs_service, doc_id)
    
    # 共有（オプション - 実際のメールアドレスに変更してください）
    # share_document(drive_service, doc_id, "your_email@example.com", "writer")
    
    print("=" * 50)
    print("✅ Google Docs API テスト完了")
    print(f"作成されたドキュメント: https://docs.google.com/document/d/{doc_id}/edit")

if __name__ == "__main__":
    main()