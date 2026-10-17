"""Build the public, curated LitDelta preview; never accept private map inputs."""

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_lineage.core import dump, load_map  # noqa: E402
from research_lineage.render import build  # noqa: E402


def preview(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError("Preview output exists; choose a fresh folder.")
    data = load_map(ROOT / "src/research_lineage/data/attention-comparisons.json")
    paths = build(data, destination)
    shutil.copyfile(destination / "map.html", destination / "index.html")
    notes = ROOT / "examples/attention-comparisons/README.md"
    shutil.copyfile(notes, destination / "sources.md")
    archive = destination / "offline.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for name in ("map.html", "map.svg", "map.json", "review.md", "sources.md"):
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            handle.writestr(entry, (destination / name).read_bytes())
    return paths + [
        str(destination / name) for name in ("index.html", "offline.zip", "sources.md")
    ]


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
