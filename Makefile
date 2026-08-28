PYTHON ?= python
.PHONY: setup validate logs test check clean
setup:
	$(PYTHON) -m pip install -e ".[dev]"
validate:
	$(PYTHON) -m evaluation.validate_benchmark
logs:
	$(PYTHON) scripts/generate_failing_logs.py
test:
	$(PYTHON) -m pytest -q tests
check: validate logs test
clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
