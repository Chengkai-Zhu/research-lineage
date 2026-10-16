import json
from pathlib import Path

import pytest


@pytest.fixture
def sample():
    path = Path(__file__).parents[1] / "src/research_lineage/data/qsp-qsvt.json"
    return json.loads(path.read_text(encoding="utf-8"))
