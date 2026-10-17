from copy import deepcopy

import pytest

from research_lineage.extraction import assess


@pytest.fixture
def candidate():
    return {
        "id": "case",
        "type": "uses_result",
        "claim": "The target uses the cited construction.",
        "basis": "author_explicit",
        "source": {
            "work_id": "paper",
            "version_id": "v2",
            "url": "https://arxiv.org/abs/1706.03762v2",
            "access": "full_text",
        },
        "evidence": {
            "work_id": "paper",
            "version_id": "v2",
            "url": "https://arxiv.org/abs/1706.03762v2",
            "locator": "Section 3",
        },
    }


def test_good_evidence_is_only_a_proposal(candidate):
    result = assess(candidate)
    assert result["decision"] == "propose" and result["review_status"] == "proposed"


@pytest.mark.parametrize(
    "mutation", ["unavailable", "locator", "version", "citation", "units"]
)
def test_inadequate_candidates_abstain(candidate, mutation):
    bad = deepcopy(candidate)
    if mutation == "unavailable":
        bad["source"]["access"] = "unavailable"
    elif mutation == "locator":
        bad["evidence"]["locator"] = ""
    elif mutation == "version":
        bad["evidence"]["version_id"] = "v1"
    elif mutation == "citation":
        bad["basis"] = "citation_only"
    else:
        bad["type"] = "improves_bound"
        bad["comparison"] = {"comparability": "comparable", "left": {}, "right": {}}
    result = assess(bad)
    assert result["decision"] == "abstain" and result["reasons"]
    assert result["review_status"] == "proposed"
