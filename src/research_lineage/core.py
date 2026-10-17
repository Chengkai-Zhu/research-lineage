"""Local IO, comparison, change proposals, and inspectable review reports."""

import json
import html
import re
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


def same_file(left, right):
    """Account for path aliases and existing hard links before writing output."""
    left, right = Path(left), Path(right)
    return left.resolve() == right.resolve() or (
        left.exists() and right.exists() and left.samefile(right)
    )


def compare(data, left, right, comparison_id=None):
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
    choices = [
        record
        for record in data.get("comparisons", [])
        if (record["left"], record["right"]) == (left, right)
    ]
    chosen = None
    if comparison_id:
        chosen = next(
            (record for record in choices if record["id"] == comparison_id), None
        )
        if chosen is None:
            raise MapError(
                "Comparison ID does not match these ordered result endpoints."
            )
    elif len(choices) == 1:
        chosen = choices[0]
    return {
        "left": left,
        "right": right,
        "fields": rows,
        "assessment": chosen["assessment"] if chosen else "unknown",
        "comparison": chosen,
        "choices": [
            {
                "id": record["id"],
                "question": record["question"],
                "regime": record["regime"],
            }
            for record in choices
        ],
        "selection_required": len(choices) > 1 and chosen is None,
        "verdict": chosen["rationale"]
        if chosen
        else "Comparability is not established by text matching. Check the source assumptions and cost units.",
    }


def diff_maps(before, after):
    if before["id"] != after["id"]:
        raise MapError("Map IDs differ; compare revisions of the same map.")
    changes = {}
    for collection in (
        "lanes",
        "works",
        "results",
        "evidence",
        "relations",
        "comparisons",
    ):
        a, b = (
            {item["id"]: item for item in source.get(collection, [])}
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
            "order": {
                "before": [item["id"] for item in before.get(collection, [])],
                "after": [item["id"] for item in after.get(collection, [])],
            }
            if list(a) != list(b)
            else None,
        }
    metadata = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in (
            "schema_version",
            "title",
            "question",
            "scope",
            "reading_route",
            "narrative",
        )
        if before.get(key) != after.get(key)
    }
    return {
        "map_id": before["id"],
        "status": "proposal_only",
        "metadata": metadata,
        "changes": changes,
    }


def review_sections(data):
    """Shared readable provenance for Markdown, CLI SVG, and browser SVG."""
    sections = [
        (
            "Scope",
            [
                data["question"],
                data["scope"]["summary"],
                f"Scope cutoff: {data['scope']['cutoff']}. Chronology is not a historical snapshot.",
                "Structural validation does not certify scientific correctness or reviewer identity.",
            ],
        ),
        ("Coverage", [data["scope"]["coverage"]]),
        ("Search strategy", [data["scope"]["search_strategy"]]),
        ("Exclusions", data["scope"]["exclusions"] or ["None recorded."]),
        ("Known gaps", data["scope"]["gaps"]),
    ]
    if "narrative" in data:
        sections.append(("Reading overview", [data["narrative"]["overview"]]))
        sections.append(
            (
                "Selected turning points",
                [
                    f"{point['title']}: {point['summary']} | Results: {', '.join(point['result_ids'])}"
                    for point in data["narrative"]["turning_points"]
                ],
            )
        )
    sources = []
    for work in data["works"]:
        sources.append(
            f"{work['id']}: {work['title']} — {', '.join(work['authors'])}. First published {work['first_published']}."
        )
        for version in work["versions"]:
            sources.append(
                f"{version['id']}: {version['label']} — {version['published']} — {version['url']}"
            )
        for group in work.get("groups", []):
            sources.append(
                f"Recorded team {group['id']}: {group['label']} | {group['version_id']} | Evidence: {', '.join(group['evidence'])}"
            )
    sections.append(("Source index", sources))
    queue = []
    for item in data["results"] + data["relations"]:
        queue.append(f"{item['id']}: {item['review_status']} — {item['summary']}")
        if "work_id" in item:
            queue.append(
                f"{item['label']} | {item['work_id']} | {item['version_id']} | {item['kind']} | lane {item['lane']}"
            )
            queue.extend(
                f"{key}: {value if value is not None else 'Not extracted'}"
                for key, value in item["settings"].items()
            )
        else:
            queue.append(
                f"{item['target']} {item['type']} {item['source']} | basis: {item['basis']} | "
                + (
                    f"legacy comparability: {item['comparability']}"
                    if "comparability" in item
                    else f"comparison: {item['comparison_id'] or 'not assessed'}"
                )
            )
        queue.append("Evidence: " + ", ".join(item["evidence"]))
        queue.extend(
            f"Recorded review (identity not authenticated): {review['name']} — {review['url']}"
            for review in item["reviews"]
        )
    sections.append(("Review queue", queue))
    comparisons = []
    for record in data.get("comparisons", []):
        comparisons.extend(
            [
                f"{record['id']}: {record['left']} → {record['right']} | {record['assessment']} | {record['review_status']} | basis: {record['basis']}",
                f"Question: {record['question']}",
                f"What changed: {record['summary']}",
                f"When it applies: {record['regime']}",
                f"Tradeoffs/gaps: {record['tradeoffs']}",
                f"Assessment reason: {record['rationale']} | Outcome: {record['outcome']}",
                f"Improvement statement: {record['improvement'] or 'None asserted'}",
                "Evidence: " + ", ".join(record["evidence"]),
            ]
        )
        comparisons.extend(
            f"{row['dimension']}: {row['left']} [{row['left_unit']}] vs {row['right']} [{row['right_unit']}] — {row['reason']} | Left evidence: {', '.join(row['left_evidence'])} | Right evidence: {', '.join(row['right_evidence'])}"
            for row in record["conditions"]
        )
        if record["conversion"]:
            comparisons.append(
                "Conversion: " + json.dumps(record["conversion"], ensure_ascii=False)
            )
        comparisons.extend(
            f"Recorded review (identity not authenticated): {review['name']} — {review['url']}"
            for review in record["reviews"]
        )
    if comparisons:
        sections.append(("Result comparisons", comparisons))
    sections.append(
        (
            "Evidence",
            [
                f"{item['id']}: {item['url']} — {item['locator']} ({item['kind']}, {item['work_id']}, {item['version_id']}; checked {item['checked']}). {item['summary']}"
                for item in data["evidence"]
            ],
        )
    )
    sections.append(
        ("Reading route", [" → ".join(data["reading_route"]) or "No route recorded."])
    )
    anchors = []
    for item in data["evidence"]:
        if "quote" in item:
            anchors.append(
                f"{item['id']}: Source excerpt: {item['quote']['exact']} | Prefix: {item['quote']['prefix']} | Suffix: {item['quote']['suffix']}"
            )
        if "anchor_check" in item:
            anchors.append(
                "Recorded local check (not reproduced): "
                + json.dumps(item["anchor_check"], ensure_ascii=False)
            )
    if anchors:
        sections.append(("Source excerpts and local checks", anchors))
    sections.append(
        ("Diagnostics", validate(data)["warnings"] or ["No structural warnings."])
    )
    return sections


def export_notes(data):
    return [
        data["title"],
        *[
            line
            for heading, lines in review_sections(data)
            for line in (heading.upper(), *lines)
        ],
    ]


def _markdown_text(value):
    # Input remains literal text even in Markdown renderers that allow raw HTML.
    escaped = html.escape(value, quote=False)
    return re.sub(r"([\\`*_{}\[\]#!|])", r"\\\1", escaped)


def review_report(data):
    lines = [f"# {_markdown_text(data['title'])} — Review report", ""]
    for heading, content in review_sections(data):
        lines += [f"## {heading}", ""]
        for line in content:
            lines.extend([_markdown_text(line), ""])
    return "\n".join(lines) + "\n"
