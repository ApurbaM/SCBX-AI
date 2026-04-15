SCB Morning Brief & Jarvis — click-through prototype (shareable zip)
====================================================================

Easiest (no install)
--------------------
1. Unzip this folder anywhere on your computer.
2. Double-click either:
     index.html                      (opens the prototype)
   or  SCB_Morning_Briefing_Demo.html   (same app)
3. In the browser, tap/click through the flow: lock screen, notifications, home,
   morning brief, Jarvis chat, portfolio, profile, wellness, voice, etc.
   No server required for normal use.

Optional launcher
-----------------
- Windows: double-click  run-demo.bat
- Mac / Linux / Git Bash: in a terminal, run:
    chmod +x run-demo.sh
    ./run-demo.sh

Jump to a specific screen (for reviews or screenshots)
------------------------------------------------------
Open the same HTML file, then add to the address bar after the file name:

  ?screen=lock
  ?screen=home
  ?screen=briefing
  ?screen=chat
  ?screen=portfolio
  ?screen=balances
  ?screen=profile
  ?screen=wellness_0   (through wellness_4)
  ?screen=jarvis_fs
  ?screen=voice
  ?screen=beyond_score
  ?screen=beyond_mba
  ?screen=beyond_bali

Example (if the file is opened via a local server; use the port from serve-demo):
  http://localhost:8844/SCB_Morning_Briefing_Demo.html?screen=briefing

Notes
-----
- You need an internet connection the first time (the page loads a small script from Figma’s domain; the demo itself works offline after cache).
- If your company blocks file:// links, use “Local server” below.

Local server (only if double-click does not work)
-------------------------------------------------
From inside this folder, in Terminal / PowerShell (8844 avoids Docker on 8080):

  python -m http.server 8844

Then in the browser open:

  http://localhost:8844/SCB_Morning_Briefing_Demo.html

(If you do not have Python, install it from python.org or use another static server you already use.)

CXO Board Dashboard — data catalog (Excel template)
---------------------------------------------------
The file `SCB_CXO_Board_Dashboard.html` loads `data/scb_data_catalog.json`, which is generated from
`Data Template_vCleaned.xlsx` by running:

  python scripts/export_data_template.py

Re-run that script whenever the Excel template changes, then refresh the dashboard.
