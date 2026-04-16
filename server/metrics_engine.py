"""Same journey + cockpit metric model as SCB_CXO_Board_Dashboard.html computeBoardMetrics (twin-driven)."""


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


def _twin_income_mid(twin):
    """Match dashboard: prefer income min/max midpoint; fall back to legacy incomeTHB."""
    if not isinstance(twin, dict):
        return 0.0
    a, b = twin.get("incomeMinTHB"), twin.get("incomeMaxTHB")
    try:
        if a is not None and b is not None:
            return (int(a) + int(b)) / 2.0
    except (TypeError, ValueError):
        pass
    try:
        return float(twin.get("incomeTHB") or 0)
    except (TypeError, ValueError):
        return 0.0


def _blend_anchor(formula_val, jm, key, weight=0.78):
    if not jm:
        return formula_val
    a = jm.get(key)
    if a is None:
        return formula_val
    return formula_val * (1 - weight) + float(a) * weight


def compute_board_metrics(twin, journey_metrics=None):
    """
    Returns dict with computed (floats) and okrs (list of dicts with key, label, value, unit, d)
    matching the browser board for the same twin JSON from SQLite.
    Optional journey_metrics anchors per customer (same keys as dashboard PhoenixCustomerRecords.journeyMetrics).
    """
    jm = dict(journey_metrics) if isinstance(journey_metrics, dict) else {}
    if jm.get("b_logins") is None:
        jm["b_logins"] = 5
    if jm.get("b_logins_baseline") is None:
        jm["b_logins_baseline"] = 4
    income = _twin_income_mid(twin)
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
    revenue_uplift = _clamp(
        ((banker * 18 + butler * 6) if income > 80000 else (banker * 10 + butler * 4)) * risk_factor * (1 + goal_boost),
        0,
        34,
    )
    nps = _clamp(40 + banker * 20 + receptionist * 8 + goal_boost * 12, 25, 82)

    brief_ctr = _clamp(5.5 + receptionist * 10.5, 4.2, 23.8)
    brief_avg_min = _clamp(2.35 + banker * 3.4, 1.55, 10.2)
    weekly_logins_baseline = float(jm.get("b_logins_baseline", 4))
    weekly_logins_count = 5
    weekly_logins_mn = weekly_logins_count / 1e6
    monthly_leads_ref = float(jm.get("d_monthly_leads_ref", 480))
    nba_ctr = _clamp(8.2 + butler * 12.5, 5.5, 30.5)
    csat_pts = _clamp(76 + butler * 16.5 + receptionist * 4, 72, 96)
    res_no_human_pct = _clamp(73 + butler * 19 + receptionist * 5, 68, 98)
    offer_ctr_pct = _clamp(6.5 + banker * 14.5, 4.2, 29)
    monthly_leads = round(_clamp(480 + income / 3800 + goal_n * 42 + banker * 95, 380, 3200))

    w = 0.78 if jm else 0.0
    brief_ctr = _blend_anchor(brief_ctr, jm, "a_ctr", w)
    brief_avg_min = _blend_anchor(brief_avg_min, jm, "a_time", w)
    nba_ctr = _blend_anchor(nba_ctr, jm, "b_nba_ctr", w)
    csat_pts = _blend_anchor(csat_pts, jm, "c_csat", w)
    res_no_human_pct = _blend_anchor(res_no_human_pct, jm, "c_res_no_hum", w)
    offer_ctr_pct = _blend_anchor(offer_ctr_pct, jm, "d_offer_ctr", w)
    monthly_leads = int(round(_blend_anchor(float(monthly_leads), jm, "d_monthly_leads", w)))

    _wl_pct = (
        ((weekly_logins_count - weekly_logins_baseline) / weekly_logins_baseline * 100)
        if weekly_logins_baseline
        else 0.0
    )
    _b_logins_d = f"{_wl_pct:+.1f}%"

    computed = {
        "inquiryContain": inquiry_contain,
        "avgRespSec": avg_resp_sec,
        "taskCompletion": task_completion,
        "callDeflect": call_deflect,
        "fcr": fcr,
        "dauUplift": dau_uplift,
        "timeSpent": time_spent,
        "revenueUplift": revenue_uplift,
        "nps": nps,
        "receptionist": receptionist,
        "butler": butler,
        "banker": banker,
        "briefCtr": brief_ctr,
        "briefAvgMin": brief_avg_min,
        "weeklyLoginsMn": weekly_logins_mn,
        "weeklyLoginsCount": weekly_logins_count,
        "nbaCtr": nba_ctr,
        "csatPts": csat_pts,
        "resNoHumanPct": res_no_human_pct,
        "offerCtrPct": offer_ctr_pct,
        "monthlyLeads": monthly_leads,
    }

    okrs = [
        {"key": "dau", "label": "DAU", "value": round(5.0 * (1 + dau_uplift / 100), 3), "unit": "Mn", "d": f"+{dau_uplift:.1f}%"},
        {"key": "time", "label": "Active time", "value": round(time_spent, 2), "unit": "min", "d": f"+{(time_spent - 6.2):.1f}"},
        {"key": "rev", "label": "Revenue uplift", "value": round(revenue_uplift, 2), "unit": "%", "d": f"+{revenue_uplift:.1f}%"},
        {"key": "nps", "label": "NPS", "value": round(nps, 2), "unit": "pts", "d": f"+{(nps - 40):.0f}"},
        {"key": "contain", "label": "Inquiry containment", "value": round(inquiry_contain, 2), "unit": "%", "d": f"+{(inquiry_contain - 50):.0f}"},
        {"key": "resp", "label": "Avg response", "value": round(avg_resp_sec, 2), "unit": "s", "d": f"-{(10 - avg_resp_sec):.1f}s"},
        {"key": "task", "label": "Task completion", "value": round(task_completion, 2), "unit": "%", "d": f"+{(task_completion - 60):.0f}"},
        {"key": "fcr", "label": "FCR", "value": round(fcr, 2), "unit": "%", "d": f"+{(fcr - 58):.0f}"},
        {"key": "a_ctr", "label": "CTR · Morning Brief", "value": round(brief_ctr, 2), "unit": "%", "d": f"+{(brief_ctr - 5.2):.1f}"},
        {"key": "a_time", "label": "Average time spent", "value": round(brief_avg_min, 2), "unit": "min", "d": f"+{(brief_avg_min - 2.35):.1f}"},
        {
            "key": "b_logins",
            "label": "# logins",
            "value": float(weekly_logins_count),
            "unit": "",
            "d": _b_logins_d,
        },
        {"key": "b_nba_ctr", "label": "CTR · Next best action", "value": round(nba_ctr, 2), "unit": "%", "d": f"+{(nba_ctr - 8):.1f}"},
        {"key": "c_csat", "label": "CSAT", "value": round(csat_pts, 2), "unit": "pts", "d": f"+{(csat_pts - 76):.0f}"},
        {
            "key": "c_res_no_hum",
            "label": "Resolution (no human transfer)",
            "value": round(res_no_human_pct, 2),
            "unit": "%",
            "d": f"+{(res_no_human_pct - 73):.0f}",
        },
        {"key": "d_offer_ctr", "label": "CTR on offers", "value": round(offer_ctr_pct, 2), "unit": "%", "d": f"+{(offer_ctr_pct - 6.5):.1f}"},
        {
            "key": "d_monthly_leads",
            "label": "Monthly leads generated",
            "value": float(monthly_leads),
            "unit": "leads",
            "d": f"+{round((monthly_leads - monthly_leads_ref) / 12)}",
        },
    ]
    return {"computed": computed, "okrs": okrs}
