# Run the SCBx demos locally (for teammates)

Use this when someone sends you a **zip of the repo** or you **clone** the project. A **local web server** is recommended so every page (especially the ontology map and optional API) works reliably.

---

## What you need installed

- **Python 3.10+** on your machine ([python.org](https://www.python.org/downloads/))  
  - Check: `python --version` (Windows) or `python3 --version` (Mac/Linux)

No Node.js is required unless you want to use your own static server instead of Python.

---

## Quick path (recommended)

1. **Unzip** the folder somewhere easy (e.g. Desktop), **or** clone the git repo into a folder.  
2. Open **PowerShell** (Windows) or **Terminal** (Mac) and **go into that folder**:
   ```bash
   cd path/to/SCBX
   ```
3. **Start a local static server** (recommended: picks a free port, binds **127.0.0.1**, opens your browser):
   - **Windows:** double-click **`serve-demo.bat`**, **or** run:
     ```bash
     py serve_local.py
     ```
     (or `python serve_local.py` if you do not have `py`.)
   - **Mac/Linux:** `chmod +x serve-demo.sh && ./serve-demo.sh` **or** `python3 serve_local.py`
   - **Manual one-liner** (fixed port): `python -m http.server 8844 -b 127.0.0.1`
4. Open a browser using the **URL printed in the terminal** (often **8844**). Typical links:
   - **Hub:** `http://127.0.0.1:8844/index.html`  
   - **CXO journey board:** `http://127.0.0.1:8844/SCB_CXO_Board_Dashboard.html`  
   - **Ontology map:** `http://127.0.0.1:8844/SCB_Ontology_Map.html`  
   Use **127.0.0.1** instead of **localhost** if the page does not load (some Windows setups resolve `localhost` to IPv6 only).
5. When finished, go back to the terminal and press **Ctrl+C** to stop the server.

---

## Optional: local API + database (Vera Hub–style demo)

Use this if you want the board to pull **metrics / ontology** from a tiny backend (SQLite + Python).

1. In a **second** terminal, from the **same project folder**:
   ```bash
   python server/seed.py
   python server/cxo_api.py
   ```
   The API listens on **http://127.0.0.1:8765** by default.

2. Open the CXO board with a query parameter (same static server still running — use the **port** from the terminal):
   ```
   http://127.0.0.1:8844/SCB_CXO_Board_Dashboard.html?veraHub=http://127.0.0.1:8765
   ```

3. **Windows shortcut:** double-click **`run-cxo-api.bat`** to start the API (keep **`serve-demo.bat`** / `serve_local.py` running for the HTML).

---

## Double-click only (may work, may not)

- **`run-demo.bat`** (Windows) opens **`index.html`** via `file://`.  
- Some companies **block** `file://`, or **fetch** to JSON files may fail. If anything looks broken, use the **Quick path** above.

---

## Troubleshooting

| Issue | What to try |
|--------|-------------|
| Ontology map is blank / errors | Serve over **http://127.0.0.1:…** (not `file://`). |
| Port 8844 already in use | **`serve_local.py`** tries **8845, 8846, …** automatically. Or run `python -m http.server 8090 -b 127.0.0.1` and open `http://127.0.0.1:8090/...` |
| **localhost** does not open | Use **http://127.0.0.1:PORT/...** instead (IPv6 / DNS issue on some PCs). |
| **localhost:8080** shows 404 for SCB files | **8080 is often used by Docker**, not this repo. Use **`serve-demo.bat`** or **`serve_local.py`**. |
| `python` not found | Install Python, or use **`py serve_local.py`** on Windows. |
| CXO + API not talking | Same machine: use `?veraHub=http://127.0.0.1:8765` and ensure **both** static server and `cxo_api.py` are running. |

---

## Who to ask

If you received a **zip** from a colleague, ask them for the latest package or repo link. Regenerate the share zip from the repo with **`scripts/make_share_zip.ps1`** (Windows) or follow your team’s packaging process.
