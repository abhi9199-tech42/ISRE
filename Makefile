.PHONY: install install-all install-dev install-server test test-cov lint format typecheck clean build run serve docker-build

install:
	pip install -e .

install-all:
	pip install -e ".[all]"

install-dev:
	pip install -e ".[test,dev]"

install-server:
	pip install -e ".[server]"

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

serve:
	python -m isre.api.server

docker-build:
	docker compose build

benchmark:
	python scripts/benchmark.py
