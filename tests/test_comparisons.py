"""Known-answer controls for authored comparisons, not scholarly ground truth."""

import json
import re
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

import jsonschema
import pytest

from research_lineage.anchors import check_anchor
from research_lineage.cli import main
from research_lineage.contract import SCHEMA, SCHEMA_1_1, validate
from research_lineage.core import MapError, compare, diff_maps, load_map, review_report
from research_lineage.extraction import assess
from research_lineage.render import build
from research_lineage.temporal import update_proposal

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def comparison_map():
    return load_map(ROOT / "tests/fixtures/comparison-map.json")


def candidate(data):
    return {"id": "gate-control", "map": data, "relation_id": "edge"}


def test_version_dispatch_and_published_contracts(comparison_map, sample):
    frozen = deepcopy(sample)
    for version, schema, data, file in (
        ("1.0", SCHEMA, sample, "map-v1.json"),
        ("1.1", SCHEMA_1_1, comparison_map, "map-v1.1.json"),
    ):
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())
        assert (
            json.loads((ROOT / "schema" / file).read_text(encoding="utf-8")) == schema
        )
        assert data["schema_version"] == version and validate(data)["valid"]
    assert sample == frozen
    sample["comparisons"] = []
    assert not validate(sample)["valid"]
    for version in ("2.0", [], None):
        comparison_map["schema_version"] = version
        assert "Unsupported schema_version" in validate(comparison_map)["errors"][0]


def test_comparison_survives_every_export_and_cli(comparison_map, tmp_path, capsys):
    original = deepcopy(comparison_map)
    build(comparison_map, tmp_path / "reading")
    generated = tmp_path / "reading"
    assert load_map(generated / "map.json") == original
    svg = ET.fromstring((generated / "map.svg").read_text(encoding="utf-8"))
    assert json.loads(svg.find("{http://www.w3.org/2000/svg}metadata").text) == original
    html = (generated / "map.html").read_text(encoding="utf-8")
    embedded = re.search(
        r'<script type="application/json" id="map-data">(.*?)</script>', html, re.S
    )
    assert json.loads(embedded[1]) == original
    report = review_report(comparison_map)
    assert "100 calls" in report and "50 calls" in report and "e-a, e-b" in report
    assert (
        main(
            [
                "compare",
                str(generated / "map.json"),
                "a",
                "b",
                "--comparison",
                "c-improvement",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["assessment"] == "comparable"
    assert result["comparison"] == original["comparisons"][0]
    assert comparison_map == original


@pytest.mark.parametrize(
    "fault",
    [
        "units",
        "missing",
        "unknown",
        "citation",
        "version",
        "abstract",
        "wrong-side",
        "null-condition",
    ],
)
def test_intake_and_direct_map_share_negative_gate(comparison_map, fault):
    record = comparison_map["comparisons"][0]
    if fault == "units":
        record["conditions"][2]["right_unit"] = "seconds"
    elif fault == "missing":
        comparison_map["comparisons"] = []
    elif fault == "unknown":
        record.update(assessment="unknown", outcome="not_assessed", improvement=None)
    elif fault == "citation":
        record["basis"] = "citation_only"
    elif fault == "version":
        comparison_map["evidence"][1]["version_id"] = "v-a"
    elif fault == "abstract":
        comparison_map["evidence"][0]["kind"] = "abstract"
    elif fault == "wrong-side":
        record["conditions"][0]["left_evidence"] = ["e-b"]
    else:
        record["conditions"][2]["left"] = None
    validation = validate(comparison_map)
    assessed = assess(candidate(comparison_map))
    assert not validation["valid"]
    assert assessed["decision"] == "abstain"
    assert all(error in assessed["reasons"] for error in validation["errors"])
    assert assessed["review_status"] == "proposed"


def test_valid_intake_is_only_proposed_and_legacy_shape_cannot_bypass(comparison_map):
    assert assess(candidate(comparison_map))["decision"] == "propose"
    assert assess(candidate(comparison_map))["review_status"] == "proposed"
    for bad in (None, [], {"relations": None}):
        assert (
            assess({"id": "bad", "map": bad, "relation_id": "edge"})["decision"]
            == "abstain"
        )


def test_units_need_conversion_and_source_record(comparison_map):
    record = comparison_map["comparisons"][0]
    record["conditions"][2]["right_unit"] = "batch calls"
    assert not validate(comparison_map)["valid"]
    record["conversion"] = {
        "summary": "One batch is one oracle call in this fixture.",
        "assumptions": "Only this synthetic interface.",
        "evidence": ["e-b"],
    }
    assert validate(comparison_map)["valid"]
    record["conversion"]["evidence"] = ["missing"]
    assert not validate(comparison_map)["valid"]


def test_equal_unknown_multichoice_and_reverse_do_not_create_improvements(
    comparison_map,
):
    comparison_map["relations"] = []
    record = comparison_map["comparisons"][0]
    record.update(
        outcome="equal", improvement=None, summary="Equal on the selected criterion."
    )
    assert validate(comparison_map)["valid"]
    result = compare(comparison_map, "a", "b")
    assert (
        result["comparison"]["outcome"] == "equal" and not comparison_map["relations"]
    )
    other = deepcopy(record)
    other.update(
        id="other-question",
        question="A different regime?",
        assessment="unknown",
        outcome="not_assessed",
    )
    comparison_map["comparisons"].append(other)
    unresolved = compare(comparison_map, "a", "b")
    assert unresolved["selection_required"] and unresolved["assessment"] == "unknown"
    assert unresolved["comparison"] is None and len(unresolved["choices"]) == 2
    assert (
        compare(comparison_map, "a", "b", "other-question")["assessment"] == "unknown"
    )
    assert compare(comparison_map, "b", "a")["assessment"] == "unknown"
    with pytest.raises(MapError, match="ordered result endpoints"):
        compare(comparison_map, "b", "a", "c-improvement")
    comparison_map["comparisons"] = []
    comparison_map["results"][1]["settings"] = deepcopy(
        comparison_map["results"][0]["settings"]
    )
    unknown = compare(comparison_map, "a", "b")
    assert all(row["status"] == "same_reported" for row in unknown["fields"])
    assert unknown["assessment"] == "unknown" and unknown["comparison"] is None


def test_conflicting_legacy_field_and_wrong_direction_rejected(comparison_map):
    relation = comparison_map["relations"][0]
    relation["comparability"] = "comparable"
    assert not validate(comparison_map)["valid"]
    del relation["comparability"]
    relation["source"], relation["target"] = relation["target"], relation["source"]
    assert any("direction" in error for error in validate(comparison_map)["errors"])


def test_comparison_only_edit_and_late_context_are_visible(comparison_map):
    before = deepcopy(comparison_map)
    comparison_map["comparisons"][0]["rationale"] = "Changed premise to inspect."
    changes = diff_maps(before, comparison_map)["changes"]
    assert (
        changes["comparisons"]["changed"][0]["fields"]["rationale"]["after"]
        == "Changed premise to inspect."
    )
    assert not changes["results"]["changed"] and not changes["relations"]["changed"]
    work = comparison_map["works"][0]
    work["versions"].append(
        {
            "id": "late-v",
            "label": "Later context",
            "published": "2021-01-01",
            "url": "https://example.org/later",
        }
    )
    comparison_map["evidence"].append(
        {
            **comparison_map["evidence"][0],
            "id": "late-e",
            "version_id": "late-v",
            "url": "https://example.org/later",
        }
    )
    comparison_map["comparisons"][0]["evidence"].append("late-e")
    assert validate(comparison_map)["valid"]
    proposal = update_proposal(before, comparison_map, "2020-06-01")
    assert proposal["eligible_result_ids"] == ["a", "b"]
    assert (
        not proposal["eligible_comparison_ids"]
        and not proposal["eligible_relation_ids"]
    )
    assert {item["reason"] for item in proposal["conflicts"]} == {
        "comparison_evidence_after_cutoff",
        "comparison_unavailable_at_cutoff",
    }


def test_source_anchor_outcomes_binding_and_review_separation(comparison_map):
    evidence = comparison_map["evidence"][0]
    evidence["quote"] = {"exact": "the result", "prefix": "", "suffix": ""}
    report = check_anchor(evidence, "before the\nresult after")
    assert report["outcome"] == "matched" and len(report["text_sha256"]) == 64
    assert (
        check_anchor(evidence, "the result then the result")["outcome"] == "ambiguous"
    )
    assert check_anchor(evidence, "a different statement")["outcome"] == "missing"
    assert check_anchor(evidence)["outcome"] == "unchecked"
    assert (
        check_anchor(evidence, "before the result after")["text_sha256"]
        != report["text_sha256"]
    )
    evidence["anchor_check"] = report
    assert validate(comparison_map)["valid"]
    assert comparison_map["results"][0]["review_status"] == "proposed"
    evidence["quote"]["exact"] = "a different result"
    assert not validate(comparison_map)["valid"]
    assert check_anchor(evidence, "before the result after")["outcome"] == "missing"


def test_anchor_context_disambiguates_and_script_text_is_literal(
    comparison_map, tmp_path
):
    evidence = comparison_map["evidence"][0]
    evidence["quote"] = {"exact": "result", "prefix": "second", "suffix": "end"}
    assert (
        check_anchor(evidence, "first result end; second result end")["outcome"]
        == "matched"
    )
    evidence["quote"] = {
        "exact": "<script>globalThis.injected=true</script>",
        "prefix": "",
        "suffix": "",
    }
    build(comparison_map, tmp_path)
    html = (tmp_path / "map.html").read_text(encoding="utf-8")
    assert "<script>globalThis.injected" not in html
    assert "\\u003cscript\\u003e" in html
    assert comparison_map["evidence"][0]["quote"]["exact"].startswith("<script>")


def test_same_paper_distinct_results_and_multiple_question_fixture():
    data = load_map(ROOT / "src/research_lineage/data/attention-comparisons.json")
    assert len(data["works"]) == 1 and len(data["results"]) == 4
    assert len({r["id"] for r in data["results"]}) == 4
    choices = compare(data, "r-recurrent", "r-attention")
    assert choices["selection_required"] and len(choices["choices"]) == 2
    assert (
        compare(data, "r-recurrent", "r-attention", "c-parallel-depth")["comparison"][
            "conditions"
        ][2]["right"]
        == "O(1)"
    )
    assert compare(data, "r-attention", "r-quality")["assessment"] == "incomparable"


def test_anchor_cli_preserves_input_and_existing_report(
    comparison_map, tmp_path, capsys
):
    comparison_map["evidence"][0]["quote"] = {
        "exact": "the result",
        "prefix": "",
        "suffix": "",
    }
    source, text, output = (
        tmp_path / name for name in ("map.json", "text.txt", "check.json")
    )
    source.write_text(json.dumps(comparison_map), encoding="utf-8")
    text.write_text("before the result after", encoding="utf-8")
    original = source.read_bytes()
    args = ["anchor", str(source), "e-a", "--text", str(text), "--out", str(output)]
    assert main(args) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["outcome"] == "matched"
    snapshot = output.read_bytes()
    assert main(args) == 2 and "exists" in capsys.readouterr().err
    assert source.read_bytes() == original and output.read_bytes() == snapshot
    assert main(["anchor", str(source), "missing"]) == 2
    assert "does not exist" in capsys.readouterr().err


def test_quote_checks_reject_empty_selector_and_oversized_text(comparison_map):
    evidence = comparison_map["evidence"][0]
    evidence["quote"] = {"exact": " ", "prefix": "", "suffix": ""}
    with pytest.raises(ValueError, match="quote selector"):
        check_anchor(evidence, "anything")
    evidence["quote"]["exact"] = "result"
    with pytest.raises(ValueError, match="5 MB"):
        check_anchor(evidence, "a" * 5_000_001)
