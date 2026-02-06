#!/bin/bash

# Mac mini 2014 - GitHub自動同期スクリプト
# 作成日: 2025-12-15
# 修正日: 2026-02-06 (shebangバグ修正, 頻度変更対応)

echo "GitHub同期開始: $(date)"

cd /home/fujinosuke/projects || exit 1

# 変更確認
if ! git diff --quiet || ! git diff --quiet --staged; then
    echo "変更を検出"
    git add .
    git commit -m "auto-sync: $(date +'%Y-%m-%d %H:%M:%S')"

    if git push origin main 2>&1; then
        echo "GitHubにプッシュ完了"
    else
        echo "プッシュをスキップ"
    fi
else
    echo "変更なし - スキップ"
fi

echo "GitHub同期完了: $(date)"
