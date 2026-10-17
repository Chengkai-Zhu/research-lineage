import json
import hashlib
import subprocess
import sys
import zipfile
import runpy
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
    created = json.loads(result.stdout)["created"]
    assert str(destination / "index.html") in created
    landing = (destination / "index.html").read_text(encoding="utf-8")
    assert "nmt/map.html#author=Yoshua%20Bengio" in landing
    assert "surface-code/map.html#overview" in landing
    assert "PARTIAL RESEARCH" in landing and "offline.zip" in landing
    canonical = json.loads(
        (ROOT / "src/research_lineage/data/attention-comparisons.json").read_text(
            encoding="utf-8"
        )
    )
    with zipfile.ZipFile(destination / "offline.zip") as archive:
        assert {
            "map.html",
            "map.json",
            "map.svg",
            "review.md",
            "sources.md",
            "START-HERE.html",
            "manifest.json",
            "nmt/map.html",
            "surface-code/map.html",
            "surface-code/audit.json",
            "downloads/research-lineage-skill-0.2.0.zip",
        } <= set(archive.namelist())
        assert "index.html" not in archive.namelist()
        assert json.loads(archive.read("map.json")) == canonical
        assert archive.read("map.html") == (destination / "map.html").read_bytes()
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest == json.loads((destination / "manifest.json").read_text())
        assert manifest["research_status"] == "PARTIAL"
        for name, item in manifest["files"].items():
            raw = (destination / name).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == item["sha256"]
            assert len(raw) == item["bytes"]
            if item["in_offline_collection"]:
                assert archive.read(name) == raw
        assert b"offline.zip" not in archive.read("START-HERE.html")
        assert (
            json.loads(archive.read("surface-code/audit.json"))["status"] == "PARTIAL"
        )
        assert len(json.loads(archive.read("surface-code/map.json"))["works"]) == 52
        assert len(json.loads(archive.read("nmt/map.json"))["works"]) == 6
        notes = archive.read("surface-code/sources.md").decode()
        assert "[Open this collection's reader](map.html)" in notes
        assert "](research-log.json)" not in notes
        assert "/docs/test-reports/surface-code-rerun/research-log.json)" in notes
        nmt_notes = archive.read("nmt/sources.md").decode()
        assert "](../../docs/" not in nmt_notes
        assert "/docs/test-reports/test-feature-20261017-nmt.md)" in nmt_notes
    snapshot = (destination / "offline.zip").read_bytes()
    refused = subprocess.run(command, capture_output=True, text=True)
    assert refused.returncode != 0 and "exists" in refused.stderr
    assert (destination / "offline.zip").read_bytes() == snapshot
    verifier = [
        sys.executable,
        str(ROOT / "scripts/verify_preview.py"),
        "--directory",
        str(destination),
    ]
    good = tmp_path / "preview-verified.json"
    verified = subprocess.run(
        verifier + ["--out", str(good)], capture_output=True, text=True
    )
    assert verified.returncode == 0, verified.stderr
    observed = json.loads(good.read_text())
    assert observed["status"] == "PASS" and observed["research_status"] == "PARTIAL"
    assert all(item["status"] == "PASS" for item in observed["checks"])
    (destination / "map.html").write_text("tampered", encoding="utf-8")
    bad = tmp_path / "preview-tampered.json"
    rejected = subprocess.run(
        verifier + ["--out", str(bad)], capture_output=True, text=True
    )
    assert rejected.returncode == 2
    failed = json.loads(bad.read_text())
    assert failed["status"] == "FAIL"
    assert {"file": "map.html", "status": "FAIL"} in failed["checks"]


def test_preview_verifier_rejects_manifest_path_escape_before_fetching():
    verify = runpy.run_path(str(ROOT / "scripts/verify_preview.py"))["verify"]
    fetched = []

    def fetch(name):
        fetched.append(name)
        return json.dumps(
            {
                "product": "LitDelta",
                "files": {"../private.txt": {"sha256": "a" * 64}},
            }
        ).encode()

    import pytest

    with pytest.raises(ValueError, match="file paths"):
        verify(fetch)
    assert fetched == ["manifest.json"]
