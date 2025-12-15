#!/usr/bin/env python3
"""
Google 19種類 API システム状態確認スクリプト
実行前の環境確認用
"""

import os
import pickle
import sys
from datetime import datetime

def check_python_version():
    """Python バージョン確認"""
    print("🐍 Python バージョン確認")
    version = sys.version.split()[0]
    print(f"   バージョン: {version}")
    
    major, minor = map(int, version.split('.')[:2])
    if major >= 3 and minor >= 7:
        print("   ✅ Python 3.7 以上 - OK")
        return True
    else:
        print("   ❌ Python 3.7 以上が必要です")
        return False

def check_required_libraries():
    """必要ライブラリの確認"""
    print("\n📚 必要ライブラリ確認")
    
    required_libs = [
        'google.auth',
        'google_auth_oauthlib', 
        'googleapiclient',
        'google.cloud.vision',
        'google.cloud.storage',
        'google.cloud.bigquery',
        'requests',
        'pandas'
    ]
    
    missing_libs = []
    
    for lib in required_libs:
        try:
            __import__(lib.replace('-', '_').replace('.', '_'))
            print(f"   ✅ {lib}")
        except ImportError:
            print(f"   ❌ {lib} - 未インストール")
            missing_libs.append(lib)
    
    if missing_libs:
        print(f"\n💡 不足ライブラリのインストール:")
        print(f"   pip install -r requirements.txt")
        return False
    
    print("   ✅ 全ライブラリ確認完了")
    return True

def check_essential_files():
    """必須ファイルの確認"""
    print("\n📁 必須ファイル確認")
    
    files_status = {
        'credentials.json': {
            'required': True,
            'description': 'Google Cloud OAuth認証情報'
        },
        'google_api_complete_token.pkl': {
            'required': False, 
            'description': '19種類API認証済みトークン'
        },
        'test_19_google_apis.py': {
            'required': True,
            'description': 'メイン19API実行スクリプト（従来版）'
        },
        'improved_api_connector.py': {
            'required': True,
            'description': 'メイン19API実行スクリプト（改善版・推奨）'
        },
        'working_google_api_demo.py': {
            'required': True,
            'description': '実用デモスクリプト'
        },
        'setup_auth.py': {
            'required': True,
            'description': '認証セットアップスクリプト'
        },
        'requirements.txt': {
            'required': True,
            'description': 'ライブラリ依存関係（基本版）'
        },
        'requirements_improved.txt': {
            'required': True,
            'description': 'ライブラリ依存関係（改善版・推奨）'
        }
    }
    
    all_good = True
    
    for filename, info in files_status.items():
        exists = os.path.exists(filename)
        
        if exists:
            size = os.path.getsize(filename)
            print(f"   ✅ {filename} ({size} bytes)")
        else:
            if info['required']:
                print(f"   ❌ {filename} - 必須ファイルが見つかりません")
                print(f"      説明: {info['description']}")
                all_good = False
            else:
                print(f"   ⚠️ {filename} - 未作成（初回実行時に自動生成）")
                print(f"      説明: {info['description']}")
    
    return all_good

def check_token_status():
    """認証トークンの状態確認"""
    print("\n🔐 19種類API認証トークン状態確認")
    
    token_file = 'google_api_complete_token.pkl'
    
    if not os.path.exists(token_file):
        print("   ⚠️ トークンファイルが見つかりません")
        print("   💡 初回実行時は setup_auth.py を実行してください")
        return False
    
    try:
        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)
        
        print(f"   ✅ トークンファイル読み込み成功")
        
        # トークン有効期限確認
        if hasattr(credentials, 'expiry') and credentials.expiry:
            now = datetime.now().replace(tzinfo=credentials.expiry.tzinfo)
            if credentials.expiry > now:
                remaining = credentials.expiry - now
                print(f"   ✅ トークン有効 (残り: {remaining})")
            else:
                print(f"   ⚠️ トークン期限切れ (自動更新されます)")
        
        # スコープ確認
        if hasattr(credentials, '_scopes'):
            scopes = len(credentials._scopes)
            print(f"   📋 認証スコープ数: {scopes}種類")
            if scopes >= 15:
                print(f"   ✅ 十分なスコープが確保されています")
            else:
                print(f"   ⚠️ スコープ数が少ない可能性があります")
        
        return True
        
    except Exception as e:
        print(f"   ❌ トークン読み込みエラー: {e}")
        print(f"   💡 setup_auth.py を実行して認証を再セットアップしてください")
        return False

def show_available_scripts():
    """利用可能なスクリプト確認"""
    print("\n🚀 利用可能なスクリプト")
    
    scripts = [
        {
            'file': 'improved_api_connector.py',
            'description': '19種類API高速並行接続テスト（改善版・推奨）',
            'command': 'python3 improved_api_connector.py'
        },
        {
            'file': 'test_19_google_apis.py',
            'description': '19種類API一括接続テスト（従来版）',
            'command': 'python3 test_19_google_apis.py'
        },
        {
            'file': 'working_google_api_demo.py', 
            'description': '実用的なAPI機能デモンストレーション',
            'command': 'python3 working_google_api_demo.py'
        },
        {
            'file': 'test_all_google_apis.py',
            'description': '全API包括テストシステム', 
            'command': 'python3 test_all_google_apis.py'
        },
        {
            'file': 'complete_9_google_apis.py',
            'description': '主要9API集中テスト',
            'command': 'python3 complete_9_google_apis.py'
        }
    ]
    
    available_count = 0
    for script in scripts:
        if os.path.exists(script['file']):
            print(f"   ✅ {script['description']}")
            print(f"      実行: {script['command']}")
            available_count += 1
        else:
            print(f"   ❌ {script['file']} - ファイルが見つかりません")
    
    print(f"\n📊 利用可能スクリプト: {available_count}/{len(scripts)}種類")
    return available_count

def show_system_summary():
    """システム概要表示"""
    print("\n📊 システム概要")
    print("=" * 50) 
    print("プロジェクト: Google 19種類 API完全接続システム")
    print("機能: Google Cloud Platform API統合テスト")
    print("対象API: Gmail, Calendar, Drive, Vision等 19種類")
    print("認証方式: OAuth 2.0")
    print("用途: API学習・システム統合・監視")
    print("=" * 50)

def show_next_steps(all_checks_passed):
    """次のステップガイド"""
    print("\n📋 次のステップ")
    
    if all_checks_passed:
        print("✅ 全てのチェックが完了しました！")
        print("\n🚀 推奨実行順序:")
        print("   1. python3 improved_api_connector.py # 19API高速並行テスト（推奨）")
        print("   2. python3 test_19_google_apis.py    # 19API従来版テスト")
        print("   3. python3 working_google_api_demo.py # 実用デモ")
        print("   4. python3 test_all_google_apis.py   # 包括テスト")
    else:
        print("⚠️ いくつかの問題が見つかりました。")
        print("\n🔧 修復手順:")
        print("1. 不足ライブラリのインストール:")
        print("   pip install -r requirements_improved.txt  # 改善版（推奨）")
        print("   pip install -r requirements.txt          # 基本版")
        print("2. 認証情報の設定:")
        print("   python3 setup_auth.py") 
        print("3. 再度確認:")
        print("   python3 check_system.py")

def main():
    """メイン実行"""
    print("🔍 Google 19種類 API システム - 状態確認（改善版対応）")
    print("=" * 70)
    print("📋 Google Cloud Platform API統合システムの動作確認")
    print("🎯 対象: Gmail, Calendar, Drive, Vision AI等 19種類")
    print("✨ 改善版: 並行処理・自動復旧・高速化対応")
    print("=" * 70)
    
    # 各種チェック実行
    python_ok = check_python_version()
    libs_ok = check_required_libraries()
    files_ok = check_essential_files()
    token_ok = check_token_status()
    scripts_count = show_available_scripts()
    
    # システム概要表示
    show_system_summary()
    
    # 総合判定
    all_checks_passed = (python_ok and libs_ok and files_ok and 
                        token_ok and scripts_count >= 2)
    
    print(f"\n🎯 総合結果")
    if all_checks_passed:
        print("✅ 全チェック完了 - 19種類API システム実行可能!")
    else:
        print("⚠️ 一部問題あり - 修復が必要")
    
    # 次のステップ案内
    show_next_steps(all_checks_passed)
    
    print(f"\n✨ チェック完了 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"🌐 Google API Master Collection System Ready!")

if __name__ == '__main__':
    main()