"""
Build dist/SCBX-local-demo.zip for sharing (stdlib only; works when .ps1 is blocked).

Run from repo root:
  python scripts/make_share_zip.py
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
ZIP_PATH = DIST / "SCBX-local-demo.zip"

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".cursor",
    "dist",
    "terminals",
    ".venv",
    "venv",
    "agent-transcripts",
}
SKIP_NAMES = {"SCBX-local-demo.zip", "SCBX-share.zip"}
# Dev / bytecode
SKIP_SUFFIXES = {".pyc", ".pyo"}
# Large media & decks not needed to run the HTML dashboard locally
SKIP_SUFFIXES_MEDIA = {
    ".pptx",
    ".ppt",
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".wmv",
    ".m4v",
}
# Skip individual huge files (e.g. stray PDFs) — data Excel can be ~1–2 MB
MAX_FILE_BYTES = 12 * 1024 * 1024


def should_skip(path: Path, rel: Path) -> bool:
    parts_lower = {p.lower() for p in rel.parts}
    if parts_lower & SKIP_DIRS:
        return True
    if rel.name in SKIP_NAMES:
        return True
    suf = path.suffix.lower()
    if suf in SKIP_SUFFIXES or suf in SKIP_SUFFIXES_MEDIA:
        return True
    if path.is_file():
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                return True
        except OSError:
            return True
    if suf == ".db" and "server" in parts_lower:
        return True
    return False


def main():
    DIST.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.is_file():
        ZIP_PATH.unlink()

    count = 0
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            # prune dirs in-place
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for name in filenames:
                if name in SKIP_NAMES:
                    continue
                full = Path(dirpath) / name
                rel = full.relative_to(ROOT)
                if should_skip(full, rel):
                    continue
                try:
                    zf.write(full, arcname=str(rel).replace("\\", "/"))
                    count += 1
                except OSError as e:
                    print(f"Skip (unreadable): {rel} ({e})")

    size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Wrote {ZIP_PATH} ({count} files, {size_mb:.2f} MB)")
    print("Recipients: unzip, open the folder, double-click serve-demo.bat (Windows) or run: py -3 serve_local.py")
    print("Then open: http://127.0.0.1:8844/SCB_CXO_Board_Dashboard.html (port from terminal if different)")


if __name__ == "__main__":
    main()
