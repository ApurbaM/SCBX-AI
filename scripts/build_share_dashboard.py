"""
Build share/SCB_CXO_Board_Dashboard_offline.html — offline-friendly copy of the repo-root dashboard.

- Source of truth: SCB_CXO_Board_Dashboard.html at repository root (served by serve_local.py).
- Embeds avatar placeholders as data: SVG (no dicebear.com dependency).
- Sets a clear <title> and description meta for recipients.

Run from repo root: py -3 scripts/build_share_dashboard.py
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote


def _svg_avatar_uri(initials: str, fill: str, text_fill: str = "#ffffff") -> str:
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 72 72">'
        f'<rect fill="{fill}" width="72" height="72" rx="18"/>'
        f'<text x="36" y="46" text-anchor="middle" fill="{text_fill}" '
        f'font-size="22" font-family="Arial,sans-serif" font-weight="700">{initials}</text>'
        f"</svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "SCB_CXO_Board_Dashboard.html"
    out_dir = root / "share"
    out = out_dir / "SCB_CXO_Board_Dashboard_offline.html"

    if not src.is_file():
        raise SystemExit(f"Missing source dashboard: {src}")

    text = src.read_text(encoding="utf-8")

    replacements = [
        (
            "https://api.dicebear.com/7.x/micah/svg?seed=AriyaKlaimongkol&backgroundColor=4e2a84&radius=18",
            _svg_avatar_uri("AK", "#4e2a84"),
        ),
        (
            "https://api.dicebear.com/7.x/micah/svg?seed=NattapongSrisawat&backgroundColor=2d1654&radius=18",
            _svg_avatar_uri("NS", "#2d1654"),
        ),
        (
            "https://api.dicebear.com/7.x/micah/svg?seed=SiripornVejchapinan&backgroundColor=c9a84c&radius=18",
            _svg_avatar_uri("SW", "#c9a84c", "#1a1028"),
        ),
    ]
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"Expected substring not found (file changed?): {old[:60]}…")
        text = text.replace(old, new, 1)

    text = text.replace(
        "<title>Phoenix Dashboard — SCBx personalization journeys</title>",
        "<title>SCBx Phoenix Dashboard (shareable demo)</title>",
        1,
    )

    if 'name="description"' not in text:
        text = text.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
            '  <meta name="description" content="SCBx Phoenix personalization board — single HTML file. '
            'Figma journey frames need internet; optional API via ?cxo_api= when you host the backend." />',
            1,
        )

    banner = (
        "\n  <!-- Built by scripts/build_share_dashboard.py — avatars inlined for offline/share. -->\n"
    )
    if "build_share_dashboard.py" not in text:
        text = text.replace("<head>\n", "<head>" + banner, 1)

    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
