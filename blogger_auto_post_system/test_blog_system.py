#!/usr/bin/env python3
"""
ブログシステムテスト - 実行用スクリプト
Gemini AI & Claude Code 連携システムのテスト
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# パス追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'refactored_v2'))

from refactored_v2.blog_posting_service import BlogPostingService, PublishConfig
from refactored_v2.models import BlogPost

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_blog_system():
    """ブログシステムテスト"""
    print("🚀 Gemini AI & Claude Code 連携ブログシステム テスト開始")
    print("=" * 70)

    service = None
    try:
        # ブログサービス初期化
        service = BlogPostingService()

        # 対話式の認証セットアップ
        print("\n① 対話式の認証セットアップを実行します...")
        auth_success = await service.interactive_auth_setup()

        if not auth_success:
            print("\n❌ セットアップに失敗しました。処理を中断します。")
            return False

        print("✅ セットアップ完了：投稿準備OK")

        # システム状態確認
        print("\n② システム状態確認中...")
        status = await service.get_status()
        print(f"   初期化: {status.get('initialized', False)}")
        print(f"   認証状態: {status.get('auth_status', {}).get('is_valid', False)}")

        # テスト投稿実行
        print("\n③ テスト投稿実行中...")

        test_title = "✅ ワンクリックブロガー テスト投稿"
        test_content = f"""
# {test_title}

**テスト実行日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}  

## テスト概要

Gemini AI & Claude Code 連携により改修されたワンクリックブログ投稿システムのテストです。

### 改修された機能

1. **自動認証機能** - OAuth2.0トークンの自動更新
2. **ワンクリック投稿** - タイトル・本文入力で即時投稿
3. **エラー自動回復** - 最大3回の自動リトライ
4. **スケジュール投稿** - 指定日時での自動投稿

### AI連携の成果

- **Gemini AI**: アーキテクチャ設計、ベストプラクティス提案
- **Claude Code**: 実装のコード生成、システム安定化

## 結論

このテストにより、AI連携ブログ投稿システムが正常に動作することを確認できました。

---
*この投稿はワンクリックブロガーによる自動投稿です*
"""

        result = await service.one_click_post(
            title=test_title,
            content=test_content,
            labels=["テスト", "AI連携", "ワンクリックブロガー", "自動投稿"],
            config=PublishConfig(auto_retry=True, max_retries=3)
        )

        if result.success:
            print("\n✅ テスト投稿成功!")
            print(f"   投稿URL: {result.post_url}")
            print(f"   投稿ID: {result.post_id}")
            return True
        else:
            print(f"\n❌ テスト投稿失敗: {result.error}")
            if result.requires_reauth:
                print("   再認証が必要です。")
            return False

    except Exception as e:
        print(f"❌ テスト全体で予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # クリーンアップ
        if service:
            try:
                await service.cleanup()
            except:
                pass

async def main():
    """メイン処理"""
    from datetime import datetime
    
    print("--- ブログシステム安定化テスト ---")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = await test_blog_system()

    print("\n" + "=" * 70)
    if success:
        print("✅ テスト完了: システムは正常に動作しています！")
        print("   Gemini AI & Claude Code 連携による改修成功。")
    else:
        print("❌ テスト失敗: システムに問題があります。")
        print("   認証設定などを確認してください。")
    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ テスト中断")
    except Exception as e:
        print(f"❌ システムエラー: {e}")
