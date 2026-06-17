# Intentional Semantic Reasoning Engine (ISRE)

A deterministic, 5-layer semantic reasoning system that converts natural language into language-agnostic semantic primitives, builds explicit intent graphs, generates multiple competing reasoning paths, and reconstructs decisions into text, code, or actions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ISRE Pipeline                            │
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
│  ├── ReasoningPathGenerator (multi-path)                    │
│  ├── CompetitiveSelector (multi-objective scoring)          │
│  └── OscillatoryGate (Hopf bifurcation dynamics)            │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: World Knowledge Integration                       │
│  ├── KnowledgeQueryEngine (external KB interface)           │
│  ├── KnowledgeGapDetector (missing knowledge)               │
│  ├── PhysicsRuleEngine (physical constraints)               │
│  └── DomainLogicManager (plugin system)                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 5: Semantic Reconstruction                           │
│  ├── LanguageGenerator (→ text)                             │
│  ├── CodeGenerator (→ code)                                 │
│  ├── ActionPlanner (→ action plan)                          │
│  └── MultiFormatTranslator (coordinator)                    │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/abhi9199-tech42/ISRE.git
cd ISRE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[test]"
```

## Quick Start

```python
from isre.pipeline import ISREPipeline

# Initialize the pipeline
pipeline = ISREPipeline()

# Process natural language input
result = pipeline.process("Run quickly but stay slow.", "text")

# Access outputs
print(result["outputs"]["text"])   # Text output
print(result["outputs"]["code"])   # Code output
print(result["outputs"]["action"]) # Action plan

# Inspect reasoning trace
trace = pipeline.get_trace(result["request_id"])
for entry in trace:
    print(f"{entry['stage']}: {entry['data']}")
```

## Features

### Deterministic Processing
- SHA-256 hashing for consistent primitive IDs
- No probabilistic next-token prediction
- Full traceability of every decision

### Conflict Resolution
- Explicit conflict detection between semantic concepts
- Multi-path generation with branching strategies
- Oscillatory dynamics (Hopf bifurcations) for path selection

### Knowledge Integration
- Gap detection instead of hallucination
- Pluggable knowledge backends (SQLite, PostgreSQL, JSON)
- Domain-specific logic modules

### Multi-Modal Output
- Natural language generation
- Code snippet generation
- Structured action plans

## Configuration

Create a `config.toml` in your project root:

```toml
[pipeline]
memory_threshold_mb = 500.0

[compression]
semantic_map_path = "path/to/custom_map.json"

[reasoning]
oscillator_frequency = 1.0
oscillator_bifurcation = 1.0

[knowledge]
backend = "sqlite"
db_path = "knowledge.db"
```

## Development

### Setup

```bash
pip install -e ".[test]"
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=isre --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check isre/

# Formatting
ruff format isre/

# Type checking
mypy isre/
```

## Project Structure

```
ISRE/
├── isre/
│   ├── __init__.py
│   ├── types.py                    # Enums: IntentType, EdgeType, SemanticType
│   ├── models/                     # Pydantic data models
│   │   ├── primitives.py           # SemanticPrimitive
│   │   ├── intent.py               # IntentNode, IntentEdge, IntentGraph
│   │   └── reasoning.py            # ReasoningPath, ReasoningDecision
│   ├── compression/                # Layer 1: Semantic Compression
│   │   ├── base.py                 # SemanticCompressor (ABC)
│   │   ├── text.py                 # ConceptMapper
│   │   ├── speech.py               # PhonemeExtractor
│   │   └── multimodal.py           # MultimodalProcessor
│   ├── graph/                      # Layer 2: Intent Graph
│   │   └── builder.py              # IntentGraphBuilder
│   ├── reasoning/                  # Layer 3: Reasoning Engine
│   │   ├── generator.py            # ReasoningPathGenerator
│   │   ├── selection.py            # CompetitiveSelector
│   │   └── dynamics.py             # OscillatoryGate
│   ├── knowledge/                  # Layer 4: Knowledge Integration
│   │   ├── engine.py               # KnowledgeQueryEngine
│   │   ├── gaps.py                 # KnowledgeGapDetector
│   │   ├── physics.py              # PhysicsRuleEngine
│   │   └── domain.py               # DomainLogicManager
│   ├── reconstruction/             # Layer 5: Output Generation
│   │   ├── base.py                 # OutputReconstructor (ABC)
│   │   ├── language.py             # LanguageGenerator
│   │   ├── code.py                 # CodeGenerator
│   │   ├── action.py               # ActionPlanner
│   │   └── translator.py           # MultiFormatTranslator
│   ├── pipeline/                   # Orchestrator
│   │   └── orchestrator.py         # ISREPipeline
│   └── utils/
│       ├── architectural_validator.py
│       └── resources.py
├── tests/                          # Test suite
├── examples/                       # Demo scripts
├── docs/                           # Documentation
├── pyproject.toml                  # Build configuration
└── LICENSE                         # GPL-3.0 License
```

## Key Concepts

### Semantic Primitives
Atomic units of meaning, language-agnostic, with deterministic IDs:
```python
SemanticPrimitive(
    id="sem_abc123def456",
    concept="fruit",
    modality="text",
    semantic_weight=1.0
)
```

### Intent Graph
Directed graph with typed nodes and explicit conflict markers:
```python
IntentNode(
    id="node_1",
    type=IntentType.GOAL,
    semantic_payload=[primitive],
    conflict_markers=[{"partner_id": "node_2", "type": "semantic_opposition"}]
)
```

### Oscillatory Dynamics
Hopf bifurcation dynamics for path activation gating:
```
dz/dt = z(mu - |z|²) + iωz
```

## Roadmap

See [roadmapproduction.md](roadmapproduction.md) for the full production roadmap.

### Current Status: Prototype (v0.1.0)
- [x] Core 5-layer architecture
- [x] Basic semantic compression
- [x] Intent graph construction
- [x] Multi-path reasoning
- [x] Knowledge integration
- [x] Multi-format output
- [x] Comprehensive test suite

### Next Steps
- [ ] Production bug fixes
- [ ] Configuration system
- [ ] Knowledge base upgrade (SQLite)
- [ ] Expanded concept mappings
- [ ] CLI interface
- [ ] API server
- [ ] Docker deployment
- [ ] PyPI publication

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python 3.13+
- Uses Pydantic for data validation
- Tested with pytest and Hypothesis
