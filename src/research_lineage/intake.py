"""Turn one user input into a research brief without inventing researched content."""

import hashlib
import re
from datetime import date
from pathlib import Path

from .contract import safe_url, validate
from .core import MapError, dump, write_text
from .identity import identifiers, seed_kind


def empty_map(question, map_id, cutoff):
    return {
        "schema_version": "1.0",
        "id": map_id,
        "title": question[:180],
        "question": question,
        "scope": {
            "summary": "A selected research history; establish inclusion criteria from the seed.",
            "cutoff": cutoff,
            "coverage": "No sources collected yet.",
            "search_strategy": "Record queries, sources, dates, and failures during research.",
            "exclusions": [],
            "gaps": ["Research has not started."],
        },
        "lanes": [{"id": "main", "label": "Main thread", "color": "teal"}],
        "works": [],
        "results": [],
        "evidence": [],
        "relations": [],
        "reading_route": [],
    }


def prepare(value, kind="auto", language="auto", cutoff=None):
    value = value.strip()
    if not value or len(value) > 500:
        raise MapError(
            "Provide a topic or paper reference between 1 and 500 characters."
        )
    if kind not in ("auto", "topic", "paper") or language not in ("auto", "en", "zh"):
        raise MapError("Use kind auto/topic/paper and language auto/en/zh.")
    kind = seed_kind(value) if kind == "auto" else kind
    language = (
        ("zh" if re.search(r"[\u3400-\u9fff]", value) else "en")
        if language == "auto"
        else language
    )
    if value.startswith(("http:", "https:")) and not safe_url(value):
        raise MapError("Use a paper URL without credentials or unsupported characters.")
    local = value.lower().endswith(".pdf") and not value.startswith(
        ("http://", "https://")
    )
    if local and not Path(value).is_file():
        raise MapError(
            "Local paper does not exist. Supply the PDF path or a public identifier."
        )
    ids = identifiers(value)
    map_id = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:40] or "research"
    map_id += "-" + hashlib.sha256(value.encode()).hexdigest()[:8]
    draft = empty_map(value, map_id, cutoff or date.today().isoformat())
    check = validate(draft)
    if not check["valid"]:
        raise MapError("\n".join(check["errors"]))
    brief = {
        "seed": value,
        "kind": kind,
        "language": language,
        "identifiers": ids,
        "local_document": local,
        "cutoff": draft["scope"]["cutoff"],
        "source_budget": 12,
        "status": "awaiting_host_research",
        "scope": "Trace the seed's central contribution backward to foundations and forward to checked follow-ups."
        if kind == "paper"
        else "Select the central developments, competing approaches, and changes in assumptions.",
        "next_steps": [
            "Resolve seed identity and exact version; a title alone is not a verified paper.",
            "Use host research tools; read a review and primary papers, recording access and locators.",
            "Write a short overview and 3–5 source-linked turning points; keep unreviewed claims proposed.",
            "Validate, build and inspect the output; deliver map.html first, supporting files second.",
        ],
        "privacy": "Local documents stay local. This helper performs no network requests.",
    }
    return draft, brief


def start(value, destination, **options):
    draft, brief = prepare(value, **options)
    folder = Path(destination)
    paths = [folder / name for name in ("map.json", "research-brief.json")]
    if any(p.exists() for p in paths):
        raise MapError(
            "Research folder already has a draft or brief. Choose a new folder."
        )
    for path, data in zip(paths, (draft, brief)):
        write_text(path, dump(data))
    return {
        "created": [str(p) for p in paths],
        "status": brief["status"],
        "kind": brief["kind"],
    }
