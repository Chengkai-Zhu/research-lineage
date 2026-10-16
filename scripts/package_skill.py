"""Create a portable skill ZIP from canonical runtime sources."""

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from research_lineage import __version__  # noqa: E402


def package(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"research-lineage-skill-{__version__}.zip"
    files = []
    for base, prefix in (
        (ROOT / "skills" / "research-lineage", "research-lineage"),
        (
            ROOT / "src" / "research_lineage",
            "research-lineage/scripts/vendor/research_lineage",
        ),
    ):
        for path in sorted(base.rglob("*")):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
            ):
                files.append((path, prefix + "/" + path.relative_to(base).as_posix()))
    files.append((ROOT / "LICENSE", "research-lineage/LICENSE"))
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in files:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return output


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", default="dist")
    print(package(cli.parse_args().out))
