.PHONY: install install-dev test lint format typecheck clean build

install:
	pip install -e .

install-dev:
	pip install -e ".[test,dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=isre --cov-report=html

lint:
	ruff check isre/

format:
	ruff format isre/

typecheck:
	mypy isre/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:
	python -m build

run:
	python -m isre.cli
