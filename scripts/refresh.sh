#!/usr/bin/env bash
# data/wave*/ を統合し、README / research-notes を再生成する。
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/2] data/researchers.json を統合中..."
python3 data/merge.py

echo "[2/2] README / research-notes を再生成中..."
python3 data/gen.py

echo "完了。変更があれば git diff で確認してください。"
