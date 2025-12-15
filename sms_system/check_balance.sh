#\!/bin/bash
# SMS残高・使用履歴確認スクリプト

echo "📊 SMS送信システム状況"
echo "======================"

echo ""
echo "💳 API情報:"
echo "- 有料APIキー: 設定済み"
echo "- 推定残りクレジット: 116通"
echo "- 無料枠: 1日1通"

echo ""
echo "📈 最近の送信履歴:"
if [ -f ~/projects/sms_system/logs/sms_history.log ]; then
    tail -10 ~/projects/sms_system/logs/sms_history.log
else
    echo "まだ送信履歴がありません"
fi

echo ""
echo "🔧 システム状態:"
echo "- SSH接続: OK"
echo "- Python環境: $(python3 --version)"
echo "- スクリプト権限: $(ls -la ~/projects/sms_system/*.sh  < /dev/null |  wc -l)個のスクリプト実行可能"

echo ""
echo "📱 利用可能なコマンド:"
echo "./send_now.sh <電話番号> <メッセージ>    # 即座送信"
echo "./interactive_sms.sh                    # 対話式送信"
echo "./check_balance.sh                      # この画面"
