"""Supply one reserve prefix. Keep the raw response. Then show one teacher packet.

This module keeps the specified sequence of local instructions. It does not prevent file access or automatically give a grade.

Before the learner gives an answer, do not load this module or teacher packets into the learner context.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

import exposure_tools as exposure

ROOT = Path(__file__).resolve().parents[1]
CASE = "H01"
SYMBOL = "TRAIN-H01"
START, END = "2025-03-03", "2025-03-17"


def _run(record, run_id):
    matches = [r for r in record.get("holdout_runs", []) if r.get("run_id") == run_id]
    if not isinstance(run_id, str) or not run_id.strip() or len(matches) != 1:
        raise ValueError("Use the unique ID of this holdout attempt.")
    return matches[0]


def _step(step):
    if type(step) is not int or step not in (1, 2, 3):
        raise ValueError("The step must be 1, 2 or 3.")


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _response(record, run_id, step):
    rows = [r for r in record.get("responses", [])
            if r.get("run_id") == run_id and r.get("exercise") == f"H01-{step:02}"]
    if len(rows) != 1 or not _nonempty(rows[0].get("raw_response")):
        raise ValueError("Keep exactly one nonempty raw response for this attempt and exercise.")
    return rows[0]


def _feedback_complete(row):
    if not _nonempty(row.get("feedback_evidence")):
        return False
    if row.get("feedback_status") == "delivered":
        return _nonempty(row.get("feedback"))
    return (row.get("feedback_status") == "declined" and row.get("feedback") is None
            and _nonempty(row.get("feedback_declined_request")))


def _previous_feedback(record, run_id, step):
    if step > 1 and not _feedback_complete(_response(record, run_id, step - 1)):
        raise ValueError("Before the next step, record delivered feedback or the learner's explicit decline.")


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
    _step(step)
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
    _step(step)
    run = _run(record, run_id)
    if step != len(run["revealed_steps"]) + 1:
        raise ValueError("Before the next prefix, complete the raw response for this step. Then show the teacher packet.")
    _previous_feedback(record, run_id, step)
    packet = _packet(step)
    _refresh(record, run)
    if step not in run["opened_steps"]:
        _observe(record, run, exposure.packet_events(f"H01-{step:02}", packet)[0])
        run["opened_steps"].append(step)
    return dict(packet, support=run["support"])


def save_response(record, run_id, step, raw_response):
    _step(step)
    run = _run(record, run_id)
    if (step not in run["opened_steps"] or step in run["answered_steps"] or
            step != len(run["revealed_steps"]) + 1):
        raise ValueError('Record one raw response for the open step for this attempt.')
    if not isinstance(raw_response, str) or not raw_response.strip():
        raise ValueError("The raw response must contain the words that the learner gave.")
    _previous_feedback(record, run_id, step)
    _refresh(record, run)
    record["responses"].append(dict(exercise=f"H01-{step:02}", run_id=run_id,
                                    raw_response=raw_response, support=run["support"],
                                    feedback_status="pending", feedback=None))
    run["answered_steps"].append(step)


def mark_hint(record, run_id):
    _run(record, run_id)["support"] = "hinted"


def reveal(record, run_id, step):
    _step(step)
    run = _run(record, run_id)
    if (step not in run["opened_steps"] or step not in run["answered_steps"] or
            step != len(run["revealed_steps"]) + 1):
        raise ValueError("Before you show this teacher packet, keep the related raw response.")
    row = _response(record, run_id, step)
    _previous_feedback(record, run_id, step)
    # After the raw response gate, read only this teacher packet.
    teacher = _packet(step, teacher=True)
    decision = _packet(step)
    _refresh(record, run)
    _observe(record, run, exposure.packet_events(f"H01-{step:02}", decision, teacher)[-1])
    run["revealed_steps"].append(step)
    row["teacher_material"] = deepcopy(teacher)
    return deepcopy(teacher)


def record_feedback(record, run_id, step, text, evidence, declined=False):
    """Record a tutor's statement after the message or explicit opt-out is visible.

    This function checks state and sequence. It cannot verify delivery or feedback quality.
    A hint-only retry remains pending; do not record it as completed feedback.
    """
    _step(step)
    run = _run(record, run_id)
    latest = len(run["revealed_steps"])
    if (step not in (latest, latest + 1) or step not in run["opened_steps"]
            or step not in run["answered_steps"]):
        raise ValueError("Record feedback for the current or most recently revealed step with a raw response.")
    if not _nonempty(text) or not _nonempty(evidence) or type(declined) is not bool:
        raise ValueError("Supply nonempty text and evidence, and an exact boolean for declined.")
    row = _response(record, run_id, step)
    if step == latest + 1:
        _previous_feedback(record, run_id, step)
    if _feedback_complete(row):
        raise ValueError("This response already has delivered feedback or an explicit decline.")
    _refresh(record, run)
    if isinstance(row.get("feedback"), (str, dict)):
        row["legacy_feedback"] = deepcopy(row["feedback"])
    row["feedback"] = None if declined else text
    row["feedback_status"] = "declined" if declined else "delivered"
    row["feedback_evidence"] = evidence
    if declined:
        row["feedback_declined_request"] = text
    return {"saved": True, "feedback_status": row["feedback_status"]}


def _record_path(path):
    path = path.expanduser().resolve()
    protected = [ROOT]
    for home in (Path.home() / ".codex", Path.home() / ".agents"):
        protected.append((home / "skills").resolve())
    if os.environ.get("CODEX_HOME"):
        protected.append((Path(os.environ["CODEX_HOME"]) / "skills").expanduser().resolve())
    if any(path.is_relative_to(folder) for folder in protected):
        raise ValueError("Write records in a location that is not in installed skills or the portable skill.")
    if any((parent / "SKILL.md").is_file() for parent in path.parents):
        raise ValueError("Write records in a location that is not in a skill directory.")
    return path


def _prepare_output(output, encoding):
    rendered = json.dumps(output, ensure_ascii=False, indent=2)
    try:
        rendered.encode(encoding or "utf8")
    except UnicodeEncodeError:
        rendered = json.dumps(output, ensure_ascii=True, indent=2)
        rendered.encode(encoding or "utf8")
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "open", "answer", "reveal", "hint", "feedback"))
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--run")
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--raw-file", type=Path)
    parser.add_argument("--feedback-file", type=Path)
    parser.add_argument("--evidence")
    parser.add_argument("--declined", action="store_true")
    args = parser.parse_args()
    try:
        path = _record_path(args.record)
        record = json.loads(path.read_text(encoding="utf8"))
        if args.action == "start":
            run_id = start_run(record)
            output = dict(run_id=run_id, support=_run(record, run_id)["support"])
        else:
            if not args.run:
                raise ValueError("After start, --run is necessary.")
            if args.action == "open":
                output = open_step(record, args.run, args.step)
            elif args.action == "reveal":
                output = reveal(record, args.run, args.step)
            elif args.action == "hint":
                mark_hint(record, args.run)
                output = {"support": "hinted"}
            elif args.action == "feedback":
                if args.feedback_file is None:
                    raise ValueError("Supply --feedback-file with the already shown tutor message or learner opt-out.")
                output = record_feedback(record, args.run, args.step,
                                         args.feedback_file.read_bytes().decode("utf8"),
                                         args.evidence, declined=args.declined)
            else:
                if args.raw_file is None:
                    raise ValueError("For answer, supply --raw-file with the learner response without changes.")
                save_response(record, args.run, args.step, args.raw_file.read_bytes().decode("utf8"))
                output = {"saved": True}
        # Validate serialization and terminal encoding before committing progress.
        rendered = _prepare_output(output, sys.stdout.encoding)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf8", dir=path.parent,
                                             prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(rendered)


if __name__ == "__main__":
    main()
