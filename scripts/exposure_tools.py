"""These checks are about prior access to observations or answers for an instrument and date interval.
If there is no history, the result stays unknown.
"""
from datetime import date, timedelta
import re


def instrument_key(value):
    if not isinstance(value, str):
        raise ValueError("The instrument must have an exchange-qualified code or a synthetic ID.")
    value = value.strip()
    match = re.fullmatch(r"(sh|sz|bj)(\d{6})", value.lower())
    if match:
        return "".join(match.groups())
    match = re.fullmatch(r"(\d{6})\.(sh|sz|bj)", value.lower())
    if match:
        return match[2] + match[1]
    if re.fullmatch(r"[A-Z][A-Z0-9]*-[A-Z0-9-]+", value):
        return value
    raise ValueError("The instrument must have an exchange-qualified code or a synthetic ID.")


def _day(value):
    if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
        raise ValueError("The date must use YYYY-MM-DD.")
    return value


def _interval(instrument, start, end):
    result = dict(instrument=instrument_key(instrument), start=_day(start), end=_day(end))
    if start > end:
        raise ValueError("The interval start is after its end.")
    return result


def eligibility(history, instrument, start, end):
    target = _interval(instrument, start, end)
    if history is None or history == {}:
        return {"support": "unknown", "matches": []}
    if not isinstance(history, dict) or history.get("status") not in ("complete", "unknown") or not isinstance(history.get("events"), list):
        raise ValueError("The history must have status and events.")
    matches = []
    for event in history["events"]:
        row = _interval(event["instrument"], event["start"], event["end"])
        if row["instrument"] == target["instrument"] and row["start"] <= end and start <= row["end"]:
            matches.append(dict(event, **row))
    support = "assisted" if matches else ("independent" if history["status"] == "complete" else "unknown")
    return {"support": support, "matches": matches}


def union_ranges(events):
    rows = sorted((_interval(e["instrument"], e["start"], e["end"]) for e in events),
                  key=lambda e: (e["instrument"], e["start"], e["end"]))
    result = []
    for row in rows:
        if (result and row["instrument"] == result[-1]["instrument"] and
                (date.fromisoformat(row["start"]) - date.fromisoformat(result[-1]["end"])) <= timedelta(days=1)):
            result[-1]["end"] = max(result[-1]["end"], row["end"])
        else:
            result.append(row.copy())
    return result


def packet_events(case_id, decision, revealed=None):
    symbol = instrument_key(decision["symbol"])
    cutoff = _day(decision["cutoff"])
    result = []
    for kind, packet in (("observed", decision), ("revealed", revealed)):
        if packet is None:
            continue
        packet_symbol = packet.get("symbol", packet.get("source", {}).get("symbol", symbol))
        if instrument_key(packet_symbol) != symbol:
            raise ValueError('The instrument in the observed bars and the instrument in the exposure record are different.')
        days = [_day(row["date"]) for row in packet["bars"]]
        if not days or days != sorted(set(days)):
            raise ValueError("The packet must have nonempty daily bars in date sequence.")
        if kind == "observed" and days[-1] != cutoff:
            raise ValueError('The last observed bar must be at the cutoff.')
        result.append(dict(_interval(symbol, days[0], days[-1]), case_id=case_id, kind=kind))
    return result
