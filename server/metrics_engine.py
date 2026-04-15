"""Mirror of SCB_CXO_Board_Dashboard.html computeBoardMetrics + primaryChannel (demo model)."""


def _clamp(n, a, b):
    return max(a, min(b, n))


def primary_channel(twin):
    raw = (twin.get("channels") or ["mobile_first"])[0] if isinstance(twin.get("channels"), list) else "mobile_first"
    if raw == "advisory_led":
        return "advisory_led"
    if raw in ("mobile_first", "social_messaging"):
        return "mobile_first"
    if raw in ("omnichannel", "branch_network", "phone_ivr", "web_portal", "atm_self_serve"):
        return "omnichannel"
    return "mobile_first"


def compute_board_metrics(twin):
    """Returns dict with keys matching Vera Hub normalized metrics + okrs list."""
    income = int(twin.get("incomeTHB") or 0)
    cc = _clamp(int(twin.get("contextCompleteness") or 0), 0, 100) / 100.0
    ch = primary_channel(twin)
    risk = twin.get("risk") or "moderate"
    risk_factor = 0.85 if risk == "low" else 1.12 if risk == "high" else 1.05
    goal_tags = twin.get("goalTags") or []
    goal_n = len(goal_tags) if isinstance(goal_tags, list) else 0
    goal_boost = min(goal_n * 0.02, 0.08)

    receptionist = (0.18 + 0.45 * cc) * (1.05 if ch == "mobile_first" else 1.0)
    butler = (0.10 + 0.52 * cc) * (0.92 if ch == "advisory_led" else 1.0)
    banker = (0.08 + 0.40 * cc) * (1.12 if income > 80000 else 0.96) * risk_factor

    inquiry_contain = _clamp(receptionist * 88, 30, 92)
    avg_resp_sec = _clamp(11 - receptionist * 7.5, 2.5, 12)
    task_completion = _clamp(52 + butler * 40, 45, 95)
    call_deflect = _clamp(butler * 72, 0, 80)
    fcr = _clamp(58 + butler * 32, 55, 93)
    dau_uplift = _clamp(banker * 18 + butler * 6 + receptionist * 3, 0, 25)
    time_spent = 6.2 + banker * 7.2
    base_rev = (banker * 18 + butler * 6) if income > 80000 else (banker * 10 + butler * 4)
    revenue_uplift = _clamp(base_rev * risk_factor * (1 + goal_boost), 0, 34)
    nps = _clamp(40 + banker * 20 + receptionist * 8 + goal_boost * 12, 25, 82)

    computed = {
        "inquiryContain": round(inquiry_contain, 2),
        "avgRespSec": round(avg_resp_sec, 2),
        "taskCompletion": round(task_completion, 2),
        "callDeflect": round(call_deflect, 2),
        "fcr": round(fcr, 2),
        "dauUplift": round(dau_uplift, 2),
        "timeSpent": round(time_spent, 2),
        "revenueUplift": round(revenue_uplift, 2),
        "nps": round(nps, 2),
        "receptionist": round(receptionist, 4),
        "butler": round(butler, 4),
        "banker": round(banker, 4),
    }
    okrs = [
        {"key": "dau", "label": "DAU", "value": round(5.0 * (1 + dau_uplift / 100), 3), "unit": "Mn"},
        {"key": "time", "label": "Active time", "value": round(time_spent, 2), "unit": "min"},
        {"key": "rev", "label": "Revenue uplift", "value": round(revenue_uplift, 2), "unit": "%"},
        {"key": "nps", "label": "NPS", "value": round(nps, 2), "unit": "pts"},
        {"key": "contain", "label": "Inquiry containment", "value": round(inquiry_contain, 2), "unit": "%"},
        {"key": "resp", "label": "Avg response", "value": round(avg_resp_sec, 2), "unit": "s"},
        {"key": "task", "label": "Task completion", "value": round(task_completion, 2), "unit": "%"},
        {"key": "fcr", "label": "FCR", "value": round(fcr, 2), "unit": "%"},
    ]
    return {"computed": computed, "okrs": okrs}
