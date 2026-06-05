#!/usr/bin/env bash
# GitHub リポジトリにAI研究者リスト向けTopicsを設定する。
set -euo pipefail

cd "$(dirname "$0")/.."

repo_args=()
if [[ $# -gt 0 && -n "${1:-}" ]]; then
  repo_args=("$1")
fi

gh repo edit "${repo_args[@]}" \
  --add-topic awesome \
  --add-topic awesome-list \
  --add-topic awesome-lists \
  --add-topic artificial-intelligence \
  --add-topic machine-learning \
  --add-topic deep-learning \
  --add-topic researchers \
  --add-topic ai-research \
  --add-topic research \
  --add-topic computer-vision \
  --add-topic nlp \
  --add-topic natural-language-processing \
  --add-topic reinforcement-learning \
  --add-topic data-mining \
  --add-topic theoretical-computer-science \
  --add-topic robotics \
  --add-topic curated-list \
  --add-topic academia \
  --add-topic scientists \
  --add-topic resources

echo "Topics を設定しました。確認: gh repo view ${repo_args[*]:-} --json repositoryTopics"
