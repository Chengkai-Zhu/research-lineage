"""Command surface shared by the installed package and portable skill."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .contract import SCHEMAS, validate
from .anchors import check_anchor
from .core import (
    MapError,
    compare,
    diff_maps,
    dump,
    load_map,
    review_report,
    same_file,
    write_text,
)
from .render import OUTPUT_NAMES, build
from .discovery import discover
from .evaluation import evaluate, study_report
from .extraction import assess
from .identity import reconcile
from .intake import start
from .temporal import update_proposal

DATA = Path(__file__).parent / "data"


def parser():
    cli = argparse.ArgumentParser(
        prog="research-lineage",
        description="LitDelta: see what research changes, under which conditions, and why.",
    )
    cli.add_argument("--version", action="version", version=__version__)
    commands = cli.add_subparsers(dest="command", required=True)
    seed = commands.add_parser(
        "start", help="Prepare a topic or paper for the host research agent"
    )
    seed.add_argument("seed")
    seed.add_argument("--kind", choices=("auto", "topic", "paper"), default="auto")
    seed.add_argument("--language", choices=("auto", "en", "zh"), default="auto")
    seed.add_argument("--cutoff", default=date.today().isoformat())
    seed.add_argument("--out", default="output/research")
    search = commands.add_parser(
        "discover", help="Explicit bounded online metadata search"
    )
    search.add_argument("query")
    search.add_argument("--provider", choices=("crossref", "arxiv"), default="crossref")
    search.add_argument("--limit", type=int, default=12)
    search.add_argument("--max-requests", type=int, default=3)
    search.add_argument("--out", required=True)
    for name in ("reconcile", "assess", "evaluate", "study"):
        command = commands.add_parser(
            name, help="Inspect structured research/evaluation input"
        )
        command.add_argument("input")
        command.add_argument("--out")
    update = commands.add_parser(
        "update", help="Propose changes with source-version availability at a cutoff"
    )
    update.add_argument("before")
    update.add_argument("after")
    update.add_argument("--as-of", required=True)
    update.add_argument("--out")
    demo = commands.add_parser(
        "demo", help="Build the bundled QSP/QSVT example without network access"
    )
    demo.add_argument("--out", default="output/research-lineage")
    demo.add_argument("--force", action="store_true")
    demo.add_argument("--example", choices=("qsp", "comparisons"), default="qsp")
    init = commands.add_parser(
        "init", help="Create a valid empty draft for a research question"
    )
    init.add_argument("question")
    init.add_argument("--id", default="my-research")
    init.add_argument("--cutoff", default=date.today().isoformat())
    init.add_argument("--out", required=True)
    init.add_argument("--format-version", choices=tuple(SCHEMAS), default="1.0")
    for name in ("validate", "build", "review", "compare"):
        command = commands.add_parser(name)
        command.add_argument("map")
        if name in ("build", "review"):
            command.add_argument("--out", required=True)
        if name == "build":
            command.add_argument("--force", action="store_true")
        if name == "compare":
            command.add_argument("left")
            command.add_argument("right")
            command.add_argument(
                "--comparison",
                help="Select an authored comparison ID for this ordered pair",
            )
    anchor = commands.add_parser(
        "anchor", help="Explicitly check an evidence quote against optional local text"
    )
    anchor.add_argument("map")
    anchor.add_argument("evidence_id")
    anchor.add_argument(
        "--text", help="Local UTF-8 source text; omitted means unchecked"
    )
    anchor.add_argument("--out")
    difference = commands.add_parser(
        "diff", help="Describe changes without applying or approving them"
    )
    difference.add_argument("before")
    difference.add_argument("after")
    difference.add_argument("--out")
    schema = commands.add_parser("schema", help="Export the canonical JSON Schema")
    schema.add_argument("--out")
    schema.add_argument("--format-version", choices=tuple(SCHEMAS), default="1.0")
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            print(
                dump(
                    start(
                        args.seed,
                        args.out,
                        kind=args.kind,
                        language=args.language,
                        cutoff=args.cutoff,
                    )
                )
            )
        elif args.command == "discover":
            if Path(args.out).exists():
                raise MapError("Discovery log exists; choose a new output path.")
            result = discover(args.query, args.provider, args.limit, args.max_requests)
            write_text(args.out, dump(result))
            print(
                dump(
                    {
                        "log": args.out,
                        "status": result["status"],
                        "candidates": len(result["candidates"]),
                    }
                )
            )
            return 3 if result["failures"] else 0
        elif args.command in ("reconcile", "assess", "evaluate", "study", "update"):
            if args.out and Path(args.out).exists():
                raise MapError(
                    "Output exists; choose a new path to preserve the input and earlier reports."
                )
            if args.command == "update":
                result = update_proposal(
                    load_map(args.before), load_map(args.after), args.as_of
                )
            else:
                path = Path(args.input)
                if path.stat().st_size > 5_000_000:
                    raise MapError("Research input exceeds 5 MB.")
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                if args.command in ("evaluate", "study") and not isinstance(data, dict):
                    raise MapError("Evaluation/study input must be a JSON object.")
                result = {
                    "reconcile": reconcile,
                    "assess": assess,
                    "evaluate": evaluate,
                    "study": study_report,
                }[args.command](data)
            write_text(args.out, dump(result)) if args.out else print(dump(result))
        elif args.command == "demo":
            name = (
                "attention-comparisons.json"
                if args.example == "comparisons"
                else "qsp-qsvt.json"
            )
            data = load_map(DATA / name)
            print(dump({"created": build(data, args.out, args.force)}))
        elif args.command == "init":
            if Path(args.out).exists():
                raise MapError(
                    "Draft path exists; choose a new path to preserve existing work."
                )
            data = {
                "schema_version": args.format_version,
                "id": args.id,
                "title": args.question,
                "question": args.question,
                "scope": {
                    "summary": "Define inclusion criteria before researching.",
                    "cutoff": args.cutoff,
                    "coverage": "No sources collected yet.",
                    "search_strategy": "Record queries, sources, dates, and failures here.",
                    "exclusions": [],
                    "gaps": ["Research has not started."],
                },
                "lanes": [{"id": "main", "label": "Main thread", "color": "teal"}],
                "works": [],
                "results": [],
                "evidence": [],
                "relations": [],
                "reading_route": [],
            }
            if args.format_version == "1.1":
                data["comparisons"] = []
            check = validate(data)
            if not check["valid"]:
                raise MapError("\n".join(check["errors"]))
            write_text(args.out, dump(data))
            print(f"Created draft: {args.out}")
        elif args.command == "schema":
            output = dump(SCHEMAS[args.format_version])
            write_text(args.out, output) if args.out else print(output)
        elif args.command == "anchor":
            data = load_map(args.map)
            evidence = next(
                (e for e in data["evidence"] if e["id"] == args.evidence_id), None
            )
            if evidence is None:
                raise MapError("Evidence ID does not exist in this map.")
            if args.out and Path(args.out).exists():
                raise MapError("Anchor report exists; choose a new output path.")
            text = None
            if args.text:
                with Path(args.text).open("rb") as handle:
                    raw = handle.read(5_000_001)
                if len(raw) > 5_000_000:
                    raise MapError("Source text exceeds the 5 MB local-check limit.")
                text = raw.decode("utf-8-sig")
            output = dump(check_anchor(evidence, text))
            write_text(args.out, output) if args.out else print(output)
        elif args.command == "diff":
            if args.out and any(
                same_file(args.out, path) for path in (args.before, args.after)
            ):
                raise MapError("Diff output cannot overwrite either input revision.")
            output = dump(diff_maps(load_map(args.before), load_map(args.after)))
            write_text(args.out, output) if args.out else print(output)
        else:
            data = load_map(args.map)
            if args.command == "validate":
                print(dump(validate(data)))
            elif args.command == "build":
                if any(
                    same_file(Path(args.out) / name, args.map) for name in OUTPUT_NAMES
                ):
                    raise MapError(
                        "Build output would overwrite its input. Choose a separate output folder."
                    )
                print(dump({"created": build(data, args.out, args.force)}))
            elif args.command == "review":
                if same_file(args.out, args.map):
                    raise MapError("Review output cannot overwrite its input.")
                write_text(args.out, review_report(data))
                print(f"Wrote review report: {args.out}")
            elif args.command == "compare":
                print(dump(compare(data, args.left, args.right, args.comparison)))
        return 0
    except (MapError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
