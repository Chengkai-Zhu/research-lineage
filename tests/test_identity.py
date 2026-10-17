import pytest

from research_lineage.core import MapError
from research_lineage.identity import identifiers, reconcile


def test_same_title_does_not_merge_distinct_dois_or_unidentified_works():
    records = [
        {"id": "a", "title": "Same title", "doi": "10.1234/a"},
        {"id": "b", "title": "Same title", "doi": "10.1234/b"},
        {"id": "c", "title": "Same title"},
    ]
    result = reconcile(records)
    assert [g["records"] for g in result["groups"]] == [["a"], ["b"], ["c"]]


def test_pinned_versions_group_but_remain_distinct():
    result = reconcile(
        [
            {"id": "v1", "arxiv": "1706.03762v1"},
            {"id": "v2", "arxiv": "https://arxiv.org/pdf/1706.03762v2.pdf"},
        ]
    )
    assert result["groups"][0]["records"] == ["v1", "v2"]
    assert [i["version"] for i in result["groups"][0]["identifiers"]] == ["v1", "v2"]


def test_conflicting_identifiers_never_auto_merge():
    result = reconcile(
        [
            {"id": "a", "arxiv": "1706.03762v1", "doi": "10.1234/a"},
            {"id": "b", "arxiv": "1706.03762v2", "doi": "10.1234/b"},
        ]
    )
    assert len(result["groups"]) == 2 and result["conflicts"][0]["record"] == "b"
    assert identifiers("https://doi.org/10.1234/ABC") == {"doi": "10.1234/abc"}


def test_separate_version_is_preserved_and_conflicts_are_rejected():
    record = {"id": "paper", "arxiv": "1706.03762", "version": "v2"}
    result = reconcile([record])
    assert result["groups"][0]["identifiers"] == [
        {"arxiv": "1706.03762", "version": "v2"}
    ]
    for changes in ({"arxiv": "1706.03762v1"}, {"version": "2"}, {"version": 2}):
        with pytest.raises(MapError):
            reconcile([{**record, **changes}])
