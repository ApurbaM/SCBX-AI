"""Align twin shape with SCB_CXO_Board_Dashboard hydrateTwin / pickSingleChannelFromDefaults."""


def pick_single_channel_from_defaults(chs):
    arr = chs if isinstance(chs, list) and chs else []
    if "advisory_led" in arr:
        return ["advisory_led"]
    if "omnichannel" in arr:
        return ["omnichannel"]
    if "mobile_first" in arr:
        return ["mobile_first"]
    return [arr[0] if arr else "mobile_first"]


def hydrate_twin(defaults):
    import copy

    t = copy.deepcopy(defaults)
    ch = t.get("channels")
    if not isinstance(ch, list) or not ch:
        t["channels"] = [t.get("channel") or "mobile_first"]
    else:
        t["channels"] = pick_single_channel_from_defaults(ch)
    if "channel" in t:
        del t["channel"]
    goals = t.get("goalTags")
    if not isinstance(goals, list) or not goals:
        t["goalTags"] = ["ease_of_banking"]
    else:
        mapped = []
        for g in goals:
            if g == "everyday":
                g = "ease_of_banking"
            if g and g != "protect":
                mapped.append(g)
        t["goalTags"] = list(dict.fromkeys(mapped)) or ["ease_of_banking"]
    if t.get("risk") == "balanced":
        t["risk"] = "moderate"
    return t


def merge_twin(base, patch):
    import copy

    out = copy.deepcopy(base)
    for k, v in (patch or {}).items():
        if k == "goalTags" and isinstance(v, list):
            out[k] = v
        elif k == "channels" and isinstance(v, list):
            out[k] = pick_single_channel_from_defaults(v)
        else:
            out[k] = v
    return hydrate_twin(out)
