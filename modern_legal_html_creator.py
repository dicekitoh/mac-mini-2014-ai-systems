#!/usr/bin/env python3
"""
モダンな役員変更登記申請書作成システム（HTML版）
"""

import os
from datetime import datetime

class ModernLegalHTMLCreator:
    def __init__(self):
        self.output_dir = "/home/fujinosuke/ocr_inbox"
        
    def create_modern_legal_html(self):
        """モダンな役員変更登記申請書をHTMLで作成"""
        
        today = datetime.now()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>役員変更登記申請書（モダン版） - {today.strftime('%Y年%m月%d日')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 25px;
            border-radius: 10px;
            background: #f8f9ff;
            border-left: 5px solid #667eea;
        }}
        
        .section-title {{
            font-size: 1.4em;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title .emoji {{
            font-size: 1.2em;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 15px;
            margin: 15px 0;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #555;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .info-value {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #e1e5e9;
        }}
        
        .change-item {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border: 1px solid #e1e5e9;
        }}
        
        .change-type {{
            font-weight: 600;
            color: #dc3545;
            margin-bottom: 10px;
        }}
        
        .change-type.new {{
            color: #28a745;
        }}
        
        .person-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .docs-list {{
            list-style: none;
            padding: 0;
        }}
        
        .docs-list li {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            border: 1px solid #e1e5e9;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .signature-section {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #2d3436;
        }}
        
        .digital-auth {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}
        
        .footer {{
            background: #2d3436;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .footer .tech-info {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 15px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            background: #28a745;
            color: white;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            margin-left: 10px;
        }}
        
        @media (max-width: 768px) {{
            .info-grid, .person-info {{
                grid-template-columns: 1fr;
            }}
            
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>役員変更登記申請書</h1>
            <div class="subtitle">Modern Corporate Registration Application</div>
            <div class="status-badge">申請準備完了</div>
        </div>
        
        <div class="content">
            <!-- 会社情報 -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🏢</span>
                    会社概要 / Company Information
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>🏷️</span> 商号
                    </div>
                    <div class="info-value">
                        <strong>株式会社イノベーション・テクノロジーズ</strong><br>
                        <em>Innovation Technologies Inc.</em>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📍</span> 本店所在地
                    </div>
                    <div class="info-value">
                        〒060-0001<br>
                        北海道札幌市中央区北一条西3丁目2番地 パークビル5階<br>
                        <em>5F Park Building, 3-2 Nishi 3-chome, Kita 1-jo,<br>
                        Chuo-ku, Sapporo, Hokkaido 060-0001, Japan</em>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📞</span> 連絡先
                    </div>
                    <div class="info-value">
                        TEL: 011-123-4567<br>
                        Email: legal@innovation-tech.co.jp<br>
                        担当者: 法務部 田中智子
                    </div>
                </div>
            </div>
            
            <!-- 変更事項 -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🔄</span>
                    変更事項 / Changes
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📅</span> 変更年月日
                    </div>
                    <div class="info-value">
                        {today.strftime('%Y年%m月%d日')} ({today.strftime('%B %d, %Y')})
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📝</span> 変更の理由
                    </div>
                    <div class="info-value">
                        任期満了による取締役の改選<br>
                        <em>Election of new director due to expiration of term</em>
                    </div>
                </div>
                
                <!-- 退任者情報 -->
                <div class="change-item">
                    <div class="change-type">【退任】Resignation</div>
                    <div class="person-info">
                        <div><strong>氏名:</strong> 佐藤 健一</div>
                        <div><strong>Name:</strong> Kenichi Sato</div>
                        <div><strong>生年月日:</strong> 1975年3月15日</div>
                        <div><strong>Born:</strong> March 15, 1975</div>
                        <div><strong>住所:</strong> 札幌市中央区大通西1丁目4-2</div>
                        <div><strong>退任理由:</strong> 任期満了</div>
                    </div>
                </div>
                
                <!-- 新任者情報 -->
                <div class="change-item">
                    <div class="change-type new">【新任】New Appointment</div>
                    <div class="person-info">
                        <div><strong>氏名:</strong> 鈴木 美咲</div>
                        <div><strong>Name:</strong> Misaki Suzuki</div>
                        <div><strong>生年月日:</strong> 1985年7月22日</div>
                        <div><strong>Born:</strong> July 22, 1985</div>
                        <div><strong>住所:</strong> 札幌市北区北10条西3丁目1-5</div>
                        <div><strong>職歴:</strong> IT企業経営10年、MBA取得</div>
                    </div>
                </div>
            </div>
            
            <!-- 法的事項 -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">⚖️</span>
                    法的事項 / Legal Matters
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>💰</span> 登録免許税
                    </div>
                    <div class="info-value">
                        <strong>¥10,000</strong><br>
                        支払方法: 収入印紙
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📋</span> 添付書類
                    </div>
                    <div class="info-value">
                        <ul class="docs-list">
                            <li><span>📄</span> 株主総会議事録　1通</li>
                            <li><span>📝</span> 就任承諾書　1通</li>
                            <li><span>🆔</span> 印鑑証明書　1通</li>
                            <li><span>📋</span> 本人確認書類　1通</li>
                        </ul>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📖</span> 法的根拠
                    </div>
                    <div class="info-value">
                        会社法第911条第3項第3号<br>
                        <em>Companies Act Article 911, Paragraph 3, Item 3</em>
                    </div>
                </div>
            </div>
            
            <!-- デジタル認証 -->
            <div class="section digital-auth">
                <div class="section-title">
                    <span class="emoji">🔐</span>
                    デジタル認証 / Digital Authentication
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>✍️</span> デジタル署名
                    </div>
                    <div class="info-value">
                        代表取締役: 山田 太郎<br>
                        署名日時: {today.strftime('%Y年%m月%d日 %H:%M')}<br>
                        認証ID: CORP-2025-{today.strftime('%m%d')}-001
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>🌐</span> オンライン申請
                    </div>
                    <div class="info-value">
                        申請システム: e-Gov電子申請<br>
                        受付番号: 未発番（申請後自動発行）<br>
                        処理状況: 申請準備完了
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📧</span> 通知設定
                    </div>
                    <div class="info-value">
                        メール通知: legal@innovation-tech.co.jp<br>
                        SMS通知: 090-1234-5678<br>
                        処理完了通知: ON
                    </div>
                </div>
            </div>
            
            <!-- 申請者情報 -->
            <div class="section signature-section">
                <div class="section-title">
                    <span class="emoji">📋</span>
                    申請者情報 / Applicant Information
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>📅</span> 申請日
                    </div>
                    <div class="info-value">
                        {today.strftime('%Y年%m月%d日')}
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-label">
                        <span>🏛️</span> 申請先
                    </div>
                    <div class="info-value">
                        札幌法務局
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.8); border-radius: 10px;">
                    <div style="font-size: 1.2em; margin-bottom: 20px;">
                        <strong>株式会社イノベーション・テクノロジーズ</strong>
                    </div>
                    <div style="font-size: 1.1em;">
                        代表取締役　山田　太郎　　　　[印]
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div>
                本申請書は最新の会社法に基づき、<br>
                デジタル時代に対応したモダンな形式で作成されています。
            </div>
            <div class="tech-info">
                Generated with Claude Code Assistant<br>
                Created: {today.strftime('%Y-%m-%d %H:%M:%S')}<br>
                Format: Modern HTML5 + CSS3 Responsive Design
            </div>
        </div>
    </div>
    
    <script>
        // 印刷時の最適化
        window.addEventListener('beforeprint', function() {{
            document.body.style.background = 'white';
        }});
        
        window.addEventListener('afterprint', function() {{
            document.body.style.background = 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)';
        }});
        
        // ページ読み込み完了時の演出
        window.addEventListener('load', function() {{
            document.querySelector('.container').style.opacity = '0';
            document.querySelector('.container').style.transform = 'translateY(20px)';
            document.querySelector('.container').style.transition = 'all 0.6s ease';
            
            setTimeout(function() {{
                document.querySelector('.container').style.opacity = '1';
                document.querySelector('.container').style.transform = 'translateY(0)';
            }}, 100);
        }});
    </script>
</body>
</html>
"""
        
        # HTMLファイルを保存
        timestamp = today.strftime('%Y%m%d_%H%M%S')
        filename = f"modern_legal_document_{timestamp}.html"
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ モダンな役員変更登記申請書を作成しました: {filename}")
            print(f"📁 保存場所: {file_path}")
            
            return file_path
            
        except Exception as e:
            print(f"❌ ファイル保存に失敗: {e}")
            return None

def main():
    """メイン処理"""
    print("🏢 モダン役員変更登記申請書作成システム（HTML版）")
    print("="*70)
    
    creator = ModernLegalHTMLCreator()
    
    # モダンな申請書を作成
    file_path = creator.create_modern_legal_html()
    
    if file_path:
        print("\n" + "="*70)
        print("✅ モダンな役員変更登記申請書の作成が完了しました")
        print("="*70)
        print(f"📄 ファイル名: {os.path.basename(file_path)}")
        print(f"📁 保存場所: {file_path}")
        
        print("\n📋 作成された申請書の特徴:")
        print("• 📱 レスポンシブデザイン（スマホ・PC対応）")
        print("• 🎨 モダンなグラデーション＆カラーリング")
        print("• 🌍 英語併記によるグローバル対応")
        print("• 😊 絵文字による視覚的わかりやすさ")
        print("• 🔐 デジタル認証情報の記載")
        print("• 🌐 オンライン申請対応")
        print("• 🖨️ 印刷最適化")
        print("• ⚡ アニメーション効果")
        
        print(f"\n🌐 ブラウザで開くには:")
        print(f"   file://{file_path}")
        
        return True
    else:
        print("❌ ドキュメント作成に失敗しました")
        return False

if __name__ == "__main__":
    main()