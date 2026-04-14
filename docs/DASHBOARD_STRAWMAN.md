# Dashboard strawman (to be built)

**Status:** Reference only — not implemented yet.  
**Source sketch:** [`dashboard-strawman-sketch.png`](dashboard-strawman-sketch.png) (hand-drawn wireframe on grid paper).

## Purpose

Internal **dashboard** for a board or product team to **toggle personas (segments)** and see how **personalization** changes the **morning brief** and **app home** experiences, plus follow-on journeys.

## Layout (two-pane)

### Left: Persona sidebar

- Header area (sketch label: “mach-u” — treat as placeholder / TBD title).
- **Persona 1**, **Persona 2**, **Persona 3** (vertical list).
- Each persona: avatar placeholder + short metadata lines.
- **Persona 1** detail (expand / drill-down in sketch): **Income**, **Balance**, interest tags (e.g. **Fashion**, **Travel**, **Food**).
- **Note (red):** “Dashboard — where the board can toggle between the segments.”

### Right: Main content — user journeys

#### Journey 1 — Morning brief & home

| Screen | Label | Content (from sketch) |
|--------|--------|------------------------|
| A | **Morning brief** | Mobile-style vertical layout; stacked cards (**Film**, **Action**, **Context** — labels may map to content modules); scroll regions (“scroll 1”, “scroll 2”). **Agent** affordance at top (**agent powered**, purple). |
| B | **App home page** | Central circular graphic with satellite circles; stacked rectangular cards below; top label “Baruch” in sketch (placeholder). |

#### Journey 2 — Conversation & post-conversation

| Screen | Label | Content (from sketch) |
|--------|--------|------------------------|
| C | **During convo personalization** | Chat-like or personalized feed; variable-width content blocks. |
| D | **Post convo** | **S2S** (screen-to-screen) style; grid/list of cards/blocks. Highlighted in sketch as key output of this journey. |

## Personalization engine (bottom band)

- Purple horizontal strip labeled **PERSONALIZATION ENGINE**.
- **Note (red):** Shows how **morning brief** and **app home** change based on the **persona selected** in the sidebar.
- Implication for build: persona selection drives **state** → updates **Journey 1** (and related preview for Journey 2 if in scope).

## Visual / annotation language (from sketch)

- **Black:** structure and titles.
- **Red:** functional notes (toggle segments, engine behavior).
- **Purple:** agent-powered features and flow emphasis.

## Build hints (for implementation later)

- Model as **segment/persona** in global state; sidebar switches active persona.
- **Journey 1** screens are **previews** or **embedded iframes** of product surfaces, or **low-fi mirrored layouts** — decide fidelity when scoping.
- **Journey 2** ties **conversational personalization** → **post-convo S2S** destination.
- Keep sketch labels (Film/Action/Context, Baruch, mach-u) as **placeholders** until replaced with real module names and branding.

---

*Captured from stakeholder wireframe; align naming with SCB Easy / Jarvis product language when implementing.*
