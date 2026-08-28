PYTHON ?= python
.PHONY: setup validate logs inspect test check clean
setup:
	$(PYTHON) -m pip install -e ".[dev]"
validate:
	$(PYTHON) -m evaluation.validate_benchmark
logs:
	$(PYTHON) scripts/generate_failing_logs.py
inspect:
	$(PYTHON) -m evaluation.evaluator --mode inspect
test:
	$(PYTHON) -m pytest -q tests
check: validate logs inspect test
clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]"
