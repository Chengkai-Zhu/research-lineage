import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_static_preview_is_same_render_and_portable_bundle(tmp_path):
    destination = tmp_path / "preview"
    command = [
        sys.executable,
        str(ROOT / "scripts/build_preview.py"),
        "--out",
        str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert len(json.loads(result.stdout)["created"]) == 7
    assert (destination / "index.html").read_bytes() == (
        destination / "map.html"
    ).read_bytes()
    canonical = json.loads(
        (ROOT / "src/research_lineage/data/attention-comparisons.json").read_text(
            encoding="utf-8"
        )
    )
    with zipfile.ZipFile(destination / "offline.zip") as archive:
        assert set(archive.namelist()) == {
            "map.html",
            "map.json",
            "map.svg",
            "review.md",
            "sources.md",
        }
        assert json.loads(archive.read("map.json")) == canonical
        assert archive.read("map.html") == (destination / "index.html").read_bytes()
    snapshot = (destination / "offline.zip").read_bytes()
    refused = subprocess.run(command, capture_output=True, text=True)
    assert refused.returncode != 0 and "exists" in refused.stderr
    assert (destination / "offline.zip").read_bytes() == snapshot
