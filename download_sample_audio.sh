#!/bin/bash
# Google Cloud公式サンプル音声ファイルをダウンロード

echo "Google Cloud公式サンプル音声をダウンロード中..."

# 日本語サンプル
wget -O sample_japanese.wav "https://storage.googleapis.com/cloud-samples-data/speech/commercial_mono.wav" 2>/dev/null

if [ -f "sample_japanese.wav" ]; then
    echo "✓ サンプル音声のダウンロード完了: sample_japanese.wav"
    echo "このファイルで文字起こしをテストできます："
    echo "python google_speech_to_text.py sample_japanese.wav --language en-US"
else
    echo "ダウンロードに失敗しました。"
    echo ""
    echo "代替方法："
    echo "1. スマートフォンのボイスレコーダーで音声を録音"
    echo "2. 録音した音声ファイルをPCに転送"
    echo "3. python google_speech_to_text.py <音声ファイル>"
fi