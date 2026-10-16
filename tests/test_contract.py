from copy import deepcopy

import jsonschema
import pytest

from research_lineage.contract import SCHEMA, safe_url, validate


def test_schema_and_runtime_accept_real_sample(sample):
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    jsonschema.validate(sample, SCHEMA, format_checker=jsonschema.FormatChecker())
    result = validate(sample)
    assert result["valid"]
    assert "14 results/relationships" in result["warnings"][0]


@pytest.mark.parametrize(
    "field", ["scope", "works", "results", "evidence", "relations", "reading_route"]
)
def test_missing_required_collection_is_actionable(sample, field):
    del sample[field]
    result = validate(sample)
    assert not result["valid"]
    assert any(field in message for message in result["errors"])


@pytest.mark.parametrize(
    "collection", ["lanes", "works", "results", "evidence", "relations"]
)
def test_duplicate_ids(sample, collection):
    sample[collection].append(deepcopy(sample[collection][0]))
    assert not validate(sample)["valid"]


@pytest.mark.parametrize(
    "path,value,expected",
    [
        (("results", 0, "work_id"), "missing", "reference"),
        (("results", 0, "version_id"), "qsvt-v1", "reference"),
        (("results", 0, "lane"), "missing", "lane"),
        (("results", 0, "evidence"), ["missing"], "evidence"),
        (("relations", 0, "target"), "missing", "endpoint"),
        (("relations", 0, "basis"), "citation_only", "citation alone"),
        (("relations", 0, "source"), "r-qsvt", "self relationship"),
        (("evidence", 0, "url"), "https://example.org/wrong-version", "pinned"),
        (("evidence", 0, "checked"), "2015-01-01", "before source"),
        (("evidence", 0, "checked"), "2026-02-30", "calendar"),
        (("works", 0, "first_published"), "2027-01-01", "cutoff"),
    ],
)
def test_invalid_references_and_evidence(sample, path, value, expected):
    target = sample
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    result = validate(sample)
    assert not result["valid"]
    assert any(expected in error for error in result["errors"])


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "data:text/html,test",
        "file:///secret",
        "https://user:password@example.org",
        "https://example.org\nattack",
        "https://example.org\\bad",
        "https://[bad",
        "//example.org",
        "https:///missing",
    ],
)
def test_unsafe_links_are_rejected(sample, url):
    assert not safe_url(url)
    sample["works"][0]["versions"][0]["url"] = url
    assert not validate(sample)["valid"]


def test_version_cutoff_and_source_ownership(sample):
    sample["scope"]["cutoff"] = "2020-01-01"
    assert not validate(sample)["valid"]
    sample["scope"]["cutoff"] = "2026-10-16"
    sample["evidence"][0]["version_id"] = "qsvt-v1"
    assert not validate(sample)["valid"]


def test_review_cannot_be_self_certified_with_abstract(sample):
    item = sample["results"][0]
    item["review_status"] = "reviewed"
    assert not validate(sample)["valid"]
    item["reviews"] = [
        {"name": "Recorded Reviewer", "url": "https://example.org/review/1"}
    ]
    assert not validate(sample)["valid"]
    sample["evidence"][0]["kind"] = "full_text"
    check = validate(sample)
    assert check["valid"]
    assert any("not authenticated" in warning for warning in check["warnings"])


def test_high_risk_review_needs_distinct_people_and_links(sample):
    edge = sample["relations"][3]
    edge["review_status"] = "reviewed"
    edge["reviews"] = [
        {"name": "A", "url": "https://example.org/1"},
        {"name": "A", "url": "https://example.org/2"},
    ]
    sample["evidence"][5]["kind"] = "full_text"
    assert not validate(sample)["valid"]
    edge["reviews"][1]["name"] = "B"
    assert validate(sample)["valid"]


def test_unknown_settings_cannot_support_improvement(sample):
    edge = sample["relations"][0]
    edge["type"] = "improves_bound"
    edge["comparability"] = "comparable"
    assert not validate(sample)["valid"]
    for item in sample["results"]:
        item["settings"] = dict.fromkeys(
            item["settings"], "Explicitly specified for test"
        )
    assert validate(sample)["valid"]


def test_proof_cycle_is_rejected_but_other_relations_may_cycle(sample):
    edge = sample["relations"][0]
    reverse = {
        **edge,
        "id": "reverse",
        "source": edge["target"],
        "target": edge["source"],
        "basis": "editorial_inference",
    }
    sample["relations"].append(reverse)
    assert validate(sample)["valid"]
    edge["type"] = reverse["type"] = "uses_result"
    assert any("cycle" in error for error in validate(sample)["errors"])


@pytest.mark.parametrize("route", [["missing"], ["r-qsp", "r-qsp"]])
def test_broken_reading_routes(sample, route):
    sample["reading_route"] = route
    assert not validate(sample)["valid"]


@pytest.mark.parametrize("value", [None, [], 1, "map", True])
def test_malformed_roots_do_not_crash(value):
    assert not validate(value)["valid"]


def test_duplicate_evidence_and_extra_fields_are_errors(sample):
    sample["results"][0]["evidence"] *= 2
    assert not validate(sample)["valid"]


@pytest.mark.parametrize("text", ["control\x00text", "unpaired\ud800"])
def test_non_exportable_unicode_is_rejected(sample, text):
    sample["title"] = text
    assert not validate(sample)["valid"]
    sample["invented_expert_score"] = 100
    assert not validate(sample)["valid"]
