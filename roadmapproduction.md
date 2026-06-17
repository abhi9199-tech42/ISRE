# ISRE Production Roadmap

## Phase 0: Critical Bug Fixes (Week 1)

### 0.1 Missing Dependency
- Add `psutil>=5.9.0` to `pyproject.toml` dependencies
- File: `pyproject.toml:5-7`

### 0.2 Duplicate Imports
- Remove duplicate lines in `isre/models/__init__.py:2,5`
- Files: `isre/models/__init__.py`

### 0.3 Pydantic Deprecation
- Replace `p.dict()` with `p.model_dump()` in `isre/pipeline/orchestrator.py:58`
- Audit all `.dict()` calls across codebase

### 0.4 Missing `__init__.py`
- Create `isre/utils/__init__.py`

### 0.5 Type Annotation Issue
- `list[str]` in `isre/reconstruction/translator.py:25` — use `List[str]` for Python 3.8 compat or set min Python version

---

## Phase 1: Project Infrastructure (Week 1-2)

### 1.1 Essential Files
- [ ] Create `README.md` with project overview, installation, usage, architecture
- [ ] Create `.gitignore` (Python: `__pycache__`, `.pytest_cache`, `*.pyc`, `.hypothesis`, `dist`, `*.egg-info`)
- [ ] Create `LICENSE` (MIT or Apache 2.0)
- [ ] Create `requirements.txt` from `pyproject.toml` for wider compatibility

### 1.2 Dev Tooling
- [ ] Add `[project.scripts]` entry point in `pyproject.toml` → `isre = "isre.cli:main"`
- [ ] Create `isre/cli.py` with argparse CLI
- [ ] Add `ruff.toml` or `[tool.ruff]` in `pyproject.toml` for linting
- [ ] Add `[tool.mypy]` config for type checking
- [ ] Add `[tool.black]` or `[tool.ruff.format]` for formatting
- [ ] Create `Makefile` or `justfile` with common commands (lint, test, format, typecheck)

### 1.3 CI/CD
- [ ] Create `.github/workflows/ci.yml` — run tests, lint, typecheck on push/PR
- [ ] Create `.github/workflows/release.yml` — publish to PyPI on tag

### 1.4 Clean Root Directory
- [ ] Move 16 `test_*.txt` output files into `test_outputs/` or delete them
- [ ] Move `verify_isre.py`, `console_test.py`, `demo_paraphrase_and_conflict.py`, `test_paraphrase_consistency.py` into `scripts/` or `examples/`
- [ ] Move `final_coverage_report.txt` to `reports/` or delete

---

## Phase 2: Core Bug Fixes & Code Quality (Week 2-3)

### 2.1 Semantic Coherence Placeholder
- `isre/reasoning/selection.py:79-84` — `_score_semantic_coherence()` always returns 0.8
- Implement real coherence scoring based on:
  - Semantic similarity between consecutive nodes
  - Concept relatedness via knowledge base
  - Path continuity (edge type consistency)

### 2.2 Oscillatory Gate Not Integrated
- `isre/pipeline/orchestrator.py:118-137` — `_ensure_convergence()` creates a fresh `OscillatoryGate` each time, runs it, but never uses the output
- Fix: Pass `paths` into the gate, use activation values to modulate path scores in `CompetitiveSelector`

### 2.3 Hardcoded Conflict Detection
- `isre/graph/builder.py:96-99` — Only 2 oppositions hardcoded
- Expand to: antonym database, semantic distance threshold, configurable conflict rules
- Create `isre/knowledge/antonyms.py` or integrate with WordNet

### 2.4 ConceptMapper Toy Mappings
- `isre/compression/text.py:15-25` — Only 9 mappings
- Options:
  - Integrate NLTK WordNet for hypernym extraction
  - Create comprehensive concept dictionary (1000+ entries)
  - Add config file for custom mappings
  - Add fallback to character-level hashing for unknown words

### 2.5 Thread Safety
- `isre/pipeline/orchestrator.py` — shared `trace_log`, `knowledge_engine` across threads
- Add `threading.Lock` to `ISREPipeline` for concurrent access
- Or make pipeline instances thread-local

### 2.6 Resource Monitor Robustness
- `isre/utils/resources.py:2` — hard import of `psutil` with no fallback
- Add try/except with mock fallback for environments without psutil

---

## Phase 3: Architecture Improvements (Week 3-5)

### 3.1 Configuration System
- Create `isre/config.py` with Pydantic `BaseSettings`
- Support YAML/TOML config files
- Make all hardcoded values configurable:
  - Semantic maps
  - Conflict rules
  - Scoring weights
  - Memory thresholds
  - Oscillator parameters

### 3.2 Knowledge Base Upgrade
- Replace in-memory dict with pluggable storage:
  - SQLite (default)
  - PostgreSQL (optional)
  - JSON file (development)
- Create `isre/knowledge/backends/` with:
  - `sqlite.py`
  - `json_file.py`
  - `base.py` (abstract interface)

### 3.3 Expand Semantic Compression
- Create `isre/compression/semantic_map.json` — externalized concept dictionary
- Add `isre/compression/embedding.py` — optional sentence-transformer compression
- Add `isre/compression/tokenizer.py` — BPE/token-level compression option

### 3.4 Reasoning Engine Improvements
- Replace simple conflict branching with CSP solver for multi-conflict graphs
- Add `isre/reasoning/csp.py` — constraint satisfaction solver
- Integrate oscillatory dynamics into path scoring (not just logging)

### 3.5 Reconstruction Improvements
- Add `isre/reconstruction/markdown.py` — Markdown output
- Add `isre/reconstruction/yaml.py` — YAML output
- Add `isre/reconstruction/natural_language.py` — template-based NLG with grammar rules
- Make reconstructors configurable and extensible

---

## Phase 4: Testing & Quality Assurance (Week 5-7)

### 4.1 Test Infrastructure
- [ ] Create `pytest.ini` or enhance `pyproject.toml` pytest config
- [ ] Add `conftest.py` with more shared fixtures
- [ ] Set up `coverage` with minimum threshold (80%+)
- [ ] Add `tox.ini` for multi-Python testing

### 4.2 Fix Existing Tests
- [ ] Remove internal state manipulation in tests (fragile mocks)
- [ ] Add proper unit tests for each module with clear assertions
- [ ] Fix test naming inconsistencies

### 4.3 New Test Categories
- [ ] `tests/unit/` — isolated module tests
- [ ] `tests/integration/` — pipeline flow tests
- [ ] `tests/e2e/` — full system tests
- [ ] `tests/performance/` — benchmarks with `pytest-benchmark`
- [ ] `tests/security/` — input sanitization tests

### 4.4 Property-Based Testing Expansion
- [ ] Expand Hypothesis tests to cover edge cases
- [ ] Add invariant checks for graph operations
- [ ] Add stateful testing for pipeline

---

## Phase 5: Documentation (Week 7-8)

### 5.1 Core Documentation
- [ ] `README.md` — overview, install, quickstart, architecture diagram
- [ ] `docs/architecture.md` — 5-layer architecture deep dive
- [ ] `docs/api.md` — auto-generated from docstrings (sphinx/mkdocs)
- [ ] `docs/configuration.md` — all config options
- [ ] `docs/contributing.md` — development setup, coding standards

### 5.2 Reduce Documentation Claims
- [ ] Update `COMPLETE_VALIDATION_SUMMARY.md` to reflect actual state
- [ ] Remove "FULLY VALIDATED AND OPERATIONAL" claims
- [ ] Add "Prototype Status" disclaimers

### 5.3 Examples & Tutorials
- [ ] Create `examples/basic_usage.py`
- [ ] Create `examples/custom_compressor.py`
- [ ] Create `examples/custom_domain.py`
- [ ] Create `examples/advanced_config.py`

---

## Phase 6: Production Hardening (Week 8-10)

### 6.1 Logging
- Replace `print` statements with `logging` module
- Add structured logging (JSON format)
- Create `isre/logging_config.py`

### 6.2 Error Handling
- Create custom exception hierarchy:
  - `ISREError` (base)
  - `CompressionError`
  - `GraphError`
  - `ReasoningError`
  - `KnowledgeError`
  - `ReconstructionError`
- Add proper error messages and recovery

### 6.3 Performance
- [ ] Add caching layer for frequent queries
- [ ] Optimize O(N^2) conflict detection with spatial indexing
- [ ] Add async support for knowledge queries
- [ ] Profile and optimize hot paths

### 6.4 Monitoring
- [ ] Add metrics collection (Prometheus format)
- [ ] Add health check endpoint
- [ ] Add request tracing (OpenTelemetry)

### 6.5 Security
- [ ] Input sanitization for all user inputs
- [ ] Rate limiting for API endpoints
- [ ] Audit logging

---

## Phase 7: Packaging & Distribution (Week 10-11)

### 7.1 Python Package
- [ ] Finalize `pyproject.toml` with all metadata
- [ ] Add `py.typed` marker for PEP 561
- [ ] Build and test wheel/sdist
- [ ] Publish to PyPI

### 7.2 Docker
- [ ] Create `Dockerfile`
- [ ] Create `docker-compose.yml` for development
- [ ] Create `.dockerignore`

### 7.3 API Server (Optional)
- [ ] Create `isre/server/` with FastAPI
- [ ] REST API endpoints: `/process`, `/health`, `/metrics`
- [ ] OpenAPI documentation

---

## Priority Summary

| Priority | Phase | Effort | Impact |
|----------|-------|--------|--------|
| P0 | Phase 0: Bug Fixes | 1-2 days | Critical |
| P1 | Phase 1: Infrastructure | 1 week | High |
| P2 | Phase 2: Core Fixes | 1-2 weeks | High |
| P3 | Phase 3: Architecture | 2-3 weeks | Medium-High |
| P4 | Phase 4: Testing | 2 weeks | Medium |
| P5 | Phase 5: Documentation | 1 week | Medium |
| P6 | Phase 6: Production | 2 weeks | Medium |
| P7 | Phase 7: Packaging | 1 week | Low-Medium |

---

## Estimated Total Timeline: 10-12 weeks

### Quick Wins (Do First)
1. Fix missing `psutil` dependency
2. Remove duplicate imports
3. Replace deprecated `.dict()` calls
4. Create `.gitignore`
5. Create `README.md`

### High-Impact Items
1. Implement real semantic coherence scoring
2. Integrate oscillatory gate into path selection
3. Expand concept mappings
4. Add configuration system
5. Upgrade knowledge base to SQLite

### Long-Term Goals
1. CSP solver for multi-conflict reasoning
2. Embedding-based compression
3. REST API server
4. Docker deployment
5. PyPI publication
