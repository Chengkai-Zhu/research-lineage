import json
from copy import deepcopy
from html import unescape
from xml.etree import ElementTree as ET

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
