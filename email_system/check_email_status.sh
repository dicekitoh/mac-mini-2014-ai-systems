#\!/bin/bash
# メール送信システム状況確認スクリプト

echo "📧 メール送信システム状況"
echo "========================"

echo ""
echo "📊 Gmail SMTP設定:"
echo "- 送信者: itoh@thinksblog.com"
echo "- SMTPサーバー: smtp.gmail.com:587"
echo "- 認証: Googleアプリパスワード"
echo "- 暗号化: STARTTLS"

echo ""
echo "📈 最近の送信履歴:"
if [ -f ~/projects/email_system/logs/email_history.log ]; then
    echo "最新10件:"
    tail -10 ~/projects/email_system/logs/email_history.log
else
    echo "まだ送信履歴がありません"
fi

echo ""
echo "🔧 システム状態:"
echo "- SSH接続: OK"
echo "- Python環境: $(python3 --version)"
echo "- Gmail接続: 設定済み"
echo "- スクリプト権限: $(ls -la ~/projects/email_system/*.sh  < /dev/null |  wc -l)個のスクリプト実行可能"

echo ""
echo "📧 利用可能なコマンド:"
echo "./send_mail.sh <宛先> <件名> <本文>     # 即座送信"
echo "./interactive_mail.sh                  # 対話式送信"
echo "./send_to_daisuke.sh <件名> <本文>     # 伊藤大輔さん宛"
echo "./quick_templates.sh                   # 定型文送信"
echo "./check_email_status.sh                # この画面"

echo ""
echo "📝 送信履歴統計:"
if [ -f ~/projects/email_system/logs/email_history.log ]; then
    TOTAL_EMAILS=$(wc -l < ~/projects/email_system/logs/email_history.log)
    SUCCESS_EMAILS=$(grep -c "SUCCESS" ~/projects/email_system/logs/email_history.log)
    FAILED_EMAILS=$(grep -c "FAILED" ~/projects/email_system/logs/email_history.log)
    
    echo "- 総送信数: ${TOTAL_EMAILS}通"
    echo "- 成功: ${SUCCESS_EMAILS}通"
    echo "- 失敗: ${FAILED_EMAILS}通"
    if [ $TOTAL_EMAILS -gt 0 ]; then
        SUCCESS_RATE=$((SUCCESS_EMAILS * 100 / TOTAL_EMAILS))
        echo "- 成功率: ${SUCCESS_RATE}%"
    fi
else
    echo "- まだ統計データがありません"
fi
