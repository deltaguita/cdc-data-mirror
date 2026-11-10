#!/usr/bin/env bash
# 每日排程進入點：抓取 -> 有變更才 commit -> push origin main
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

./fetch.py

git add csv/ status.json MANIFEST.md README.md fetch.py update.sh
if git diff --cached --quiet; then
  echo "no changes"
  exit 0
fi
git commit -q -m "chore: update CDC mirror $(date -u +%Y-%m-%d)"
git push -q origin main
echo "pushed $(git rev-parse --short HEAD)"
