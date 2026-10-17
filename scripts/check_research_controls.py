"""Calibrate the run audit against an actual run and deliberately broken copies."""

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_lineage.core import MapError, dump, load_map, write_text  # noqa: E402
from research_lineage.render import render_html  # noqa: E402
from research_lineage.research_scope import audit_run  # noqa: E402


def replace_artifact(folder, manifest, name, content):
    path = folder / manifest["artifacts"][name]["path"]
    path.write_text(content, encoding="utf-8", newline="\n")
    manifest["artifacts"][name]["sha256"] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def controls(path, baseline):
    path = Path(path).resolve()
    original = json.loads(path.read_text(encoding="utf-8"))
    positive = audit_run(path)
    required = ("execution_provenance", "cutoff_consistency", "source_trail")
    if positive["status"] not in ("PASS", "PARTIAL") or any(
        positive["checks"][name]["status"] != "PASS" for name in required
    ):
        raise MapError(
            "The unmodified run needs intact provenance, cutoff and sources."
        )
    cases = []
    scratch = ROOT / ".research-lineage" / "controls"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="run-audit-", dir=scratch) as temp:
        temp_root = Path(temp).resolve()
        if not temp_root.is_relative_to(scratch.resolve()):
            raise MapError("Control workspace escaped its intended scratch parent.")
        for name in ("baseline-relabel", "missing-forward", "hidden-gap"):
            folder = temp_root / name
            folder.mkdir()
            manifest = json.loads(json.dumps(original))
            for artifact in manifest["artifacts"].values():
                destination = folder / artifact["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path.parent / artifact["path"], destination)
            log = json.loads(
                (folder / manifest["artifacts"]["research_log"]["path"]).read_text(
                    encoding="utf-8"
                )
            )
            if name == "baseline-relabel":
                data = load_map(baseline)
                replace_artifact(folder, manifest, "map", dump(data))
                replace_artifact(folder, manifest, "html", render_html(data))
                manifest["execution"]["context"] = "existing"
                log["stop"]["status"] = "complete"
                replace_artifact(folder, manifest, "research_log", dump(log))
                note = "Relabel the old authored four-work baseline as the fresh completed run, leaving incompatible provenance, cutoff and source evidence. This is a deliberate bad copy, not a second research execution."
            elif name == "missing-forward":
                removed = {
                    s["id"] for s in log["searches"] if s["direction"] == "forward"
                }
                log["searches"] = [s for s in log["searches"] if s["id"] not in removed]
                for record in log["candidates"] + log["branches"]:
                    record["search_ids"] = [
                        s for s in record["search_ids"] if s not in removed
                    ]
                log["stop"]["status"] = "complete"
                replace_artifact(folder, manifest, "research_log", dump(log))
                note = "Remove forward-search records and assert completion. On a partial positive run, this also contradicts its retained gap; the isolated forward-only failure is covered in tests/test_research_scope.py."
            else:
                log["branches"][0].update(
                    status="gap",
                    gap="Injected negative-control gap; not an actual gap in the original run.",
                )
                log["stop"].update(status="complete", unresolved_branch_ids=[])
                replace_artifact(folder, manifest, "research_log", dump(log))
                note = (
                    "Inject an unresolved branch and hide it from the stopping summary."
                )
            candidate = folder / "manifest.json"
            candidate.write_text(dump(manifest), encoding="utf-8")
            observed = audit_run(candidate)
            failed = [
                key
                for key, check in observed["checks"].items()
                if check["status"] == "FAIL"
            ]
            expected_check = (
                "execution_provenance"
                if name == "baseline-relabel"
                else "research_completion"
            )
            passed = observed["status"] == "FAIL" and expected_check in failed
            cases.append(
                {
                    "id": name,
                    "status": "PASS" if passed else "FAIL",
                    "expected": "FAIL",
                    "observed": observed["status"],
                    "failed_checks": failed,
                    "description": note,
                }
            )
    return {
        "status": "PASS" if all(c["status"] == "PASS" for c in cases) else "FAIL",
        "positive_run": positive["status"],
        "controls": cases,
        "limit": "These copies calibrate recorded-evidence checks, not the scientific quality of the literature selection.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument(
        "--baseline", default=str(ROOT / "examples/surface-code/map.json")
    )
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.out and Path(args.out).exists():
            raise MapError("Control report exists; choose a new output path.")
        result = controls(args.manifest, args.baseline)
        if args.out:
            write_text(args.out, dump(result))
        print(f"{result['positive_run']} unmodified actual run")
        for case in result["controls"]:
            print(
                f"{case['status']} {case['id']}: expected {case['expected']}, observed {case['observed']}; {', '.join(case['failed_checks'])}"
            )
        return 0 if result["status"] == "PASS" else 2
    except (MapError, OSError, ValueError) as exc:
        print(f"FAIL controls: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
