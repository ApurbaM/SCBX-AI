# What this CXO-style dashboard actually is (plain English)

This is a **short, non-technical** note about the journey board you see in the browser (**`SCB_CXO_Board_Dashboard.html`**) and the files around it: what it does, what it connects to, and what is **only for show / demo**.

---

## What you see on the screen

**On the left** you can pick one of **three example customer types** (“personas”) and adjust simple sliders and tags—things like age, income, life stage, how they bank, what they care about, and risk appetite. There is also a **read-only “how complete is this picture?”** style number so it *feels* like a digital twin, but it is all **coded in the web page**, not pulled from a real customer record.

**On the right** you see **two journey areas** with headline numbers (things like engagement, completion, satisfaction-style metrics) and **little phone-style previews** that load other HTML demos inside the page (morning brief, a static home screenshot, a loan chat flow, an “unusual transaction” flow).

So in everyday terms: **it is an interactive storyboard** for how journeys might look for different customer types—not a live operations system.

---

## How it is “built” under the hood (still simple)

Think of it as **a set of web pages that talk to each other in the simplest way possible**:

- There is **no separate app server** in this folder that you install and run. Your browser opens HTML files and runs the JavaScript inside them.
- The **main dashboard page** remembers which persona you picked and passes that choice to the smaller demos by **changing the web address** each mini-screen loads (for example “which persona am I showing?”).
- There is a **small optional hook** (“Vera Hub”) that *could* call a real company API later for numbers or a relationship diagram. **Right now that hook is turned off** unless someone configures a real web address—so day-to-day, everything runs **locally in the browser**.

No hidden database server starts when you open these files.

---

## Database

**There isn’t one** in this project—not in the sense of “where customer accounts live.”

Nothing here is storing your clicks in Postgres, SQL Server, etc. If you hear “data,” it usually means **files shipped with the demo** (see below), not a running bank database.

---

## “Tables”

In bank IT language people often say **“tables”** meaning **big analytical datasets** (deposits, profiles, and so on).

In *this* repo, those names and descriptions live in a **single large JSON file** (`data/scb_data_catalog.json`). It is basically a **phone book of datasets**: what they are called, what they are about, how often they refresh, and what columns exist.

**Important:** the dashboard does **not** go query those datasets in real time. The catalog is there so **humans and the ontology map** can browse “what data exists in principle.”

---

## Ontology (the “map of how data fits together”)

**Ontology** here means “a picture of how data pieces relate”—not a magic AI on its own.

- **`SCB_Ontology_Map.html`** draws a **clickable diagram** from that same catalog file so you can explore how datasets and fields connect. Good for **workshops and explanations**.
- The optional Vera Hub path could, in the future, show a **similar style diagram from a company server**. That is **not required** for what you see today.

There is no separate “ontology database” sitting in this folder.

---

## What is mock or demo-only (the honest list)

- **The three personas** are **made-up profiles** written into the page to illustrate segments—not real people from the bank’s systems.
- **The headline KPI numbers** are **worked out with simple rules** from the sliders (plus a bit of math so the arrows and percentages look believable). They are **not** official management reporting.
- **The small month-to-month style bumps** on some numbers are **fake but stable** for the demo (same persona always gets the same “fake trend” so the screen doesn’t jump randomly every refresh).
- **The phone journeys** are **click-through prototypes** (stories and screens). They are **not** wired to real payments, real loans, or real fraud alerts.
- **Vera Hub** is **optional and off by default**—so you should assume **no live metrics feed** unless someone deliberately plugs one in.
- The **sketch notes** in `docs/DASHBOARD_STRAWMAN.md` are **design intent on paper**, not a second finished product.

---

## Optional: local “backend” for demos (still not a bank system)

If you want a **real small database file** and a **tiny web service** on your laptop (so the board can load personas, metrics, and an ontology graph over HTTP), use the **`server/`** folder: run **`python server/seed.py`** then **`python server/cxo_api.py`**, and point the dashboard at `http://127.0.0.1:8765` (see **`docs/CXO_API_SERVER.md`**). That SQLite file holds the same **demo** personas and catalog snapshot plus a **merged ontology** (data catalog + simple CXO journey links). It does **not** connect to production banking systems.

---

## In one sentence

**This is a browser-based demo board: fake-but-consistent personas and numbers, plus embedded story-like journey pages, a browsable data catalog for storytelling, and an optional hook for a real API later—no bank database and no production personalization engine running inside this repo.**
