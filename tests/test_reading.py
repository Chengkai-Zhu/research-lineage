import json
import re
from copy import deepcopy
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from research_lineage.contract import validate
from research_lineage.core import diff_maps, review_report
from research_lineage.render import export_svg, render_html


def test_narrative_references_must_resolve(sample):
    sample["narrative"]["turning_points"][0]["result_ids"] = ["missing"]
    assert not validate(sample)["valid"]
    sample["narrative"]["turning_points"][0]["result_ids"] = [
        sample["results"][0]["id"]
    ] * 2
    assert not validate(sample)["valid"]


def test_narrative_survives_all_exports_and_revision_proposal(sample):
    html = render_html(sample)
    report = review_report(sample)
    svg = ET.fromstring(export_svg(sample))
    embedded = svg.find("{http://www.w3.org/2000/svg}metadata").text
    assert json.loads(embedded) == sample
    assert sample["narrative"]["overview"] in unescape(html)
    assert sample["narrative"]["overview"] in report
    before = deepcopy(sample)
    sample["narrative"]["overview"] = "A revised orientation."
    diff = diff_maps(before, sample)
    assert (
        diff["metadata"]["narrative"]["after"]["overview"] == "A revised orientation."
    )


def test_legacy_input_does_not_acquire_invented_turning_points(sample):
    sample.pop("narrative")
    assert validate(sample)["valid"]
    html = render_html(sample)
    assert "A few places to begin" in html and "no authored historical overview" in html
    assert "<h2>The turning points</h2>" not in html


def test_story_text_is_literal_not_markup(sample):
    sample["narrative"]["overview"] = "<img src=x onerror=alert(1)>"
    sample["narrative"]["turning_points"][0]["title"] = "<script>alert(2)</script>"
    html = render_html(sample)
    assert "<img src=x" not in html and "<script>alert(2)" not in html
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in html


@pytest.mark.parametrize("source", [
    "src/research_lineage/data/qsp-qsvt.json",
    "src/research_lineage/data/attention-comparisons.json",
    "docs/test-reports/surface-code-rerun/map.json",
])
def test_reading_workspace_bundles_offline_without_reducing_map(source):
    data = json.loads((Path(__file__).parents[1] / source).read_text(encoding="utf-8"))
    html = render_html(data)
    embedded = re.search(r'id="map-data">(.*?)</script>', html, re.S)[1]
    assert json.loads(embedded) == data
    assert 'id="reading-button"' in html
    assert 'id="collection-preference">[]</script>' in html
    assert html.index("function noteText(") < html.index("function comparisonBrief(")
    assert html.index("function createReadingCollection(") < html.index("function createReadingWorkspace(")
    assert html.index("function createReadingWorkspace(") < html.index("const readingWorkspace =")
    assert "Export research note" in html and "Prepare evidence check" in html
    assert "connect-src 'none'" in html
