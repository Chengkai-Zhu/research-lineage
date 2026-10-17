"""Deterministic SVG and self-contained HTML; no remote assets or graph service."""

import html
import json
import textwrap
from datetime import date
from pathlib import Path

from .contract import validate
from .core import MapError, dump, export_notes, review_report, write_text

ASSETS = Path(__file__).parent / "assets"
OUTPUT_NAMES = ("map.json", "map.html", "map.svg", "review.md")
PALETTE = {
    "teal": "#147d70",
    "blue": "#426dad",
    "amber": "#ad742b",
    "rose": "#b35568",
    "violet": "#7a62aa",
}
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
    works = {work["id"]: work for work in data["works"]}
    dates = {
        result["id"]: date.fromisoformat(
            works[result["work_id"]]["first_published"]
        ).toordinal()
        for result in data["results"]
    }
    low, high = min(dates.values()), max(dates.values())
    positions, bands = {}, []
    y = 75
    for lane in data["lanes"]:
        rows = []
        for result in sorted(
            (result for result in data["results"] if result["lane"] == lane["id"]),
            key=lambda item: (dates[item["id"]], item["id"]),
        ):
            x = 150 + (dates[result["id"]] - low) / max(high - low, 1) * 930
            row = next(
                (index for index, last in enumerate(rows) if x - last > 218), len(rows)
            )
            if row == len(rows):
                rows.append(x)
            else:
                rows[row] = x
            positions[result["id"]] = (round(x, 2), y + 32 + row * 96)
        height = max(len(rows), 1) * 96 + 30
        bands.append((lane, y, height))
        y += height
    return positions, bands, y + 50, low, high


def render_svg(data):
    positions, bands, height, low, high = layout(data)
    works = {work["id"]: work for work in data["works"]}
    lanes = {lane["id"]: lane for lane in data["lanes"]}
    esc = html.escape
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 {height}" role="group" aria-label="Interactive research lineage map" id="lineage-map">',
        f"<title>{esc(data['title'])}</title>",
        "<desc>Publication chronology, not an as-of reconstruction. Arrows connect source and target results; the target performs the relationship. Results in one paper need not be chronologically ordered. Dashed edges await review.</desc>",
        '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="#93a49e"/></marker></defs>',
        "<style>text{font-family:Arial,sans-serif}.node{cursor:pointer}.node rect{fill:#fff;stroke:#d6dfda;stroke-width:1.2}.node:hover rect,.node:focus rect{stroke:#147d70;stroke-width:2}.node .label{fill:#243a32;font-weight:600}.node .meta{fill:#6c7b75}.relation{cursor:pointer}.edge{fill:none;stroke:#93a49e;stroke-width:1.7}.pending .edge{stroke-dasharray:5 4}.relation:focus .edge,.relation:hover .edge{stroke:#147d70;stroke-width:3}.lane-label{fill:#78877f;font-weight:600;font-size:11px;letter-spacing:1px}.year{fill:#7b8881;font-size:12px}.band{fill:#f5f8f5}.hidden{display:none}.dim{opacity:.15}.selected rect{stroke:#147d70;stroke-width:2.5;fill:#f2faf6}.selected .edge{stroke:#147d70;stroke-width:3}.route-node rect{stroke:#147d70;stroke-width:2}</style>",
        '<rect width="1240" height="100%" fill="#fcfdfb"/>',
    ]
    min_year, max_year = date.fromordinal(low).year, date.fromordinal(high).year
    for year in range(min_year, max_year + 1, max(1, (max_year - min_year + 11) // 12)):
        ordinal = max(low, min(high, date(year, 7, 1).toordinal()))
        x = 150 + (ordinal - low) / max(high - low, 1) * 930
        svg.append(
            f'<text class="year" x="{x:.2f}" y="40" text-anchor="middle">{year}</text>'
        )
    for lane, y, band_height in bands:
        color = PALETTE[lane["color"]]
        svg.append(
            f'<rect class="band" x="20" y="{y}" width="1200" height="{band_height - 8}" rx="12"/>'
        )
        svg.append(
            f'<circle cx="40" cy="{y + 22}" r="3" fill="{color}"/><text class="lane-label" x="50" y="{y + 26}">{esc(lane["label"].upper())}</text>'
        )
    for edge in data["relations"]:
        x1, y1 = positions[edge["source"]]
        x2, y2 = positions[edge["target"]]
        start, end = x1 + 85, x2 - 85
        middle = (start + end) / 2
        result_labels = {result["id"]: result["label"] for result in data["results"]}
        description = f"{result_labels[edge['target']]} {LABELS[edge['type']]} {result_labels[edge['source']]}"
        status = "pending" if edge["review_status"] == "proposed" else "recorded"
        path = f"M {start} {y1 + 26} C {middle} {y1 + 26}, {middle} {y2 + 26}, {end} {y2 + 26}"
        svg.append(
            f'<g class="relation {status}" id="relation-{edge["id"]}" data-id="{edge["id"]}" role="button" tabindex="0" aria-label="{esc(description, quote=True)}"><title>{esc(description)}. {esc(edge["summary"])}</title><path d="{path}" fill="none" stroke="transparent" stroke-width="16"/><path class="edge" d="{path}" marker-end="url(#arrow)"/></g>'
        )
    for result in data["results"]:
        x, y = positions[result["id"]]
        work = works[result["work_id"]]
        color = PALETTE[lanes[result["lane"]]["color"]]
        title_lines = textwrap.wrap(result["label"], 23)[:2]
        svg.append(
            f'<g class="node" id="result-{result["id"]}" data-id="{result["id"]}" transform="translate({x - 88},{y - 5})" tabindex="0" role="button" aria-label="{esc(result["label"], quote=True)}"><title>{esc(result["summary"])}</title><rect width="186" height="78" rx="10"/><rect x="0" y="17" width="3" height="39" rx="1.5" style="fill:{color};stroke:none"/>'
        )
        for index, line in enumerate(title_lines):
            svg.append(
                f'<text class="label" x="15" y="{25 + index * 17}" font-size="14">{esc(line)}</text>'
            )
        svg.append(
            f'<text class="meta" x="15" y="64" font-size="10.5">{work["first_published"][:4]} · {esc(result["kind"])} · {"draft" if result["review_status"] == "proposed" else "review recorded"}</text></g>'
        )
    svg.append(
        f'<text x="30" y="{height - 14}" class="year">LITDELTA · Cutoff {data["scope"]["cutoff"]} · {sum(result["review_status"] == "proposed" for result in data["results"])} draft results · Consult the scope and evidence before reuse</text></svg>'
    )
    return "".join(svg)


def export_svg(data):
    chart = render_svg(data)
    height = layout(data)[2]
    esc = html.escape
    lines = export_notes(data)
    wrapped = [part for line in lines for part in textwrap.wrap(line, 145)]
    extra = "".join(
        f'<text x="30" y="{height + 30 + i * 18}" fill="#43594d" font-size="12">{esc(line)}</text>'
        for i, line in enumerate(wrapped)
    )
    return chart.replace(
        f'viewBox="0 0 1240 {height}"',
        f'viewBox="0 0 1240 {height + 60 + len(wrapped) * 18}"',
    ).replace(
        "</svg>",
        f'<metadata id="research-lineage-data">{esc(dump(data))}</metadata>'
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
        "CSS": (ASSETS / "viewer.css").read_text(encoding="utf-8"),
        "JS": (ASSETS / "identity-view.js").read_text(encoding="utf-8")
        + "\n"
        + (ASSETS / "viewer.js").read_text(encoding="utf-8"),
        "DATA": serialized,
        "SVG": render_svg(data),
        "STORY": render_story(data),
        "COMPARISONS": render_comparison_cards(data),
        "EXPORT_NOTES": json.dumps(export_notes(data), ensure_ascii=False)
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
