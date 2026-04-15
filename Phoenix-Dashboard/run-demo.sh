#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
HTML="index.html"
if [[ ! -f "$HTML" ]]; then
  echo "Missing $HTML in $(pwd)" >&2
  exit 1
fi
if command -v open >/dev/null 2>&1; then
  open "$HTML"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$HTML"
elif command -v start >/dev/null 2>&1; then
  start "$HTML"
else
  echo "Open this file in your browser: $(pwd)/$HTML" >&2
  exit 1
fi
