"""Verify a local preview or explicitly fetch its public files and offline bundle."""

import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_FILE = 5_000_000
MAX_TOTAL = 30_000_000


def safe_name(name):
    return (
        isinstance(name, str)
        and bool(re.fullmatch(r"[A-Za-z0-9_./-]+", name))
        and all(part not in ("", ".", "..") for part in name.split("/"))
    )


def verify(fetch):
    raw_manifest = fetch("manifest.json")
    manifest = json.loads(raw_manifest)
    files = manifest["files"]
    if (
        manifest.get("product") != "LitDelta"
        or not isinstance(files, dict)
        or not 1 <= len(files) <= 100
        or not all(safe_name(name) for name in files)
        or not {"index.html", "map.html", "START-HERE.html"} <= files.keys()
    ):
        raise ValueError("Invalid preview manifest or file paths.")
    rows, total = [], 0
    for name, expected in files.items():
        if (
            not isinstance(expected["bytes"], int)
            or not 0 <= expected["bytes"] <= MAX_FILE
            or not re.fullmatch(r"[a-f0-9]{64}", expected["sha256"])
            or not isinstance(expected["in_offline_collection"], bool)
        ):
            raise ValueError(f"Invalid manifest entry: {name}")
        raw = fetch(name)
        total += len(raw)
        if total > MAX_TOTAL:
            raise ValueError("Preview exceeds the total verification limit.")
        valid = (
            len(raw) == expected["bytes"]
            and hashlib.sha256(raw).hexdigest() == expected["sha256"]
        )
        rows.append({"file": name, "status": "PASS" if valid else "FAIL"})
    raw_archive = fetch("offline.zip")
    with zipfile.ZipFile(io.BytesIO(raw_archive)) as archive:
        packaged = {
            name for name, entry in files.items() if entry["in_offline_collection"]
        } | {"manifest.json"}
        infos = archive.infolist()
        if (
            len(infos) != len(packaged)
            or {item.filename for item in infos} != packaged
            or any(item.file_size > MAX_FILE for item in infos)
            or sum(item.file_size for item in infos) > MAX_TOTAL
        ):
            raise ValueError("Offline archive inventory or size does not match.")
        if archive.read("manifest.json") != raw_manifest:
            raise ValueError("Offline archive contains a different manifest.")
        for name in packaged - {"manifest.json"}:
            raw = archive.read(name)
            expected = files[name]
            if (
                len(raw) != expected["bytes"]
                or hashlib.sha256(raw).hexdigest() != expected["sha256"]
            ):
                raise ValueError(f"Offline archive checksum mismatch: {name}")
    rows.append({"file": "offline.zip", "status": "PASS"})
    return {
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
        "source_revision": manifest.get("revision"),
        "working_tree_dirty": manifest.get("working_tree_dirty"),
        "research_status": manifest.get("research_status"),
        "checks": rows,
        "limits": "Checks public file availability and byte integrity against the manifest, not browser behavior, source authenticity or scientific correctness.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--directory", type=Path)
    source.add_argument(
        "--url", help="Explicit HTTP(S) preview URL; makes bounded network requests"
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("Report exists; choose a fresh output path.")
    if args.url:
        parsed = urlsplit(args.url)
        if (
            parsed.scheme not in ("https", "http")
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            parser.error(
                "Use an HTTP(S) site root without credentials, query or fragment."
            )
        root = args.url.rstrip("/") + "/"

        def fetch(name):
            request = Request(
                root + name, headers={"User-Agent": "LitDelta-preview-verifier"}
            )
            with urlopen(request, timeout=20) as response:
                if response.status != 200:
                    raise ValueError(f"{name}: HTTP {response.status}")
                raw = response.read(MAX_FILE + 1)
            if len(raw) > MAX_FILE:
                raise ValueError(f"{name}: exceeds the 5 MB limit.")
            return raw
    else:
        root = str(args.directory.resolve())

        def fetch(name):
            if not safe_name(name):
                raise ValueError("Invalid artifact path.")
            path = args.directory / name
            if not path.resolve().is_relative_to(args.directory.resolve()):
                raise ValueError("Artifact symlink leaves the preview directory.")
            with path.open("rb") as handle:
                raw = handle.read(MAX_FILE + 1)
            if len(raw) > MAX_FILE:
                raise ValueError(f"{name}: exceeds the 5 MB limit.")
            return raw

    try:
        report = verify(fetch)
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        report = {"status": "FAIL", "error": str(exc)}
    report.update(source=root, checked_at=datetime.now(timezone.utc).isoformat())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Preview: {report['status']}; report: {args.out}")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
