#!/bin/bash

# Blogger自動投稿システム 常時待機・監視スクリプト
# Mac mini 2014専用

set -e

# ===========================================
# 設定
# ===========================================
BASE_DIR="/home/fujinosuke/projects/blogger_auto_post_system"
VENV_PATH="$BASE_DIR/blog_env"
MONITOR_DIR="$BASE_DIR/monitoring"
LOG_DIR="$MONITOR_DIR/logs"
PID_FILE="$MONITOR_DIR/blogger_keeper.pid"

# ログファイル
LOG_FILE="$LOG_DIR/blogger_keeper_$(date +%Y%m%d).log"

# ===========================================
# 関数定義
# ===========================================

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log_message "📋 Bloggerシステム前提条件チェック"
    
    # ディレクトリ存在確認
    if [ ! -d "$BASE_DIR" ]; then
        log_message "❌ Bloggerベースディレクトリが見つかりません: $BASE_DIR"
        return 1
    fi
    
    # 仮想環境確認
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        log_message "❌ Blog仮想環境が見つかりません: $VENV_PATH"
        return 1
    fi
    
    # ログディレクトリ作成
    mkdir -p "$LOG_DIR"
    
    # 必須ファイル確認
    REQUIRED_FILES=(
        "$BASE_DIR/test_blog_system.py"
        "$BASE_DIR/refactored_v2/blog_posting_service.py"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            log_message "⚠️ 重要ファイルが見つかりません: $file"
        fi
    done
    
    log_message "✅ Blogger前提条件チェック完了"
    return 0
}

start_monitoring() {
    log_message "🚀 Blogger自動投稿システム常時監視を開始"
    
    # 既存プロセス確認
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log_message "⚠️ 既存のBlogger監視プロセスが実行中です (PID: $OLD_PID)"
            log_message "   停止する場合: $0 stop"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # 仮想環境アクティベートとPython実行
    cd "$BASE_DIR"
    source "$VENV_PATH/bin/activate"
    
    # バックグラウンドで監視開始
    nohup python3 monitoring/blogger_always_monitoring.py > "$LOG_DIR/monitor_output.log" 2>&1 &
    MONITOR_PID=$!
    
    # PIDファイル保存
    echo "$MONITOR_PID" > "$PID_FILE"
    
    log_message "✅ Blogger監視プロセス開始: PID $MONITOR_PID"
    log_message "📊 ログ確認: tail -f $LOG_FILE"
    
    return 0
}

stop_monitoring() {
    log_message "🛑 Blogger自動投稿システム監視を停止"
    
    if [ ! -f "$PID_FILE" ]; then
        log_message "⚠️ PIDファイルが見つかりません。Blogger監視は実行されていません。"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        log_message "✅ Blogger監視プロセス停止: PID $PID"
    else
        log_message "⚠️ PID $PID のプロセスが見つかりません"
    fi
    
    rm -f "$PID_FILE"
    return 0
}

status_check() {
    log_message "📊 Blogger自動投稿システム状況確認"
    
    if [ ! -f "$PID_FILE" ]; then
        log_message "❌ Blogger監視は実行されていません"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        log_message "✅ Blogger監視プロセス実行中: PID $PID"
        
        # 最新ログの表示
        if [ -f "$LOG_FILE" ]; then
            log_message "📋 最新ログ (最後の10行):"
            tail -n 10 "$LOG_FILE" | while IFS= read -r line; do
                echo "   $line"
            done
        fi
        
        # 認証ファイル確認
        log_message "🔐 認証ファイル状況:"
        
        CONFIG_FILES=(
            "$BASE_DIR/config/credentials.json"
            "$BASE_DIR/google_api_complete_token.pkl"
            "$BASE_DIR/config/google_api_complete_token.pkl"
        )
        
        for file in "${CONFIG_FILES[@]}"; do
            if [ -f "$file" ]; then
                size=$(stat -c%s "$file")
                echo "   ✅ $(basename "$file"): ${size} bytes"
            else
                echo "   ❌ $(basename "$file"): 不存在"
            fi
        done
        
        return 0
    else
        log_message "❌ PIDファイルは存在しますが、プロセスが見つかりません"
        rm -f "$PID_FILE"
        return 1
    fi
}

test_once() {
    log_message "🧪 Blogger自動投稿システム接続テスト (1回のみ)"
    
    cd "$BASE_DIR"
    source "$VENV_PATH/bin/activate"
    
    python3 monitoring/blogger_always_monitoring.py --once
    
    case $? in
        0)
            log_message "✅ Bloggerテスト成功"
            return 0
            ;;
        2)
            log_message "⚠️ Bloggerテスト: 認証エラー"
            return 2
            ;;
        *)
            log_message "❌ Bloggerテスト失敗"
            return 1
            ;;
    esac
}

install_cron() {
    log_message "⏰ Blogger用cron設定を追加"
    
    CRON_SCRIPT="$BASE_DIR/monitoring/blogger_keeper.sh"
    
    # 現在のスクリプトをmonitoring/にコピー
    cp "$0" "$CRON_SCRIPT"
    chmod +x "$CRON_SCRIPT"
    
    # cron設定追加 (10分毎の状況確認)
    CRON_ENTRY="*/10 * * * * $CRON_SCRIPT status >/dev/null 2>&1"
    
    # 既存のcron確認
    if crontab -l 2>/dev/null | grep -q "blogger_keeper"; then
        log_message "⚠️ Blogger関連のcronエントリが既に存在します"
    else
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        log_message "✅ Blogger用cron設定追加完了"
        log_message "   監視間隔: 10分毎"
    fi
    
    return 0
}

repair_auth() {
    log_message "🔧 Blogger認証修復を実行"
    
    cd "$BASE_DIR"
    source "$VENV_PATH/bin/activate"
    
    # 利用可能な認証修復スクリプト
    REPAIR_SCRIPTS=("fix_auth.py" "simple_auth.py" "refresh_auth.py")
    
    for script in "${REPAIR_SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            log_message "🔄 認証修復スクリプト実行: $script"
            
            timeout 30s python3 "$script"
            
            if [ $? -eq 0 ]; then
                log_message "✅ 認証修復成功: $script"
                return 0
            else
                log_message "⚠️ 認証修復失敗: $script"
            fi
        fi
    done
    
    log_message "❌ 全ての認証修復スクリプトが失敗"
    log_message "📋 手動認証が必要です:"
    log_message "   1. Google Cloud Consoleで認証確認"
    log_message "   2. credentials.json更新"
    log_message "   3. OAuth2.0トークン再生成"
    
    return 1
}

show_help() {
    echo "Blogger自動投稿システム 常時待機・監視システム"
    echo "==============================================="
    echo ""
    echo "使用方法:"
    echo "  $0 start    - Blogger監視開始"
    echo "  $0 stop     - Blogger監視停止" 
    echo "  $0 status   - 状況確認"
    echo "  $0 test     - 接続テスト (1回のみ)"
    echo "  $0 repair   - 認証修復"
    echo "  $0 install  - cron設定追加"
    echo "  $0 logs     - ログ表示"
    echo ""
    echo "ファイル:"
    echo "  監視ログ: $LOG_FILE"
    echo "  PIDファイル: $PID_FILE"
    echo "  認証設定: $BASE_DIR/config/"
}

show_logs() {
    log_message "📜 Blogger自動投稿システム監視ログ"
    
    if [ -f "$LOG_FILE" ]; then
        echo "最新30行:"
        tail -n 30 "$LOG_FILE"
    else
        echo "ログファイルが見つかりません: $LOG_FILE"
    fi
}

# ===========================================
# メイン実行
# ===========================================

case "$1" in
    start)
        check_prerequisites && start_monitoring
        ;;
    stop)
        stop_monitoring
        ;;
    status)
        status_check
        ;;
    test)
        check_prerequisites && test_once
        ;;
    repair)
        check_prerequisites && repair_auth
        ;;
    install)
        check_prerequisites && install_cron
        ;;
    logs)
        show_logs
        ;;
    *)
        show_help
        exit 1
        ;;
esac

exit $?