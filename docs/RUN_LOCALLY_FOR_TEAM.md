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
3. **Start a local static server** on port **8844**:
   - **Windows:** double-click **`serve-demo.bat`** in the project folder, **or** run:
     ```bash
     python -m http.server 8844
     ```
   - **Mac/Linux:** `chmod +x serve-demo.sh && ./serve-demo.sh` **or** `python3 -m http.server 8844`
4. Open a browser and go to:
   - **Hub:** [http://localhost:8844/index.html](http://localhost:8844/index.html)  
   - **CXO journey board:** [http://localhost:8844/SCB_CXO_Board_Dashboard.html](http://localhost:8844/SCB_CXO_Board_Dashboard.html)  
   - **Ontology map:** [http://localhost:8844/SCB_Ontology_Map.html](http://localhost:8844/SCB_Ontology_Map.html)  
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

2. Open the CXO board with a query parameter (same static server on 8844 still running):
   ```
   http://localhost:8844/SCB_CXO_Board_Dashboard.html?veraHub=http://127.0.0.1:8765
   ```

3. **Windows shortcut:** you can double-click **`run-cxo-api.bat`** in the project root to start the API (still start `python -m http.server 8844` separately for the HTML).

---

## Double-click only (may work, may not)

- **`run-demo.bat`** (Windows) opens **`index.html`** via `file://`.  
- Some companies **block** `file://`, or **fetch** to JSON files may fail. If anything looks broken, use the **Quick path** above.

---

## Troubleshooting

| Issue | What to try |
|--------|-------------|
| Ontology map is blank / errors | Serve over **http://localhost:8844** (not `file://`). |
| Port 8844 already in use | Run `python -m http.server 8090` and open `http://localhost:8090/...` |
| **localhost:8080** shows 404 for SCB files | **8080 is often used by Docker or other apps**, not this repo. Use **`serve-demo.bat`** (port **8844**) or pick another free port. |
| `python` not found | Install Python, or try `py -m http.server 8844` (Windows) / `python3` (Mac). |
| CXO + API not talking | Same machine: use `?veraHub=http://127.0.0.1:8765` and ensure **both** static server and `cxo_api.py` are running. |

---

## Who to ask

If you received a **zip** from a colleague, ask them for the latest package or repo link. Regenerate the share zip from the repo with **`scripts/make_share_zip.ps1`** (Windows) or follow your team’s packaging process.
