# Arguo developer tasks.
# Recipe lines below use real tabs. Edit this file with a tab-aware editor.

PYTHON ?= python3

.DEFAULT_GOAL := help

.PHONY: help install test lint fmt validate catalog docs-index site-stats package run-cli clean check

help:
	@echo "Arguo: available targets"
	@echo "  make install     Install the Python package with dev dependencies"
	@echo "  make test        Run the offline test suite"
	@echo "  make lint        Run ruff over python, tests, scripts, evals, examples"
	@echo "  make fmt         Apply ruff formatting"
	@echo "  make validate    Run the resource, per-file, and skill validators"
	@echo "  make catalog     Rebuild the merged catalog from data/resources"
	@echo "  make docs-index  Regenerate the docs index and llms.txt outputs"
	@echo "  make site-stats  Regenerate public/data/site-stats.json when the tool exists"
	@echo "  make run-cli     Run the CLI module from the repo checkout"
	@echo "  make check       Run lint, test, and validate together"
	@echo "  make clean       Remove Python caches and local build artifacts"

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/ -q

lint:
	ruff check python/ tests/ scripts/ evals/ examples/

fmt:
	ruff format python/ tests/ scripts/ evals/ examples/

validate:
	$(PYTHON) scripts/validate_resources.py
	@for f in data/resources/*.jsonl; do \
		$(PYTHON) scripts/validate_catalog_file.py "$$f" || exit 1; \
	done
	$(PYTHON) scripts/validate_skill.py all

catalog:
	$(PYTHON) scripts/build_resource_catalog.py
	$(PYTHON) tools/generate_site_stats.py

package:
	git archive --format=zip --prefix=arguo/ -o public/arguo-latest.zip HEAD -- . ":(exclude)public/arguo-latest.zip" ":(exclude)public/arguo-latest.tar.gz"
	git archive --format=tar.gz --prefix=arguo/ -o public/arguo-latest.tar.gz HEAD -- . ":(exclude)public/arguo-latest.zip" ":(exclude)public/arguo-latest.tar.gz"
	@echo "Archives written to public/arguo-latest.zip and public/arguo-latest.tar.gz"

docs-index:
	$(PYTHON) scripts/generate_docs.py

site-stats:
	@if [ -f tools/generate_site_stats.py ]; then \
		$(PYTHON) tools/generate_site_stats.py; \
	else \
		echo "note: tools/generate_site_stats.py does not exist yet; public/data/site-stats.json is maintained manually"; \
	fi

run-cli:
	PYTHONPATH=python $(PYTHON) -m arguo

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -not -path "./node_modules/*" -not -path "./.git/*" -exec rm -rf {} +

check: lint test validate
	@echo "check: lint, test, and validate all passed"
