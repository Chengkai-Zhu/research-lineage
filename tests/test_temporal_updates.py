from copy import deepcopy

import pytest

from research_lineage.temporal import update_proposal


@pytest.mark.parametrize("cutoff", ["20240101", "2024-W01-1"])
def test_equivalent_cutoff_formats_cannot_change_source_availability(sample, cutoff):
    canonical = update_proposal(sample, sample, "2024-01-01")
    assert update_proposal(sample, sample, cutoff) == canonical


def test_late_revision_is_not_backdated_to_first_publication(sample):
    before = deepcopy(sample)
    result = sample["results"][0]
    work = next(w for w in sample["works"] if w["id"] == result["work_id"])
    version = next(v for v in work["versions"] if v["id"] == result["version_id"])
    as_of = work["first_published"]
    version["published"] = "2026-10-16"
    proposal = update_proposal(before, sample, as_of)
    assert result["id"] not in proposal["eligible_result_ids"]
    assert any(r["id"] == result["id"] for r in proposal["excluded_results"])
    assert proposal["historical_reconstruction"] == "unavailable"
    assert before != sample and proposal["proposal_only"] is True


def test_proposal_never_mutates_inputs_or_cascades_critique(sample):
    original = deepcopy(sample)
    proposal = update_proposal(sample, sample, sample["scope"]["cutoff"])
    assert sample == original
    assert len(proposal["eligible_result_ids"]) == len(sample["results"])
    assert proposal["excluded_results"] == []
    assert proposal["changes"]["status"] == "proposal_only"
