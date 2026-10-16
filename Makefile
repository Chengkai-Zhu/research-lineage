.PHONY: help install test lint format check demo package
PYTHON ?= python
help:
	@echo "Targets: install test lint format check demo package"
install:
	$(PYTHON) -m pip install -e ".[dev]"
test:
	$(PYTHON) -m pytest
lint:
	$(PYTHON) -m ruff check src tests scripts skills
format:
	$(PYTHON) -m ruff format src tests scripts skills
check: lint test
demo:
	$(PYTHON) -m research_lineage demo --out output/demo
package:
	$(PYTHON) scripts/package_skill.py --out dist
