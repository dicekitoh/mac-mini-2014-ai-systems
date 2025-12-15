#!/usr/bin/env python3
"""
実際のOCRデータを使用した役所提出用役員変更登記申請書作成システム
"""

import os
from datetime import datetime

class OfficialLegalDocCreator:
    def __init__(self):
        self.output_dir = "/home/fujinosuke/ocr_inbox"
        
    def create_official_legal_html(self):
        """実際のOCRデータを使用して役所提出用申請書をHTMLで作成"""
        
        today = datetime.now()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>役員変更登記申請書 - 有限会社越後屋商店</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'MS Gothic', 'Hiragino Kaku Gothic Pro', 'Meiryo', monospace;
            line-height: 1.6;
            color: #000;
            background: white;
            padding: 40px;
            font-size: 14px;
        }}
        
        .document {{
            max-width: 210mm;
            margin: 0 auto;
            background: white;
            padding: 0;
        }}
        
        .title {{
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 40px;
            letter-spacing: 2px;
        }}
        
        .section {{
            margin-bottom: 25px;
        }}
        
        .section-item {{
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }}
        
        .section-label {{
            min-width: 200px;
            font-weight: bold;
            margin-right: 20px;
        }}
        
        .section-content {{
            flex: 1;
            border-bottom: 1px solid #000;
            padding-bottom: 2px;
            min-height: 20px;
        }}
        
        .indent {{
            margin-left: 40px;
        }}
        
        .double-indent {{
            margin-left: 80px;
        }}
        
        .signature-section {{
            margin-top: 60px;
            text-align: right;
            margin-right: 80px;
        }}
        
        .signature-date {{
            margin-bottom: 40px;
        }}
        
        .signature-info {{
            text-align: left;
            margin-bottom: 10px;
        }}
        
        .attachment-section {{
            margin-top: 50px;
        }}
        
        .attachment-title {{
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .attachment-list {{
            margin-left: 40px;
        }}
        
        .footer {{
            margin-top: 80px;
            text-align: center;
            font-size: 16px;
            font-weight: bold;
        }}
        
        .stamp-area {{
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 2px solid #000;
            margin-left: 20px;
            vertical-align: middle;
            position: relative;
        }}
        
        .stamp-area::after {{
            content: "印";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 12px;
            color: #666;
        }}
        
        .address-block {{
            line-height: 1.8;
            margin-bottom: 10px;
        }}
        
        .legal-basis {{
            font-size: 12px;
            color: #333;
            margin-top: 10px;
        }}
        
        @media print {{
            body {{
                padding: 20px;
            }}
            
            .stamp-area {{
                border: 2px solid #000;
            }}
        }}
    </style>
</head>
<body>
    <div class="document">
        <div class="title">
            役員変更登記申請書
        </div>
        
        <div class="section">
            <div class="section-item">
                <div class="section-label">１．商　　　号</div>
                <div class="section-content">有限会社越後屋商店</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-item">
                <div class="section-label">１．本　　　店</div>
                <div class="section-content">北海道札幌市南区川沿十三条二丁目1番51号</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-item">
                <div class="section-label">１．登記の事由</div>
                <div class="section-content">取締役の変更</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-item">
                <div class="section-label">１．登記すべき事項</div>
                <div class="section-content">
                    <div>平成20年10月20日</div>
                    <div class="indent">北海道札幌市中央区宮の森一条十五丁目5番12―305号</div>
                    <div class="double-indent">取締役荒井　尚辞任</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-item">
                <div class="section-label">１．登録免許税</div>
                <div class="section-content">金１０，０００円</div>
            </div>
        </div>
        
        <div class="attachment-section">
            <div class="section-item">
                <div class="section-label">１．添付書類</div>
                <div class="section-content">
                    <div class="attachment-list">
                        辞任届　　　　　　　１通
                    </div>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 60px; text-align: center;">
            上記のとおり登記の申請をします。
        </div>
        
        <div class="signature-section">
            <div class="signature-date">
                平成20年10月23日
            </div>
            
            <div class="signature-info">
                <div class="address-block">
                    北海道札幌市南区川沿十三条二丁目1番51号
                </div>
                <div>
                    申請人　有限会社越後屋商店
                </div>
            </div>
            
            <div class="signature-info" style="margin-top: 20px;">
                <div class="address-block">
                    北海道札幌市南区川沿十三条二丁目1番51号
                </div>
                <div>
                    代表取締役　佐藤　明美
                    <span class="stamp-area"></span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                連絡先の電話番号　（〇一一）五七三―〇七四〇
            </div>
        </div>
        
        <div class="footer">
            札幌法務局　御中
        </div>
        
        <!-- 収入印紙貼付台紙 -->
        <div style="page-break-before: always; margin-top: 100px;">
            <div class="title">
                収入印紙貼付台紙
            </div>
            
            <div style="margin-top: 60px; text-align: center;">
                <div style="border: 3px solid #000; width: 150px; height: 100px; margin: 0 auto; position: relative;">
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 14px;">
                        収　入<br>
                        印　紙<br>
                        <span style="font-size: 12px;">10,000円</span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 40px; font-size: 12px; color: #666;">
                ※収入印紙10,000円を貼付し、割印を押印してください。
            </div>
        </div>
        
        <!-- 辞任届 -->
        <div style="page-break-before: always; margin-top: 100px;">
            <div class="title">
                辞　任　届
            </div>
            
            <div style="margin-top: 60px; text-align: left; line-height: 2.0;">
                <p>
                　私は，このたび一身上の都合により，貴社の取締役を辞任いたしたく，お届けいたします。
                </p>
            </div>
            
            <div style="margin-top: 80px; text-align: right; margin-right: 100px;">
                <div style="margin-bottom: 40px;">
                    平成20年10月20日
                </div>
                
                <div style="text-align: left;">
                    <div class="address-block">
                        北海道札幌市中央区宮の森一条十五丁目5番12―305号
                    </div>
                    <div style="margin-top: 20px;">
                        荒井　尚
                        <span class="stamp-area"></span>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 80px; text-align: left;">
                <div style="margin-left: 60px;">
                    有限会社越後屋商店　御中
                </div>
            </div>
        </div>
        
        <!-- 受付番号票貼付欄 -->
        <div style="page-break-before: always; margin-top: 100px;">
            <div style="text-align: center; font-size: 16px; font-weight: bold; margin-bottom: 40px;">
                受付番号票貼付欄
            </div>
            
            <div style="border: 2px solid #000; width: 200px; height: 100px; margin: 0 auto; position: relative;">
                <div style="position: absolute; top: 10px; left: 10px; font-size: 12px; color: #666;">
                    ※法務局で発行される<br>受付番号票を貼付
                </div>
            </div>
            
            <div style="margin-top: 60px; font-size: 12px; color: #333;">
                <div class="legal-basis">
                    <strong>【法的根拠】</strong><br>
                    ・商業登記法第20条（登記の申請）<br>
                    ・商業登記法第21条（申請書の記載事項）<br>
                    ・商業登記法第24条（添付書面）<br>
                    ・会社法第911条第3項第3号（役員の変更登記）
                </div>
                
                <div style="margin-top: 30px;">
                    <strong>【提出書類一覧】</strong><br>
                    １．役員変更登記申請書　　　　　　　１通<br>
                    ２．辞任届（荒井尚）　　　　　　　　１通<br>
                    ３．収入印紙貼付台紙　　　　　　　　１通<br>
                    ４．受付番号票貼付欄　　　　　　　　１通
                </div>
                
                <div style="margin-top: 30px; font-size: 10px; color: #999;">
                    作成日: {today.strftime('%Y年%m月%d日')}<br>
                    元データ: 11-1-07法務局役員変更.rtf（OCR読み取り）<br>
                    作成システム: Claude Code Assistant
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        # HTMLファイルを保存
        timestamp = today.strftime('%Y%m%d_%H%M%S')
        filename = f"official_legal_document_{timestamp}.html"
        file_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ 役所提出用役員変更登記申請書を作成しました: {filename}")
            print(f"📁 保存場所: {file_path}")
            
            return file_path
            
        except Exception as e:
            print(f"❌ ファイル保存に失敗: {e}")
            return None

def main():
    """メイン処理"""
    print("🏛️ 役所提出用役員変更登記申請書作成システム")
    print("="*60)
    print("📋 OCRデータ: 有限会社越後屋商店（11-1-07法務局役員変更.rtf）")
    print("="*60)
    
    creator = OfficialLegalDocCreator()
    
    # 役所提出用申請書を作成
    file_path = creator.create_official_legal_html()
    
    if file_path:
        print("\n" + "="*60)
        print("✅ 役所提出用役員変更登記申請書の作成が完了しました")
        print("="*60)
        print(f"📄 ファイル名: {os.path.basename(file_path)}")
        print(f"📁 保存場所: {file_path}")
        
        print("\n📋 実際のOCRデータを使用した内容:")
        print("• 🏢 会社名: 有限会社越後屋商店")
        print("• 📍 本店: 北海道札幌市南区川沿十三条二丁目1番51号")
        print("• 👤 退任者: 荒井尚（取締役）")
        print("• 📅 退任日: 平成20年10月20日")
        print("• 💰 登録免許税: 10,000円")
        print("• 📞 連絡先: (011)573-0740")
        print("• 👩‍💼 代表取締役: 佐藤明美")
        
        print("\n📄 作成された書類:")
        print("• 📋 役員変更登記申請書（メインページ）")
        print("• 💴 収入印紙貼付台紙")
        print("• 📝 辞任届（荒井尚）")
        print("• 🎫 受付番号票貼付欄")
        
        print("\n🏛️ 役所提出用の特徴:")
        print("• 📐 正式な法務局フォーマット準拠")
        print("• 🖨️ A4印刷最適化")
        print("• 📋 必要書類完備")
        print("• ⚖️ 法的根拠明記")
        print("• 🔍 OCR元データ完全再現")
        
        print(f"\n📄 使用方法:")
        print(f"   1. ブラウザで {file_path} を開く")
        print(f"   2. 印刷してA4用紙に出力")
        print(f"   3. 収入印紙10,000円を貼付・割印")
        print(f"   4. 代表取締役印を押印")
        print(f"   5. 札幌法務局へ提出")
        
        return True
    else:
        print("❌ ドキュメント作成に失敗しました")
        return False

if __name__ == "__main__":
    main()