import pytest

from research_lineage.core import MapError
from research_lineage.evaluation import evaluate, study_report


def candidate(case_id):
    return {
        "id": case_id,
        "type": "result",
        "claim": "An explicitly supplied claim.",
        "source": {
            "work_id": "w",
            "version_id": "v",
            "url": "https://example.org/v1",
            "access": "abstract",
        },
        "evidence": {
            "work_id": "w",
            "version_id": "v",
            "url": "https://example.org/v1",
            "locator": "Abstract",
        },
    }


def test_metrics_have_teeth_and_are_not_scientific_precision():
    bad = candidate("c")
    bad["source"]["access"] = "unavailable"
    report = evaluate(
        {
            "provenance": {"kind": "engineering_fixture"},
            "cases": [
                {"candidate": candidate("a"), "expected": "propose"},
                {"candidate": candidate("b"), "expected": "abstain"},
                {"candidate": bad, "expected": "abstain"},
            ],
        }
    )
    metrics = report["per_type"]["result"]
    assert metrics["decision_precision"] == 0.5 and metrics["coverage"] == 2 / 3
    assert (
        report["outcomes"][1]["correct"] is False and not report["external_validation"]
    )


def test_missing_labels_and_unsupported_human_provenance_reject():
    with pytest.raises(MapError):
        evaluate(
            {
                "provenance": {"kind": "engineering_fixture"},
                "cases": [{"candidate": candidate("a")}],
            }
        )
    with pytest.raises(MapError):
        evaluate({"provenance": {"kind": "independent_human"}, "cases": []})


def test_empty_study_is_unavailable_not_perfect():
    report = study_report({"observations": []})
    assert report["participants"] == 0 and report["status"] == "awaiting_participants"
    assert report["conditions"]["map"]["accuracy"] is None


def observations():
    return [
        {
            "participant": "anon-01",
            "task": "source-check",
            "condition": condition,
            "seconds": seconds,
            "source_check_correct": correct,
            "consent": True,
        }
        for condition, seconds, correct in (("baseline", 90, False), ("map", 45, True))
    ]


def test_paired_observations_and_negative_controls():
    rows = observations()
    report = study_report({"observations": rows})
    assert report["participants"] == 1 and report["paired_tasks"] == 1
    assert report["conditions"]["baseline"]["mean_seconds"] == 90
    assert report["conditions"]["map"]["accuracy"] == 1
    for bad in (rows[:1], rows + rows[:1], [{**rows[0], "consent": False}, rows[1]]):
        with pytest.raises(MapError):
            study_report({"observations": bad})
