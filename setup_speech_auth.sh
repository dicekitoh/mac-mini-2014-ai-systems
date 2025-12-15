#!/bin/bash
# Google Speech-to-Text API 認証設定スクリプト

echo "Google Speech-to-Text API 認証設定"
echo "=================================="

# 認証ディレクトリ作成
mkdir -p ~/google_auth

# JSONファイルの検索
echo -e "\n認証JSONファイルを検索中..."
json_files=$(find ~/ -name "*.json" -type f 2>/dev/null | grep -E "(civil-authority|speech)" | head -5)

if [ -z "$json_files" ]; then
    echo "認証JSONファイルが見つかりません。"
    echo "ダウンロードしたJSONファイルのパスを入力してください:"
    read -r json_path
else
    echo "見つかったJSONファイル:"
    echo "$json_files" | nl -v 1
    echo -e "\n使用するファイルの番号を入力してください (または新しいパスを入力):"
    read -r selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]]; then
        json_path=$(echo "$json_files" | sed -n "${selection}p")
    else
        json_path="$selection"
    fi
fi

# ファイル存在確認
if [ ! -f "$json_path" ]; then
    echo "エラー: ファイルが見つかりません: $json_path"
    exit 1
fi

# 認証ファイルをコピー
cp "$json_path" ~/google_auth/speech_credentials.json
echo "認証ファイルをコピーしました: ~/google_auth/speech_credentials.json"

# 環境変数の設定
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/google_auth/speech_credentials.json"

# .bashrcに追加
if ! grep -q "GOOGLE_APPLICATION_CREDENTIALS" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Google Speech-to-Text API認証" >> ~/.bashrc
    echo "export GOOGLE_APPLICATION_CREDENTIALS=\"\$HOME/google_auth/speech_credentials.json\"" >> ~/.bashrc
    echo ".bashrcに環境変数を追加しました"
fi

# 設定確認
echo -e "\n設定完了!"
echo "環境変数: GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS"
echo -e "\n次回ログイン時から自動的に設定されます。"
echo "今すぐ使用する場合は以下を実行してください:"
echo "source ~/.bashrc"