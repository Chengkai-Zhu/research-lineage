"""Report safety uses engineering records, not simulated literature evidence."""

import importlib.util
import json
from pathlib import Path

import pytest

from research_lineage.core import MapError, dump
from research_lineage.research_scope import audit_run
from test_research_scope import change, make_map, write_run


@pytest.fixture
def report_run(sample, tmp_path):
    path = write_run(tmp_path, make_map(sample, 4))
    (tmp_path / "audit.json").write_text(dump(audit_run(path)), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "render_report", Path(__file__).parents[1] / "scripts/render_research_report.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return path, module


def test_report_rechecks_evidence_and_renders_escaped_text(report_run):
    path, module = report_run
    change(
        path, "trace", lambda t: t.update(query="<script>alert(1)</script>")
    )
    (path.parent / "audit.json").write_text(dump(audit_run(path)), encoding="utf-8")
    assert module.main([str(path.parent)]) == 0
    page = (path.parent / "report.html").read_text(encoding="utf-8")
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "<script>alert(1)</script>" not in page


@pytest.mark.parametrize("rehash", [False, True])
def test_report_rejects_unsafe_trace_link_even_when_rehashed(report_run, rehash):
    path, module = report_run
    if rehash:
        change(
            path, "trace", lambda t: t["urls"].append("javascript:alert(1)")
        )
    else:
        trace = path.parent / "tool-trace.jsonl"
        data = json.loads(trace.read_text(encoding="utf-8"))
        data["urls"].append("javascript:alert(1)")
        trace.write_text(json.dumps(data) + "\n", encoding="utf-8")
    assert module.main([str(path.parent)]) == 2
    assert not (path.parent / "report.html").exists()


def test_report_rejects_stale_audit_bad_completion_and_output_collision(report_run):
    path, module = report_run
    cached = path.parent / "audit.json"
    report = audit_run(path)
    report["counts"]["map_works"] += 1
    cached.write_text(dump(report), encoding="utf-8")
    with pytest.raises(MapError, match="Cached audit"):
        module.write(path.parent)
    cached.write_text(dump(audit_run(path)), encoding="utf-8")
    # A valid artifact named report.html must never be overwritten by the notebook.
    manifest = json.loads(path.read_text(encoding="utf-8"))
    original_html = path.parent / manifest["artifacts"]["html"]["path"]
    original = original_html.read_bytes()
    destination = path.parent / "report.html"
    destination.write_bytes(original)
    manifest["artifacts"]["html"]["path"] = "report.html"
    path.write_text(dump(manifest), encoding="utf-8")
    with pytest.raises(MapError, match="alias"):
        module.write(path.parent)
    assert destination.read_bytes() == original
    assert audit_run(path)["status"] == "PASS"
    change(
        path,
        "research_log",
        lambda log: log["branches"][0].update(status="gap", gap="Not resolved"),
    )
    assert module.main([str(path.parent)]) == 2
    assert destination.read_bytes() == original
