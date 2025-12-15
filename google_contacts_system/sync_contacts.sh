#\!/bin/bash

# Google Contacts ローカル同期管理スクリプト
# Usage: ./sync_contacts.sh [sync < /dev/null | search|status]

SCRIPT_DIR="/home/fujinosuke/projects/google_contacts_system"
SYNC_SCRIPT="$SCRIPT_DIR/contacts_sync_system.py"
SEARCH_SCRIPT="$SCRIPT_DIR/contacts_fast_search.py"

cd "$SCRIPT_DIR"

function show_usage() {
    echo "Google Contacts ローカル同期システム"
    echo ""
    echo "使用方法:"
    echo "  ./sync_contacts.sh sync                # 完全同期実行"
    echo "  ./sync_contacts.sh search <keyword>    # 高速検索"
    echo "  ./sync_contacts.sh status              # 状況確認"
    echo ""
    echo "例:"
    echo "  ./sync_contacts.sh sync"
    echo "  ./sync_contacts.sh search \"伊藤\""
    echo "  ./sync_contacts.sh status"
}

function run_sync() {
    echo "🔄 Google Contacts 完全同期開始..."
    echo ""
    
    python3 "$SYNC_SCRIPT" sync
    sync_result=$?
    
    echo ""
    if [ $sync_result -eq 0 ]; then
        echo "✅ 同期完了"
        echo ""
        echo "📊 同期後の状況:"
        python3 "$SEARCH_SCRIPT" status
    else
        echo "❌ 同期失敗"
        return 1
    fi
}

function run_search() {
    if [ -z "$1" ]; then
        echo "❌ 検索キーワードを指定してください"
        echo "例: ./sync_contacts.sh search \"伊藤\""
        return 1
    fi
    
    python3 "$SEARCH_SCRIPT" "$1"
}

function show_status() {
    echo "📊 Google Contacts システム状況"
    echo ""
    
    # 同期システム状況
    echo "🔄 同期システム:"
    python3 "$SYNC_SCRIPT" status
    echo ""
    
    # 検索システム状況
    echo "🔍 検索システム:"
    python3 "$SEARCH_SCRIPT" status
    echo ""
    
    # ファイル情報
    echo "📁 ファイル情報:"
    if [ -f "$SCRIPT_DIR/contacts_local_db.json" ]; then
        file_size=$(du -h "$SCRIPT_DIR/contacts_local_db.json" | cut -f1)
        file_date=$(stat -c %y "$SCRIPT_DIR/contacts_local_db.json" | cut -d. -f1)
        echo "   ローカルDB: $file_size ($file_date)"
    else
        echo "   ローカルDB: 未作成"
    fi
    
    if [ -f "$SCRIPT_DIR/sync_log.txt" ]; then
        log_lines=$(wc -l < "$SCRIPT_DIR/sync_log.txt")
        echo "   同期ログ: $log_lines 行"
        echo ""
        echo "📝 最新の同期ログ (最後の5行):"
        tail -5 "$SCRIPT_DIR/sync_log.txt"
    else
        echo "   同期ログ: なし"
    fi
}

# メイン処理
case "$1" in
    "sync")
        run_sync
        ;;
    "search")
        run_search "$2"
        ;;
    "status")
        show_status
        ;;
    "")
        show_usage
        ;;
    *)
        echo "❌ 不明なコマンド: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
