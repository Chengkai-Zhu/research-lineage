"""Print a reader-friendly offline research-run audit; PASS is not scholarly review."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from research_lineage.core import MapError
from research_lineage.research_scope import audit_run


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python scripts/verify_research_run.py <run-manifest.json>")
        return 2
    try:
        report = audit_run(args[0])
    except (MapError, OSError, ValueError) as exc:
        print(f"FAIL research_record: {exc}")
        return 2
    for name, check in report["checks"].items():
        print(f"{check['status']} {name}")
        for detail in check["details"]:
            print(f"  {detail}")
    print(f"{report['status']} recorded research run; counts: {report['counts']}")
    print(report["limits"])
    return {"PASS": 0, "PARTIAL": 3, "FAIL": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
