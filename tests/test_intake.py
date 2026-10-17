import json

import pytest

from research_lineage.cli import main
from research_lineage.core import MapError, load_map
from research_lineage.intake import prepare, start


def test_topic_is_a_research_brief_not_a_hidden_demo(tmp_path):
    text = "请整理quantum signal processing这个方向的发展历史"
    output = start(text, tmp_path)
    draft = load_map(tmp_path / "map.json")
    brief = json.loads((tmp_path / "research-brief.json").read_text(encoding="utf-8"))
    assert output["kind"] == "topic"
    assert draft["question"] == text and draft["works"] == draft["results"] == []
    assert brief["language"] == "zh" and brief["source_budget"] is None
    assert brief["research_plan"]["corpus_limit"] is None
    assert brief["cutoff_origin"] == "run_date"
    assert (
        main(["build", str(tmp_path / "map.json"), "--out", str(tmp_path / "built")])
        == 2
    )
    before = (tmp_path / "map.json").read_bytes()
    with pytest.raises(MapError, match="already"):
        start("different question", tmp_path)
    assert (tmp_path / "map.json").read_bytes() == before


@pytest.mark.parametrize(
    "seed,ids",
    [
        (
            "https://arxiv.org/abs/2406.10377v2",
            {"arxiv": "2406.10377", "version": "v2"},
        ),
        (
            "https://doi.org/10.1103/PhysRevLett.118.010501",
            {"doi": "10.1103/physrevlett.118.010501"},
        ),
    ],
)
def test_paper_identity_and_pinned_version_are_preserved(seed, ids):
    draft, brief = prepare(seed)
    assert brief["kind"] == "paper" and brief["identifiers"] == ids
    assert draft["evidence"] == [] and brief["status"] == "awaiting_host_research"


def test_local_paper_is_not_read_or_uploaded(tmp_path, monkeypatch):
    paper = tmp_path / "private.pdf"
    paper.write_bytes(b"private document")
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda *a, **k: pytest.fail("unexpected network")
    )
    _, brief = prepare(str(paper))
    assert brief["local_document"] and brief["kind"] == "paper"
    assert paper.read_bytes() == b"private document"
    with pytest.raises(MapError, match="does not exist"):
        prepare(str(tmp_path / "missing.pdf"))


def test_bare_title_is_explicitly_unresolved():
    _, brief = prepare("A new quantum algorithm", kind="paper")
    assert brief["identifiers"] == {} and brief["status"] == "awaiting_host_research"


@pytest.mark.parametrize(
    "seed", [" ", "x" * 501, "https://user:secret@example.com/paper"]
)
def test_invalid_seed_is_rejected(seed):
    with pytest.raises(MapError):
        prepare(seed)
