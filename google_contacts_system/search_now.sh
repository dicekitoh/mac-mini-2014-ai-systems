#\!/bin/bash

# Google Contacts 高速検索（iPhone最適化）
# Usage: ./search_now.sh "検索キーワード"

if [ -z "$1" ]; then
    echo "❌ 検索キーワードを指定してください"
    echo "例: ./search_now.sh \"伊藤\""
    exit 1
fi

cd /home/fujinosuke/projects/google_contacts_system
python3 contacts_fast_search.py "$1"
