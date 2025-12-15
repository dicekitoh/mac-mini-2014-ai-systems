#\!/bin/bash
# iPhone最適化 即座SMS送信スクリプト

echo "📱 SMS送信システム v2.0"
echo "========================="

# 引数チェック
if [ $# -ne 2 ]; then
    echo "使用方法:"
    echo "./send_now.sh <電話番号> <メッセージ>"
    echo ""
    echo "例:"
    echo "./send_now.sh 09068765380 \"テストメッセージ\""
    exit 1
fi

PHONE=$1
MESSAGE=$2

# 基本チェック
if [ -z "$PHONE" ] || [ -z "$MESSAGE" ]; then
    echo "❌ 電話番号またはメッセージが空です"
    exit 1
fi

# メッセージ長チェック
MSG_LENGTH=$(echo -n "$MESSAGE"  < /dev/null |  wc -c)
if [ $MSG_LENGTH -gt 70 ]; then
    echo "❌ メッセージが長すぎます (${MSG_LENGTH}/70文字)"
    exit 1
fi

# 送信情報表示
echo "📞 宛先: $PHONE"
echo "💬 内容: $MESSAGE"
echo "📏 文字数: ${MSG_LENGTH}文字"
echo ""

# スマート送信実行
echo "🚀 送信開始..."
python3 ~/send_textbelt_sms_smart.py "$PHONE" "$MESSAGE"

# 結果をログに記録
mkdir -p ~/projects/sms_system/logs
echo "$(date "+%Y-%m-%d %H:%M:%S") - $PHONE - $MESSAGE" >> ~/projects/sms_system/logs/sms_history.log
