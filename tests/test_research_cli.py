import json
from copy import deepcopy

import pytest

from research_lineage.cli import main


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return str(path)


def test_identity_and_evidence_commands_preserve_input(tmp_path, capsys):
    records = [
        {"id": "v1", "arxiv": "2408.13687v1"},
        {"id": "v2", "arxiv": "2408.13687v2"},
        {"id": "other", "doi": "10.1234/other"},
    ]
    source = save(tmp_path / "identities.json", records)
    assert main(["reconcile", source]) == 0
    report = json.loads(capsys.readouterr().out)
    assert [g["records"] for g in report["groups"]] == [["v1", "v2"], ["other"]]
    assert report["input_records"] == records
    assert main(["reconcile", source, "--out", source]) == 2
    assert "Output exists" in capsys.readouterr().err
    assert json.loads((tmp_path / "identities.json").read_text()) == records
    candidate = save(tmp_path / "candidate.json", {"id": "no-text", "type": "result"})
    destination = tmp_path / "decision.json"
    assert main(["assess", candidate, "--out", str(destination)]) == 0
    decision = json.loads(destination.read_text())
    assert decision["decision"] == "abstain" and decision["review_status"] == "proposed"
    assert any("unavailable" in reason for reason in decision["reasons"])


def test_update_command_excludes_later_version_without_editing_maps(
    sample, tmp_path, capsys
):
    before = deepcopy(sample)
    first = sample["results"][0]
    work = next(w for w in sample["works"] if w["id"] == first["work_id"])
    version = next(v for v in work["versions"] if v["id"] == first["version_id"])
    version["published"] = "2026-10-16"
    old = save(tmp_path / "before.json", before)
    new = save(tmp_path / "after.json", sample)
    assert main(["update", old, new, "--as-of", "2020-01-01"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert first["id"] not in report["eligible_result_ids"]
    assert (
        report["proposal_only"] and report["historical_reconstruction"] == "unavailable"
    )
    assert json.loads((tmp_path / "before.json").read_text()) == before
    assert json.loads((tmp_path / "after.json").read_text()) == sample


@pytest.mark.parametrize("command", ["assess", "reconcile", "evaluate", "study"])
def test_malformed_research_input_reports_an_actionable_error(
    command, tmp_path, capsys
):
    path = save(tmp_path / "bad.json", None)
    assert main([command, path]) == 2
    error = capsys.readouterr().err
    assert error.startswith("error: ") and "Traceback" not in error
