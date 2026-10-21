"""Supply one reserve prefix. Keep the raw response. Then show one teacher packet.

This module keeps the specified sequence of local instructions. It does not prevent file access or automatically give a grade.

Before the learner gives an answer, do not load this module or teacher packets into the learner context.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import uuid

import exposure_tools as exposure

ROOT = Path(__file__).resolve().parents[1]
CASE = "H01"
SYMBOL = "TRAIN-H01"
START, END = "2025-03-03", "2025-03-17"


def _run(record, run_id):
    return next(r for r in record["holdout_runs"] if r["run_id"] == run_id)


def _refresh(record, run):
    history = record.get("exposure_history")
    if history:
        history = dict(history, events=[e for e in history["events"] if e.get("event_id") not in run["own_exposure_ids"]])
    support = exposure.eligibility(history, SYMBOL, START, END)["support"]
    rank = {"independent": 0, "unknown": 1, "assisted": 2, "hinted": 3}
    if rank[support] > rank[run["support"]]:
        run["support"] = support


def _observe(record, run, event):
    event = dict(event, event_id=uuid.uuid4().hex)
    record["exposure_history"]["events"].append(event)
    run["own_exposure_ids"].append(event["event_id"])


def _packet(step, teacher=False):
    if type(step) is not int or step not in (1, 2, 3):
        raise ValueError("The step must be 1, 2 or 3.")
    folder = "references/assessment/holdout-replay" if teacher else "assets/holdout-replay"
    return json.loads((ROOT / folder / f"{step:02}.json").read_text(encoding="utf8"))


def start_run(record):
    if record.get("exposure_history") is None or record["exposure_history"] == {}:
        record["exposure_history"] = {"status": "unknown", "events": []}
    support = exposure.eligibility(record["exposure_history"], SYMBOL, START, END)["support"]
    run = dict(run_id=uuid.uuid4().hex, case_id=CASE, support=support,
               opened_steps=[], answered_steps=[], revealed_steps=[], own_exposure_ids=[])
    record.setdefault("holdout_runs", []).append(run)
    record.setdefault("responses", [])
    return run["run_id"]


def open_step(record, run_id, step):
    run = _run(record, run_id)
    if type(step) is not int or step not in (1, 2, 3) or step != len(run["revealed_steps"]) + 1:
        raise ValueError("Before the next prefix, complete the raw response for this step. Then show the teacher packet.")
    packet = _packet(step)
    _refresh(record, run)
    if step not in run["opened_steps"]:
        _observe(record, run, exposure.packet_events(f"H01-{step:02}", packet)[0])
        run["opened_steps"].append(step)
    return dict(packet, support=run["support"])


def save_response(record, run_id, step, raw_response):
    if type(step) is not int or step not in (1, 2, 3):
        raise ValueError("The step must be 1, 2 or 3.")
    run = _run(record, run_id)
    if (step not in run["opened_steps"] or step in run["answered_steps"] or
            step != len(run["revealed_steps"]) + 1):
        raise ValueError('Record one raw response for the open step for this attempt.')
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise ValueError("The raw response must contain the words that the learner gave.")
    _refresh(record, run)
    record["responses"].append(dict(exercise=f"H01-{step:02}", run_id=run_id,
                                    raw_response=raw_response, support=run["support"]))
    run["answered_steps"].append(step)


def mark_hint(record, run_id):
    _run(record, run_id)["support"] = "hinted"


def reveal(record, run_id, step):
    if type(step) is not int or step not in (1, 2, 3):
        raise ValueError("The step must be 1, 2 or 3.")
    run = _run(record, run_id)
    has_raw = any(r.get("run_id") == run_id and r.get("exercise") == f"H01-{step:02}" and
                  isinstance(r.get("raw_response"), str) and r["raw_response"].strip()
                  for r in record["responses"])
    if step not in run["answered_steps"] or step != len(run["revealed_steps"]) + 1 or not has_raw:
        raise ValueError("Before you show this teacher packet, keep the related raw response.")
    # After the raw response gate, read only this teacher packet.
    teacher = _packet(step, teacher=True)
    decision = _packet(step)
    _refresh(record, run)
    _observe(record, run, exposure.packet_events(f"H01-{step:02}", decision, teacher)[-1])
    run["revealed_steps"].append(step)
    return deepcopy(teacher)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "open", "answer", "reveal", "hint"))
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--run")
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--raw-file", type=Path)
    args = parser.parse_args()
    path = args.record.resolve()
    if path.is_relative_to(ROOT):
        parser.error("Use a record in the learner workspace in a location that is not in the portable skill.")
    record = json.loads(path.read_text(encoding="utf8"))
    if args.action == "start":
        run_id = start_run(record)
        output = dict(run_id=run_id, support=_run(record, run_id)["support"])
    else:
        if not args.run:
            parser.error("After start, --run is necessary.")
        if args.action == "open":
            output = open_step(record, args.run, args.step)
        elif args.action == "reveal":
            output = reveal(record, args.run, args.step)
        elif args.action == "hint":
            mark_hint(record, args.run)
            output = {"support": "hinted"}
        else:
            if not args.raw_file:
                parser.error("For answer, supply --raw-file with the learner response without changes.")
            save_response(record, args.run, args.step, args.raw_file.read_text(encoding="utf8"))
            output = {"saved": True}
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    temporary.replace(path)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
