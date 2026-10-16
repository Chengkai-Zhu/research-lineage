"""Create the reviewed milestone/issue plan. Dry run unless --apply is supplied."""

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def gh(endpoint, payload=None, listing=False):
    command = ["gh", "api", endpoint]
    if listing:
        command += ["--paginate", "--slurp"]
    if payload is not None:
        command += ["--method", "POST", "--input", "-"]
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    parsed = json.loads(result.stdout)
    return [item for page in parsed for item in page] if listing else parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Chengkai-Zhu/research-lineage")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    plan = json.loads((ROOT / "docs/backlog.json").read_text(encoding="utf-8"))
    if not args.apply:
        print(
            json.dumps({"repo": args.repo, "action": "dry_run", "plan": plan}, indent=2)
        )
        return
    base = f"repos/{args.repo}"
    milestones = {
        item["title"]: item
        for item in gh(base + "/milestones?state=all&per_page=100", listing=True)
    }
    for item in plan["milestones"]:
        if item["title"] not in milestones:
            milestones[item["title"]] = gh(base + "/milestones", item)
    existing = {
        item["title"]: item
        for item in gh(base + "/issues?state=all&per_page=100", listing=True)
        if "pull_request" not in item
    }
    numbers = {}
    for item in plan["issues"]:
        if item["title"] not in existing:
            dependencies = (
                ", ".join(f"#{numbers[key]}" for key in item["dependencies"]) or "None."
            )
            body = (
                f"## Problem\n\n{item['problem']}\n\n## Deliverable\n\n{item['deliverable']}\n\n"
                f"## Acceptance\n\n{item['acceptance']}\n\n## Negative case\n\n{item['negative']}\n\n"
                f"## Dependencies\n\n{dependencies}\n\n## Original plan\n\n{item['original']}\n"
            )
            milestone = milestones[plan["milestones"][item["milestone"]]["title"]][
                "number"
            ]
            existing[item["title"]] = gh(
                base + "/issues",
                {"title": item["title"], "body": body, "milestone": milestone},
            )
        created = existing[item["title"]]
        numbers[item["key"]] = created["number"]
        print(
            json.dumps(
                {
                    "key": item["key"],
                    "number": created["number"],
                    "url": created["html_url"],
                }
            )
        )


if __name__ == "__main__":
    main()
