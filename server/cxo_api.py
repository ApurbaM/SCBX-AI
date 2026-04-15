"""
Lightweight HTTP API for the CXO dashboard (SQLite + JSON).

Endpoints (CORS enabled for local HTML demos):
  GET  /health
  GET  /ecliptos/vera                     — discovery (EcliptOS Vera Hub compatible layer; JSON links)
  GET  /ecliptos/vera/...                 — same as /... (optional mount prefix for proxies)
  GET  /api/v1/personas
  GET  /api/v1/personas/{personaId}/twin
  PUT  /api/v1/personas/{personaId}/twin   (JSON body partial twin)
  GET  /api/v1/cockpit/metrics?personaId=&horizon=   (Vera Hub compatible)
  GET  /api/v1/ontology                             (Vera Hub compatible)
  GET  /api/v1/catalog/datasets?limit=50&subject_area=

Run from repo root:
  python server/cxo_api.py

First start creates the DB via server/seed.py if missing.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from metrics_engine import compute_board_metrics
from twin_utils import merge_twin

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB_PATH = HERE / "cxo_dashboard.db"
SEED_SCRIPT = HERE / "seed.py"
DEFAULT_PORT = 8765
VERA_HUB_MOUNT = "/ecliptos/vera"


def strip_vera_mount(path: str) -> str:
    """Allow base URL …/ecliptos/vera with the same paths the dashboard already calls."""
    if path == VERA_HUB_MOUNT:
        return path
    if path.startswith(VERA_HUB_MOUNT + "/"):
        inner = path[len(VERA_HUB_MOUNT) :]
        return inner if inner else "/"
    return path


def vera_discovery_payload(port: int) -> dict:
    root = f"http://127.0.0.1:{port}"
    return {
        "product": "EcliptOS Vera Hub compatible CXO API (local SQLite)",
        "layer": "SCB CXO dashboard backend",
        "links": {
            "health": f"{root}/health",
            "ontologyJson": f"{root}/api/v1/ontology",
            "cockpitMetricsExample": f"{root}/api/v1/cockpit/metrics?personaId=young_professional&horizon=month",
            "personas": f"{root}/api/v1/personas",
            "catalogDatasets": f"{root}/api/v1/catalog/datasets?limit=50",
            "ontologyViaMount": f"{root}{VERA_HUB_MOUNT}/api/v1/ontology",
        },
        "note": "Graph UI for the static pack uses SCB_Ontology_Map.html + data/scb_data_catalog.json; this API serves the same ontology graph from SQLite after seeding.",
    }


def ensure_db():
    if not DB_PATH.is_file():
        subprocess.check_call([sys.executable, str(SEED_SCRIPT)], cwd=str(ROOT))


def connect():
    return sqlite3.connect(str(DB_PATH))


def connect_row():
    c = connect()
    c.row_factory = sqlite3.Row
    return c


def send_json(handler: BaseHTTPRequestHandler, status: int, obj: dict):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
    handler.end_headers()
    handler.wfile.write(body)


def send_text(handler: BaseHTTPRequestHandler, status: int, text: str, content_type="text/plain; charset=utf-8"):
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path_raw = parsed.path.rstrip("/") or "/"
        qs = urllib.parse.parse_qs(parsed.query)

        if path_raw == VERA_HUB_MOUNT:
            port = self.server.server_address[1]
            return send_json(self, 200, vera_discovery_payload(port))

        path = strip_vera_mount(path_raw)

        if path == "/health":
            return send_json(self, 200, {"ok": True, "db": str(DB_PATH.name)})

        if path == "/api/v1/personas":
            conn = connect_row()
            try:
                rows = conn.execute(
                    "SELECT persona_id, display_name, short_desc, avatar_url, defaults_json FROM persona ORDER BY persona_id"
                ).fetchall()
                out = []
                for r in rows:
                    out.append(
                        {
                            "personaId": r["persona_id"],
                            "name": r["display_name"],
                            "short": r["short_desc"],
                            "avatar": r["avatar_url"],
                            "defaults": json.loads(r["defaults_json"]),
                        }
                    )
                return send_json(self, 200, {"personas": out})
            finally:
                conn.close()

        if path.startswith("/api/v1/personas/") and path.endswith("/twin"):
            pid = path[len("/api/v1/personas/") : -len("/twin")]
            conn = connect_row()
            try:
                row = conn.execute(
                    "SELECT state_json FROM persona_twin WHERE persona_id = ?", (pid,)
                ).fetchone()
                if not row:
                    return send_json(self, 404, {"error": "persona not found"})
                return send_json(self, 200, {"personaId": pid, "twin": json.loads(row["state_json"])})
            finally:
                conn.close()

        if path in ("/api/v1/cockpit/metrics", "/cockpit/metrics", "/metrics/cockpit"):
            pid = (qs.get("personaId") or qs.get("persona") or [""])[0]
            conn = connect_row()
            try:
                row = conn.execute(
                    "SELECT state_json FROM persona_twin WHERE persona_id = ?", (pid,)
                ).fetchone()
                if not row:
                    return send_json(self, 404, {"error": "unknown personaId"})
                twin = json.loads(row["state_json"])
                payload = compute_board_metrics(twin)
                payload["personaId"] = pid
                payload["horizon"] = (qs.get("horizon") or ["month"])[0]
                return send_json(self, 200, payload)
            finally:
                conn.close()

        if path in ("/api/v1/ontology", "/ontology/graph", "/ontology"):
            conn = connect_row()
            try:
                nodes = []
                for r in conn.execute("SELECT uri, kind, label, payload_json FROM ontology_node"):
                    n = json.loads(r["payload_json"])
                    if "id" not in n:
                        n["id"] = r["uri"]
                    nodes.append(n)
                edges = []
                for r in conn.execute("SELECT from_uri, to_uri, rel FROM ontology_edge"):
                    edges.append({"from": r["from_uri"], "to": r["to_uri"], "rel": r["rel"]})
                return send_json(self, 200, {"ontology": {"nodes": nodes, "edges": edges}})
            finally:
                conn.close()

        if path == "/api/v1/catalog/datasets":
            limit = int((qs.get("limit") or ["200"])[0])
            limit = max(1, min(limit, 500))
            sa = (qs.get("subject_area") or [None])[0]
            conn = connect_row()
            try:
                if sa:
                    rows = conn.execute(
                        """
                        SELECT dataset_name, full_name, subject_area, update_frequency
                        FROM catalog_dataset WHERE subject_area = ? ORDER BY dataset_name LIMIT ?
                        """,
                        (sa, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT dataset_name, full_name, subject_area, update_frequency
                        FROM catalog_dataset ORDER BY dataset_name LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
                return send_json(
                    self,
                    200,
                    {
                        "datasets": [dict(r) for r in rows],
                    },
                )
            finally:
                conn.close()

        return send_json(self, 404, {"error": "not found", "path": path})

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path_raw = parsed.path.rstrip("/") or "/"
        path = strip_vera_mount(path_raw)
        if path.startswith("/api/v1/personas/") and path.endswith("/twin"):
            pid = path[len("/api/v1/personas/") : -len("/twin")]
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                patch = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                return send_json(self, 400, {"error": "invalid JSON"})
            conn = connect_row()
            try:
                row = conn.execute(
                    "SELECT state_json FROM persona_twin WHERE persona_id = ?", (pid,)
                ).fetchone()
                if not row:
                    return send_json(self, 404, {"error": "persona not found"})
                current = json.loads(row["state_json"])
                merged = merge_twin(current, patch)
                conn.execute(
                    "UPDATE persona_twin SET state_json = ?, updated_at = datetime('now') WHERE persona_id = ?",
                    (json.dumps(merged, ensure_ascii=False), pid),
                )
                conn.commit()
                return send_json(self, 200, {"personaId": pid, "twin": merged})
            finally:
                conn.close()
        return send_json(self, 404, {"error": "not found"})


def main():
    import os

    ensure_db()
    port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print(f"CXO API listening on http://127.0.0.1:{port}")
    print("  GET /ecliptos/vera  (Vera Hub discovery JSON)")
    print("  GET /api/v1/personas")
    print("  GET /api/v1/cockpit/metrics?personaId=young_professional&horizon=month")
    print("  GET /api/v1/ontology")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
