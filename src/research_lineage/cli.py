"""Command surface shared by the installed package and portable skill."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .contract import SCHEMA, validate
from .core import (
    MapError,
    compare,
    diff_maps,
    dump,
    load_map,
    review_report,
    write_text,
)
from .render import build

DATA = Path(__file__).parent / "data"


def parser():
    cli = argparse.ArgumentParser(
        prog="research-lineage",
        description="Trace how research ideas evolve. Local tools; evidence stays visible.",
    )
    cli.add_argument("--version", action="version", version=__version__)
    commands = cli.add_subparsers(dest="command", required=True)
    demo = commands.add_parser(
        "demo", help="Build the bundled QSP/QSVT example without network access"
    )
    demo.add_argument("--out", default="output/research-lineage")
    demo.add_argument("--force", action="store_true")
    init = commands.add_parser(
        "init", help="Create a valid empty draft for a research question"
    )
    init.add_argument("question")
    init.add_argument("--id", default="my-research")
    init.add_argument("--cutoff", default=date.today().isoformat())
    init.add_argument("--out", required=True)
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
    difference = commands.add_parser(
        "diff", help="Describe changes without applying or approving them"
    )
    difference.add_argument("before")
    difference.add_argument("after")
    difference.add_argument("--out")
    schema = commands.add_parser("schema", help="Export the canonical JSON Schema")
    schema.add_argument("--out")
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "demo":
            data = load_map(DATA / "qsp-qsvt.json")
            print(dump({"created": build(data, args.out, args.force)}))
        elif args.command == "init":
            if Path(args.out).exists():
                raise MapError(
                    "Draft path exists; choose a new path to preserve existing work."
                )
            data = {
                "schema_version": "1.0",
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
            check = validate(data)
            if not check["valid"]:
                raise MapError("\n".join(check["errors"]))
            write_text(args.out, dump(data))
            print(f"Created draft: {args.out}")
        elif args.command == "schema":
            output = dump(SCHEMA)
            write_text(args.out, output) if args.out else print(output)
        elif args.command == "diff":
            if args.out and Path(args.out).resolve() in (
                Path(args.before).resolve(),
                Path(args.after).resolve(),
            ):
                raise MapError("Diff output cannot overwrite either input revision.")
            output = dump(diff_maps(load_map(args.before), load_map(args.after)))
            write_text(args.out, output) if args.out else print(output)
        else:
            data = load_map(args.map)
            if args.command == "validate":
                print(dump(validate(data)))
            elif args.command == "build":
                output = Path(args.out).resolve() / "map.json"
                if output == Path(args.map).resolve():
                    raise MapError(
                        "Build output would overwrite its input. Choose a separate output folder."
                    )
                print(dump({"created": build(data, args.out, args.force)}))
            elif args.command == "review":
                if Path(args.out).resolve() == Path(args.map).resolve():
                    raise MapError("Review output cannot overwrite its input.")
                write_text(args.out, review_report(data))
                print(f"Wrote review report: {args.out}")
            elif args.command == "compare":
                print(dump(compare(data, args.left, args.right)))
        return 0
    except (MapError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
