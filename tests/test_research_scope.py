"""Engineering evidence fixtures; these tests do not simulate literature research."""

import hashlib
import json
from copy import deepcopy
from datetime import date

import pytest

from research_lineage.cli import main
from research_lineage.core import MapError, dump
from research_lineage.intake import prepare
from research_lineage.render import render_html
from research_lineage.research_scope import audit_run

SEED = "https://arxiv.org/abs/2408.13687v1"


def make_map(sample, count):
    data = deepcopy(sample)
    base_result = sample["results"][0]
    base_work = next(w for w in sample["works"] if w["id"] == base_result["work_id"])
    base_evidence = next(
        e for e in sample["evidence"] if e["id"] == base_result["evidence"][0]
    )
    data.update(works=[], results=[], evidence=[], relations=[], reading_route=[])
    data.pop("narrative", None)
    data["scope"]["cutoff"] = date.today().isoformat()
    for i in range(count):
        work, result, evidence = deepcopy((base_work, base_result, base_evidence))
        work["id"], result["id"], evidence["id"] = f"w-{i}", f"r-{i}", f"e-{i}"
        version = next(v for v in work["versions"] if v["id"] == result["version_id"])
        version["id"] = f"v-{i}"
        work["versions"] = [version]
        result.update(
            work_id=work["id"], version_id=version["id"], evidence=[evidence["id"]]
        )
        evidence.update(work_id=work["id"], version_id=version["id"])
        data["works"].append(work)
        data["results"].append(result)
        data["evidence"].append(evidence)
    data["reading_route"] = ["r-0"]
    data["narrative"] = {
        "overview": "Synthetic engineering fixture.",
        "turning_points": [
            {"title": "A change", "summary": "Fixture only.", "result_ids": ["r-0"]}
        ],
    }
    return data


def write_run(folder, data):
    cutoff = data["scope"]["cutoff"]
    _, brief = prepare(SEED)
    candidates = [
        {
            "id": f"c-{i}",
            "title": work["title"],
            "url": work["versions"][0]["url"],
            "access": "abstract",
            "locator": "Abstract (synthetic audit fixture)",
            "decision": "include",
            "reason": "Fixture membership, not a research judgment.",
            "work_id": work["id"],
            "search_ids": ["seed"],
            "branch_ids": ["branch"],
            "trace_ids": ["trace"],
        }
        for i, work in enumerate(data["works"])
    ]
    cids = [c["id"] for c in candidates]
    log = {
        "schema_version": "1.0",
        "cutoff": cutoff,
        "scope": {
            "mode": "history",
            "summary": "Engineering fixture.",
            "request": None,
        },
        "reference_sets": [
            {
                "id": "refs",
                "url": SEED,
                "locator": "Fixture references",
                "purpose": "Test cross-references, not literature coverage.",
                "candidate_ids": cids,
            }
        ],
        "searches": [
            {
                "id": direction,
                "direction": direction,
                "query": f"Fixture {direction}",
                "checked": cutoff,
                "status": "ok",
                "trace_ids": ["trace"],
                "candidate_ids": cids if direction == "seed" else [],
                "finding": "Synthetic engineering fixture.",
            }
            for direction in ("seed", "review", "backward", "forward")
        ],
        "candidates": candidates,
        "branches": [
            {
                "id": "branch",
                "label": "Fixture branch",
                "basis": "Fixture provenance.",
                "reference_set_ids": ["refs"],
                "candidate_ids": cids,
                "search_ids": ["seed", "forward"],
                "status": "covered",
                "gap": None,
            }
        ],
        "stop": {
            "status": "complete",
            "reason": "Synthetic fixture is accounted for.",
            "unresolved_candidate_ids": [],
            "unresolved_branch_ids": [],
        },
    }
    trace = {
        "id": "trace",
        "at": cutoff + "T00:00:01+00:00",
        "tool": "fixture",
        "query": "Synthetic query",
        "status": "ok",
        "urls": list(dict.fromkeys([SEED] + [c["url"] for c in candidates])),
        "observation": "Synthetic test data; no actual literature search.",
    }
    files = {
        "brief": ("research-brief.json", dump(brief)),
        "map": ("map.json", dump(data)),
        "research_log": ("research-log.json", dump(log)),
        "trace": ("tool-trace.jsonl", json.dumps(trace) + "\n"),
        "html": ("map.html", render_html(data)),
        "skill": ("SKILL.used.md", "Synthetic skill fixture."),
        "prompt": ("invocation.txt", "Synthetic test invocation: " + SEED),
    }
    for name, content in files.values():
        (folder / name).write_text(content, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "input": {"seed": SEED, "cutoff": cutoff, "cutoff_request": None},
        "execution": {
            "host": "Unit-test fixture",
            "agent_id": "synthetic-agent",
            "model": None,
            "context": "fresh",
            "isolation": "Synthetic test, not a real host run.",
            "research_date": cutoff,
            "started_at": cutoff + "T00:00:00+00:00",
            "finished_at": cutoff + "T00:01:00+00:00",
            "skill_revision": "fixture",
            "tools": ["fixture"],
        },
        "artifacts": {
            key: {
                "path": name,
                "sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest(),
            }
            for key, (name, _) in files.items()
        },
    }
    path = folder / "manifest.json"
    path.write_text(dump(manifest), encoding="utf-8")
    return path


def change(path, key, transform):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    artifact = manifest["artifacts"][key]
    target = path.parent / artifact["path"]
    data = json.loads(target.read_text(encoding="utf-8"))
    transform(data)
    target.write_text(
        json.dumps(data) + "\n" if key == "trace" else dump(data), encoding="utf-8"
    )
    artifact["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    path.write_text(dump(manifest), encoding="utf-8")


def test_pinned_seed_does_not_shorten_default_cutoff():
    draft, brief = prepare(SEED)
    assert brief["identifiers"] == {"arxiv": "2408.13687", "version": "v1"}
    assert brief["cutoff"] == draft["scope"]["cutoff"] == date.today().isoformat()
    assert (
        brief["source_budget"] is None
        and brief["research_plan"]["corpus_limit"] is None
    )
    _, bounded = prepare(SEED, cutoff="2025-01-01")
    assert bounded["cutoff"] == "2025-01-01" and bounded["cutoff_origin"] == "provided"


@pytest.mark.parametrize("count", [4, 40])
def test_corpus_size_is_independent_of_presentation(sample, tmp_path, count):
    path = write_run(tmp_path, make_map(sample, count))
    report = audit_run(path)
    assert report["status"] == "PASS"
    assert report["counts"]["map_works"] == report["counts"]["include"] == count
    assert report["counts"]["route_steps"] == report["counts"]["overview_cards"] == 1


@pytest.mark.parametrize("count", [4, 40])
def test_large_or_small_corpus_cannot_hide_missing_forward_search(
    sample, tmp_path, count
):
    path = write_run(tmp_path, make_map(sample, count))

    def remove(log):
        log["searches"] = [s for s in log["searches"] if s["direction"] != "forward"]
        log["branches"][0]["search_ids"] = ["seed"]

    change(path, "research_log", remove)
    report = audit_run(path)
    assert report["status"] == "FAIL"
    assert report["checks"]["research_completion"]["status"] == "FAIL"


def test_unrequested_cutoff_change_fails_even_with_matching_map(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    manifest = json.loads(path.read_text())
    manifest["input"]["cutoff"] = "2024-08-24"
    path.write_text(dump(manifest))
    report = audit_run(path)
    assert report["checks"]["cutoff_consistency"]["status"] == "FAIL"


def test_unresolved_branch_is_partial_and_cannot_be_hidden(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))

    def partial(log):
        log["branches"][0].update(status="gap", gap="Missing central evidence.")
        log["stop"].update(status="partial", unresolved_branch_ids=["branch"])

    change(path, "research_log", partial)
    assert audit_run(path)["status"] == "PARTIAL"
    assert main(["audit-research", str(path)]) == 3
    change(
        path,
        "research_log",
        lambda log: log["stop"].update(status="complete", unresolved_branch_ids=[]),
    )
    report = audit_run(path)
    assert report["status"] == "FAIL"
    assert "hides" in " ".join(report["checks"]["research_completion"]["details"])


def test_included_candidate_requires_access_and_actual_source_trace(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    change(
        path,
        "research_log",
        lambda log: log["candidates"][0].update(
            access="metadata", url="https://example.org/unread"
        ),
    )
    report = audit_run(path)
    assert report["checks"]["source_trail"]["status"] == "FAIL"
    assert any(
        "tool trace" in message
        for message in report["checks"]["source_trail"]["details"]
    )


def test_html_cannot_drop_works_from_larger_corpus(sample, tmp_path):
    data = make_map(sample, 12)
    path = write_run(tmp_path, data)
    manifest = json.loads(path.read_text())
    html = tmp_path / "map.html"
    html.write_text(render_html(make_map(sample, 4)), encoding="utf-8")
    manifest["artifacts"]["html"]["sha256"] = hashlib.sha256(
        html.read_bytes()
    ).hexdigest()
    path.write_text(dump(manifest))
    assert audit_run(path)["checks"]["source_trail"]["status"] == "FAIL"


@pytest.mark.parametrize("bad", ["../outside.json", "/outside.json"])
def test_artifact_paths_cannot_escape_run_folder(sample, tmp_path, bad):
    path = write_run(tmp_path, make_map(sample, 4))
    manifest = json.loads(path.read_text())
    manifest["artifacts"]["brief"]["path"] = bad
    path.write_text(dump(manifest))
    with pytest.raises(MapError, match="inside"):
        audit_run(path)


def test_artifact_tampering_and_duplicate_records_fail(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    (tmp_path / "invocation.txt").write_text("Changed")
    with pytest.raises(MapError, match="SHA-256"):
        audit_run(path)
    path = write_run(tmp_path, make_map(sample, 4))
    change(
        path,
        "research_log",
        lambda log: log["candidates"].append(deepcopy(log["candidates"][0])),
    )
    with pytest.raises(MapError, match="duplicate IDs"):
        audit_run(path)


def test_existing_context_or_undeclared_narrowing_does_not_pass(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    manifest = json.loads(path.read_text())
    manifest["execution"]["context"] = "existing"
    path.write_text(dump(manifest))
    change(path, "research_log", lambda log: log["scope"].update(mode="reading_path"))
    report = audit_run(path)
    assert report["checks"]["execution_provenance"]["status"] == "FAIL"
    assert report["checks"]["research_completion"]["status"] == "FAIL"


def test_explicit_narrow_reading_path_does_not_require_a_field_survey(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))

    def narrow(log):
        log["scope"].update(
            mode="reading_path",
            request="Show a short ancestry reading path ending at this paper.",
        )
        log["searches"] = [
            s for s in log["searches"] if s["direction"] in ("seed", "backward")
        ]
        log["branches"][0]["search_ids"] = ["seed", "backward"]

    change(path, "research_log", narrow)
    assert audit_run(path)["status"] == "PASS"


@pytest.mark.parametrize(
    "field,value", [("at", "2000-01-01T00:00:00+00:00"), ("tool", "unrecorded-tool")]
)
def test_trace_time_and_tool_must_agree_with_execution(sample, tmp_path, field, value):
    path = write_run(tmp_path, make_map(sample, 4))
    change(path, "trace", lambda trace: trace.update({field: value}))
    assert audit_run(path)["checks"]["execution_provenance"]["status"] == "FAIL"


def test_unread_reference_set_cannot_ground_coverage(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    change(
        path,
        "research_log",
        lambda log: log["reference_sets"][0].update(
            url="https://example.org/unread-review"
        ),
    )
    assert audit_run(path)["checks"]["source_trail"]["status"] == "FAIL"


def test_failed_source_read_cannot_be_rescued_by_unrelated_success(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    manifest = json.loads(path.read_text(encoding="utf-8"))
    trace_path = tmp_path / "tool-trace.jsonl"
    failed = json.loads(trace_path.read_text(encoding="utf-8"))
    failed.update(id="failed", status="failed")
    success = {**failed, "id": "success", "status": "ok", "urls": [SEED]}
    trace_path.write_text(
        json.dumps(failed) + "\n" + json.dumps(success) + "\n", encoding="utf-8"
    )
    manifest["artifacts"]["trace"]["sha256"] = hashlib.sha256(
        trace_path.read_bytes()
    ).hexdigest()
    path.write_text(dump(manifest), encoding="utf-8")

    def substitute(log):
        for search in log["searches"]:
            search["trace_ids"] = ["success"]
        for candidate in log["candidates"]:
            candidate["trace_ids"] = ["failed"]

    change(path, "research_log", substitute)
    report = audit_run(path)
    assert report["checks"]["research_completion"]["status"] == "PASS"
    assert report["checks"]["source_trail"]["status"] == "FAIL"


def test_failed_access_can_remain_as_an_explicit_deferred_gap(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    manifest = json.loads(path.read_text(encoding="utf-8"))
    trace_path = tmp_path / "tool-trace.jsonl"
    failure = {
        "id": "unavailable",
        "at": date.today().isoformat() + "T00:00:02+00:00",
        "tool": "fixture",
        "query": "Failed fixture open",
        "status": "failed",
        "urls": ["https://example.org/unavailable"],
        "observation": "HTTP access failure.",
    }
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(failure) + "\n")
    manifest["artifacts"]["trace"]["sha256"] = hashlib.sha256(
        trace_path.read_bytes()
    ).hexdigest()
    path.write_text(dump(manifest), encoding="utf-8")

    def defer(log):
        log["candidates"].append(
            {
                "id": "pending",
                "title": "Unavailable central source",
                "url": "https://example.org/unavailable",
                "access": "unavailable",
                "locator": "Failed access",
                "decision": "defer",
                "reason": "Needs source access.",
                "work_id": None,
                "search_ids": ["forward"],
                "branch_ids": ["branch"],
                "trace_ids": ["unavailable"],
            }
        )
        log["searches"][-1]["candidate_ids"].append("pending")
        log["branches"][0]["candidate_ids"].append("pending")
        log["branches"][0].update(status="gap", gap="Central source is unavailable.")
        log["stop"].update(
            status="partial",
            unresolved_branch_ids=["branch"],
            unresolved_candidate_ids=["pending"],
        )

    change(path, "research_log", defer)
    report = audit_run(path)
    assert report["status"] == "PARTIAL"
    assert report["checks"]["source_trail"]["status"] == "PASS"


def test_cli_and_reader_friendly_checker(sample, tmp_path, capsys):
    import importlib.util
    from pathlib import Path

    path = write_run(tmp_path, make_map(sample, 4))
    spec = importlib.util.spec_from_file_location(
        "verify", Path(__file__).parents[1] / "scripts/verify_research_run.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main([str(path)]) == 0
    assert "PASS cutoff_consistency" in capsys.readouterr().out
    output = tmp_path / "report.json"
    assert main(["audit-research", str(path), "--out", str(output)]) == 0
    assert json.loads(output.read_text())["counts"]["map_works"] == 4
    assert main(["audit-research", str(path), "--out", str(output)]) == 2
    schema = tmp_path / "schemas.json"
    assert main(["research-schema", "--out", str(schema)]) == 0
    assert set(json.loads(schema.read_text())) == {
        "manifest",
        "research_log",
        "trace_entry",
    }
