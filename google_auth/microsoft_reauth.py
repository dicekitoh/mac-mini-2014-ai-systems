#!/usr/bin/env python3
"""
Microsoft Graph API 再認証スクリプト
カレンダー権限を追加したため再認証が必要
"""

import sys
sys.path.append('/home/rootmax')

from microsoft_graph_contacts import MicrosoftGraphContacts

def main():
    print("=== Microsoft Graph 再認証（カレンダー権限追加） ===")
    
    graph = MicrosoftGraphContacts()
    
    print("\n1. 以下のURLにアクセスしてください:")
    auth_url = graph.get_auth_url()
    print(auth_url)
    print("\n2. Microsoftアカウントでログインし、権限を許可してください")
    print("   ※ 今回は連絡先に加えてカレンダーの権限も要求されます")
    print("\n3. リダイレクトされたURLから'code='の後の値をコピーしてください")
    print("   ※ localhost接続エラーは無視してください。URLの'code='部分が重要です")

if __name__ == '__main__':
    main()