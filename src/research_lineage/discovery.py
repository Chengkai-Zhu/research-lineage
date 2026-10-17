"""Explicit, bounded metadata discovery. Candidates are never research claims."""

import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .core import MapError
from .identity import identifiers

ATOM = "{http://www.w3.org/2005/Atom}"
OPEN = "{http://a9.com/-/spec/opensearch/1.1/}"


def fetch(url):
    request = Request(
        url,
        headers={
            "User-Agent": "LitDelta/0.2 (https://github.com/Chengkai-Zhu/litdelta)"
        },
    )
    with urlopen(request, timeout=15) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Provider response exceeds 2 MB.")
    return raw


def crossref_page(raw):
    message = json.loads(raw)["message"]
    if not isinstance(message, dict) or not isinstance(message.get("items"), list):
        raise ValueError("Crossref response has no items list.")
    return message["items"], message.get("next-cursor"), message.get("total-results")


def arxiv_page(raw):
    root = ET.fromstring(raw)
    if root.tag != ATOM + "feed" or root.find(OPEN + "totalResults") is None:
        raise ValueError("arXiv response is not a paged Atom feed.")
    entries = root.findall(ATOM + "entry")
    return entries, None, int(root.findtext(OPEN + "totalResults"))


def candidate(item, provider):
    if provider == "crossref":
        ids = identifiers(str(item.get("DOI", "")))
        titles = item.get("title")
        if not isinstance(titles, list) or not titles:
            raise ValueError("Crossref title must be a nonempty list of text.")
        title = titles[0]
        if "doi" not in ids or not isinstance(title, str) or not title.strip():
            raise ValueError("Missing DOI or title.")
        return {
            "id": ids["doi"],
            "title": title.strip(),
            "doi": ids["doi"],
            "url": "https://doi.org/" + ids["doi"],
            "access": "metadata",
            "date_parts": item.get("published", {}).get("date-parts"),
            "authors": [
                " ".join(filter(None, (a.get("given"), a.get("family"))))
                for a in item.get("author", [])
            ],
        }
    url = item.findtext(ATOM + "id", "")
    ids = identifiers(url.replace("http://", "https://"))
    title = item.findtext(ATOM + "title", "").strip()
    if "arxiv" not in ids or not title:
        raise ValueError("Missing arXiv identity or title.")
    return {
        "id": ids["arxiv"] + (ids["version"] or ""),
        "title": " ".join(title.split()),
        **ids,
        "url": url.replace("http://", "https://"),
        "access": "abstract",
        "published": item.findtext(ATOM + "published"),
        "updated": item.findtext(ATOM + "updated"),
        "abstract": item.findtext(ATOM + "summary", "").strip(),
        "authors": [a.findtext(ATOM + "name") for a in item.findall(ATOM + "author")],
    }


def discover(
    query,
    provider="crossref",
    limit=12,
    max_requests=3,
    page_size=10,
    transport=fetch,
    pause=time.sleep,
):
    if provider not in ("crossref", "arxiv"):
        raise MapError("Choose provider crossref or arxiv.")
    if not query.strip() or len(query) > 500:
        raise MapError("Discovery query must contain 1–500 characters.")
    if not (1 <= limit <= 200 and 1 <= max_requests <= 10 and 1 <= page_size <= 100):
        raise MapError("Use limit 1–200, max-requests 1–10, and page-size 1–100.")
    items, rejected, requests, failures, seen = [], [], [], [], set()
    cursor, offset, total, exhausted = "*", 0, None, False
    for attempt in range(max_requests):
        count = min(page_size, limit - len(items))
        if provider == "crossref":
            params = {"query.bibliographic": query, "rows": count, "cursor": cursor}
            url = "https://api.crossref.org/works?" + urlencode(params)
        else:
            if attempt:
                pause(3)
            params = {"search_query": query, "start": offset, "max_results": count}
            url = "https://export.arxiv.org/api/query?" + urlencode(params)
        request_log = {
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "offset": offset,
            "requested": count,
        }
        requests.append(request_log)
        try:
            raw = transport(url)
            page, next_cursor, total = (
                crossref_page if provider == "crossref" else arxiv_page
            )(raw)
            request_log.update(status="ok", returned=len(page))
            for index, entry in enumerate(page):
                try:
                    result = candidate(entry, provider)
                    if result["id"] in seen:
                        raise ValueError("Duplicate candidate identity.")
                    if len(items) >= limit:
                        raise ValueError("Candidate cap reached.")
                    seen.add(result["id"])
                    items.append(result)
                except (
                    ValueError,
                    KeyError,
                    TypeError,
                    IndexError,
                    AttributeError,
                ) as exc:
                    rejected.append(
                        {
                            "request": attempt + 1,
                            "index": index,
                            "reason": str(exc),
                            "source_record": entry
                            if provider == "crossref"
                            else ET.tostring(entry, encoding="unicode"),
                        }
                    )
            offset += len(page)
            exhausted = len(page) < count or (
                isinstance(total, int) and offset >= total
            )
            if exhausted or len(items) >= limit:
                break
            if provider == "crossref":
                if not next_cursor or next_cursor == cursor:
                    failures.append(
                        {
                            "request": attempt + 1,
                            "reason": "Provider pagination did not advance.",
                        }
                    )
                    break
                cursor = next_cursor
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            ValueError,
            KeyError,
            TypeError,
            ET.ParseError,
        ) as exc:
            failure = {
                "request": attempt + 1,
                "reason": str(exc),
                "http_status": getattr(exc, "code", None),
            }
            failures.append(failure)
            request_log.update(status="failed", error=failure)
            break
    return {
        "provider": provider,
        "query": query,
        "limit": limit,
        "max_requests": max_requests,
        "candidates": items,
        "rejected": rejected,
        "requests": requests,
        "failures": failures,
        "total_reported": total,
        "truncated": not exhausted,
        "status": "partial" if failures or rejected or not exhausted else "complete",
        "meaning": "Metadata candidates only. No full-text access or semantic relationship is inferred.",
    }
