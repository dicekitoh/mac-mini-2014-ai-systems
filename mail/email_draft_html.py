#!/usr/bin/env python3
"""
メール下書きをHTML形式で表示するシステム
"""

import json
import sys
from datetime import datetime
import webbrowser
import os

class EmailDraftHTML:
    def __init__(self, contacts_file='contacts.json'):
        self.contacts_file = contacts_file
        self.contacts = self.load_contacts()
    
    def load_contacts(self):
        """連絡先情報を読み込む"""
        try:
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('contacts', [])
        except:
            return []
    
    def find_contact(self, name):
        """名前から連絡先を検索"""
        for contact in self.contacts:
            if name in contact['name']:
                return contact
        return None
    
    def create_first_visit_thank_you(self, name):
        """初回訪問お礼メールの作成"""
        contact = self.find_contact(name)
        if not contact:
            return None, None, f"{name}さんの連絡先が見つかりません"
        
        subject = "本日はありがとうございました"
        
        body = f"""{contact['name']}様

お世話になっております。

本日はお忙しい中、貴重なお時間をいただき誠にありがとうございました。

{contact['name']}様から直接お話を伺うことができ、大変勉強になりました。
特に、貴社の事業展開についてのお話は、私にとって新たな視点を与えていただきました。

今後とも末永くお付き合いいただければ幸いです。
何かお役に立てることがございましたら、お気軽にお申し付けください。

改めまして、本日は誠にありがとうございました。

今後ともよろしくお願いいたします。"""
        
        return contact['email'], subject, body
    
    def generate_html(self, email, subject, body):
        """HTMLファイルを生成"""
        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>メール下書き - {subject}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .email-header {{
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .email-field {{
            margin-bottom: 15px;
            display: flex;
            align-items: baseline;
        }}
        .field-label {{
            font-weight: bold;
            width: 80px;
            color: #666;
        }}
        .field-value {{
            flex: 1;
            color: #333;
        }}
        .email-body {{
            white-space: pre-wrap;
            line-height: 1.8;
            color: #333;
            font-size: 15px;
            margin-top: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .action-buttons {{
            margin-top: 30px;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            padding: 10px 30px;
            margin: 0 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }}
        .btn:hover {{
            background-color: #0056b3;
        }}
        .btn-secondary {{
            background-color: #6c757d;
        }}
        .btn-secondary:hover {{
            background-color: #5a6268;
        }}
        .timestamp {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <h1 style="text-align: center; color: #333;">メール下書き</h1>
        
        <div class="email-header">
            <div class="email-field">
                <span class="field-label">宛先:</span>
                <span class="field-value">{email}</span>
            </div>
            <div class="email-field">
                <span class="field-label">件名:</span>
                <span class="field-value">{subject}</span>
            </div>
        </div>
        
        <div class="email-body">{body}</div>
        
        <div class="action-buttons">
            <button class="btn" onclick="copyToClipboard()">本文をコピー</button>
            <button class="btn btn-secondary" onclick="window.print()">印刷</button>
        </div>
        
        <div class="timestamp">
            作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
        </div>
    </div>
    
    <script>
        function copyToClipboard() {{
            const body = `{body}`;
            navigator.clipboard.writeText(body).then(() => {{
                alert('本文をクリップボードにコピーしました');
            }}).catch(err => {{
                console.error('コピーに失敗しました:', err);
            }});
        }}
    </script>
</body>
</html>"""
        
        # HTMLファイルを保存
        filename = f"email_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename

def main():
    """初回訪問お礼メールのHTML生成"""
    creator = EmailDraftHTML()
    
    # 伊藤大輔さんへの初回訪問お礼メール作成
    email, subject, body = creator.create_first_visit_thank_you("伊藤大輔")
    
    if email:
        # HTMLファイル生成
        filename = creator.generate_html(email, subject, body)
        print(f"メール下書きを作成しました: {filename}")
        
        # ブラウザで開く
        abs_path = os.path.abspath(filename)
        file_url = f"file://{abs_path}"
        print(f"ブラウザで開いています: {file_url}")
        webbrowser.open(file_url)
    else:
        print(body)  # エラーメッセージ

if __name__ == "__main__":
    main()