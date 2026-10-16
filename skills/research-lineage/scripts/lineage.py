"""Run from a repository checkout or the self-contained release ZIP."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
runtime = HERE / "vendor"
if not (runtime / "research_lineage").is_dir():
    runtime = HERE.parents[2] / "src"
if not (runtime / "research_lineage").is_dir():
    raise SystemExit(
        "Runtime not found. Use the complete research-lineage skill ZIP from GitHub "
        "Releases, or keep this skill inside its repository checkout."
    )
sys.path.insert(0, str(runtime))

from research_lineage.cli import main  # noqa: E402

raise SystemExit(main())
