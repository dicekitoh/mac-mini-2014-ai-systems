#!/usr/bin/env python3
"""
ブログ投稿システム - メインエントリーポイント
完全版統合システム
"""

import sys
import os
from datetime import datetime

# パス設定
sys.path.append(os.path.dirname(__file__))

from core.blog_system import BlogSystem

def main():
    """メイン実行関数"""
    print("="*80)
    print("🚀 ブログ投稿システム - 統合版")
    print("="*80)
    print("機能: AI記事生成・自動投稿・日付修正・API制限管理")
    print("")
    
    try:
        # システム初期化
        print("🔧 システム初期化中...")
        blog_system = BlogSystem()
        
        # システム状態確認
        status = blog_system.get_system_status()
        
        print(f"\n📊 システム状態確認:")
        print(f"   Gemini API: {status['api_limits']['gemini']['remaining']}/20 残り")
        print(f"   Blogger API: {status['api_limits']['blogger']['remaining']}/300 残り")
        print(f"   キャッシュ: {status['cache_stats']['cache_count']}件")
        print(f"   タイムゾーン: {'✅正常' if status['timezone_status'] else '❌問題あり'}")
        
        # インタラクティブモード
        interactive_mode(blog_system)
        
    except Exception as e:
        print(f"❌ システムエラー: {e}")
        print("\n🔧 トラブルシューティング:")
        print("1. APIキーが正しく設定されているか確認")
        print("2. 認証ファイル（credentials.json, token.pkl）が存在するか確認") 
        print("3. インターネット接続を確認")

def interactive_mode(blog_system: BlogSystem):
    """インタラクティブモード"""
    print(f"\n🎯 インタラクティブモード開始")
    print("利用可能なコマンド:")
    print("  1. post    - 新しい記事を投稿")
    print("  2. status  - システム状態確認")
    print("  3. test    - テスト投稿")
    print("  4. help    - ヘルプ表示")
    print("  5. quit    - 終了")
    print("")
    
    while True:
        try:
            command = input("📝 コマンド入力 > ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                print("👋 ブログ投稿システム終了")
                break
            
            elif command in ['1', 'post']:
                handle_post_command(blog_system, is_test=False)
            
            elif command in ['2', 'status']:
                handle_status_command(blog_system)
            
            elif command in ['3', 'test']:
                handle_post_command(blog_system, is_test=True)
            
            elif command in ['4', 'help']:
                show_help()
            
            elif command == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            
            else:
                print(f"❓ 不明なコマンド: {command}")
                print("'help' でコマンド一覧を確認してください")
            
        except KeyboardInterrupt:
            print("\n👋 ブログ投稿システム終了")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")

def handle_post_command(blog_system: BlogSystem, is_test: bool = False):
    """記事投稿コマンド処理"""
    print(f"\n📝 {'テスト' if is_test else '本番'}記事投稿")
    
    try:
        # テーマ入力
        topic = input("📋 記事テーマを入力 > ").strip()
        if not topic:
            print("❌ テーマが入力されていません")
            return
        
        # 文字数入力（オプション）
        length_input = input("📏 目標文字数 (デフォルト: 800) > ").strip()
        try:
            target_length = int(length_input) if length_input else 800
        except ValueError:
            target_length = 800
            print("📏 デフォルト文字数(800)を使用")
        
        # 確認
        print(f"\n📋 投稿内容確認:")
        print(f"   テーマ: {topic}")
        print(f"   目標文字数: {target_length}")
        print(f"   投稿種別: {'テスト投稿' if is_test else '本番投稿'}")
        
        confirm = input("\n実行しますか？ (y/N) > ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 投稿をキャンセルしました")
            return
        
        # 記事投稿実行
        print("\n🚀 記事投稿開始...")
        result = blog_system.complete_workflow(
            topic=topic,
            target_length=target_length,
            is_test=is_test
        )
        
        if result['success']:
            print(f"\n🎊 投稿成功!")
            print(f"   📰 URL: {result['post_url']}")
            print(f"   📏 文字数: {result['content_length']}")
            print(f"   ⭐ 品質: {result['quality_score']}/10")
            print(f"   📅 投稿日時: {result['published_jst']}")
        else:
            print(f"\n❌ 投稿失敗: {result['error']}")
            
    except Exception as e:
        print(f"❌ 投稿処理エラー: {e}")

def handle_status_command(blog_system: BlogSystem):
    """ステータス確認コマンド処理"""
    print(f"\n📊 システム状態確認")
    
    try:
        status = blog_system.get_system_status()
        
        # API制限状況
        gemini_info = status['api_limits']['gemini']
        blogger_info = status['api_limits']['blogger']
        
        print(f"\n🤖 Gemini API:")
        print(f"   使用済み: {gemini_info['used']}/{gemini_info['limit']}")
        print(f"   残り: {gemini_info['remaining']}")
        print(f"   状態: {'✅利用可能' if gemini_info['can_use'] else '❌制限到達'}")
        
        print(f"\n📝 Blogger API:")
        print(f"   使用済み: {blogger_info['used']}/{blogger_info['limit']}")
        print(f"   残り: {blogger_info['remaining']}")
        
        print(f"\n💾 キャッシュ:")
        cache_info = status['cache_stats']
        print(f"   ファイル数: {cache_info['cache_count']}件")
        print(f"   サイズ: {cache_info['cache_size_mb']}MB")
        
        print(f"\n⚙️ コンポーネント:")
        components = status['components_status']
        for comp_name, comp_status in components.items():
            print(f"   {comp_name}: {'✅正常' if comp_status else '❌問題あり'}")
        
    except Exception as e:
        print(f"❌ ステータス取得エラー: {e}")

def show_help():
    """ヘルプ表示"""
    print(f"\n📚 ヘルプ - ブログ投稿システム")
    print(f"="*50)
    
    print(f"\n🎯 主要機能:")
    print(f"  • AI記事生成 (Gemini 2.5-Flash)")
    print(f"  • 自動ブログ投稿 (Blogger API)")
    print(f"  • Markdown→HTML変換")
    print(f"  • 日付・タイムゾーン修正")
    print(f"  • API制限管理")
    print(f"  • インテリジェントキャッシュ")
    
    print(f"\n📋 使用方法:")
    print(f"  1. 'post' - 本番記事投稿")
    print(f"  2. 'test' - テスト記事投稿") 
    print(f"  3. 'status' - システム状態確認")
    print(f"  4. 'clear' - 画面クリア")
    print(f"  5. 'quit' - システム終了")
    
    print(f"\n⚠️ 重要な制限:")
    print(f"  • Gemini API: 20リクエスト/日")
    print(f"  • 制限到達時は自動でキャッシュ使用")
    print(f"  • 毎日09:00 (JST)にリセット")
    
    print(f"\n🔧 トラブルシューティング:")
    print(f"  • API制限: cache使用、翌日再試行")
    print(f"  • 認証エラー: credentials.json確認")
    print(f"  • 日付ずれ: 自動修正済み")
    
    print(f"\n📁 ファイル構成:")
    print(f"  • config/ - 認証・設定ファイル")
    print(f"  • core/ - システム本体")
    print(f"  • utils/ - ユーティリティ")
    print(f"  • docs/ - ドキュメント")
    print(f"  • cache/ - キャッシュファイル")

# クイックテスト関数
def quick_test():
    """クイックテスト実行"""
    print("🧪 クイックテスト実行")
    
    try:
        blog_system = BlogSystem()
        
        # ステータス確認のみ
        status = blog_system.get_system_status()
        
        print("✅ システム正常")
        print(f"   Gemini残り: {status['api_limits']['gemini']['remaining']}")
        print(f"   キャッシュ: {status['cache_stats']['cache_count']}件")
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")

if __name__ == "__main__":
    # コマンドライン引数チェック
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            quick_test()
        elif sys.argv[1] == "help":
            show_help()
        else:
            print(f"❓ 不明な引数: {sys.argv[1]}")
            print("利用可能: python main.py [test|help]")
    else:
        main()