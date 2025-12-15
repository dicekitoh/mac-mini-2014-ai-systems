#!/usr/bin/env python3
"""
Chrome安全ログインガイド
ブックマーク整理を保持したままGoogleアカウントにログインする方法
"""

import subprocess
import time

def create_login_guide():
    print("🔐 Chrome安全ログインガイド")
    print("=" * 50)
    
    print("\n⚠️ 重要な注意事項:")
    print("現在の新規プロファイル「Profile Fresh」は同期無効状態です。")
    print("Googleアカウントにログインすると同期が再開される可能性があります。")
    
    print("\n🛡️ 安全なログイン方法:")
    print("\n【方法1: 同期選択ログイン（推奨）】")
    print("1. Googleアカウントにログイン")
    print("2. 同期設定画面で「詳細設定」をクリック")
    print("3. 「ブックマーク」の同期を**オフ**にする")
    print("4. 他の項目（パスワード、履歴など）は必要に応じて同期")
    print("5. 「確認」をクリック")
    
    print("\n【方法2: 完全同期無効ログイン（最安全）】")
    print("1. Googleアカウントにログイン")
    print("2. 同期設定画面で「同期をオフにする」を選択")
    print("3. 「データを保持」を選択")
    print("4. これで認証のみでローカルデータ使用")
    
    print("\n【方法3: 別プロファイル併用（推奨）】")
    print("1. 現在の「Profile Fresh」は整理済みブックマーク専用")
    print("2. 別の新規プロファイルでGoogleログイン")
    print("3. 用途に応じてプロファイルを使い分け")
    
    print("\n🚨 ログイン時の警告サイン:")
    print("- 「ブックマークを同期しますか？」→ 「いいえ」")
    print("- 「既存データを置き換えますか？」→ 「キャンセル」")
    print("- 「同期を有効にしますか？」→ 「後で」")
    
    return True

def create_separate_profile():
    """Googleログイン専用の別プロファイルを作成"""
    try:
        print("\n🆕 Googleログイン専用プロファイルを作成しますか？")
        print("これにより、整理済みブックマークを保護できます。")
        
        # 新しいプロファイルでChromeを起動
        subprocess.Popen([
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
            "--profile-directory=Profile Login",
            "--new-window"
        ])
        
        print("🚀 Googleログイン専用プロファイル「Profile Login」で起動")
        print("このプロファイルでGoogleアカウントにログインしてください。")
        
        return True
    except Exception as e:
        print(f"❌ プロファイル作成エラー: {e}")
        return False

def main():
    create_login_guide()
    
    print(f"\n❓ どの方法を選択しますか？")
    print(f"1: 現在のProfile Freshでブックマーク同期のみオフにしてログイン")
    print(f"2: 現在のProfile Freshで完全同期オフログイン")
    print(f"3: 新しいプロファイルでGoogleログイン（推奨）")
    print(f"4: 何もしない（現在の状態を維持）")
    
    choice = input(f"\n選択肢を入力してください (1-4): ").strip()
    
    if choice == "1":
        print(f"\n📋 手順:")
        print(f"1. 現在のChromeでGoogleアカウントにログイン")
        print(f"2. 同期設定で「ブックマーク」のみオフ")
        print(f"3. 他の同期項目は自由に設定")
        
    elif choice == "2":
        print(f"\n📋 手順:")
        print(f"1. 現在のChromeでGoogleアカウントにログイン")
        print(f"2. 同期設定で「同期をオフにする」")
        print(f"3. 「データを保持」を選択")
        
    elif choice == "3":
        create_separate_profile()
        
    elif choice == "4":
        print(f"\n✅ 現在の整理済み状態を維持します")
        
    else:
        print(f"\n❌ 無効な選択です")
    
    print(f"\n💡 ヒント: 複数のプロファイルを使い分けることで")
    print(f"   整理済みブックマークと同期データを両方活用できます")

if __name__ == "__main__":
    main()