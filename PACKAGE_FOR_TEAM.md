# Shareable package — SCBx CXO + demos

## What to send others

- **Best:** a **zip** of this project folder (see **“Create the zip”** below), **or** a **git repo URL** they can clone.  
- Tell them to follow **`docs/RUN_LOCALLY_FOR_TEAM.md`** (full steps + optional API).

## Steps for recipients (short)

1. Install **Python 3.10+**.  
2. Unzip / clone into a folder and open a terminal **in that folder**.  
3. Start the local server — easiest: double-click **`serve-demo.bat`** (Windows) or **`serve-demo.sh`** (Mac/Linux). That runs **`serve_local.py`**, which picks a free port (starts at **8844**), binds **127.0.0.1**, and opens your browser. Alternatives: `py serve_local.py` / `python3 serve_local.py`, or `python -m http.server 8844 -b 127.0.0.1`.  
4. If the browser did not open, use the URL printed in the terminal — usually **`http://127.0.0.1:8844/index.html`** or **`http://127.0.0.1:8844/SCB_CXO_Board_Dashboard.html`**.  
5. *(Optional)* Second terminal: `python server/seed.py` then `python server/cxo_api.py`, then add **`?veraHub=http://127.0.0.1:8765`** to the CXO URL (same port as step 4).

## Create the zip (Windows / Mac / Linux — recommended)

From the project root (needs Python):

```bash
python scripts/make_share_zip.py
```

Output: **`dist/SCBX-local-demo.zip`** — share that file. It excludes `node_modules`, `.git`, local SQLite DBs, `dist/`, etc.

**Alternative (Windows PowerShell only):** if your machine allows scripts,

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\make_share_zip.ps1
```

## Create the zip (manual)

Zip the folder yourself, **excluding** `.git`, `node_modules`, `__pycache__`, `dist/`, and `server/cxo_dashboard.db` if present—or share a **git clone URL** instead.

---

Full detail: **`docs/RUN_LOCALLY_FOR_TEAM.md`**
