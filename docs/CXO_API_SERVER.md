# CXO dashboard — local API and database

This adds a **small Python service** and a **SQLite file** so the demo can behave more like a real app: personas and “twin” state live in a database, **cockpit metrics** are computed from that state, and an **ontology graph** (catalog + CXO journey layer) is served as JSON.

## What you get

| Piece | Purpose |
|--------|---------|
| **`server/cxo_dashboard.db`** | SQLite file (created by seeding). **Not committed to git** (see `.gitignore`). |
| **`server/schema.sql`** | Table definitions: personas, twin state, catalog datasets, ontology nodes/edges. |
| **`server/seed.py`** | Loads the three dashboard personas, **93 catalog datasets** from `data/scb_data_catalog.json`, **ontology nodes/edges** from the same file (truncated export in JSON), plus **CXO journey / persona** nodes for the board story. |
| **`server/cxo_api.py`** | HTTP API on **http://127.0.0.1:8765** (change with `PORT=8888`). **CORS** enabled for local HTML. |
| **`server/metrics_engine.py`** | Same demo math as the browser `computeBoardMetrics` so numbers match when you point Vera Hub at this API. |

## Commands (from repo root)

```bash
# Build or rebuild the database (optional --force wipes DB)
python server/seed.py
python server/seed.py --force

# Start API (creates DB automatically if missing)
python server/cxo_api.py
```

## HTTP routes

- **`GET /health`** — liveness check.
- **`GET /api/v1/personas`** — list personas + default twin fields.
- **`GET /api/v1/personas/{personaId}/twin`** — current twin JSON (used for metrics).
- **`PUT /api/v1/personas/{personaId}/twin`** — merge a partial JSON body into the twin (e.g. after sliders in a future UI).
- **`GET /api/v1/cockpit/metrics?personaId=…&horizon=…`** — Vera Hub–style payload: `{ "computed": { … } }`.
- **`GET /api/v1/ontology`** — `{ "ontology": { "nodes": [...], "edges": [...] } }` (same broad shape as `vera_hub_backend.js` expects).
- **`GET /api/v1/catalog/datasets?limit=50&subject_area=Deposit`** — browse seeded catalog rows.

## Hooking the CXO HTML board to this API

1. Serve the repo over HTTP (any static server on one port).
2. Run **`python server/cxo_api.py`** on **8765**.
3. In the browser, open the dashboard with a Vera Hub base URL, for example:

   `SCB_CXO_Board_Dashboard.html?veraHub=http://127.0.0.1:8765`

   Or set **`localStorage.veraHubBaseUrl`** to `http://127.0.0.1:8765` using the board’s configure flow / devtools.

The existing **`js/vera_hub_backend.js`** will call **`/api/v1/cockpit/metrics`** and **`/api/v1/ontology`** against that base.

## Notes

- Metrics are still the **same demo model** as in the dashboard script; only the **storage** moved to SQLite and the **serving** to HTTP.
- Ontology in the DB merges **catalog graph** (from JSON) with a thin **CXO layer** (journeys A–D, personalization concept, links from each `persona:{id}` to journeys/engine).
- Re-run **`python server/seed.py --force`** after you change `data/scb_data_catalog.json` or persona definitions in **`server/seed.py`**.
