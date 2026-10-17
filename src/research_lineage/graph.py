"""Dependency-free Aurora graph for static exports and the offline viewer."""

import html
import re
import unicodedata
from datetime import date

CARD_WIDTH = 240
CARD_HEIGHT = 122
PALETTE = {
    "teal": "#40ad9c",
    "blue": "#6e9edb",
    "amber": "#c89d52",
    "rose": "#d4859b",
    "violet": "#a28bd1",
}


def text_width(text):
    return sum(
        0
        if unicodedata.combining(char)
        else 2
        if unicodedata.east_asian_width(char) in {"W", "F"}
        else 1
        for char in text
    )


def wrap_label(text, width, max_lines=None):
    """Wrap CJK and long tokens conservatively; keep full text in accessible titles."""
    rows, line = [], ""
    for token in re.findall(r"\S+\s*|\s+", text):
        if line and text_width(line + token.rstrip()) > width:
            rows.append(line.rstrip())
            line = ""
        for char in token:
            if text_width(line + char) > width:
                rows.append(line.rstrip())
                line = ""
            if line or not char.isspace():
                line += char
    if line.strip():
        rows.append(line.rstrip())
    if max_lines and len(rows) > max_lines:
        rows = rows[:max_lines]
        while text_width(rows[-1] + "…") > width:
            rows[-1] = rows[-1][:-1]
        rows[-1] = rows[-1].rstrip() + "…"
    return rows


def timeline_layout(data):
    works = {work["id"]: work for work in data["works"]}
    ordered = sorted(
        data["results"], key=lambda r: (works[r["work_id"]]["first_published"], r["id"])
    )
    dates = [
        date.fromisoformat(works[r["work_id"]]["first_published"]) for r in ordered
    ]
    columns = min(4, len(ordered))
    positions, periods = {}, []
    for column in range(columns):
        items = ordered[
            column * len(ordered) // columns : (column + 1) * len(ordered) // columns
        ]
        x = 46 + column * 302
        years = [works[r["work_id"]]["first_published"][:4] for r in items]
        periods.append(
            (
                years[0] if years[0] == years[-1] else years[0] + "–" + years[-1],
                x,
                len(items),
            )
        )
        for row, result in enumerate(items):
            positions[result["id"]] = (x, 90 + row * 162)
    height = 150 + max((p[2] for p in periods), default=0) * 162
    return (positions, periods, height, min(dates).toordinal(), max(dates).toordinal())


def connection_path(start, end, width=CARD_WIDTH, height=CARD_HEIGHT):
    x1, y1 = start
    x2, y2 = end
    y1 += height / 2
    y2 += height / 2
    if x1 == x2:
        x = x1 + width
        return f"M{x} {y1} C{x + 32} {y1}, {x + 32} {y2}, {x} {y2}"
    if x1 > x2:
        x1, x2 = x1, x2 + width
    else:
        x1 += width
    middle = (x1 + x2) / 2
    return f"M{x1} {y1} C{middle} {y1}, {middle} {y2}, {x2} {y2}"


def render_graph(data):
    from .render import LABELS

    positions, periods, height, _, _ = timeline_layout(data)
    works = {work["id"]: work for work in data["works"]}
    lanes = {lane["id"]: lane for lane in data["lanes"]}
    results = {result["id"]: result for result in data["results"]}
    esc = html.escape
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 {height}" role="group" aria-label="Interactive research lineage map" id="lineage-map">',
        f"<title>{esc(data['title'])}</title>",
        "<desc>Results grouped by first publication date. Spacing is schematic, not a linear time scale or an as-of reconstruction. Arrows connect source and target results; the target performs the relationship. Dashed edges await review.</desc>",
        '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="context-stroke"/></marker></defs>',
        '<style>text{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.graph-paper{fill:#f4f8fa}.node{cursor:pointer}.node-card{fill:#fff;stroke:#d7e4e9;stroke-width:1.2}.node .label{fill:#18313f;font-weight:550;font-size:14px}.node .meta{fill:#617b89;font-size:10px}.node:focus .node-card,.node:hover .node-card,.selected .node-card{stroke:#008c80;stroke-width:2}.relation{cursor:pointer}.edge{fill:none;stroke:#99b9be;stroke-width:1.5}.pending .edge{stroke-dasharray:5 4}.relation:hover .edge,.relation:focus .edge,.relation.selected .edge{stroke:#008c80;stroke-width:2.5}.period-label{fill:#5f7985;font-size:12px}.period-line{stroke:#dae5e9;stroke-width:1}.graph-note{fill:#5f7985;font-size:11px}.hidden{display:none}.identity-muted{opacity:.28}</style>',
        '<rect class="graph-paper" width="1240" height="100%"/>',
        '<g class="periods" aria-hidden="true">',
    ]
    for label, x, _ in periods:
        svg.append(
            f'<text class="period-label" x="{x}" y="40">{label}</text>'
            f'<path class="period-line" d="M{x} 57 H{x + CARD_WIDTH}"/>'
        )
    svg.append("</g>")
    for edge in data["relations"]:
        description = (
            f"{results[edge['target']]['label']} "
            f"{LABELS[edge['type']]} "
            f"{results[edge['source']]['label']}"
        )
        status = "pending" if edge["review_status"] == "proposed" else "recorded"
        path = connection_path(positions[edge["source"]], positions[edge["target"]])
        svg.append(
            f'<g class="relation {status}" id="relation-{edge["id"]}" data-id="{edge["id"]}" role="button" tabindex="0" aria-label="{esc(description, quote=True)}"><title>{esc(description)}. {esc(edge["summary"])}</title><path class="edge-hit" d="{path}" fill="none" stroke="transparent" stroke-width="14"/><path class="edge" d="{path}" marker-end="url(#arrow)"/></g>'
        )
    for result in data["results"]:
        x, y = positions[result["id"]]
        work = works[result["work_id"]]
        color = PALETTE[lanes[result["lane"]]["color"]]
        status = (
            "Proposed" if result["review_status"] == "proposed" else "Review recorded"
        )
        svg.append(
            f'<g class="node" id="result-{result["id"]}" data-id="{result["id"]}" transform="translate({x},{y})" tabindex="0" role="button" aria-label="{esc(result["label"], quote=True)}"><title>{esc(result["label"])} — {esc(result["summary"])}</title><rect class="node-card" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="12"/><rect class="thread-mark" x="16" y="17" width="6" height="6" rx="3" style="fill:{color};stroke:none"/><text class="meta node-year" x="29" y="24">{work["first_published"][:4]}</text><text class="label" x="16" y="48">'
        )
        for index, line in enumerate(wrap_label(result["label"], 28, 3)):
            svg.append(
                f'<tspan x="16" dy="{0 if index == 0 else 18}">{esc(line)}</tspan>'
            )
        svg.append(
            f'</text><text class="meta node-status" x="16" y="105">{status}</text></g>'
        )
    svg.append(
        f'<text x="30" y="{height - 20}" class="graph-note">LITDELTA · Cutoff {data["scope"]["cutoff"]} · {sum(r["review_status"] == "proposed" for r in data["results"])} proposed results · Consult the scope and evidence before reuse</text></svg>'
    )
    return "".join(svg)
