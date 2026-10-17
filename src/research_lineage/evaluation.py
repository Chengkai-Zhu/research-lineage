"""Transparent fixture metrics and consent-aware paired reading observations."""

from .core import MapError
from .extraction import assess


def evaluate(manifest):
    provenance = manifest.get("provenance", {})
    if not isinstance(provenance, dict):
        raise MapError("Evaluation provenance must be an object.")
    if provenance.get("kind") not in ("engineering_fixture", "independent_human"):
        raise MapError("Declare engineering_fixture or independent_human provenance.")
    if provenance["kind"] == "independent_human" and (
        provenance.get("consent") is not True
        or not all(provenance.get(k) for k in ("review_reference", "method"))
    ):
        raise MapError(
            "Human-label provenance needs consent, method and a real review reference."
        )
    cases, seen, outcomes = manifest.get("cases"), set(), []
    if not isinstance(cases, list):
        raise MapError("Evaluation manifest needs a cases list.")
    for case in cases:
        if not isinstance(case, dict) or "candidate" not in case:
            raise MapError("Each case needs a candidate and an expected decision.")
        if case.get("expected") not in ("propose", "abstain"):
            raise MapError("Every evaluation case needs an expected decision.")
        decision = assess(case["candidate"])
        if decision["id"] in seen:
            raise MapError("Evaluation case IDs must be unique.")
        seen.add(decision["id"])
        outcomes.append(
            {
                **decision,
                "expected": case["expected"],
                "correct": decision["decision"] == case["expected"],
            }
        )
    per_type = {}
    for kind in sorted({item["type"] for item in outcomes}):
        rows = [item for item in outcomes if item["type"] == kind]
        proposed = [item for item in rows if item["decision"] == "propose"]
        per_type[kind] = {
            "cases": len(rows),
            "proposed": len(proposed),
            "decision_precision": sum(i["correct"] for i in proposed) / len(proposed)
            if proposed
            else None,
            "coverage": len(proposed) / len(rows),
            "abstention": 1 - len(proposed) / len(rows),
        }
    return {
        "provenance": provenance,
        "cases": len(outcomes),
        "per_type": per_type,
        "outcomes": outcomes,
        "external_validation": provenance["kind"] == "independent_human",
        "interpretation": "These metrics measure agreement with supplied labels. Engineering fixtures do not measure scientific precision; reviewer identity is recorded, not authenticated.",
    }


def study_report(study):
    rows, seen, pairs = study.get("observations"), set(), {}
    if not isinstance(rows, list):
        raise MapError("Study input needs an observations list.")
    for row in rows:
        if not isinstance(row, dict):
            raise MapError("Each observation must be an object.")
        if row.get("consent") is not True:
            raise MapError("Only explicitly consented observations may be reported.")
        if not all(
            isinstance(row.get(k), str) and row[k].strip()
            for k in ("participant", "task")
        ):
            raise MapError("Use non-identifying participant and task IDs.")
        if row.get("condition") not in ("baseline", "map"):
            raise MapError("Observation condition must be baseline or map.")
        key = (row["participant"], row["task"], row["condition"])
        if key in seen:
            raise MapError("Duplicate participant/task/condition observation.")
        seen.add(key)
        if (
            isinstance(row.get("seconds"), bool)
            or not isinstance(row.get("seconds"), (int, float))
            or not 0 < row["seconds"] < 86400
        ):
            raise MapError("Record an actual positive duration shorter than 24 hours.")
        if type(row.get("source_check_correct")) is not bool:
            raise MapError("Record a boolean source-check outcome.")
        pairs.setdefault(key[:2], {})[row["condition"]] = row
    if any(set(pair) != {"baseline", "map"} for pair in pairs.values()):
        raise MapError(
            "Every participant/task needs paired baseline and map observations."
        )
    conditions = {}
    for name in ("baseline", "map"):
        subset = [r for r in rows if r["condition"] == name]
        conditions[name] = {
            "observations": len(subset),
            "mean_seconds": sum(r["seconds"] for r in subset) / len(subset)
            if subset
            else None,
            "accuracy": sum(r["source_check_correct"] for r in subset) / len(subset)
            if subset
            else None,
        }
    return {
        "participants": len({r["participant"] for r in rows}),
        "paired_tasks": len(pairs),
        "status": "observations_recorded" if rows else "awaiting_participants",
        "conditions": conditions,
        "limitations": study.get("limitations", []),
        "interpretation": "Descriptive paired observations only; no causal claim or scientific certification.",
    }
