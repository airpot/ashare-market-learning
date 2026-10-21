"""This module gives Decimal arithmetic and paper practice with aid in four steps.

The ledger starts with cash and zero units.
It does not calculate settlement, frozen assets, entitlement, conversion, taxes, or an exchange execution rule.
The packet gate keeps the specified sequence of instructions. It does not prevent file access.
"""
import argparse
from copy import deepcopy
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, ROUND_HALF_UP
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("ETF", "LOF", "CB", "REIT", "MONEY", "CLOSED")
CENT = Decimal("0.01")


def _decimal(value, name, zero=False):
    if type(value) not in (str, int, float, Decimal):
        raise ValueError(f"{name} must have a finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must have a finite number") from None
    if not result.is_finite() or result < 0 or (not zero and result == 0):
        raise ValueError(f"{name} must be {'a nonnegative finite number' if zero else 'a positive finite number'}.")
    return result


def _fee(value):
    try:
        return _decimal(value, "external fee", zero=True).quantize(CENT, rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError('The function cannot round this external fee to cents.') from None


def _units(value, name="quantity"):
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must have a positive exact integer")
    return value


def premium(price, nav):
    """Return the percent. The supplied NAV or conversion value is the denominator."""
    price, nav = _decimal(price, "price"), _decimal(nav, "nav")
    return (price / nav - 1) * 100


def conversion_value(stock, conversion_price, par):
    """Before rounding, return the theoretical stock value for each supplied face amount."""
    stock = _decimal(stock, "stock price")
    conversion_price = _decimal(conversion_price, "conversion price")
    return _decimal(par, "face amount") / conversion_price * stock


def size_position(cash, budget, entry, stop, lot, buyfee, sellfee):
    """Calculate the size of a long cash purchase in the cash and planned-loss limits.

    Fees have fixed totals from external inputs. The function rounds each fee to cents one time with HALF_UP.
    The calculation uses an exit at the stop price as an assumption. A gap can cause a loss that is more than the planned loss.
    """
    cash, budget = _decimal(cash, "cash"), _decimal(budget, "budget")
    entry, stop = _decimal(entry, "entry"), _decimal(stop, "stop")
    lot = _units(lot, "lot")
    buyfee, sellfee = _fee(buyfee), _fee(sellfee)
    if stop >= entry:
        raise ValueError("For this long-only worksheet, stop must be less than entry.")
    if cash <= buyfee or budget <= buyfee + sellfee:
        return 0
    cash_units = (cash - buyfee) / entry
    risk_units = (budget - buyfee - sellfee) / (entry - stop)
    return int((min(cash_units, risk_units) / lot).to_integral_value(rounding=ROUND_FLOOR)) * lot


def reconcile(opening_cash, events, mark=None):
    """Use fills and cash distributions in sequence, from a zero opening position.

    A fill price is currency for each unit. For CB, this is currency for each bond.
    Orders without fills do not become part of this ledger.
    For a positive holding, the supplied mark must be a positive number.

    Before you call this function, change the quote from per-100-face to currency for each bond.
    If prices or NAV include expenses, do not add these expenses to the fee again.
    """
    opening_cash = _decimal(opening_cash, "opening cash", zero=True)
    cash, quantity = opening_cash, 0
    if not isinstance(events, (list, tuple)):
        raise ValueError("The events must be a list or tuple in sequence.")
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Each event must be a dictionary.")
        kind = event.get("kind")
        required = {"kind", "amount"} if kind == "distribution" else {"kind", "quantity", "price", "fee"}
        if kind not in ("buy", "sell", "distribution") or not required <= event.keys():
            raise ValueError("Use a buy/sell fill or a cash distribution.")
        if event.keys() - required - {"event_id", "date"}:
            raise ValueError("The script cannot use this ledger field. Use the different state worksheet.")
        if "event_id" in event:
            identifier = event["event_id"]
            if type(identifier) is not str or not identifier.strip() or identifier in seen:
                raise ValueError("event_id must be a unique nonempty string.")
            seen.add(identifier)
        if kind == "distribution":
            # The worksheet gives the eligibility and the cash receipt date.
            cash += _decimal(event["amount"], "cash distribution")
            continue
        units = _units(event["quantity"])
        value = units * _decimal(event["price"], "fill price")
        fee = _fee(event["fee"])
        if kind == "buy":
            if value + fee > cash:
                raise ValueError("The fill is more than the cash in the ledger.")
            cash -= value + fee
            quantity += units
        else:
            if units > quantity:
                raise ValueError("The sell quantity is more than the number of units in the ledger.")
            if cash + value < fee:
                raise ValueError("The sell fee is more than the cash in the ledger plus proceeds.")
            cash += value - fee
            quantity -= units
    mark = _decimal(mark, "mark") if mark is not None else None
    if quantity and mark is None:
        raise ValueError("The remaining units must have a mark for total PnL.")
    total = cash + quantity * (mark if mark is not None else Decimal(0))
    return {"cash": cash, "quantity": quantity, "total_pnl": total - opening_cash}


def _step(step):
    if type(step) is not int or step not in (1, 2, 3, 4):
        raise ValueError("The step must be an exact integer from 1 to 4.")


def _run(record, run_id, step):
    _step(step)
    if type(run_id) is not str or record.get("product_practice_active_run") != run_id:
        raise ValueError("Use the ID of this attempt.")
    matches = [r for r in record.get("product_runs", []) if r.get("run_id") == run_id]
    if len(matches) != 1 or step != len(matches[0]["revealed_steps"]) + 1:
        raise ValueError("Complete each step one time, in sequence.")
    return matches[0]


def _packet(track, step, teacher=False):
    _step(step)
    if type(track) is not str or track not in TRACKS:
        raise ValueError("The product track is unknown.")
    folder = "references/assessment/product-practice" if teacher else "assets/product-practice"
    packet = json.loads((ROOT / folder / track / f"{step:02}.json").read_text(encoding="utf8"))
    if packet.get("track") != track or type(packet.get("step")) is not int or packet["step"] != step:
        raise ValueError("The packet identity does not agree with the request.")
    return packet


def start(record, track):
    """Start an attempt with aid. Keep all previous attempts and raw responses."""
    if type(track) is not str or track not in TRACKS:
        raise ValueError("The track must be ETF, LOF, CB, REIT, MONEY or CLOSED.")
    if not isinstance(record, dict) or not isinstance(record.get("responses", []), list):
        raise ValueError("The record must be a dictionary. If there is a responses field, it must be a list.")
    run_id = uuid.uuid4().hex
    run = dict(run_id=run_id, track=track, support="assisted", opened_steps=[],
               answered_steps=[], revealed_steps=[], related_exposure=[])
    record.setdefault("product_runs", []).append(run)
    record.setdefault("responses", [])
    record["product_practice_active_run"] = run_id
    return run_id


def open_step(record, run_id, step):
    run = _run(record, run_id, step)
    if step in run["opened_steps"]:
        raise ValueError("This attempt opened the packet at a previous time.")
    packet = _packet(run["track"], step)
    run["opened_steps"].append(step)
    run["related_exposure"].append(dict(step=step, kind="learner_packet_seen",
                                         items=deepcopy(packet.get("related_exposure", []))))
    return dict(deepcopy(packet), run_id=run_id, support="assisted")


def answer(record, run_id, step, raw):
    run = _run(record, run_id, step)
    if step not in run["opened_steps"] or step in run["answered_steps"]:
        raise ValueError('Record one raw response for the open packet for this attempt.')
    if type(raw) is not str or not raw.strip():
        raise ValueError("The raw response must contain the words that the learner gave.")
    record["responses"].append(dict(run_id=run_id, track=run["track"], step=step,
                                    exercise=f"PRODUCT-{run['track']}-{step:02}",
                                    raw_response=raw, support="assisted"))
    run["answered_steps"].append(step)


def reveal(record, run_id, step):
    run = _run(record, run_id, step)
    rows = [r for r in record.get("responses", []) if r.get("run_id") == run_id
            and r.get("track") == run["track"] and type(r.get("step")) is int and r["step"] == step
            and r.get("exercise") == f"PRODUCT-{run['track']}-{step:02}"]
    if (step not in run["opened_steps"] or step not in run["answered_steps"] or len(rows) != 1
            or type(rows[0].get("raw_response")) is not str or not rows[0]["raw_response"].strip()):
        raise ValueError("Before feedback, keep the raw response without changes for this attempt.")
    # Before the checks of the raw response, the script does not read a packet, also for a learner.
    teacher = _packet(run["track"], step, teacher=True)
    run["revealed_steps"].append(step)
    run["related_exposure"].append(dict(step=step, kind="teacher_feedback_seen"))
    rows[0]["support"] = "assisted"
    rows[0]["feedback"] = deepcopy(teacher)
    return dict(deepcopy(teacher), run_id=run_id, support="assisted")


def _record_path(path):
    path = path.expanduser().resolve()
    protected = [ROOT]
    for home in (Path.home() / ".codex", Path.home() / ".agents"):
        protected.append((home / "skills").resolve())
    if os.environ.get("CODEX_HOME"):
        protected.append((Path(os.environ["CODEX_HOME"]) / "skills").expanduser().resolve())
    if any(path.is_relative_to(folder) for folder in protected):
        raise ValueError("Write records in a location that is not in installed skills or the portable skill.")
    # A different portable copy is also a protected destination.
    if any((parent / "SKILL.md").is_file() for parent in path.parents):
        raise ValueError("Write records in a location that is not in a skill directory.")
    return path


def _prepare_output(output, encoding):
    """Before you record progress, do the serialization validation, also for GBK terminals."""
    rendered = json.dumps(output, ensure_ascii=False, indent=2)
    try:
        rendered.encode(encoding or "utf-8")
    except UnicodeEncodeError:
        rendered = json.dumps(output, ensure_ascii=True, indent=2)
        rendered.encode(encoding or "utf-8")
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "open", "answer", "reveal"))
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--track", choices=TRACKS)
    parser.add_argument("--run")
    parser.add_argument("--step", type=int)
    parser.add_argument("--raw-file", type=Path)
    args = parser.parse_args()
    try:
        path = _record_path(args.record)
        if path.exists():
            record = json.loads(path.read_text(encoding="utf8"))
        elif args.action == "start":
            record = {"responses": []}
        else:
            raise ValueError("Before this command, start a record.")
        if args.action == "start":
            output = {"run_id": start(record, args.track), "support": "assisted"}
        elif args.action == "open":
            output = open_step(record, args.run, args.step)
        elif args.action == "reveal":
            output = reveal(record, args.run, args.step)
        else:
            if args.raw_file is None:
                raise ValueError("For answer, supply --raw-file with the learner response without changes.")
            answer(record, args.run, args.step, args.raw_file.read_text(encoding="utf8"))
            output = {"saved": True, "support": "assisted"}
        # Before you record the progress for a feedback step after consumption, prepare the wire text.
        rendered = _prepare_output(output, sys.stdout.encoding)
        # Only after all command and output checks give satisfactory results, replace the record.
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        try:
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(rendered)


if __name__ == "__main__":
    main()
