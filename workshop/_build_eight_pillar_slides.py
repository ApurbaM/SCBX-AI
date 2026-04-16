"""
Duplicate slide-3 style deep dives for all 8 experience pillars using PowerPoint COM.
Requires: Windows, PowerPoint installed, pywin32.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

SRC = Path(
    r"C:\Users\Apurba Mukherjee\OneDrive - McKinsey & Company\Desktop\AM\SCBX\workshop\20260416_Design Workshop.pptx"
)
OUT = Path(
    r"C:\Users\Apurba Mukherjee\OneDrive - McKinsey & Company\Desktop\AM\SCBX\workshop\20260416_Design_Workshop_Eight_Pillar_DeepDives.pptx"
)
TMP = Path(os.environ["TEMP"]) / "dw_workshop_src.pptx"


PILLARS: list[dict[str, str]] = [
    {
        "title": "1. Defining the persona",
        "mean": (
            "What it means: Decide the assistant’s role, tone, boundaries, and channel presence so customers "
            "experience one coherent SCB character—not a different voice per journey.\n"
            "Guiding check: Is it obvious who the assistant is, whom it serves, what it can do, and where the line is?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Posture: guide vs. doer vs. coach—and when humans remain default.\n"
            "• Segments & modes: fraud, collections, wealth, SME—without breaking one brand.\n"
            "• Identity system: named vs. abstract; chat vs. voice cadence; partner co-brand rules.\n"
            "• Scope & guardrails: plain-language limits; clarify vs. act when uncertain."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "Bank of America markets Erica as a warm, proactive in-app financial assistant—named, "
            "task-integrated, bank-serious tone.\n"
            "https://www.bankofamerica.com/erica/"
        ),
    },
    {
        "title": "2. Recognizing user intent",
        "mean": (
            "What it means: Go beyond keyword matching to infer goals, entities, urgency, and ambiguity—"
            "especially in banking where phrasing is informal but stakes are high.\n"
            "Guiding check: Does it understand me beyond my exact words?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Intent taxonomy aligned to regulated journeys (payments, cards, loans, fraud).\n"
            "• Multilingual + code-switching handling; Thai/English mix patterns.\n"
            "• Confidence thresholds + safe clarification prompts; escalation triggers.\n"
            "• Grounding policy: when retrieval is allowed and how to cite sources."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "NatWest describes upgrading Cora with generative AI to handle more complex customer queries—"
            "signals intent expansion with controls.\n"
            "https://www.natwestgroup.com/news-and-insights/latest-stories/ai-and-data/2024/aug/we-are-giving-our-digital-assistant-cora-a-generative-ai-upgrade.html"
        ),
    },
    {
        "title": "3. Crafting conversational flows",
        "mean": (
            "What it means: Design dialogue so the next step is obvious—minimal dead-ends, graceful repair, "
            "and continuity when customers change their mind mid-task.\n"
            "Guiding check: Does the conversation move naturally and seamlessly?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Journey templates (authenticate → diagnose → act → confirm → receipt).\n"
            "• Error/retry microcopy; timeouts; resume-after-interrupt behavior.\n"
            "• Channel parity: same logical flow in chat, voice, and secure messaging.\n"
            "• Analytics hooks: drop-off points, containment vs. handoff reasons."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "Industry guidance on conversational UX patterns (turn-taking, confirmations) from Nielsen Norman Group.\n"
            "https://www.nngroup.com/topic/ai/"
        ),
    },
    {
        "title": "4. Personalizing interactions",
        "mean": (
            "What it means: Use permitted customer context to reduce repetition and tailor next-best actions—"
            "without crossing creepiness or fairness lines.\n"
            "Guiding check: Does it feel like it knows me?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Data eligibility matrix: what can be used in-session vs. batch; consent flags.\n"
            "• Personalization tiers: anonymous → recognized → authenticated → high-trust.\n"
            "• Fairness testing for offers/routing; explain why something is suggested.\n"
            "• Opt-out and “forget for this session” patterns for sensitive topics."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "McKinsey public material on personalization at scale in financial services (segmented offers, "
            "next-best-action framing).\n"
            "https://www.mckinsey.com/industries/financial-services/our-insights"
        ),
    },
    {
        "title": "5. Ensuring transparency and trust",
        "mean": (
            "What it means: Make limits, reasons, and risks visible—especially for money movement, eligibility, "
            "and model-driven advice.\n"
            "Guiding check: Can I see what’s happening?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Disclosure patterns: fees, FX, cutoffs, cooling-off steps, dispute rights.\n"
            "• “Why this answer?” summaries; logging customer-visible references where allowed.\n"
            "• Model governance: human review for high-risk intents; incident comms templates.\n"
            "• Regulatory alignment: map controls to local banking/consumer-protection expectations."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "UK FCA Consumer Duty (outcomes-focused transparency and support) is a public benchmark for "
            "clarity and fair treatment.\n"
            "https://www.fca.org.uk/publications/finalised-guidance/fg22-5-guiding-principles-consumer-duty"
        ),
    },
    {
        "title": "6. Enabling continuous learning",
        "mean": (
            "What it means: Close the loop from production conversations to measurable improvement—safely, with "
            "privacy and change control.\n"
            "Guiding check: Does the system get better over time?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Feedback capture (thumbs, reason codes) tied to intent IDs.\n"
            "• Offline eval sets; red-team cadence; promotion gates for prompt/model changes.\n"
            "• Human-in-the-loop labeling for low-confidence clusters.\n"
            "• KPIs per journey: resolution, CSAT, handoff quality, defect rate."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "Google Cloud publishes operational guidance for improving production LLM systems (evaluation, "
            "monitoring, iteration).\n"
            "https://cloud.google.com/architecture/ai-ml"
        ),
    },
    {
        "title": "7. Orchestrating human handoffs",
        "mean": (
            "What it means: When automation stops, the human receives structured context so customers don’t repeat "
            "themselves.\n"
            "Guiding check: Are handoffs to humans seamless and context-complete?"
        ),
        "design": (
            "SCB design choices:\n"
            "• Warm transfer packet: intent, entities, attempted steps, risk flags, transcripts policy.\n"
            "• Routing logic: skills, language, VIP, vulnerability cues (where permitted).\n"
            "• SLA messaging + callback scheduling; branch pre-booking handoffs.\n"
            "• Agent desktop integration (CRM/tickets) with minimal swivel-chair."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "Salesforce Service Cloud documents AI-to-agent handoff patterns used in regulated service contexts.\n"
            "https://www.salesforce.com/products/service-cloud/overview/"
        ),
    },
    {
        "title": "8. Designing for effortless use",
        "mean": (
            "What it means: Reduce cognitive load—plain language, progressive disclosure, accessibility, and "
            "predictable controls across devices.\n"
            "Guiding check: Can anyone use this without thinking twice?"
        ),
        "design": (
            "SCB design choices:\n"
            "• WCAG-aligned UI/voice patterns; large-type and contrast modes.\n"
            "• Plain-language defaults; reading level targets; jargon glossary.\n"
            "• Consistent confirmation patterns for irreversible actions.\n"
            "• Low-literacy and stress-state testing (fraud alerts, dunning, outages)."
        ),
        "ex": (
            "Leading practice + public link:\n"
            "W3C WAI publishes Web Content Accessibility Guidelines (WCAG) referenced globally for inclusive design.\n"
            "https://www.w3.org/WAI/standards-guidelines/wcag/"
        ),
    },
]


def _set_slide_texts(slide, title: str, mean: str, design: str, ex: str) -> None:
    """Slide 3 template uses specific shape indices (1-based) in our inspected deck."""
    # Try by placeholder title first
    for sh in slide.Shapes:
        try:
            if sh.Type == 14:  # msoPlaceholder
                if sh.PlaceholderFormat.Type == 1:  # ppPlaceholderTitle
                    sh.TextFrame.TextRange.Text = title
        except Exception:
            pass

    # Fallback: set known indices from inspection (1-based): 2 title placeholder, 3/4/7 textboxes
    mapping = {
        2: title,
        3: mean,
        4: design,
        7: ex,
    }
    for idx, txt in mapping.items():
        try:
            sh = slide.Shapes(idx)
            if sh.HasTextFrame:
                sh.TextFrame.TextRange.Text = txt
        except Exception:
            continue


def main() -> int:
    shutil.copy2(SRC, TMP)
    out_path = str(OUT)

    try:
        import win32com.client  # type: ignore
    except Exception:
        print("pywin32 not available; install with: python -m pip install pywin32", file=sys.stderr)
        return 2

    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    prs = ppt.Presentations.Open(str(TMP), WithWindow=True)

    try:
        # Remove empty slide 4 if present (tracker slide)
        if prs.Slides.Count >= 4:
            s4 = prs.Slides(4)
            try:
                t = ""
                for sh in s4.Shapes:
                    if getattr(sh, "HasTextFrame", False):
                        t += sh.TextFrame.TextRange.Text
                if not str(t).strip():
                    s4.Delete()
            except Exception:
                pass

        # Ensure we have slide 3 as template
        if prs.Slides.Count < 3:
            print("Expected at least 3 slides (cover, grid, deep dive template).", file=sys.stderr)
            return 3

        # Duplicate slide 3 until we have 8 slides starting at slide 3
        while prs.Slides.Count < 10:
            prs.Slides(3).Duplicate()

        # If we overshot (already had >3 pillar slides), trim extras beyond 10? keep 10 slides total: 1 cover, 2 grid, 8 deep dives
        while prs.Slides.Count > 10:
            prs.Slides(prs.Slides.Count).Delete()

        for i, pillar in enumerate(PILLARS, start=1):
            slide = prs.Slides(2 + i)  # slides 3..10
            _set_slide_texts(
                slide,
                pillar["title"],
                pillar["mean"],
                pillar["design"],
                pillar["ex"],
            )

        if OUT.exists():
            OUT.unlink()
        prs.SaveAs(out_path)
        prs.Close()
    finally:
        try:
            ppt.Quit()
        except Exception:
            pass

    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
