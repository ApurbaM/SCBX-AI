#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo ""
echo "  SCBx local demo server"
echo "  ----------------------"
echo "  Port 8844 avoids Docker and other tools that often bind 8080."
echo "  Open: http://localhost:8844/index.html"
echo "        http://localhost:8844/SCB_CXO_Board_Dashboard.html"
echo ""
echo "  Press Ctrl+C to stop."
echo ""
exec python3 -m http.server 8844
