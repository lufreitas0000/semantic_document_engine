# Makefile

.PHONY: test lint

test:
	lint-imports
	xenon --max-absolute B --max-modules B --max-average A semantic_engine/
	radon cc semantic_engine/ -a -s
	python -m mypy semantic_engine/
	python -m pytest --cov=semantic_engine --cov-fail-under=90 semantic_engine/tests/
