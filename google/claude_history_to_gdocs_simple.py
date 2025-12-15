#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
既存のGoogle Drive権限でテキストファイルをGoogle ドキュメントにアップロード
"""

import sys
import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

def upload_to_google_docs():
    """Claude Code使用履歴をGoogle ドキュメントにアップロード"""
    
    print("📤 Claude Code使用履歴をGoogle ドキュメントにアップロード中...")
    
    try:
        # 既存の認証情報を使用
        token_path = "/home/fujinosuke/token_drive.pickle"
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
        
        # トークンリフレッシュ
        if not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        
        # Drive API接続
        service = build('drive', 'v3', credentials=creds)
        
        # テキストファイル作成
        content = '''Claude Code 使用履歴まとめ
2025年5月6日～5月21日

【正確な日付順の作業記録】

■ 2025年5月6日
- dicekitoh環境でClaude Code使用開始
- ホームページ（Webサイト）作成 - 最初の作業

■ 2025年5月7日
- 最初のAPIキー作成（claude_code_key_itoh_nhkb）
- Claude Code本格使用開始

■ 2025年5月9日～12日
- 金融データ分析プロジェクト開始
- 家計データ分析、運転経費計算、ETC利用ルート分析
- データ可視化ツール作成

■ 2025年5月13日
- クレジット追加 $6.00（使用量増加）
- 車両管理システム（COROLLA_AXIO）開発開始

■ 2025年5月14日
- 2番目のAPIキー作成（claude_code_key_itoh_uzmj）
- 車両管理システム完成（メンテナンス履歴、PDF請求書処理）
- 仕入れデータ処理（shiire-d）プロジェクト

■ 2025年5月16日
- dicekitoh環境での作業終了
- root環境へ移行

■ 2025年5月19日
- クレジット追加 $5.00
- 2番目のAPIキー最終使用

■ 2025年5月21日
- rootmax環境へ移行（現在の環境）

【作成したプロジェクト詳細】

1. ホームページ作成（5月6日）
   - Webサイト作成
   - Claude Codeの初期学習

2. 金融データ分析（5月9日～）
   - analyze_finance.py - 家計データ分析
   - calculate_driving_expenses.py - 運転経費計算
   - etc_route_analysis.py - ETC利用ルート分析
   - visualize_finance.py - データ可視化

3. 車両管理システム（5月13日～14日）
   - COROLLA_AXIOプロジェクト
   - maintenance_history.html - メンテナンス履歴表示
   - extract_pdf_text.py - PDF請求書読み取り
   - read_invoice.py - 請求書データ抽出

4. 仕入れデータ処理（5月14日）
   - shiire-dプロジェクト
   - extract_car_info.py - 車両情報抽出
   - list_excel_files.py - Excelファイル一覧

【環境遷移】
- dicekitoh環境: 2025年5月6日～5月16日
- root環境: 2025年5月16日～5月21日
- rootmax環境: 2025年5月21日～現在

【APIキー・クレジット履歴】
- 5月1日: 無料クレジット $5.00
- 5月7日: APIキー作成 + クレジット $5.00
- 5月13日: クレジット追加 $6.00
- 5月14日: 2番目のAPIキー作成
- 5月19日: クレジット追加 $5.00
- 6月1日: 月次請求 $0.00（クレジット利用）

【現在の稼働システム】
- Contact Manager v2 Bot: 正常稼働中
- ToDo Manager Bot: 正常稼働中
- Google Drive API: 接続中
- Telegram API: 2個のBOTが正常動作

作成日時: 2025年6月15日
'''
        
        # 一時ファイル作成
        temp_file = "/tmp/claude_code_history.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Google ドキュメントとしてアップロード
        doc_name = f"Claude Code使用履歴_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        file_metadata = {
            'name': doc_name,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        media = MediaFileUpload(temp_file, 
                                mimetype='text/plain',
                                resumable=True)
        
        print(f"📄 ドキュメント名: {doc_name}")
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink,name'
        ).execute()
        
        # 一時ファイル削除
        os.remove(temp_file)
        
        print(f"\\n✅ Google ドキュメント作成成功！")
        print(f"📄 ドキュメント名: {file.get('name')}")
        print(f"🔗 URL: {file.get('webViewLink')}")
        print(f"🆔 ドキュメントID: {file.get('id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ アップロードエラー: {e}")
        return False

if __name__ == '__main__':
    upload_to_google_docs()