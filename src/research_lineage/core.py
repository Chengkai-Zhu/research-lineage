"""Local IO, comparison, change proposals, and inspectable review reports."""

import json
from pathlib import Path

from .contract import validate

MAX_BYTES = 5_000_000


class MapError(ValueError):
    pass


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise MapError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_map(path):
    path = Path(path)
    with path.open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise MapError("Map exceeds the 5 MB input limit.")
    try:
        data = json.loads(
            raw.decode("utf-8-sig"),
            object_pairs_hook=_unique,
            parse_constant=lambda token: (_ for _ in ()).throw(
                MapError(f"Invalid JSON constant: {token}")
            ),
        )
        check = validate(data)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise MapError(f"Cannot read map: {exc}") from exc
    if not check["valid"]:
        raise MapError("\n".join(check["errors"]))
    return data


def dump(data):
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def compare(data, left, right):
    results = {result["id"]: result for result in data["results"]}
    if left not in results or right not in results:
        raise MapError("Comparison needs two existing result IDs.")
    rows = []
    for key in ("input", "assumptions", "cost", "error"):
        a, b = results[left]["settings"][key], results[right]["settings"][key]
        rows.append(
            {
                "field": key,
                "left": a,
                "right": b,
                "status": "unknown"
                if a is None or b is None
                else "same_reported"
                if a == b
                else "different",
            }
        )
    return {
        "left": left,
        "right": right,
        "fields": rows,
        "verdict": "Comparability is not established by text matching. Check the source assumptions and cost units.",
    }


def diff_maps(before, after):
    if before["id"] != after["id"]:
        raise MapError("Map IDs differ; compare revisions of the same map.")
    changes = {}
    for collection in ("lanes", "works", "results", "evidence", "relations"):
        a, b = (
            {item["id"]: item for item in source[collection]}
            for source in (before, after)
        )
        changes[collection] = {
            "added": [b[key] for key in sorted(b.keys() - a.keys())],
            "removed": [a[key] for key in sorted(a.keys() - b.keys())],
            "changed": [
                {
                    "id": key,
                    "fields": {
                        field: {"before": a[key].get(field), "after": b[key].get(field)}
                        for field in sorted(a[key].keys() | b[key].keys())
                        if a[key].get(field) != b[key].get(field)
                    },
                }
                for key in sorted(a.keys() & b.keys())
                if a[key] != b[key]
            ],
        }
    metadata = {
        key: {"before": before[key], "after": after[key]}
        for key in ("title", "question", "scope", "reading_route")
        if before[key] != after[key]
    }
    return {
        "map_id": before["id"],
        "status": "proposal_only",
        "metadata": metadata,
        "changes": changes,
    }


def review_report(data):
    check = validate(data)
    lines = [
        f"# {data['title']} — Review report",
        "",
        data["question"],
        "",
        f"Scope cutoff: {data['scope']['cutoff']}. Chronology is not a historical snapshot.",
        "",
        "Structural validation does not certify scientific correctness or reviewer identity.",
        "",
        "## Coverage",
        "",
        data["scope"]["coverage"],
        "",
        "## Known gaps",
        "",
    ]
    lines += [f"- {gap}" for gap in data["scope"]["gaps"]]
    lines += ["", "## Review queue", ""]
    for item in data["results"] + data["relations"]:
        lines += [
            f"- `{item['id']}`: {item['review_status']} — {item.get('summary', '')}"
        ]
    lines += ["", "## Evidence", ""]
    for item in data["evidence"]:
        lines += [
            f"- `{item['id']}`: {item['url']} — {item['locator']} ({item['kind']}, {item['version_id']}; checked {item['checked']}). {item['summary']}"
        ]
    lines += ["", "## Diagnostics", ""] + [
        f"- {warning}" for warning in check["warnings"]
    ]
    return "\n".join(lines) + "\n"
