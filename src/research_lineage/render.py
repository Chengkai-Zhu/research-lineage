"""Deterministic SVG and self-contained HTML; no remote assets or graph service."""

import html
import json
from pathlib import Path

from .contract import validate
from .core import MapError, dump, export_notes, review_report, write_text

ASSETS = Path(__file__).parent / "assets"
OUTPUT_NAMES = ("map.json", "map.html", "map.svg", "review.md")
LABELS = {
    "generalizes": "generalizes",
    "uses_result": "uses result",
    "improves_bound": "improves bound",
    "simplifies": "simplifies",
    "surveys": "surveys",
    "critiques": "critiques conditions",
    "refutes_claim": "refutes a claim",
    "addresses": "addresses a question",
    "independent_parallel": "parallel development",
    "empirically_checks": "experimentally checks",
    "cites": "cites",
}


def layout(data):
    """Chronological columns with equal visual weight, not a linear time scale."""
    from .graph import timeline_layout

    return timeline_layout(data)


def render_svg(data):
    from .graph import render_graph

    return render_graph(data)


def export_lines(data):
    from .graph import wrap_label

    return [part for line in export_notes(data) for part in wrap_label(line, 185)]


def export_svg(data):
    chart = render_svg(data)
    height = layout(data)[2]
    wrapped = export_lines(data)
    extra = "".join(
        f'<text x="30" y="{height + 30 + i * 18}" fill="#43594d" font-size="12">{html.escape(line)}</text>'
        for i, line in enumerate(wrapped)
    )
    return chart.replace(
        f'viewBox="0 0 1240 {height}"',
        f'viewBox="0 0 1240 {height + 60 + len(wrapped) * 18}"',
    ).replace(
        "</svg>",
        f'<metadata id="research-lineage-data">{html.escape(dump(data))}</metadata>'
        + extra
        + "</svg>",
    )


def render_story(data):
    """Source-linked orientation, never invented from a citation graph."""
    results = {r["id"]: r for r in data["results"]}
    works = {w["id"]: w for w in data["works"]}
    narrative = data.get("narrative")
    if narrative:
        points = narrative["turning_points"]
    else:
        route = data["reading_route"] or list(results)
        chosen = list(dict.fromkeys((route[0], route[len(route) // 2], route[-1])))
        points = [
            {
                "title": results[r]["label"],
                "summary": results[r]["summary"],
                "result_ids": [r],
            }
            for r in chosen
        ]
    cards = []
    for index, point in enumerate(points):
        years = sorted(
            {
                works[results[r]["work_id"]]["first_published"][:4]
                for r in point["result_ids"]
            }
        )
        dates = years[0] if len(years) == 1 else years[0] + "–" + years[-1]
        sources = "".join(
            f'<button class="story-source" data-result="{ref}">{html.escape(results[ref]["label"])} <span aria-hidden="true">↗</span></button>'
            for ref in point["result_ids"]
        )
        cards.append(
            f'<article class="story-card"><div class="story-date"><span>{index + 1:02}</span>{dates}</div>'
            f"<h3>{html.escape(point['title'])}</h3><p>{html.escape(point['summary'])}</p>"
            f'<div class="story-sources">{sources}</div></article>'
        )
    heading = (
        ("Selected results" if len(works) == 1 else "The turning points")
        if narrative
        else "A few places to begin"
    )
    note = (
        "A selected account, with the evidence one step away."
        if narrative
        else "Selected from the reading route; no authored historical overview is recorded."
    )
    return (
        f'<div class="story-heading"><h2>{heading}</h2><p>{note}</p></div><div class="story-grid">'
        + "".join(cards)
        + "</div>"
    )


def render_html(data):
    serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    serialized = (
        serialized.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    template = (ASSETS / "viewer.html").read_text(encoding="utf-8")
    values = {
        "TITLE": html.escape(data["title"]),
        "CSS": (ASSETS / "viewer.css").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "aurora.css").read_text(encoding="utf-8"),
        "JS": (ASSETS / "view-state.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "note-format.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "comparison-brief.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "reading-workspace.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "reading-controls.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "identity-view.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "aurora-graph.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "viewer.js").read_text(encoding="utf-8"),
        "DATA": serialized,
        "SVG": render_svg(data),
        "STORY": render_story(data),
        "COMPARISONS": render_comparison_cards(data),
        "EXPORT_NOTES": json.dumps(export_lines(data), ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026"),
    }
    # One pass prevents user text that resembles a template token being interpreted.
    import re

    return re.sub(
        r"@@(TITLE|CSS|JS|DATA|SVG|EXPORT_NOTES|STORY|COMPARISONS)@@",
        lambda match: values[match[1]],
        template,
    )


def render_comparison_cards(data):
    records = data.get("comparisons", [])
    if not records:
        return ""
    esc = html.escape
    cards = []
    for record in records[:5]:
        cards.append(
            f'<article class="comparison-card"><h3>{esc(record["question"])}</h3>'
            f'<p>{esc(record["summary"])}</p><p class="comparison-regime"><strong>When it applies:</strong> {esc(record["regime"])}</p>'
            f'<button class="button small comparison-open" data-comparison="{record["id"]}">Why? Check the conditions →</button></article>'
        )
    return (
        '<section class="comparison-overview" aria-labelledby="comparison-heading"><div class="story-heading">'
        '<h2 id="comparison-heading">What actually changed?</h2><p>Gains, conditions, and the comparisons that do not hold.</p></div>'
        '<div class="comparison-grid">' + "".join(cards) + "</div>"
        '<button id="all-comparisons" class="inline-button">Browse all comparisons →</button></section>'
    )


def build(data, destination, force=False):
    check = validate(data)
    if not check["valid"]:
        raise MapError("\n".join(check["errors"]))
    if not data["results"]:
        raise MapError(
            "This draft has no results. Add evidence-linked results before building."
        )
    destination = Path(destination)
    names = OUTPUT_NAMES
    if not force and any((destination / name).exists() for name in names):
        raise MapError(
            "Output already exists; choose a new folder or use --force to replace generated files."
        )
    outputs = (dump(data), render_html(data), export_svg(data), review_report(data))
    for name, content in zip(names, outputs):
        write_text(destination / name, content)
    return [str(destination / name) for name in names]
