# Intentional Semantic Reasoning Engine (ISRE)

[![CI](https://github.com/abhi9199-tech42/ISRE/actions/workflows/ci.yml/badge.svg)](https://github.com/abhi9199-tech42/ISRE/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A deterministic, 5-layer semantic reasoning system that converts natural language into language-agnostic semantic primitives, builds explicit intent graphs, generates multiple competing reasoning paths, and reconstructs decisions into text, code, markdown, or action plans.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ISRE Pipeline (v0.1)                      │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Semantic Compression                              │
│  ├── Text → ConceptMapper                                   │
│  ├── Speech → PhonemeExtractor                              │
│  └── Multimodal → MultimodalProcessor                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Intent Graph Construction                         │
│  └── IntentGraphBuilder (nodes, edges, conflicts)           │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Designed Reasoning Engine                         │
│  ├── ReasoningPathGenerator (multi-path branching)          │
│  ├── CompetitiveSelector (multi-objective scoring)          │
│  └── Oscillatory Dynamics (Hopf bifurcation modulation)     │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: World Knowledge Integration                       │
│  ├── KnowledgeQueryEngine (pluggable backends)              │
│  ├── KnowledgeGapDetector (void-filling)                   │
│  ├── PhysicsRuleEngine (physical constraints)               │
│  └── DomainLogicManager (plugin system)                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Semantic Reconstruction                           │
│  ├── LanguageGenerator → text                               │
│  ├── CodeGenerator → code                                   │
│  ├── MarkdownGenerator → markdown                           │
│  ├── ActionPlanner → structured actions                     │
│  └── MultiFormatTranslator (coordinator)                    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
git clone https://github.com/abhi9199-tech42/ISRE.git
cd ISRE

python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate

pip install -e ".[test]"
```

## Quick Start

### Python API

```python
from isre.pipeline import ISREPipeline

pipeline = ISREPipeline()

# Process natural language
result = pipeline.process("Run quickly but stay slow.", "text")

# Multi-format output
print(result["outputs"]["text"])     # Natural language
print(result["outputs"]["code"])     # Python code
print(result["outputs"]["markdown"]) # Markdown document
print(result["outputs"]["action"])   # Action plan

# Trace every processing stage
trace = pipeline.get_trace(result["request_id"])
for entry in trace:
    print(f"{entry['stage']}: {entry['data']}")
```

### REST API

```bash
# Install server extras
pip install -e ".[server]"

# Start the API server
isre-server

# Or via uvicorn directly
uvicorn isre.api.server:app --host 0.0.0.0 --port 8000
```

```bash
# Process input
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"input": "run quickly but stay slow"}'

# Health check
curl http://localhost:8000/health

# Get processing trace
curl http://localhost:8000/trace/<request_id>
```

### Docker

```bash
# Build and run
docker compose up --build

# Or build manually
docker build -t isre .
docker run -p 8000:8000 isre
```

### CLI

```bash
# Process text
isre "run quickly but stay slow"

# JSON output with trace
isre "apple" --json --trace

# Enable debug logging
isre "fly to the moon" --verbose

# All formats
isre "stay slow" --format text code action markdown
```

## Features

### Deterministic Processing
- **SHA-256 hashing** for consistent, deterministic primitive IDs
- **No probabilistic next-token prediction** — every output is derived from explicit transformations
- **Full traceability** of every decision through the pipeline

### Conflict Resolution
- **Explicit conflict detection** between semantic concepts (30+ opposition pairs + heuristic patterns)
- **Multi-path generation** with branching strategies for conflict resolution
- **Oscillatory dynamics** (Hopf bifurcation) for competitive path selection

### Knowledge Integration
- **Gap detection** instead of hallucination — system admits what it doesn't know
- **Pluggable knowledge backends**: JSON file, SQLite, or custom via `KnowledgeBackend` ABC
- **Domain-specific logic modules** and physics constraint engine

### Multi-Modal Output
All four output formats are generated from the same internal `ReasoningDecision`:

| Format | Generator | Description |
|--------|-----------|-------------|
| `text` | `LanguageGenerator` | Natural language explanation |
| `code` | `CodeGenerator` | Executable code snippet |
| `markdown` | `MarkdownGenerator` | Formatted decision document |
| `action` | `ActionPlanner` | Structured action plan |

## Configuration

The system supports JSON, YAML, and environment variable configuration:

```json
{
  "memory_threshold_mb": 1000.0,
  "compression": {
    "enable_emoji": true
  },
  "reasoning": {
    "oscillator_frequency": 1.0,
    "oscillator_bifurcation": 1.0,
    "max_oscillation_steps": 50
  },
  "knowledge": {
    "backend": "json",
    "json_path": "knowledge.json"
  },
  "reconstruction": {
    "enable_markdown": true
  }
}
```

Or via environment variables with `ISRE_` prefix:

```bash
export ISRE_MEMORY_THRESHOLD_MB=1000.0
export ISRE_REASONING_OSCILLATOR_FREQUENCY=0.5
```

## Development

```bash
# Install with all extras
pip install -e ".[all]"

# Run all tests
pytest tests/

# With coverage
pytest --cov=isre --cov-report=html

# Lint and type-check
ruff check isre/
mypy isre/

# Run benchmark
python scripts/benchmark.py

# Start dev server
make serve

# Build Docker image
docker compose build

# Build package
python -m build
```

## Project Structure

```
ISRE/
├── isre/
│   ├── __init__.py
│   ├── types.py                     # Enums: IntentType, EdgeType, SemanticType
│   ├── config.py                    # Pydantic config system (JSON/YAML/env)
│   ├── cli.py                       # CLI entry point
│   ├── models/                      # Pydantic data models
│   │   ├── primitives.py
│   │   ├── intent.py
│   │   └── reasoning.py
│   ├── compression/                 # Layer 1
│   │   ├── base.py
│   │   ├── text.py
│   │   ├── speech.py
│   │   └── multimodal.py
│   ├── graph/                       # Layer 2
│   │   └── builder.py
│   ├── reasoning/                   # Layer 3
│   │   ├── generator.py
│   │   ├── selection.py
│   │   └── dynamics.py
│   ├── knowledge/                   # Layer 4
│   │   ├── engine.py
│   │   ├── gaps.py
│   │   ├── physics.py
│   │   ├── domain.py
│   │   └── backends/
│   │       ├── base.py
│   │       └── json_backend.py
│   ├── reconstruction/              # Layer 5
│   │   ├── base.py
│   │   ├── language.py
│   │   ├── code.py
│   │   ├── action.py
│   │   ├── markdown.py
│   │   └── translator.py
│   ├── pipeline/                    # Orchestrator
│   │   └── orchestrator.py
│   └── utils/
│       ├── resources.py
│       └── architectural_validator.py
├── tests/                           # 69 tests (pytest + Hypothesis)
├── examples/                        # Demo scripts
├── docs/                            # Additional documentation
├── roadmapproduction.md             # Production roadmap
├── pyproject.toml                   # Build & tool config
├── tox.ini                          # Multi-Python testing
├── Makefile                         # Common commands
└── LICENSE                          # GPL-3.0
```

## API Reference

### `ISREPipeline`

```python
pipeline = ISREPipeline(memory_threshold_mb=500.0, config=None)
result = pipeline.process(input, modality="text", target_formats=None)
trace = pipeline.get_trace(request_id)
pipeline.clear()
```

### `ReasoningDecision`

```python
decision = ReasoningDecision(
    selected_path=path,          # The winning ReasoningPath
    justification="string",      # Why this path was chosen
    confidence=0.0..1.0,         # Confidence score
    alternative_paths=[...],     # Alternative ReasoningPath objects
    convergence_metadata={...}   # Oscillatory dynamics metadata
)
```

### Knowledge Backends

```python
from isre.knowledge.backends import JSONKnowledgeBackend, SQLiteKnowledgeBackend

# Custom backend
class MyBackend(KnowledgeBackend):
    def query(self, concept_key): ...
    def update(self, concept_key, data): ...
    def query_concepts(self, concepts): ...
    def bulk_update(self, data): ...
```

## Roadmap

See [roadmapproduction.md](roadmapproduction.md) for the production roadmap.

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
