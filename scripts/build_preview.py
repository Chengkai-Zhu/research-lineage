"""Build the public, curated LitDelta preview; never accept private map inputs."""

import argparse
import hashlib
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

from package_skill import package  # noqa: E402
from research_lineage import __version__  # noqa: E402
from research_lineage.core import dump, load_map  # noqa: E402
from research_lineage.render import ASSETS, build  # noqa: E402
from research_lineage.research_scope import audit_run  # noqa: E402


def source_revision():
    """Record local provenance without requiring Git or making network requests."""
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()
        )
    except (OSError, subprocess.SubprocessError):
        return {"revision": None, "working_tree_dirty": None}
    return {
        "revision": revision if re.fullmatch(r"[a-f0-9]{40}", revision) else None,
        "working_tree_dirty": dirty,
    }


def landing(maps, research_status, skill_name, provenance, *, offline=False):
    values = {
        "STYLE": (ASSETS / "preview.css").read_text(encoding="utf-8"),
        "JS": (ASSETS / "preview.js").read_text(encoding="utf-8"),
        "OFFLINE_ACTION": (
            '<span class="quiet">You have the complete offline collection.</span>'
            if offline
            else '<a class="button" href="offline.zip" download>Download offline collection ↓</a>'
        ),
        "SKILL_FILE": html.escape(skill_name, quote=True),
        "RESEARCH_STATUS": html.escape(research_status),
        "PROVENANCE": (
            "Preview tools "
            + __version__
            + " · "
            + (
                "source " + provenance["revision"][:12]
                if provenance["revision"]
                else "source revision unavailable"
            )
            + (" · local changes" if provenance["working_tree_dirty"] else "")
        ),
    }
    for key, data in zip(
        ("COMPARISON_COUNTS", "AUTHOR_COUNTS", "RESEARCH_COUNTS"), maps
    ):
        values[key] = (
            f"{len(data['works'])} "
            + ("paper" if len(data["works"]) == 1 else "papers")
            + f" · {len(data['results'])} results"
        )
    template = (ASSETS / "preview.html").read_text(encoding="utf-8")
    return re.sub(r"@@([A-Z_]+)@@", lambda match: values[match[1]], template)


def source_notes(source, destination, revision):
    """Keep original source notes but make checkout references explicit online links."""

    def link(match):
        target = urlsplit(match[2])
        if target.scheme or match[2].startswith("#"):
            return match[0]
        path = (source.parent / target.path).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("A source-note link leaves the repository.")
        relative = quote(path.relative_to(ROOT).as_posix(), safe="/")
        url = f"https://github.com/Chengkai-Zhu/litdelta/blob/{revision or 'main'}/{relative}"
        if target.fragment:
            url += "#" + target.fragment
        return f"{match[1]}({url})"

    text = re.sub(
        r"(\[[^\]]+\])\(([^)\s]+)\)", link, source.read_text(encoding="utf-8")
    )
    destination.write_text(
        "# Delivered reading example\n\n[Open this collection's reader](map.html).\n\n"
        "The original checkout notes follow. Their repository references open the\n"
        "pinned public source online; they are not additional files in this ZIP.\n"
        "Historical issue-status statements belong to that source record.\n\n---\n\n"
        + text,
        encoding="utf-8",
    )


def preview(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError("Preview output exists; choose a fresh folder.")
    data = load_map(ROOT / "src/research_lineage/data/attention-comparisons.json")
    paths = build(data, destination)
    nmt = load_map(ROOT / "examples/nmt-attention/map.json")
    research = load_map(ROOT / "docs/test-reports/surface-code-rerun/map.json")
    research_audit = audit_run(
        ROOT / "docs/test-reports/surface-code-rerun/manifest.json"
    )
    if research_audit["status"] == "FAIL":
        raise ValueError("The recorded public research example failed its audit.")
    paths += build(nmt, destination / "nmt")
    paths += build(research, destination / "surface-code")
    skill = package(destination / "downloads")
    provenance = source_revision()
    for name, offline in (("index.html", False), ("START-HERE.html", True)):
        (destination / name).write_text(
            landing(
                (data, nmt, research),
                research_audit["status"],
                skill.name,
                provenance,
                offline=offline,
            ),
            encoding="utf-8",
        )
    for source, name in (
        ("examples/attention-comparisons/README.md", "sources.md"),
        ("examples/nmt-attention/README.md", "nmt/sources.md"),
        ("docs/test-reports/surface-code-rerun/README.md", "surface-code/sources.md"),
    ):
        source_notes(ROOT / source, destination / name, provenance["revision"])
    (destination / "surface-code/audit.json").write_text(
        dump(research_audit), encoding="utf-8"
    )
    (destination / "README.txt").write_text(
        "LitDelta offline collection\n\n"
        "Extract this ZIP before opening START-HERE.html in your browser.\n"
        "Each example's map.html also opens independently without Python or a server.\n"
        "Source links need a connection only when you choose to open them.\n"
        "The downloads folder includes the current Python 3.11+ agent skill.\n"
        "Annotations remain proposed; the actual research run remains PARTIAL.\n"
        "manifest.json records file checksums and the source revision.\n",
        encoding="utf-8",
    )
    entries = {}
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            raw = path.read_bytes()
            name = path.relative_to(destination).as_posix()
            entries[name] = {
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "in_offline_collection": name != "index.html",
            }
    manifest = {
        "product": "LitDelta",
        "version": __version__,
        **provenance,
        "research_status": research_audit["status"],
        "files": entries,
    }
    (destination / "manifest.json").write_text(dump(manifest), encoding="utf-8")
    archive = destination / "offline.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        names = [
            name for name, item in entries.items() if item["in_offline_collection"]
        ] + ["manifest.json"]
        for name in names:
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            handle.writestr(entry, (destination / name).read_bytes())
    return sorted(str(path) for path in destination.rglob("*") if path.is_file())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        print(dump({"created": preview(args.out)}))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
