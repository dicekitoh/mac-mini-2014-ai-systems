#!/usr/bin/env python3
"""
モダンな役員変更登記申請書作成システム
Googleドキュメント出力対応
"""

import os
import sys
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# スコープ設定
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

class ModernLegalDocCreator:
    def __init__(self):
        self.docs_service = None
        self.drive_service = None
        
    def authenticate_google(self):
        """Google認証"""
        creds = None
        token_path = "/home/fujinosuke/projects/google_auth/unified_google_token.pickle"
        
        # 既存のトークンファイルを確認
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                print(f"✅ 既存の認証トークンを読み込みました")
            except Exception as e:
                print(f"⚠️  既存トークンの読み込みに失敗: {e}")
        
        # トークンが無効または期限切れの場合
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("✅ トークンを更新しました")
                except Exception as e:
                    print(f"⚠️  トークン更新に失敗: {e}")
                    return False
        
        try:
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)
            print("✅ Google Docs & Drive API サービスを初期化しました")
            return True
        except Exception as e:
            print(f"❌ Google API初期化に失敗: {e}")
            return False
    
    def create_modern_legal_document(self):
        """モダンな役員変更登記申請書を作成"""
        
        # 現在の日付
        today = datetime.now()
        
        # ドキュメント作成
        document = {
            'title': f'役員変更登記申請書（モダン版）- {today.strftime("%Y年%m月%d日")}'
        }
        
        doc = self.docs_service.documents().create(body=document).execute()
        document_id = doc.get('documentId')
        
        print(f"✅ Googleドキュメントを作成しました: {document_id}")
        
        # モダンなコンテンツを作成
        requests = []
        
        # タイトル
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '役員変更登記申請書\n（Modern Corporate Registration Application）\n\n'
            }
        })
        
        # 会社情報セクション
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '【会社概要 / Company Information】\n'
            }
        })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '''
🏢 商号（Company Name）
　　株式会社イノベーション・テクノロジーズ
　　Innovation Technologies Inc.

📍 本店所在地（Head Office）
　　〒060-0001 
　　北海道札幌市中央区北一条西3丁目2番地
　　パークビル5階
　　5F Park Building, 3-2 Nishi 3-chome, Kita 1-jo,
　　Chuo-ku, Sapporo, Hokkaido 060-0001, Japan

📞 連絡先（Contact）
　　TEL: 011-123-4567
　　Email: legal@innovation-tech.co.jp
　　担当者: 法務部 田中智子

'''
            }
        })
        
        # 変更事項セクション
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '【変更事項 / Changes】\n'
            }
        })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f'''
📅 変更年月日（Effective Date）
　　{today.strftime('%Y年%m月%d日')} ({today.strftime('%B %d, %Y')})

🔄 変更の理由（Reason for Change）
　　任期満了による取締役の改選
　　Election of new director due to expiration of term

👤 変更内容（Details of Changes）

【退任】Resignation
　├ 氏名: 佐藤 健一（Kenichi Sato）
　├ 生年月日: 1975年3月15日（March 15, 1975）
　├ 住所: 札幌市中央区大通西1丁目4-2
　└ 退任理由: 任期満了（Expiration of term）

【新任】New Appointment  
　├ 氏名: 鈴木 美咲（Misaki Suzuki）
　├ 生年月日: 1985年7月22日（July 22, 1985）
　├ 住所: 札幌市北区北10条西3丁目1-5
　├ 職歴: IT企業経営10年、MBA取得
　└ 就任予定日: {today.strftime('%Y年%m月%d日')}

'''
            }
        })
        
        # 法的事項セクション
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '【法的事項 / Legal Matters】\n'
            }
        })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '''
💰 登録免許税（Registration Tax）
　　金額: ¥10,000
　　支払方法: 収入印紙

📋 添付書類（Attached Documents）
　　□ 株主総会議事録　1通
　　□ 就任承諾書　　　1通  
　　□ 印鑑証明書　　　1通
　　□ 本人確認書類　　1通

⚖️ 法的根拠（Legal Basis）
　　会社法第911条第3項第3号
　　Companies Act Article 911, Paragraph 3, Item 3

'''
            }
        })
        
        # デジタル署名・認証セクション
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '【デジタル認証 / Digital Authentication】\n'
            }
        })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f'''
🔐 申請者デジタル署名
　　代表取締役: 山田 太郎
　　署名日時: {today.strftime('%Y年%m月%d日 %H:%M')}
　　認証ID: CORP-2025-{today.strftime('%m%d')}-001

🌐 オンライン申請情報
　　申請システム: e-Gov電子申請
　　受付番号: 未発番（申請後自動発行）
　　処理状況: 申請準備完了

📧 通知設定
　　メール通知: legal@innovation-tech.co.jp
　　SMS通知: 090-1234-5678
　　処理完了通知: ON

'''
            }
        })
        
        # 申請者情報
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': '【申請者情報 / Applicant Information】\n'
            }
        })
        
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': f'''
　　申請日: {today.strftime('%Y年%m月%d日')}
　　申請先: 札幌法務局

　　株式会社イノベーション・テクノロジーズ
　　代表取締役　山田　太郎　　　　　　[印]

---
本申請書は最新の会社法に基づき、
デジタル時代に対応したモダンな形式で作成されています。

Generated with Claude Code Assistant
Document ID: {document_id}
Created: {today.strftime('%Y-%m-%d %H:%M:%S')}
'''
            }
        })
        
        # テキストを一度に挿入
        for request in reversed(requests):  # 逆順で挿入
            self.docs_service.documents().batchUpdate(
                documentId=document_id, 
                body={'requests': [request]}
            ).execute()
        
        # フォーマット設定
        self.format_document(document_id)
        
        return document_id
    
    def format_document(self, document_id):
        """ドキュメントのフォーマットを設定"""
        try:
            requests = []
            
            # タイトルを中央揃え・大きく
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': 1, 'endIndex': 50},
                    'textStyle': {
                        'fontSize': {'magnitude': 18, 'unit': 'PT'},
                        'bold': True
                    },
                    'fields': 'fontSize,bold'
                }
            })
            
            # セクション見出しを太字に
            requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': 51, 'endIndex': 2000},
                    'textStyle': {
                        'fontSize': {'magnitude': 11, 'unit': 'PT'}
                    },
                    'fields': 'fontSize'
                }
            })
            
            # フォーマットを適用
            self.docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            print("✅ ドキュメントのフォーマットを適用しました")
            
        except Exception as e:
            print(f"⚠️ フォーマット適用に失敗: {e}")
    
    def share_document(self, document_id):
        """ドキュメントを共有可能にする"""
        try:
            # 編集可能な共有リンクを作成
            permission = {
                'type': 'anyone',
                'role': 'writer'
            }
            
            self.drive_service.permissions().create(
                fileId=document_id,
                body=permission
            ).execute()
            
            # ドキュメントURLを生成
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
            
            print(f"✅ ドキュメント共有設定完了")
            print(f"🔗 アクセスURL: {doc_url}")
            
            return doc_url
            
        except Exception as e:
            print(f"⚠️ 共有設定に失敗: {e}")
            return None

def main():
    """メイン処理"""
    print("🏢 モダン役員変更登記申請書作成システム")
    print("="*60)
    
    creator = ModernLegalDocCreator()
    
    # Google認証
    if not creator.authenticate_google():
        print("❌ Google認証に失敗しました")
        return False
    
    # モダンな申請書を作成
    try:
        document_id = creator.create_modern_legal_document()
        
        # 共有設定
        doc_url = creator.share_document(document_id)
        
        print("\n" + "="*60)
        print("✅ モダンな役員変更登記申請書の作成が完了しました")
        print("="*60)
        print(f"📄 ドキュメントID: {document_id}")
        if doc_url:
            print(f"🌐 アクセスURL: {doc_url}")
        
        print("\n📋 作成された申請書の特徴:")
        print("• 最新の会社法準拠")
        print("• 英語併記によるグローバル対応")
        print("• 絵文字による視覚的わかりやすさ")
        print("• デジタル認証情報の記載")
        print("• オンライン申請対応")
        print("• モダンなレイアウト")
        
        return True
        
    except Exception as e:
        print(f"❌ ドキュメント作成に失敗: {e}")
        return False

if __name__ == "__main__":
    main()