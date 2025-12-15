#\!/bin/bash
# 対話式SMS送信スクリプト

echo "📱 対話式SMS送信システム"
echo "========================="

# 電話番号入力
echo -n "📞 電話番号を入力してください: "
read PHONE

# メッセージ入力
echo -n "💬 メッセージ（70文字以内）: "
read MESSAGE

# 確認
echo ""
echo "=== 送信確認 ==="
echo "宛先: $PHONE"
echo "内容: $MESSAGE"
echo "文字数: $(echo -n "$MESSAGE"  < /dev/null |  wc -c)文字"
echo ""

echo -n "送信しますか？ (y/n): "
read CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "🚀 送信中..."
    python3 ~/send_textbelt_sms_smart.py "$PHONE" "$MESSAGE"
    
    # ログ記録
    mkdir -p ~/projects/sms_system/logs
    echo "$(date "+%Y-%m-%d %H:%M:%S") - $PHONE - $MESSAGE" >> ~/projects/sms_system/logs/sms_history.log
else
    echo "❌ 送信をキャンセルしました"
fi
