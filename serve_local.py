"""
Serve this repo over HTTP, pick the first free port in a small list,
print exact URLs, and open the CXO dashboard in the default browser.

- Binds IPv6 dual-stack (::) when possible so both localhost and 127.0.0.1 work.
- Falls back to 0.0.0.0 then 127.0.0.1 if IPv6 is unavailable.
- On Windows, writes %%TEMP%%\\scbx_dashboard_url.txt so serve-demo.bat can open
  the correct URL after the server is listening (avoids race / wrong port).

Run from repo root:  py -3 serve_local.py   or   python serve_local.py
"""
from __future__ import annotations

import http.server
import os
import socket
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTS = [8080, 8844, 8845, 8846, 8891, 8892, 9000] + list(range(9001, 9010))

# Windows batch waits for this file then opens the URL (correct port if not 8080).
def _dashboard_url_file() -> Path:
    base = os.environ.get("TEMP") or os.environ.get("TMP") or "."
    return Path(base) / "scbx_dashboard_url.txt"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        # Avoid stale dashboard HTML during local iteration (browser disk cache).
        path = (self.path or "").split("?", 1)[0].lower()
        if path.endswith(".html"):
            self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


class DualStackThreadingHTTPServer(http.server.ThreadingHTTPServer):
    """Listen on :: (IPv6) with dual-stack so IPv4-mapped clients (localhost) work."""

    allow_reuse_address = True
    address_family = socket.AF_INET6
    daemon_threads = True

    def server_bind(self) -> None:
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        self.socket.bind(self.server_address)


def _urls(port: int) -> tuple[str, str, str]:
    # New query each server start so the browser does not reuse a stale cached dashboard.
    _bust = int(time.time() * 1000) % 9_000_000_000
    dash = f"/SCB_CXO_Board_Dashboard.html?t={_bust}"
    hub = "/index.html"
    u4 = f"http://127.0.0.1:{port}{dash}"
    loc = f"http://localhost:{port}{dash}"
    hub_url = f"http://127.0.0.1:{port}{hub}"
    return u4, loc, hub_url


def _open_browser(url: str) -> None:
    if sys.platform == "win32":
        try:
            os.startfile(url)  # type: ignore[attr-defined]
            return
        except OSError:
            pass
    try:
        webbrowser.open(url)
    except Exception:
        pass


def _schedule_extra_browser_opens(url: str) -> None:
    def _again() -> None:
        time.sleep(1.6)
        _open_browser(url)

    threading.Thread(target=_again, daemon=True).start()


def _write_url_file(url: str) -> None:
    path = _dashboard_url_file()
    try:
        path.write_text(url.strip() + "\n", encoding="utf-8")
    except OSError:
        pass


def _clear_url_file() -> None:
    try:
        _dashboard_url_file().unlink(missing_ok=True)
    except OSError:
        pass


def _serve(httpd: socketserver.TCPServer, *, dual_stack: bool, mode: str) -> None:
    port = httpd.server_address[1]
    u4, loc, hub = _urls(port)

    def _p(msg: str = "") -> None:
        print(msg, flush=True)

    _write_url_file(u4)

    _p("")
    _p("  SCBx local demo server")
    if port != 8080:
        _p("  Note: port 8080 was busy — using this port instead. Free 8080 (e.g. Docker) to get http://localhost:8080/…")
    _p("  ----------------------")
    _p(f"  Serving: {ROOT}")
    _p(f"  Mode: {mode}")
    _p(f"  CXO dashboard: {u4}")
    _p("  (URL includes ?t= so each run opens a fresh copy; port may differ if 8080 is busy.)")
    if dual_stack:
        _p(f"                 {loc}")
    else:
        _p(f"  If {loc} fails, use {u4}.")
    _p(f"  Hub:           {hub}")
    _p("")
    _p("  Press Ctrl+C to stop.")
    _p("")
    _open_browser(u4)
    _schedule_extra_browser_opens(u4)
    try:
        httpd.serve_forever()
    finally:
        _clear_url_file()


def main() -> None:
    os.chdir(ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    _clear_url_file()
    last_err: OSError | None = None

    for port in PORTS:
        try:
            with DualStackThreadingHTTPServer(("::", port), Handler) as httpd:
                _serve(httpd, dual_stack=True, mode="IPv6 dual-stack (::)")
                return
        except OSError as e:
            last_err = e
            continue

    for port in PORTS:
        try:
            with http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler) as httpd:
                httpd.daemon_threads = True
                _serve(httpd, dual_stack=False, mode="IPv4 all (0.0.0.0)")
                return
        except OSError as e:
            last_err = e
            continue

    for port in PORTS:
        try:
            with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
                httpd.daemon_threads = True
                _serve(httpd, dual_stack=False, mode="IPv4 loopback (127.0.0.1)")
                return
        except OSError as e:
            last_err = e
            continue

    print(f"ERROR: No free port in {PORTS}. Last error: {last_err}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
