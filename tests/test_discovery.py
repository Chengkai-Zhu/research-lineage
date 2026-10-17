import json
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

import pytest

from research_lineage.discovery import discover
from research_lineage.identity import reconcile


def page(items, cursor="page-2", total=20):
    return json.dumps(
        {"message": {"items": items, "next-cursor": cursor, "total-results": total}}
    ).encode()


def work(n):
    return {
        "DOI": f"10.1234/paper{n}",
        "title": [f"Paper {n}"],
        "author": [{"family": "Researcher"}],
    }


def test_two_pages_stop_at_cap_with_auditable_queries():
    replies = iter(
        [page([work(1), {"title": ["no DOI"]}]), page([work(2), work(3)], "page-3")]
    )
    result = discover(
        "quantum signal processing",
        limit=3,
        max_requests=5,
        page_size=2,
        transport=lambda url: next(replies),
    )
    assert [c["id"] for c in result["candidates"]] == [
        "10.1234/paper1",
        "10.1234/paper2",
        "10.1234/paper3",
    ]
    assert len(result["requests"]) == 2 and result["truncated"] is True
    assert result["rejected"][0]["index"] == 1
    assert result["rejected"][0]["source_record"] == {"title": ["no DOI"]}
    assert parse_qs(urlsplit(result["requests"][1]["url"]).query)["cursor"] == [
        "page-2"
    ]
    assert all(r["timestamp"] and r["status"] == "ok" for r in result["requests"])
    assert all(c["access"] == "metadata" for c in result["candidates"])


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("timed out"),
        HTTPError("https://api.crossref.org", 429, "limited", {}, None),
        b"not json",
    ],
)
def test_failure_keeps_earlier_results_and_does_not_retry(failure):
    count = 0

    def transport(url):
        nonlocal count
        count += 1
        if count == 1:
            return page([work(1)])
        if isinstance(failure, bytes):
            return failure
        raise failure

    result = discover("example", limit=4, page_size=1, transport=transport)
    assert count == 2 and len(result["candidates"]) == 1
    assert result["status"] == "partial" and len(result["failures"]) == 1
    assert result["requests"][-1]["status"] == "failed"


def test_arxiv_version_and_abstract_are_not_full_text():
    raw = b"""<feed xmlns="http://www.w3.org/2005/Atom" xmlns:o="http://a9.com/-/spec/opensearch/1.1/">
    <o:totalResults>1</o:totalResults><entry><id>http://arxiv.org/abs/1706.03762v2</id>
    <title>Attention Is All You Need</title><published>2017-06-12T00:00:00Z</published>
    <updated>2017-06-19T00:00:00Z</updated><summary>Abstract only</summary><author><name>A Researcher</name></author></entry></feed>"""
    result = discover("attention", "arxiv", transport=lambda url: raw)
    assert result["status"] == "complete" and result["truncated"] is False
    assert result["candidates"][0]["version"] == "v2"
    assert result["candidates"][0]["access"] == "abstract"
    assert (
        reconcile(result["candidates"])["groups"][0]["identifiers"][0]["version"]
        == "v2"
    )


@pytest.mark.parametrize("title", ["A malformed title", [], None, [12]])
def test_malformed_title_is_rejected_without_losing_its_source_identity(title):
    malformed = {"DOI": "10.1234/malformed", "title": title}
    result = discover(
        "example", transport=lambda url: page([work(1), malformed], total=2)
    )
    assert [item["title"] for item in result["candidates"]] == ["Paper 1"]
    assert result["status"] == "partial"
    assert result["rejected"][0]["source_record"] == malformed
    assert "title" in result["rejected"][0]["reason"]


def test_request_cap_and_duplicate_pages_are_bounded():
    result = discover(
        "example",
        limit=10,
        max_requests=2,
        page_size=1,
        transport=lambda url: page([work(1)], cursor="unchanged"),
    )
    assert len(result["requests"]) == 2 and len(result["candidates"]) == 1
    assert result["rejected"] and result["failures"]
