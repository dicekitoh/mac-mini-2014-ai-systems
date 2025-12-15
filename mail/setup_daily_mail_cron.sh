#!/bin/bash

echo "毎朝のテストメール送信設定"
echo "========================="
echo ""
echo "このスクリプトはcrontabに毎朝のテストメール送信を設定します。"
echo ""

# 現在のcrontabを確認
echo "現在のcrontab設定:"
crontab -l 2>/dev/null || echo "（設定なし）"
echo ""

# 送信時刻を選択
echo "テストメール送信時刻を選択してください:"
echo "1) 毎朝 7:00"
echo "2) 毎朝 8:00"
echo "3) 毎朝 9:00"
echo "4) カスタム時刻"
echo ""
read -p "選択 (1-4): " choice

case $choice in
    1)
        HOUR="7"
        MINUTE="0"
        ;;
    2)
        HOUR="8"
        MINUTE="0"
        ;;
    3)
        HOUR="9"
        MINUTE="0"
        ;;
    4)
        read -p "時 (0-23): " HOUR
        read -p "分 (0-59): " MINUTE
        ;;
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

# crontabエントリを作成
CRON_ENTRY="$MINUTE $HOUR * * * /usr/bin/python3 /home/fujinosuke/projects/mail/daily_test_mail.py >> /home/fujinosuke/logs/daily_test_mail_cron.log 2>&1"

echo ""
echo "以下の設定を追加します:"
echo "$CRON_ENTRY"
echo ""

read -p "続行しますか？ (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi

# 現在のcrontabを取得
(crontab -l 2>/dev/null || echo "") > /tmp/current_cron

# 既存の同じエントリがあれば削除
grep -v "daily_test_mail.py" /tmp/current_cron > /tmp/new_cron || cp /tmp/current_cron /tmp/new_cron

# 新しいエントリを追加
echo "$CRON_ENTRY" >> /tmp/new_cron

# crontabを更新
crontab /tmp/new_cron

# 一時ファイルを削除
rm -f /tmp/current_cron /tmp/new_cron

echo ""
echo "✅ crontab設定完了"
echo ""
echo "設定内容:"
echo "- 送信時刻: 毎日 $HOUR:$(printf "%02d" $MINUTE)"
echo "- スクリプト: /home/fujinosuke/projects/mail/daily_test_mail.py"
echo "- ログファイル: /home/fujinosuke/logs/daily_test_mail_cron.log"
echo ""
echo "現在のcrontab設定:"
crontab -l | grep daily_test_mail
echo ""
echo "テスト実行:"
echo "python3 /home/fujinosuke/projects/mail/daily_test_mail.py"