"""
Serve this repo over HTTP on 127.0.0.1, pick the first free port in a small list,
print exact URLs, and open the CXO dashboard in the default browser.

Use when `python -m http.server PORT` fails (port in use, localhost quirks).
Run from repo root:  python serve_local.py   or   py -3 serve_local.py
"""
from __future__ import annotations

import http.server
import os
import socketserver
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORTS = [8844, 8845, 8846, 8891, 8892, 9000] + list(range(9001, 9010))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)


def main() -> None:
    os.chdir(ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    last_err: OSError | None = None
    for port in PORTS:
        try:
            with socketserver.TCPServer((HOST, port), Handler) as httpd:
                dash = f"http://{HOST}:{port}/SCB_CXO_Board_Dashboard.html"
                hub = f"http://{HOST}:{port}/index.html"
                def _p(msg: str = "") -> None:
                    print(msg, flush=True)

                _p("")
                _p("  SCBx local demo server")
                _p("  ----------------------")
                _p(f"  Serving: {ROOT}")
                _p(f"  CXO dashboard: {dash}")
                _p(f"  Hub:           {hub}")
                _p("")
                _p("  Press Ctrl+C to stop.")
                _p("")
                try:
                    webbrowser.open(dash)
                except Exception:
                    pass
                httpd.serve_forever()
                return
        except OSError as e:
            last_err = e
            continue
    print(f"ERROR: No free port in {PORTS}. Last error: {last_err}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
