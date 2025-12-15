#!/usr/bin/env python3
"""
Microsoft Graph API 認証完了スクリプト
"""

import sys
import os
sys.path.append('/home/rootmax')

from microsoft_graph_contacts import MicrosoftGraphContacts

def complete_auth(auth_code):
    """認証コードを使って認証を完了"""
    print("=== Microsoft Graph 認証完了処理 ===")
    
    graph = MicrosoftGraphContacts()
    
    print(f"\n認証コード: {auth_code[:20]}...")
    
    if graph.exchange_code_for_token(auth_code):
        print("\n✅ 認証成功！トークンを保存しました。")
        
        # ユーザー情報を取得してテスト
        user_info = graph.get_user_info()
        if user_info:
            print(f"\nログインユーザー: {user_info.get('displayName', 'Unknown')}")
            print(f"メール: {user_info.get('mail', user_info.get('userPrincipalName', 'Unknown'))}")
            
            # 連絡先の取得テスト
            print("\n連絡先を取得中...")
            contacts = graph.get_contacts(limit=5)
            if contacts and 'value' in contacts:
                print(f"✅ {len(contacts['value'])}件の連絡先を取得できました")
            else:
                print("連絡先が見つかりませんでした（正常です）")
                
        return True
    else:
        print("\n❌ 認証失敗")
        return False

if __name__ == '__main__':
    # 認証コード
    auth_code = "M.C536_BAY.2.U.79222676-6660-db67-a2f2-605e42ebb7d4"
    
    # クライアントシークレットが設定されているか確認
    import json
    config_file = '/home/rootmax/microsoft_graph_config.json'
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    if config['client_secret'] == 'YOUR_CLIENT_SECRET_HERE':
        print("❌ エラー: クライアントシークレットが設定されていません")
        print(f"   {config_file} を編集してクライアントシークレットを設定してください")
        sys.exit(1)
    
    complete_auth(auth_code)