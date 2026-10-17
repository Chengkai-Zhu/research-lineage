import json
import re
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from research_lineage.graph import (
    CARD_HEIGHT,
    CARD_WIDTH,
    text_width,
    timeline_layout,
    wrap_label,
)
from research_lineage.render import export_lines, export_svg, render_html

ROOT = Path(__file__).parents[1]
NS = {"svg": "http://www.w3.org/2000/svg"}


def test_dense_chronology_has_no_overlapping_or_lost_results():
    data = json.loads(
        (ROOT / "docs/test-reports/surface-code-rerun/map.json").read_text()
    )
    before = deepcopy(data)
    positions, periods, height, _, _ = timeline_layout(data)
    assert len(positions) == 54
    assert len(periods) == 4
    boxes = list(positions.values())
    for index, (x, y) in enumerate(boxes):
        assert 0 < x < x + CARD_WIDTH < 1240
        assert 0 < y < y + CARD_HEIGHT < height
        for other_x, other_y in boxes[index + 1 :]:
            assert (
                x + CARD_WIDTH <= other_x
                or other_x + CARD_WIDTH <= x
                or y + CARD_HEIGHT <= other_y
                or other_y + CARD_HEIGHT <= y
            )
    assert data == before
    data["results"].reverse()
    data["works"].reverse()
    assert timeline_layout(data)[0] == positions


@pytest.mark.parametrize(
    "label",
    [
        "含测量噪声的拓扑存储阈值及量子纠错的额外条件" * 3,
        "An exceptionallylongunbrokentoken " * 5,
        "d=3→5→7实现低于阈值存储 — CJK and English α e\u0301",
        "<script>alert('data')</script>" * 5,
    ],
)
def test_labels_fit_in_three_lines_without_losing_full_exported_title(sample, label):
    lines = wrap_label(label, 28, 3)
    assert len(lines) <= 3
    assert all(text_width(line) <= 28 for line in lines)
    sample["results"][0]["label"] = label
    svg = ET.fromstring(export_svg(sample))
    node = svg.find(f'.//svg:g[@id="result-{sample["results"][0]["id"]}"]', NS)
    assert node.attrib["aria-label"] == label
    assert node.find("svg:title", NS).text.startswith(label)
    assert not svg.findall(".//svg:script", NS)
    assert json.loads(svg.find("svg:metadata", NS).text) == sample


def test_wrapping_handles_wide_and_combining_characters():
    assert text_width("测试Ａ") == 6
    assert text_width("e\u0301") == 1
    assert wrap_label("甲乙丙丁戊己庚", 4, 2) == ["甲乙", "丙…"]
    assert wrap_label("one two three", 7) == ["one two", "three"]
    assert wrap_label("", 20) == []


def test_same_paper_results_remain_separate_and_addressable(sample):
    work = sample["works"][0]
    for result in sample["results"]:
        result["work_id"] = work["id"]
    positions, _, _, low, high = timeline_layout(sample)
    assert len(set(positions.values())) == len(sample["results"])
    assert low == high


def test_browser_and_cli_svg_share_the_cjk_safe_appendix():
    data = json.loads(
        (ROOT / "docs/test-reports/surface-code-rerun/map.json").read_text()
    )
    lines = export_lines(data)
    assert all(text_width(line) <= 185 for line in lines)
    page = render_html(data)
    browser_lines = json.loads(
        re.search(r'id="export-notes">\s*(.*?)\s*</script>', page, re.S)[1]
    )
    assert browser_lines == lines
    svg = ET.fromstring(export_svg(data))
    # Direct SVG text nodes contain the appendix; graph labels are nested groups.
    printed = [node.text for node in svg.findall("svg:text", NS)]
    assert printed[1:] == lines
