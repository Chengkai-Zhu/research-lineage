import json
import os
import subprocess
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree

import pytest

from research_lineage.cli import main
from research_lineage.core import (
    MapError,
    compare,
    diff_maps,
    dump,
    load_map,
    review_report,
)
from research_lineage.render import build, export_svg, render_html

ROOT = Path(__file__).parents[1]


def test_build_is_reproducible_and_has_all_deliverables(sample, tmp_path):
    a, b = tmp_path / "one", tmp_path / "two"
    build(sample, a)
    build(sample, b)
    assert {path.name for path in a.iterdir()} == {
        "map.html",
        "map.svg",
        "map.json",
        "review.md",
    }
    for path in a.iterdir():
        assert path.read_bytes() == (b / path.name).read_bytes()
    assert load_map(a / "map.json") == sample
    with pytest.raises(MapError, match="already exists"):
        build(sample, a)
    build(sample, a, force=True)


def test_exports_preserve_source_limits(sample):
    svg = export_svg(sample)
    ElementTree.fromstring(svg)
    assert "KNOWN GAPS" in svg and "SOURCE INDEX" in svg
    assert sample["evidence"][0]["url"] in svg
    assert sample["scope"]["cutoff"] in svg
    report = review_report(sample)
    assert "not certify scientific correctness" in report
    assert all(item["id"] in report for item in sample["relations"])


def test_html_and_svg_treat_imported_text_as_data(sample):
    attack = '</script><img src=x onerror="alert(1)">@@JS@@'
    sample["title"] = attack
    sample["results"][0]["label"] = attack
    sample["results"][0]["summary"] = attack
    page = render_html(sample)
    assert "<img src=x" not in page
    assert "\\u003c/script\\u003e" in page
    assert "@@JS@@" in page  # literal user text is not reinterpreted as a template slot
    root = ElementTree.fromstring(export_svg(sample))
    assert not root.findall(".//{http://www.w3.org/2000/svg}script")


def test_viewer_has_no_remote_runtime_dependencies(sample):
    page = render_html(sample)
    assert "connect-src 'none'" in page
    assert "<script src=" not in page and '<link rel="stylesheet"' not in page
    assert "fetch(" not in page and "XMLHttpRequest" not in page


def test_comparison_keeps_unknown_and_does_not_rank(sample):
    result = compare(sample, "r-qsp", "r-qsvt")
    assert result["fields"][0]["status"] == "different"
    assert result["fields"][2]["status"] == "unknown"
    assert "not established" in result["verdict"]
    assert compare(sample, "r-qsp", "r-qsp")["fields"][0]["status"] == "same_reported"
    with pytest.raises(MapError):
        compare(sample, "missing", "r-qsp")


def test_diff_preserves_removals_and_changed_settings(sample):
    newer = deepcopy(sample)
    newer["results"][0]["settings"]["cost"] = "Revised cost accounting"
    newer["relations"].pop()
    newer["scope"]["gaps"].append("An additional limitation")
    result = diff_maps(sample, newer)
    assert result["status"] == "proposal_only"
    assert len(result["changes"]["relations"]["removed"]) == 1
    assert "settings" in result["changes"]["results"]["changed"][0]["fields"]
    assert "scope" in result["metadata"]
    assert sample["results"][0]["settings"]["cost"] != "Revised cost accounting"
    newer["id"] = "different-map"
    with pytest.raises(MapError):
        diff_maps(sample, newer)


@pytest.mark.parametrize("raw", ['{"id":"a","id":"b"}', "NaN", "\ud800", "{broken"])
def test_invalid_json_is_reported(tmp_path, raw):
    path = tmp_path / "bad.json"
    path.write_bytes(raw.encode("utf-8", errors="surrogatepass"))
    with pytest.raises(MapError):
        load_map(path)


def test_input_limit(tmp_path):
    path = tmp_path / "large.json"
    path.write_bytes(b" " * 5_000_001)
    with pytest.raises(MapError, match="5 MB"):
        load_map(path)


def test_cli_init_uses_question_not_bundled_demo(tmp_path, capsys):
    path = tmp_path / "draft.json"
    assert (
        main(
            [
                "init",
                "How did this method evolve?",
                "--out",
                str(path),
                "--cutoff",
                "2026-10-16",
            ]
        )
        == 0
    )
    data = load_map(path)
    assert data["question"] == "How did this method evolve?"
    assert not data["results"]
    assert main(["build", str(path), "--out", str(tmp_path / "empty")]) == 2
    assert "no results" in capsys.readouterr().err
    assert main(["init", "Other question", "--out", str(path)]) == 2


def test_cli_complete_local_workflow(tmp_path, capsys):
    folder = tmp_path / "demo"
    assert main(["demo", "--out", str(folder)]) == 0
    source = folder / "map.json"
    assert main(["validate", str(source)]) == 0
    assert main(["compare", str(source), "r-qsp", "r-qsvt"]) == 0
    assert main(["build", str(source), "--out", str(tmp_path / "rebuilt")]) == 0
    assert main(["review", str(source), "--out", str(tmp_path / "review.md")]) == 0
    assert (
        main(["diff", str(source), str(source), "--out", str(tmp_path / "diff.json")])
        == 0
    )
    assert main(["schema", "--out", str(tmp_path / "schema.json")]) == 0
    assert (
        json.loads((tmp_path / "diff.json").read_text())["changes"]["results"][
            "changed"
        ]
        == []
    )
    assert main(["build", str(source), "--out", str(folder), "--force"]) == 2
    assert main(["review", str(source), "--out", str(source)]) == 2
    assert main(["diff", str(source), str(source), "--out", str(source)]) == 2
    assert main(["validate", str(tmp_path / "missing.json")]) == 2
    assert "error:" in capsys.readouterr().err


def test_isolated_skill_package_runs_without_checkout_or_installation(tmp_path):
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/package_skill.py"),
            "--out",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
    )
    archive = next(tmp_path.glob("*.zip"))
    original = archive.read_bytes()
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/package_skill.py"),
            "--out",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
    )
    assert archive.read_bytes() == original
    target = tmp_path / "isolated"
    with zipfile.ZipFile(archive) as package:
        package.extractall(target)
    runner = target / "research-lineage/scripts/lineage.py"
    environment = {
        key: value for key, value in os.environ.items() if key != "PYTHONPATH"
    }
    # -I ignores the user's Python path; the bundled runner must supply its runtime.
    process = subprocess.run(
        [sys.executable, "-I", str(runner), "demo", "--out", str(tmp_path / "output")],
        cwd=target,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert process.returncode == 0, process.stderr
    assert load_map(tmp_path / "output/map.json")["id"] == "qsp-qsvt"


def test_unreviewed_example_has_no_claimed_certification(sample):
    assert all(
        result["review_status"] == "proposed" and result["reviews"] == []
        for result in sample["results"]
    )
    assert all(item["kind"] == "abstract" for item in sample["evidence"])
    assert dump(sample).endswith("\n")
