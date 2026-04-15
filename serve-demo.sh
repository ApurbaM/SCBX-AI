#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "  SCBx local demo server"
echo "  ----------------------"
echo "  Serves on 127.0.0.1; tries ports 8844, 8845, ..."
echo "  Press Ctrl+C to stop."
echo ""
if command -v python3 >/dev/null 2>&1; then
  exec python3 serve_local.py
fi
if command -v python >/dev/null 2>&1; then
  exec python serve_local.py
fi
echo "ERROR: python3/python not found in PATH."
exit 1
