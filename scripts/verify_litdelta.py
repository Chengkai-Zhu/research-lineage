"""Run offline comparison controls; keep research and publication evidence separate."""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_lineage.anchors import check_anchor  # noqa: E402
from research_lineage.contract import validate  # noqa: E402
from research_lineage.core import compare, diff_maps, dump, load_map, write_text  # noqa: E402
from research_lineage.extraction import assess  # noqa: E402
from research_lineage.render import build  # noqa: E402
from research_lineage.temporal import update_proposal  # noqa: E402


class Controls:
    def __init__(self, destination):
        self.destination = destination
        self.rows = []

    def check(self, name, source, expected, action):
        try:
            observed = action()
        except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
            observed = {"error": str(exc)}
        self.rows.append(
            dict(
                name=name,
                input=source,
                expected=expected,
                observed=observed,
                status="PASS" if observed == expected else "FAIL",
            )
        )

    def gate(self, name, data):
        path = self.destination / "controls" / (name + ".json")
        write_text(path, dump(data))
        direct = validate(data)
        intake = assess({"id": name, "map": data, "relation_id": "edge"})
        write_text(
            path.with_suffix(".result.json"), dump({"map": direct, "intake": intake})
        )
        self.check(
            name,
            str(path.relative_to(self.destination)),
            {"map_valid": False, "intake": "abstain"},
            lambda: {"map_valid": direct["valid"], "intake": intake["decision"]},
        )


def export_control(data, folder):
    build(data, folder)
    output = load_map(folder / "map.json")
    svg = ET.fromstring((folder / "map.svg").read_text(encoding="utf-8"))
    embedded = svg.find("{http://www.w3.org/2000/svg}metadata").text
    document = (folder / "map.html").read_text(encoding="utf-8")
    payload = re.search(
        r'<script type="application/json" id="map-data">(.*?)</script>', document, re.S
    )
    return {
        "json": output == data,
        "svg": json.loads(embedded) == data,
        "html": json.loads(payload[1]) == data,
        "report": data["comparisons"][0]["rationale"]
        in (folder / "review.md").read_text(encoding="utf-8"),
    }


def comparison_controls(checks, fixture):
    checks.check(
        "authored-record",
        "tests/fixtures/comparison-map.json",
        {"assessment": "comparable", "cost": "50 calls", "intake": "propose"},
        lambda: {
            "assessment": compare(fixture, "a", "b")["assessment"],
            "cost": compare(fixture, "a", "b")["comparison"]["conditions"][2]["right"],
            "intake": assess({"id": "good", "map": fixture, "relation_id": "edge"})[
                "decision"
            ],
        },
    )
    checks.check(
        "complete-exports",
        "fixture → exports/",
        dict.fromkeys(("json", "svg", "html", "report"), True),
        lambda: export_control(fixture, checks.destination / "exports"),
    )
    for name in (
        "missing-comparison",
        "unit-mismatch",
        "citation-only",
        "wrong-version",
    ):
        bad = deepcopy(fixture)
        if name == "missing-comparison":
            bad["comparisons"] = []
        elif name == "unit-mismatch":
            bad["comparisons"][0]["conditions"][2]["right_unit"] = "seconds"
        elif name == "citation-only":
            bad["relations"][0]["basis"] = "citation_only"
        else:
            bad["evidence"][1]["version_id"] = "v-a"
        checks.gate(name, bad)
    neutral = deepcopy(fixture)
    neutral["relations"] = []
    neutral["comparisons"][0].update(outcome="equal", improvement=None)
    checks.check(
        "comparable-is-not-better",
        "equal outcome control",
        "equal",
        lambda: compare(neutral, "a", "b")["comparison"]["outcome"],
    )
    neutral["comparisons"] = []
    neutral["results"][1]["settings"] = deepcopy(neutral["results"][0]["settings"])
    checks.check(
        "equal-text-stays-unknown",
        "unassessed identical settings",
        "unknown",
        lambda: compare(neutral, "a", "b")["assessment"],
    )
    checks.check(
        "reverse-is-not-inverted",
        "reversed result endpoints",
        "unknown",
        lambda: compare(fixture, "b", "a")["assessment"],
    )
    multiple = deepcopy(fixture)
    record = deepcopy(multiple["comparisons"][0])
    record.update(id="other-question", question="A second question")
    multiple["comparisons"].append(record)
    checks.check(
        "explicit-question-selection",
        "two records for one ordered pair",
        [True, None, "other-question"],
        lambda: [
            compare(multiple, "a", "b")["selection_required"],
            compare(multiple, "a", "b")["comparison"],
            compare(multiple, "a", "b", "other-question")["comparison"]["id"],
        ],
    )


def temporal_controls(checks, fixture):
    changed = deepcopy(fixture)
    changed["comparisons"][0]["rationale"] = "A changed premise."
    checks.check(
        "comparison-edit-visible",
        "comparison-only edit",
        "A changed premise.",
        lambda: diff_maps(fixture, changed)["changes"]["comparisons"]["changed"][0][
            "fields"
        ]["rationale"]["after"],
    )
    changed["works"][0]["versions"].append(
        dict(
            id="late-v",
            label="Later context",
            published="2021-01-01",
            url="https://example.org/later",
        )
    )
    changed["evidence"].append(
        {
            **changed["evidence"][0],
            "id": "late-e",
            "version_id": "late-v",
            "url": "https://example.org/later",
        }
    )
    changed["comparisons"][0]["evidence"].append("late-e")
    checks.check(
        "late-comparison-evidence",
        "2020 cutoff with 2021 comparison context",
        [[], []],
        lambda: [
            update_proposal(fixture, changed, "2020-06-01")[key]
            for key in ("eligible_comparison_ids", "eligible_relation_ids")
        ],
    )


def anchor_controls(checks, fixture):
    evidence = deepcopy(fixture["evidence"][0])
    evidence["quote"] = dict(exact="the result", prefix="", suffix="")
    checks.check(
        "anchor-outcomes",
        "explicit local text controls",
        ["matched", "missing", "ambiguous", "unchecked"],
        lambda: [
            check_anchor(evidence, text)["outcome"]
            for text in (
                "the\nresult",
                "different text",
                "the result; the result",
                None,
            )
        ],
    )
    checks.check(
        "changed-text-rechecked",
        "different local text artifacts",
        True,
        lambda: (
            check_anchor(evidence, "the result")["text_sha256"]
            != check_anchor(evidence, "the result ")["text_sha256"]
        ),
    )
    quoted = deepcopy(fixture)
    quoted["evidence"][0].update(
        quote=evidence["quote"], anchor_check=check_anchor(evidence, "the result")
    )
    checks.check(
        "match-is-not-review",
        "recorded local match",
        [True, "proposed"],
        lambda: [validate(quoted)["valid"], quoted["results"][0]["review_status"]],
    )
    quoted["evidence"][0]["quote"]["exact"] = "changed selector"
    checks.check(
        "stale-selector-rejected",
        "edited quote with stale report",
        False,
        lambda: validate(quoted)["valid"],
    )


def alias_result(name, fixture_path):
    command = shutil.which(name)
    if command is None:
        suffix = ".exe" if os.name == "nt" else ""
        command = str(Path(sys.executable).parent / (name + suffix))
    completed = subprocess.run(
        [command, "compare", str(fixture_path), "a", "b"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    result = json.loads(completed.stdout)
    return [result["assessment"], result["comparison"]["conditions"][2]["right"]]


def research_integration(manifest):
    checker = ROOT / "scripts/verify_research_run.py"
    report = {
        "status": "PARTIAL",
        "reason": "Awaiting the corrected #14 contract and actual #12 fresh-run evidence.",
        "issues": [14, 12],
        "manifest": str(manifest) if manifest else None,
    }
    if manifest and checker.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(checker), str(manifest.resolve())],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {**report, "status": "FAIL", "reason": str(exc)}
        output = result.stdout + result.stderr
        passing = (
            result.returncode == 0
            and len(re.findall(r"\bPASS\b", output)) >= 4
            and not re.search(r"\b(?:PARTIAL|FAIL)\b", output)
        )
        report.update(
            status="PASS" if passing else "FAIL",
            checker=str(checker.relative_to(ROOT)),
            exit_code=result.returncode,
            observed=output,
            reason="Delegated to the actual #12 checker; this is not independent scholarly review.",
        )
    return report


def publish_report(destination, report):
    write_text(destination / "report.json", dump(report))
    rows = []
    for row in report["checks"]:
        cells = [
            row["name"],
            row["status"],
            row["input"],
            json.dumps(row["expected"], ensure_ascii=False),
            json.dumps(row["observed"], ensure_ascii=False),
        ]
        rows.append(
            "<tr>"
            + "".join("<td>" + html.escape(value) + "</td>" for value in cells)
            + "</tr>"
        )
    content = (
        "<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
        "<title>LitDelta acceptance evidence</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px;line-height:1.6}"
        "table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #ccc;text-align:left;overflow-wrap:anywhere}pre{white-space:pre-wrap}</style>"
        "<h1>LitDelta acceptance evidence</h1><p>Engineering controls do not establish research coverage or scientific truth.</p>"
        "<p><a href='flagship/map.html'>Open the real reading example</a> · <a href='report.json'>JSON report</a></p>"
        "<h2>Evidence streams</h2><pre>"
        + html.escape(
            dump({key: value for key, value in report.items() if key != "checks"})
        )
        + "</pre>"
        "<h2>Known-input checks</h2><table><tr><th>Check</th><th>Status</th><th>Input</th><th>Expected</th><th>Observed</th></tr>"
        + "".join(rows)
        + "</table></html>"
    )
    write_text(destination / "report.html", content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--fixture", type=Path, default=ROOT / "tests/fixtures/comparison-map.json"
    )
    parser.add_argument("--research-manifest", type=Path)
    parser.add_argument("--require-integration", action="store_true")
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error(
            "Output exists; choose a fresh directory to preserve previous evidence."
        )
    args.out.mkdir(parents=True)
    checks = Controls(args.out)
    try:
        fixture = load_map(args.fixture)
        comparison_controls(checks, fixture)
        temporal_controls(checks, fixture)
        anchor_controls(checks, fixture)
        for name in ("litdelta", "research-lineage"):
            checks.check(
                "installed-alias-" + name,
                "installed CLI with fixture",
                ["comparable", "50 calls"],
                lambda name=name: alias_result(name, args.fixture),
            )
    except (ValueError, OSError, KeyError) as exc:
        checks.check(
            "fixture-load",
            str(args.fixture),
            "valid 1.1 control map",
            lambda message=str(exc): message,
        )
    flagship = load_map(ROOT / "src/research_lineage/data/attention-comparisons.json")
    build(flagship, args.out / "flagship")
    checks.check(
        "same-paper-results",
        "flagship/map.json",
        [1, 4, "incomparable"],
        lambda: [
            len(flagship["works"]),
            len(flagship["results"]),
            compare(flagship, "r-attention", "r-quality")["assessment"],
        ],
    )
    legacy = load_map(ROOT / "examples/nmt-attention/map.json")
    snapshot = deepcopy(legacy)
    build(legacy, args.out / "legacy")
    checks.check(
        "legacy-roundtrip",
        "legacy/map.json",
        True,
        lambda: load_map(args.out / "legacy/map.json") == snapshot,
    )
    software = "PASS" if all(row["status"] == "PASS" for row in checks.rows) else "FAIL"
    integration = research_integration(args.research_manifest)
    report = dict(
        software={"status": software, "checks": len(checks.rows)},
        research_integration=integration,
        browser={
            "status": "MANUAL",
            "reason": "Record actual browser observations separately; no automated browser claim.",
        },
        public_preview={
            "status": "PARTIAL",
            "reason": "Requires the published preview and an actual reachable URL.",
        },
        study={"status": "unavailable", "participants": 0, "issue": 10},
        checks=checks.rows,
    )
    publish_report(args.out, report)
    print(
        f"Software: {software} ({sum(row['status'] == 'PASS' for row in checks.rows)}/{len(checks.rows)})"
    )
    print(f"Research integration: {integration['status']}")
    print("Browser: MANUAL; public preview: PARTIAL; participant evidence: unavailable")
    print(f"Evidence: {args.out / 'report.html'}")
    return (
        2
        if software != "PASS"
        or (args.require_integration and integration["status"] != "PASS")
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
