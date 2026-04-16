"""
Build SQLite DB for CXO dashboard: personas, twin state, catalog datasets, ontology graph.

Usage (from repo root):
  python server/seed.py
  python server/seed.py --force
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from twin_utils import hydrate_twin

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(__file__).resolve().parent / "cxo_dashboard.db"
CATALOG_PATH = ROOT / "data" / "scb_data_catalog.json"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

PERSONAS = [
    {
        "personaId": "young_professional",
        "name": "Young Professional",
        "short": "Early career · mobile-first · starter products",
        "avatar": "https://api.dicebear.com/7.x/micah/svg?seed=AriyaKlaimongkol&backgroundColor=4e2a84&radius=18",
        "customerRef": "EASY-2847193",
        "fullName": "Ms. Ariya Klaimongkol",
        "lineOfWork": "Digital marketing associate · Pathum Wan, Bangkok",
        "productHoldings": [
            {"name": "SCB Easy savings", "detail": "฿42,180 · THB"},
            {"name": "SCB Cashback credit card", "detail": "฿35,000 limit · active"},
            {"name": "Short-term fixed deposit", "detail": "฿100,000 · 6 mo"},
            {"name": "Starter unit trust", "detail": "฿8,400 balance"},
        ],
        "journeyMetrics": {
            "a_ctr": 10.8,
            "a_time": 3.4,
            "b_logins": 5,
            "b_logins_baseline": 4,
            "b_nba_ctr": 12.4,
            "c_csat": 82,
            "c_res_no_hum": 81.2,
            "d_offer_ctr": 10.9,
            "d_monthly_leads": 412,
            "d_monthly_leads_ref": 380,
        },
        "defaults": {
            "age": 26,
            "incomeTHB": 28000,
            "lifeStage": "early_career",
            "channels": ["mobile_first"],
            "risk": "moderate",
            "contextCompleteness": 62,
            "goalTags": ["ease_of_banking", "borrow"],
            "language": "EN",
            "interests": ["fashion"],
        },
    },
    {
        "personaId": "emerging_family",
        "name": "Emerging Family",
        "short": "Mid-life builder · omnichannel · protection & goals",
        "avatar": "https://api.dicebear.com/7.x/micah/svg?seed=NattapongSrisawat&backgroundColor=2d1654&radius=18",
        "customerRef": "EASY-4110287",
        "fullName": "Mr. Nattapong Srisawat",
        "lineOfWork": "Operations supervisor · Bang Na, Bangkok",
        "productHoldings": [
            {"name": "Home loan (SCB)", "detail": "฿4.2M outstanding · fixed 2.89%"},
            {"name": "Term life protection", "detail": "฿2M sum assured"},
            {"name": "Kids savings (junior)", "detail": "฿186,000"},
            {"name": "Payroll current account", "detail": "฿28,400"},
        ],
        "journeyMetrics": {
            "a_ctr": 9.9,
            "a_time": 4.1,
            "b_logins": 5,
            "b_logins_baseline": 4,
            "b_nba_ctr": 13.5,
            "c_csat": 84,
            "c_res_no_hum": 82.0,
            "d_offer_ctr": 11.0,
            "d_monthly_leads": 521,
            "d_monthly_leads_ref": 480,
        },
        "defaults": {
            "age": 38,
            "incomeTHB": 52000,
            "lifeStage": "midlife_builder",
            "channels": ["omnichannel", "mobile_first"],
            "risk": "moderate",
            "contextCompleteness": 78,
            "goalTags": ["ease_of_banking", "save"],
            "language": "TH",
            "interests": ["food"],
        },
    },
    {
        "personaId": "emerging_affluent",
        "name": "Emerging Affluent",
        "short": "Wealth builder · advisory-led · complex needs",
        "avatar": "https://api.dicebear.com/7.x/micah/svg?seed=SiripornVejchapinan&backgroundColor=c9a84c&radius=18",
        "customerRef": "EASY-9021844",
        "fullName": "Ms. Siriporn Wejchapinan",
        "lineOfWork": "Regional sales lead · Wireless Rd, Bangkok",
        "productHoldings": [
            {"name": "Premier banking · investment portfolio", "detail": "฿3.8M AUM"},
            {"name": "FX multicurrency account", "detail": "USD / THB · hedged"},
            {"name": "Structured note (note-linked)", "detail": "฿1.2M notional"},
            {"name": "Private wealth credit facility", "detail": "฿800,000 available"},
        ],
        "journeyMetrics": {
            "a_ctr": 11.8,
            "a_time": 3.1,
            "b_logins": 5,
            "b_logins_baseline": 4,
            "b_nba_ctr": 15.2,
            "c_csat": 88,
            "c_res_no_hum": 86.1,
            "d_offer_ctr": 12.6,
            "d_monthly_leads": 687,
            "d_monthly_leads_ref": 520,
        },
        "defaults": {
            "age": 46,
            "incomeTHB": 180000,
            "lifeStage": "wealth_builder",
            "channels": ["advisory_led", "omnichannel"],
            "risk": "high",
            "contextCompleteness": 88,
            "goalTags": ["invest", "ease_of_banking"],
            "language": "EN",
            "interests": ["travel"],
        },
    },
]

# CXO journey layer (uris align with dashboard concepts; edges are illustrative for personalization storyboard)
CXO_NODES = [
    {
        "id": "cxo:Journey",
        "type": "Concept",
        "label": "Customer journey",
    },
    {
        "id": "cxo:Journey:J1",
        "type": "Journey",
        "label": "Journey 1 · Daily engagement",
    },
    {
        "id": "cxo:Journey:J2",
        "type": "Journey",
        "label": "Journey 2 · Conversational servicing",
    },
    {
        "id": "cxo:Screen:morning_brief",
        "type": "Touchpoint",
        "label": "Morning brief (A)",
    },
    {
        "id": "cxo:Screen:app_home",
        "type": "Touchpoint",
        "label": "App home (B)",
    },
    {
        "id": "cxo:Screen:loan_servicing",
        "type": "Touchpoint",
        "label": "Loan servicing · Jarvis (C)",
    },
    {
        "id": "cxo:Screen:anomaly",
        "type": "Touchpoint",
        "label": "Transaction anomaly (D)",
    },
    {
        "id": "cxo:PersonalizationEngine",
        "type": "Concept",
        "label": "Personalization engine (demo model)",
    },
    {
        "id": "cxo:DataCatalog",
        "type": "Concept",
        "label": "SCB analytics catalog (datasets)",
    },
]

CXO_EDGES = [
    ("cxo:Journey:J1", "cxo:Screen:morning_brief", "includes"),
    ("cxo:Journey:J1", "cxo:Screen:app_home", "includes"),
    ("cxo:Journey:J2", "cxo:Screen:loan_servicing", "includes"),
    ("cxo:Journey:J2", "cxo:Screen:anomaly", "includes"),
    ("cxo:Journey", "cxo:Journey:J1", "contains"),
    ("cxo:Journey", "cxo:Journey:J2", "contains"),
    ("cxo:PersonalizationEngine", "cxo:Journey:J1", "shapes"),
    ("cxo:PersonalizationEngine", "cxo:Journey:J2", "shapes"),
    ("cxo:DataCatalog", "cxo:PersonalizationEngine", "informs"),
]


def run_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)


def migrate_persona_profile_columns(conn: sqlite3.Connection) -> None:
    """Add anchored customer profile columns on older DBs (CREATE IF NOT EXISTS skipped them)."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(persona)").fetchall()}
    if "customer_ref" not in cols:
        conn.execute("ALTER TABLE persona ADD COLUMN customer_ref TEXT")
    if "full_name" not in cols:
        conn.execute("ALTER TABLE persona ADD COLUMN full_name TEXT")
    if "line_of_work" not in cols:
        conn.execute("ALTER TABLE persona ADD COLUMN line_of_work TEXT")
    if "product_holdings_json" not in cols:
        conn.execute("ALTER TABLE persona ADD COLUMN product_holdings_json TEXT")
    if "journey_metrics_json" not in cols:
        conn.execute("ALTER TABLE persona ADD COLUMN journey_metrics_json TEXT")


def seed_personas(conn: sqlite3.Connection) -> None:
    for p in PERSONAS:
        pid = p["personaId"]
        defaults = hydrate_twin(p["defaults"])
        holdings = json.dumps(p.get("productHoldings") or [], ensure_ascii=False)
        jmetrics = json.dumps(p.get("journeyMetrics") or {}, ensure_ascii=False)
        conn.execute(
            """
            INSERT OR REPLACE INTO persona (
              persona_id, display_name, short_desc, avatar_url,
              customer_ref, full_name, line_of_work, product_holdings_json, journey_metrics_json, defaults_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pid,
                p["name"],
                p["short"],
                p["avatar"],
                p.get("customerRef"),
                p.get("fullName"),
                p.get("lineOfWork"),
                holdings,
                jmetrics,
                json.dumps(defaults, ensure_ascii=False),
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO persona_twin (persona_id, state_json, updated_at)
            VALUES (?, ?, datetime('now'))
            """,
            (pid, json.dumps(defaults)),
        )


def seed_catalog(conn: sqlite3.Connection) -> None:
    if not CATALOG_PATH.is_file():
        print(f"Warning: catalog not found at {CATALOG_PATH}", file=sys.stderr)
        return
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    rows = []
    for ds in data.get("dataSets") or []:
        rows.append(
            (
                ds.get("dataSetName") or "",
                ds.get("dataSetFullName") or "",
                ds.get("description") or "",
                ds.get("updateFrequency") or "",
                ds.get("subjectArea") or "",
            )
        )
    conn.executemany(
        """
        INSERT OR REPLACE INTO catalog_dataset
        (dataset_name, full_name, description, update_frequency, subject_area)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    print(f"Loaded {len(rows)} catalog datasets.")


def seed_ontology_from_catalog(conn: sqlite3.Connection) -> None:
    if not CATALOG_PATH.is_file():
        return
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    onto = data.get("ontology") or {}
    nodes = onto.get("nodes") or []
    edges = onto.get("edges") or []

    conn.execute("DELETE FROM ontology_edge WHERE from_uri LIKE 'dataset:%' OR from_uri LIKE 'column:%'")
    conn.execute("DELETE FROM ontology_node WHERE uri LIKE 'dataset:%' OR uri LIKE 'column:%' OR uri LIKE 'subjectArea:%'")

    batch_n = []
    for n in nodes:
        uri = n.get("id")
        if not uri:
            continue
        typ = n.get("type") or "Entity"
        label = n.get("label") or uri
        batch_n.append((uri, typ, label, json.dumps(n, ensure_ascii=False)))

    conn.executemany(
        "INSERT OR REPLACE INTO ontology_node (uri, kind, label, payload_json) VALUES (?, ?, ?, ?)",
        batch_n,
    )
    print(f"Loaded {len(batch_n)} ontology nodes from catalog.")

    batch_e = [(e.get("from"), e.get("to"), e.get("rel") or "related") for e in edges if e.get("from") and e.get("to")]
    conn.executemany(
        "INSERT OR IGNORE INTO ontology_edge (from_uri, to_uri, rel) VALUES (?, ?, ?)",
        batch_e,
    )
    print(f"Loaded {len(batch_e)} ontology edges from catalog.")


def seed_cxo_layer(conn: sqlite3.Connection) -> None:
    for n in CXO_NODES:
        uri = n["id"]
        conn.execute(
            "INSERT OR REPLACE INTO ontology_node (uri, kind, label, payload_json) VALUES (?, ?, ?, ?)",
            (uri, n["type"], n["label"], json.dumps(n, ensure_ascii=False)),
        )
    for fr, to, rel in CXO_EDGES:
        conn.execute(
            "INSERT OR IGNORE INTO ontology_edge (from_uri, to_uri, rel) VALUES (?, ?, ?)",
            (fr, to, rel),
        )
    # Link each persona to personalization engine + J1 (illustrative)
    for p in PERSONAS:
        pid = p["personaId"]
        conn.execute(
            "INSERT OR IGNORE INTO ontology_edge (from_uri, to_uri, rel) VALUES (?, ?, ?)",
            (f"persona:{pid}", "cxo:PersonalizationEngine", "tunedBy"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO ontology_edge (from_uri, to_uri, rel) VALUES (?, ?, ?)",
            (f"persona:{pid}", "cxo:Journey:J1", "views"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO ontology_node (uri, kind, label, payload_json) VALUES (?, ?, ?, ?)",
            (
                f"persona:{pid}",
                "PersonaSegment",
                p["name"],
                json.dumps({"personaId": pid}, ensure_ascii=False),
            ),
        )
    print("CXO journey / persona ontology layer inserted.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Delete existing DB and rebuild")
    args = ap.parse_args()

    if args.force and DB_PATH.is_file():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        run_schema(conn)
        migrate_persona_profile_columns(conn)
        seed_personas(conn)
        seed_catalog(conn)
        seed_ontology_from_catalog(conn)
        seed_cxo_layer(conn)
        conn.commit()
        print(f"Database ready: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
