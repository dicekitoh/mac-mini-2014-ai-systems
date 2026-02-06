#!/bin/bash

# Google APIs 常時接続維持スクリプト
# Mac mini 2014 - 自動化システム統合版

set -e

# ===========================================
# 設定
# ===========================================
BASE_DIR="/home/fujinosuke/projects/google_apis_integration"
VENV_PATH="$BASE_DIR/google_apis_venv"
MONITOR_DIR="$BASE_DIR/monitoring"
LOG_DIR="$MONITOR_DIR/logs"
PID_FILE="$MONITOR_DIR/google_apis_keeper.pid"

# ログファイル
LOG_FILE="$LOG_DIR/keeper_$(date +%Y%m%d).log"

# ===========================================
# 関数定義
# ===========================================

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log_message "📋 前提条件チェック開始"
    
    # ディレクトリ存在確認
    if [ ! -d "$BASE_DIR" ]; then
        log_message "❌ ベースディレクトリが見つかりません: $BASE_DIR"
        return 1
    fi
    
    # 仮想環境確認
    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        log_message "❌ 仮想環境が見つかりません: $VENV_PATH"
        return 1
    fi
    
    # ログディレクトリ作成
    mkdir -p "$LOG_DIR"
    
    log_message "✅ 前提条件チェック完了"
    return 0
}

start_monitoring() {
    log_message "🚀 Google APIs常時監視を開始"
    
    # 既存プロセス確認
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log_message "⚠️ 既存の監視プロセスが実行中です (PID: $OLD_PID)"
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
    nohup python monitoring/google_apis_monitor.py > "$LOG_DIR/monitor_output.log" 2>&1 &
    MONITOR_PID=$!
    
    # PIDファイル保存
    echo "$MONITOR_PID" > "$PID_FILE"
    
    log_message "✅ 監視プロセス開始: PID $MONITOR_PID"
    log_message "📊 ログ確認: tail -f $LOG_FILE"
    
    return 0
}

stop_monitoring() {
    log_message "🛑 Google APIs監視を停止"
    
    if [ ! -f "$PID_FILE" ]; then
        log_message "⚠️ PIDファイルが見つかりません。監視は実行されていません。"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        log_message "✅ 監視プロセス停止: PID $PID"
    else
        log_message "⚠️ PID $PID のプロセスが見つかりません"
    fi
    
    rm -f "$PID_FILE"
    return 0
}

status_check() {
    log_message "📊 Google APIs監視状況確認"
    
    if [ ! -f "$PID_FILE" ]; then
        log_message "❌ 監視は実行されていません"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        log_message "✅ 監視プロセス実行中: PID $PID"
        
        # 最新ログの表示
        if [ -f "$LOG_FILE" ]; then
            log_message "📋 最新ログ (最後の10行):"
            tail -n 10 "$LOG_FILE" | while IFS= read -r line; do
                echo "   $line"
            done
        fi
        
        return 0
    else
        log_message "❌ PIDファイルは存在しますが、プロセスが見つかりません"
        rm -f "$PID_FILE"
        return 1
    fi
}

test_once() {
    log_message "🧪 Google APIs接続テスト (1回のみ)"
    
    cd "$BASE_DIR"
    source "$VENV_PATH/bin/activate"
    
    python monitoring/google_apis_monitor.py --once
    
    if [ $? -eq 0 ]; then
        log_message "✅ 接続テスト成功"
        return 0
    else
        log_message "❌ 接続テスト失敗"
        return 1
    fi
}

install_cron() {
    log_message "⏰ cron設定を追加"
    
    CRON_SCRIPT="$BASE_DIR/monitoring/google_apis_keeper.sh"
    
    # 現在のスクリプトをmonitoring/にコピー
    cp "$0" "$CRON_SCRIPT"
    chmod +x "$CRON_SCRIPT"
    
    # cron設定追加 (5分毎の状況確認)
    CRON_ENTRY="*/5 * * * * $CRON_SCRIPT status >/dev/null 2>&1"
    
    # 既存のcron確認
    if crontab -l 2>/dev/null | grep -q "google_apis_keeper"; then
        log_message "⚠️ Google APIs関連のcronエントリが既に存在します"
    else
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
        log_message "✅ cron設定追加完了"
        log_message "   監視間隔: 5分毎"
    fi
    
    return 0
}

show_help() {
    echo "Google APIs 常時接続維持システム"
    echo "=================================="
    echo ""
    echo "使用方法:"
    echo "  $0 start    - 監視開始"
    echo "  $0 stop     - 監視停止" 
    echo "  $0 status   - 状況確認"
    echo "  $0 test     - 接続テスト (1回のみ)"
    echo "  $0 install  - cron設定追加"
    echo "  $0 logs     - ログ表示"
    echo ""
    echo "ファイル:"
    echo "  監視ログ: $LOG_FILE"
    echo "  PIDファイル: $PID_FILE"
}

show_logs() {
    log_message "📜 Google APIs監視ログ"
    
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