"""Audit an agent's recorded research trail, without certifying scholarly coverage."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from .contract import DATE, ID, URL, _structure, array, choice, obj, text
from .core import MAX_BYTES, MapError, _unique, load_map

IDS = array(ID, maximum=2000)
NULL_TEXT = {"type": ["string", "null"], "minLength": 1, "maxLength": 4000}
DIGEST = {**text(64), "pattern": "^[a-f0-9]{64}$"}
ARTIFACT = obj(path=text(500), sha256=DIGEST)
TRACE_SCHEMA = obj(
    id=ID,
    at=text(50),
    tool=text(100),
    query=text(8000),
    status=choice("ok", "failed"),
    urls=array(URL, maximum=500),
    observation=text(8000),
)
LOG_SCHEMA = obj(
    schema_version=choice("1.0"),
    cutoff=DATE,
    scope=obj(
        mode=choice("history", "reading_path"), summary=text(), request=NULL_TEXT
    ),
    reference_sets=array(
        obj(id=ID, url=URL, locator=text(), purpose=text(), candidate_ids=IDS),
        minimum=1,
    ),
    searches=array(
        obj(
            id=ID,
            direction=choice("seed", "review", "backward", "forward"),
            query=text(8000),
            checked=DATE,
            status=choice("ok", "failed"),
            trace_ids=IDS,
            candidate_ids=IDS,
            finding=text(8000),
        ),
        minimum=1,
        maximum=2000,
    ),
    candidates=array(
        obj(
            id=ID,
            title=text(500),
            url=URL,
            access=choice("full_text", "abstract", "metadata", "unavailable"),
            locator=text(),
            decision=choice("include", "exclude", "defer"),
            reason=text(),
            work_id={"type": ["string", "null"], "pattern": "^[a-z0-9][a-z0-9-]*$"},
            search_ids=IDS,
            branch_ids=IDS,
            trace_ids=IDS,
        ),
        minimum=1,
        maximum=2000,
    ),
    branches=array(
        obj(
            id=ID,
            label=text(200),
            basis=text(),
            reference_set_ids=IDS,
            candidate_ids=IDS,
            search_ids=IDS,
            status=choice("covered", "gap"),
            gap=NULL_TEXT,
        ),
        minimum=1,
    ),
    stop=obj(
        status=choice("complete", "partial"),
        reason=text(),
        unresolved_candidate_ids=IDS,
        unresolved_branch_ids=IDS,
    ),
)
MANIFEST_SCHEMA = obj(
    schema_version=choice("1.0"),
    input=obj(seed=text(500), cutoff=DATE, cutoff_request=NULL_TEXT),
    execution=obj(
        host=text(200),
        agent_id=text(200),
        model=NULL_TEXT,
        context=choice("fresh", "existing"),
        isolation=text(),
        research_date=DATE,
        started_at=text(50),
        finished_at=text(50),
        skill_revision=text(200),
        tools=array(text(100), minimum=1),
    ),
    artifacts=obj(
        brief=ARTIFACT,
        map=ARTIFACT,
        research_log=ARTIFACT,
        trace=ARTIFACT,
        html=ARTIFACT,
        skill=ARTIFACT,
        prompt=ARTIFACT,
    ),
)


def run_schemas():
    return {
        "manifest": MANIFEST_SCHEMA,
        "research_log": LOG_SCHEMA,
        "trace_entry": TRACE_SCHEMA,
    }


def _shape(data, schema, name):
    errors = []
    _structure(data, schema, name, errors)
    if errors:
        raise MapError("\n".join(errors))


def _read(path):
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise MapError(f"Research artifact exceeds 5 MB: {Path(path).name}")
    return raw


def _json(raw):
    try:
        return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise MapError(f"Cannot read research JSON: {exc}") from exc


def _index(records, name):
    result = {r["id"]: r for r in records}
    if len(result) != len(records):
        raise MapError(f"{name}: duplicate IDs")
    return result


def _refs(values, index, label, errors, required=True):
    if (
        (required and not values)
        or len(set(values)) != len(values)
        or any(v not in index for v in values)
    ):
        errors.append(f"{label}: missing, duplicate or unknown references")


def _instant(value):
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if instant.tzinfo is None:
            raise ValueError("timezone required")
        return instant
    except ValueError as exc:
        raise MapError(f"Use a timezone-aware ISO timestamp: {value}") from exc


def _artifacts(manifest, root):
    raw, paths = {}, {}
    for name, record in manifest["artifacts"].items():
        relative = Path(record["path"])
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root):
            raise MapError(f"{name}: artifact path must stay inside the run folder")
        raw[name] = _read(path)
        if hashlib.sha256(raw[name]).hexdigest() != record["sha256"]:
            raise MapError(f"{name}: artifact SHA-256 mismatch")
        paths[name] = path
    if len(set(paths.values())) != len(paths):
        raise MapError("Research artifacts must use distinct files")
    return raw, paths


def _provenance(manifest, raw, trace):
    execution, errors = manifest["execution"], []
    if execution["context"] != "fresh":
        errors.append("A fresh-context execution has not been recorded")
    started = _instant(execution["started_at"])
    finished = _instant(execution["finished_at"])
    if finished < started:
        errors.append("Execution ends before it starts")
    if started.date().isoformat() != execution["research_date"]:
        errors.append("Research date differs from the recorded start date")
    for entry in trace:
        if not started <= _instant(entry["at"]) <= finished:
            errors.append(
                f"{entry['id']}: trace time is outside the execution interval"
            )
        if entry["tool"] not in execution["tools"]:
            errors.append(f"{entry['id']}: trace tool is absent from execution.tools")
    if manifest["input"]["seed"] not in raw["prompt"].decode("utf-8-sig"):
        errors.append("Recorded invocation does not contain the input seed")
    return errors


def _cutoff(manifest, brief, data, log):
    errors = []
    expected = manifest["input"]["cutoff"]
    if (
        not manifest["input"]["cutoff_request"]
        and expected != manifest["execution"]["research_date"]
    ):
        errors.append(
            "Cutoff differs from the research date without a recorded user request"
        )
    if brief.get("seed") != manifest["input"]["seed"]:
        errors.append("Original brief seed differs from the invocation")
    if any(
        value != expected
        for value in (brief.get("cutoff"), data["scope"]["cutoff"], log["cutoff"])
    ):
        errors.append("Brief, map and research log must preserve the requested cutoff")
    return errors


def _source_trail(log, trace, data):
    errors = []
    candidates = _index(log["candidates"], "candidates")
    searches = _index(log["searches"], "searches")
    branches = _index(log["branches"], "branches")
    references = _index(log["reference_sets"], "reference_sets")
    traces = _index(trace, "trace")
    works = {w["id"]: w for w in data["works"]}
    observed_urls = {
        url for entry in trace if entry["status"] == "ok" for url in entry["urls"]
    }
    for ref in references.values():
        _refs(ref["candidate_ids"], candidates, f"{ref['id']} candidates", errors)
        if ref["url"] not in observed_urls:
            errors.append(
                f"{ref['id']}: reference-set URL has no successful tool trace"
            )
    for search in searches.values():
        _refs(search["trace_ids"], traces, f"{search['id']} trace", errors)
        _refs(
            search["candidate_ids"],
            candidates,
            f"{search['id']} candidates",
            errors,
            False,
        )
        for cid in search["candidate_ids"]:
            if cid in candidates and search["id"] not in candidates[cid]["search_ids"]:
                errors.append(
                    f"{search['id']}: candidate {cid} lacks the reciprocal search reference"
                )
    included = []
    for candidate in candidates.values():
        cid = candidate["id"]
        _refs(candidate["search_ids"], searches, f"{cid} searches", errors)
        _refs(candidate["branch_ids"], branches, f"{cid} branches", errors)
        _refs(candidate["trace_ids"], traces, f"{cid} trace", errors)
        for sid in candidate["search_ids"]:
            if sid in searches and cid not in searches[sid]["candidate_ids"]:
                errors.append(f"{cid}: search {sid} does not record this candidate")
        for bid in candidate["branch_ids"]:
            if bid in branches and cid not in branches[bid]["candidate_ids"]:
                errors.append(f"{cid}: branch {bid} does not record this candidate")
        observed = {
            url
            for tid in candidate["trace_ids"]
            if tid in traces
            and (candidate["decision"] != "include" or traces[tid]["status"] == "ok")
            for url in traces[tid]["urls"]
        }
        if candidate["url"] not in observed:
            errors.append(f"{cid}: source URL is absent from the linked tool trace")
        if candidate["decision"] == "include":
            included.append(candidate["work_id"])
            if candidate["work_id"] not in works or candidate["access"] in (
                "metadata",
                "unavailable",
            ):
                errors.append(
                    f"{cid}: included work is missing or has no content access"
                )
            elif candidate["url"] not in {
                v["url"] for v in works[candidate["work_id"]]["versions"]
            }:
                errors.append(
                    f"{cid}: candidate URL differs from the mapped source versions"
                )
        elif candidate["work_id"] is not None:
            errors.append(
                f"{cid}: excluded/deferred candidate must not claim a mapped work"
            )
    if set(included) != set(works) or len(included) != len(set(included)):
        errors.append(
            "Included candidates must account for every map work exactly once"
        )
    for branch in branches.values():
        bid = branch["id"]
        _refs(branch["reference_set_ids"], references, f"{bid} reference sets", errors)
        _refs(branch["candidate_ids"], candidates, f"{bid} candidates", errors)
        _refs(branch["search_ids"], searches, f"{bid} searches", errors)
        for cid in branch["candidate_ids"]:
            if cid in candidates and bid not in candidates[cid]["branch_ids"]:
                errors.append(
                    f"{bid}: candidate {cid} lacks the reciprocal branch reference"
                )
        if branch["status"] == "gap" and not branch["gap"]:
            errors.append(f"{bid}: a coverage gap requires an explanation")
        if branch["status"] == "covered" and branch["gap"]:
            errors.append(f"{bid}: a covered branch still records an unresolved gap")
        if branch["status"] == "covered" and not any(
            candidates.get(cid, {}).get("decision") == "include"
            for cid in branch["candidate_ids"]
        ):
            errors.append(f"{bid}: covered branch has no included evidence")
    _refs(
        log["stop"]["unresolved_candidate_ids"],
        candidates,
        "unresolved candidates",
        errors,
        False,
    )
    _refs(
        log["stop"]["unresolved_branch_ids"],
        branches,
        "unresolved branches",
        errors,
        False,
    )
    return errors


def _completion(log, trace):
    errors, partial = [], []
    traces = {t["id"]: t for t in trace}
    directions = {
        s["direction"]
        for s in log["searches"]
        if s["status"] == "ok"
        and any(traces.get(t, {}).get("status") == "ok" for t in s["trace_ids"])
    }
    required_directions = ("seed", "review", "backward", "forward")
    if log["scope"]["mode"] == "reading_path" and log["scope"]["request"]:
        required_directions = ("seed", "backward")
    for direction in required_directions:
        if direction not in directions:
            partial.append(f"No successful {direction} search is recorded")
    deferred = {c["id"] for c in log["candidates"] if c["decision"] == "defer"}
    gaps = {b["id"] for b in log["branches"] if b["status"] == "gap"}
    if deferred != set(log["stop"]["unresolved_candidate_ids"]) or gaps != set(
        log["stop"]["unresolved_branch_ids"]
    ):
        errors.append("Stopping record hides or invents unresolved candidates/branches")
    if deferred or gaps:
        partial.append("Unresolved candidates or central coverage branches remain")
    if log["scope"]["mode"] == "reading_path" and not log["scope"]["request"]:
        errors.append("A narrow reading path needs the recorded user request")
    if log["stop"]["status"] == "partial":
        partial.append("Agent declared this research run partial")
    if log["stop"]["status"] == "complete" and partial:
        errors.append(
            "Research is declared complete despite incomplete search/coverage evidence"
        )
    return errors, partial


def audit_run(path):
    """Check internal evidence consistency; a PASS is not an expert coverage verdict."""
    manifest = _json(_read(path))
    _shape(manifest, MANIFEST_SCHEMA, "manifest")
    raw, paths = _artifacts(manifest, Path(path).resolve().parent)
    brief, log = _json(raw["brief"]), _json(raw["research_log"])
    if not isinstance(brief, dict):
        raise MapError("Research brief must be a JSON object")
    _shape(log, LOG_SCHEMA, "research_log")
    trace = [_json(line) for line in raw["trace"].splitlines() if line.strip()]
    if not trace:
        raise MapError("Tool trace is empty")
    for index, entry in enumerate(trace):
        _shape(entry, TRACE_SCHEMA, f"trace[{index}]")
        _instant(entry["at"])
    data = load_map(paths["map"])
    embedded = re.search(
        rb'<script type="application/json" id="map-data">\s*(.*?)\s*</script>',
        raw["html"],
        re.S,
    )
    trail_errors = _source_trail(log, trace, data)
    if not embedded or _json(embedded[1]) != data:
        trail_errors.append("Generated HTML does not embed the complete mapped corpus")
    completion_errors, partial = _completion(log, trace)
    errors = {
        "execution_provenance": _provenance(manifest, raw, trace),
        "cutoff_consistency": _cutoff(manifest, brief, data, log),
        "source_trail": trail_errors,
        "research_completion": completion_errors,
    }
    checks = {
        key: {
            "status": "FAIL"
            if value
            else "PARTIAL"
            if key == "research_completion" and partial
            else "PASS",
            "details": value or (partial if key == "research_completion" else []),
        }
        for key, value in errors.items()
    }
    counts = {
        "candidates": len(log["candidates"]),
        "map_works": len(data["works"]),
        "route_steps": len(data["reading_route"]),
        "overview_cards": len(data.get("narrative", {}).get("turning_points", [])),
        "searches": len(log["searches"]),
        "trace_entries": len(trace),
    }
    counts.update(
        {
            decision: sum(c["decision"] == decision for c in log["candidates"])
            for decision in ("include", "exclude", "defer")
        }
    )
    return {
        "status": "FAIL" if any(errors.values()) else "PARTIAL" if partial else "PASS",
        "checks": checks,
        "counts": counts,
        "limits": "Audits recorded evidence and cross-file consistency. Does not authenticate tool execution, user authorization, branch selection, search exhaustiveness, or scientific truth; inspect the linked sources and runner records.",
    }
