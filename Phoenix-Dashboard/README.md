# Phoenix Dashboard (standalone)

Self-contained HTML prototype pack for the **Phoenix / CXO journey board**, persona demo customers, embedded Jarvis flows, and related SCBx reference pages. This tree is meant to live in **its own Git repository**—it does not depend on the parent `SCBX` monorepo layout.

## Quick start (local)

1. Install **Python 3** (so `python` or `py` is on your PATH).
2. From this folder, either:
   - **Windows:** double-click `run-demo.bat`, or  
   - **Terminal:** `python -m http.server 8889` (change the port if busy).
3. Open in the browser (HTTP, not `file://`):
   - **Dashboard:** http://127.0.0.1:8889/SCB_CXO_Board_Dashboard.html  
   - **Hub:** http://127.0.0.1:8889/index.html  

Hard refresh (Ctrl+F5) after pulling updates so CSS and HTML are not cached from an older folder.

## What is included

| Area | Role |
|------|------|
| `SCB_CXO_Board_Dashboard.html` | Phoenix journey board (Journeys 1 & 2, A–D frames, LHS profile) |
| `SCB_Morning_Briefing_Demo.html` | Morning brief iframe target |
| `SCB_Loan_Servicing_Jarvis_Flow.html` | Loan / Jarvis servicing iframe target |
| `assets/` | PNG references used by the board (including post-servicing Jarvis capture) |
| `index.html` | Small hub linking main prototypes |
| `SCB_Ontology_Map.html`, other `SCB_*.html` | Optional reference / workshop pages |
| `data/scb_data_catalog.json` | Catalog data for ontology map |
| `docs/`, `scripts/`, `js/` | Supporting notes and tooling |

## Publishing as its own remote

```bash
cd Phoenix-Dashboard
git remote add origin https://github.com/<you>/<new-repo>.git
git push -u origin main
```

Create an **empty** repository on GitHub (or your host) first, then add `origin` and push.

## Note on demo data

Customer rows in the dashboard script are **fictional demo records** (one per persona category), not production data.
