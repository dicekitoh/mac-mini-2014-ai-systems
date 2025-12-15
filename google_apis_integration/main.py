#!/usr/bin/env python3
"""
Google 19 APIs Connection System - Main Entry Point
リファクタリング済み統合システム
"""

import sys
import os
from pathlib import Path

# Add all module directories to path
current_dir = Path(__file__).parent
for subdir in ['01_authentication', '02_core_apis', '03_distance_calculator', '04_blog_automation']:
    sys.path.insert(0, str(current_dir / subdir))

def show_menu():
    """メインメニュー表示"""
    print("🌐 Google 19 APIs Connection System")
    print("=" * 50)
    print("1. 🔐 Authentication Management")
    print("2. 📡 Core API Testing")
    print("3. 📍 Distance Calculator")
    print("4. 📝 Blog Automation")
    print("5. 📊 System Status Check")
    print("6. 📋 Documentation")
    print("0. Exit")
    print("=" * 50)

def authentication_menu():
    """認証管理メニュー"""
    print("\n🔐 Authentication Management")
    print("-" * 30)
    print("1. Complete 9 Google APIs Auth")
    print("2. Photos API Quick Auth")
    print("3. Generate Auth URL")
    print("4. Process Auth Code")
    print("0. Back to main menu")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        from complete_9_google_apis import Complete9GoogleAPIs
        api_manager = Complete9GoogleAPIs()
        result = api_manager.extend_existing_token()
        print("✅ Authentication process completed")
    elif choice == '2':
        os.system('python3 01_authentication/quick_auth_helper.py')
    elif choice == '3':
        os.system('python3 01_authentication/generate_correct_auth_url.py')
    elif choice == '4':
        os.system('python3 01_authentication/process_auth_code.py')

def api_testing_menu():
    """API テストメニュー"""
    print("\n📡 Core API Testing")
    print("-" * 30)
    print("1. Test All 19 Google APIs")
    print("2. Test Core Google APIs")
    print("3. Photo Count Analyzer")
    print("4. System Health Check")
    print("0. Back to main menu")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        os.system('python3 02_core_apis/test_19_google_apis.py')
    elif choice == '2':
        os.system('python3 02_core_apis/test_all_google_apis.py')
    elif choice == '3':
        os.system('python3 02_core_apis/photo_count_analyzer.py')
    elif choice == '4':
        os.system('python3 02_core_apis/check_system.py')

def distance_calculator_redirect():
    """距離計算システムリダイレクト"""
    print("\n📍 Distance Calculator System")
    print("-" * 40)
    print("🔄 Distance Calculator system has been moved to:")
    print("📁 /home/rootmax/google_maps_distance_calculator_system/")
    print()
    print("To access the distance calculator:")
    print("cd /home/rootmax/google_maps_distance_calculator_system")
    print("python3 main.py")
    print()
    
    choice = input("Launch independent Distance Calculator now? (y/N): ").strip().lower()
    
    if choice == 'y':
        print("🚀 Launching independent Distance Calculator System...")
        os.system('cd /home/rootmax/google_maps_distance_calculator_system && python3 main.py')

def blog_automation_menu():
    """ブログ自動化メニュー"""
    print("\n📝 Blog Automation")
    print("-" * 30)
    print("1. Claude-Gemini Collaboration Post")
    print("2. Sapporo Diary Blog Post")
    print("3. Fix Blog Layout")
    print("4. Update Blog Post")
    print("0. Back to main menu")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        os.system('python3 04_blog_automation/claude_gemini_collaboration_post.py')
    elif choice == '2':
        os.system('python3 04_blog_automation/sapporo_diary_blog_post.py')
    elif choice == '3':
        os.system('python3 04_blog_automation/fix_blog_layout.py')
    elif choice == '4':
        os.system('python3 04_blog_automation/update_blog_post.py')

def show_system_status():
    """システム状況確認"""
    print("\n📊 System Status")
    print("=" * 40)
    
    # Check authentication files
    auth_files = [
        '01_authentication/credentials.json',
        '01_authentication/google_photos_token_20251213_135535.pickle'
    ]
    
    for file in auth_files:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"{status} {file}")
    
    # Check virtual environment
    venv_status = "✅" if os.path.exists('venv') else "❌"
    print(f"{venv_status} Python Virtual Environment")
    
    # Count files in each directory
    directories = [
        '01_authentication', '02_core_apis', '03_distance_calculator',
        '04_blog_automation', '05_documentation', '06_data_results'
    ]
    
    print(f"\n📂 Directory Structure:")
    for directory in directories:
        if os.path.exists(directory):
            file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f"   {directory}: {file_count} files")

def show_documentation():
    """ドキュメント表示"""
    print("\n📋 Available Documentation")
    print("=" * 40)
    
    doc_dir = '05_documentation'
    if os.path.exists(doc_dir):
        docs = [f for f in os.listdir(doc_dir) if f.endswith('.md')]
        for i, doc in enumerate(docs, 1):
            print(f"{i:2}. {doc}")
        
        choice = input(f"\nSelect document to view (1-{len(docs)}) or press Enter to return: ").strip()
        
        try:
            if choice and 1 <= int(choice) <= len(docs):
                selected_doc = docs[int(choice) - 1]
                print(f"\n📖 {selected_doc}")
                print("=" * 50)
                with open(f"{doc_dir}/{selected_doc}", 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Show first 1000 characters
                    if len(content) > 1000:
                        print(content[:1000] + "...\n[File truncated for display]")
                    else:
                        print(content)
                input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("Invalid selection")

def main():
    """メイン実行関数"""
    print("🚀 Google 19 APIs Connection System - Refactored")
    print("📅 Refactoring Date: 2025-12-13")
    print("📁 Directory: /home/rootmax/03_google_19_apis_connection_system")
    
    while True:
        print("\n" + "=" * 50)
        show_menu()
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            authentication_menu()
        elif choice == '2':
            api_testing_menu()
        elif choice == '3':
            distance_calculator_redirect()
        elif choice == '4':
            blog_automation_menu()
        elif choice == '5':
            show_system_status()
        elif choice == '6':
            show_documentation()
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()