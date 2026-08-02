# ISRE — Complete Project Analysis

**Intentional Semantic Reasoning Engine** · v0.1.0 · GPL-3.0 · Python ≥ 3.10

> A deterministic, 5-layer semantic reasoning system that converts natural language into
> language-agnostic semantic primitives, builds explicit intent graphs, generates multiple
> competing reasoning paths, selects one through oscillatory dynamics (Hopf bifurcation),
> fills knowledge gaps, and reconstructs the decision into text, code, markdown, or actions —
> **without any probabilistic next-token prediction**.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Repository Structure](#2-repository-structure)
3. [System Architecture](#3-system-architecture)
4. [End-to-End Data Flow](#4-end-to-end-data-flow)
5. [Core Data Models](#5-core-data-models)
6. [Layer 0 — Pipeline Orchestrator](#6-layer-0--pipeline-orchestrator)
7. [Layer 1 — Semantic Compression](#7-layer-1--semantic-compression)
8. [Layer 2 — Intent Graph Construction](#8-layer-2--intent-graph-construction)
9. [Layer 3 — Designed Reasoning Engine](#9-layer-3--designed-reasoning-engine)
10. [Layer 4 — World Knowledge Integration](#10-layer-4--world-knowledge-integration)
11. [Layer 5 — Semantic Reconstruction](#11-layer-5--semantic-reconstruction)
12. [The Mathematics of ISRE](#12-the-mathematics-of-isre)
13. [Configuration System](#13-configuration-system)
14. [Interfaces: CLI, REST API, Docker](#14-interfaces-cli-rest-api-docker)
15. [Testing & Validation](#15-testing--validation)
16. [Determinism & Traceability](#16-determinism--traceability)
17. [Performance & Scalability](#17-performance--scalability)
18. [Worked Example: `"run quickly but stay slow"`](#18-worked-example)
19. [Extensibility Points](#19-extensibility-points)
20. [Known Limitations & Roadmap](#20-known-limitations--roadmap)

---

## 1. Executive Summary

ISRE is a **prototype / research-grade** reasoning engine built to demonstrate an alternative
to token-prediction LLMs. Every decision the system makes is:

| Property | Implementation |
|---|---|
| **Deterministic** | SHA-256 hashing for primitive IDs; no randomness in any stage |
| **Traceable** | Every stage logs a structured event into `trace_log` |
| **Explicit** | Conflicts, knowledge gaps, and reasoning paths are first-class objects |
| **Multi-path** | The reasoning layer *generates* competing strategies instead of decoding one answer |
| **Non-hallucinating** | Missing knowledge is reported as `knowledge_gaps`, never invented |

The total runtime codebase is **~1,900 lines of Python** across 40 source files, backed by
**67 pytest tests** (including Hypothesis property-based tests).

---

## 2. Repository Structure

```
ISRE/
├── isre/                            # The package
│   ├── __init__.py                  # Public package exports
│   ├── types.py                     # Enums: IntentType, EdgeType, SemanticType
│   ├── config.py                    # Pydantic configuration (JSON/YAML/env)
│   ├── cli.py                       # argparse CLI entry point
│   ├── api/
│   │   └── server.py                # FastAPI REST server (/health /process /trace/{id})
│   ├── models/                      # Pydantic data models (Layer 0 shared types)
│   │   ├── primitives.py            # SemanticPrimitive
│   │   ├── intent.py                # IntentNode, IntentEdge, IntentGraph
│   │   └── reasoning.py             # ReasoningPath, ReasoningDecision
│   ├── compression/                 # LAYER 1 — semantic compression
│   │   ├── base.py                  # SemanticCompressor ABC
│   │   ├── text.py                  # ConceptMapper (word → concept)
│   │   ├── speech.py                # PhonemeExtractor (simulated)
│   │   ├── multimodal.py            # MultimodalProcessor (router)
│   │   └── semantic_map.json        # Externalized 160-entry concept dictionary
│   ├── graph/                       # LAYER 2 — intent graph
│   │   └── builder.py               # IntentGraphBuilder + conflict detection
│   ├── reasoning/                   # LAYER 3 — reasoning engine
│   │   ├── generator.py             # ReasoningPathGenerator (multi-path branching)
│   │   ├── selection.py             # CompetitiveSelector (multi-objective scoring)
│   │   └── dynamics.py              # OscillatoryGate (Hopf bifurcation)
│   ├── knowledge/                   # LAYER 4 — knowledge integration
│   │   ├── engine.py                # KnowledgeQueryEngine + backend factory
│   │   ├── gaps.py                  # KnowledgeGapDetector
│   │   ├── physics.py               # PhysicsRuleEngine
│   │   ├── domain.py                # DomainLogicManager (plugin system)
│   │   └── backends/
│   │       ├── base.py              # KnowledgeBackend ABC
│   │       ├── json_backend.py      # JSON file storage
│   │       └── sqlite_backend.py    # SQLite storage (ACID, thread-safe)
│   ├── reconstruction/              # LAYER 5 — semantic reconstruction
│   │   ├── base.py                  # OutputReconstructor ABC
│   │   ├── language.py              # LanguageGenerator  → text
│   │   ├── code.py                  # CodeGenerator     → code
│   │   ├── action.py                # ActionPlanner     → action plan (JSON)
│   │   ├── markdown.py              # MarkdownGenerator → markdown
│   │   └── translator.py            # MultiFormatTranslator (coordinator)
│   ├── pipeline/
│   │   └── orchestrator.py          # ISREPipeline — the conductor
│   └── utils/
│       ├── resources.py             # ResourceMonitor (memory → graceful degradation)
│       ├── logging.py               # Structured logging singleton
│       └── architectural_validator.py # AST-based layer-separation lint
├── tests/                           # 67 pytest tests (22 files)
├── examples/                        # 5 demo scripts
├── docs/                            # 5 deep-dive docs (100 questions, validation, etc.)
├── scripts/                         # benchmarks, console tests, verify_isre
├── dist/                            # Built wheel + sdist artifacts
├── pyproject.toml                   # Build, lint (ruff), type (mypy), pytest config
├── tox.ini                          # Multi-Python (3.10–3.13) matrix
├── Makefile                         # dev task runner
├── Dockerfile / docker-compose.yml  # Containerized REST deployment
├── roadmapproduction.md             # Production roadmap
└── CONTRIBUTING.md, LICENSE         # Docs & GPL-3.0 license
```

**Package totals:** 40 `.py` files, ~1,900 lines of source.

---

## 3. System Architecture

### 3.1 The 5-Layer Diagram

```
                     ┌─────────────────────────────────────────────┐
                     │           ISRE PIPELINE (v0.1)              │
                     │           ISREPipeline (orchestrator)       │
                     └─────────────────────────────────────────────┘
                                        │
      ┌───────────┬───────────┬──────────┴───────────┬───────────┐
      ▼           ▼           ▼                      ▼           ▼
┌───────────┐ ┌───────────┐ ┌──────────────────┐ ┌──────────┐ ┌─────────────┐
│ LAYER 1   │ │ LAYER 2   │ │ LAYER 3          │ │ LAYER 4  │ │ LAYER 5     │
│ Semantic  │ │ Intent    │ │ Designed         │ │ World    │ │ Semantic    │
│ Compress- │ │ Graph     │ │ Reasoning Engine │ │ Knowledge│ │ Reconstruct-│
│ ion       │ │ Build     │ │                  │ │ Integr-  │ │ ion         │
│           │ │           │ │                  │ │ ation    │ │             │
│ Text →    │ │ Nodes =   │ │ Path Generator   │ │ Query    │ │ Language    │
│ Concept-  │ │ Intent    │ │  └─ branch on    │ │ Engine   │ │ Generator   │
│ Mapper    │ │ Edges =   │ │    conflicts     │ │  └─ JSON │ │  → text     │
│ Speech →  │ │ Temporal  │ │                  │ │    /     │ │ Code        │
│ Phoneme   │ │ Conflicts │ │ Oscillatory Gate │ │    SQLite│ │ Generator   │
│ Extractor │ │ marked    │ │  └─ Hopf         │ │ Gap      │ │  → code     │
│ Multimodal│ │           │ │    bifurcation   │ │ Detector │ │ Action      │
│ Processor │ │           │ │                  │ │ Physics  │ │ Planner     │
│           │ │           │ │ Competitive      │ │ Rule     │ │  → actions  │
│           │ │           │ │ Selector         │ │ Engine   │ │ Markdown    │
│           │ │           │ │  └─ multi-obj    │ │ Domain   │ │ Generator   │
│           │ │           │ │    scoring       │ │ Modules  │ │  → markdown │
└───────────┘ └───────────┘ └──────────────────┘ └──────────┘ └─────────────┘
```

### 3.2 Module Dependency Graph (layer separation)

The `ArchitecturalValidator` (AST-based) enforces these rules:

```
isre.models ────────────► shared by ALL layers (allowed)
isre.types  ────────────► shared by ALL layers (allowed)

compression  ──► models            (may NOT import reasoning/knowledge/reconstruction)
graph        ──► models, types     (may NOT import reasoning/reconstruction/...)
reasoning    ──► models, types     (may NOT import reconstruction/compression/pipeline)
knowledge    ──► models            (may NOT import reconstruction/reasoning/pipeline)
reconstruction─► models            (may NOT import reasoning/knowledge/compression/pipeline)
pipeline     ──► everything        (orchestrator; the only "God" module)
```

### 3.3 Design Patterns Used

| Pattern | Where |
|---|---|
| **Strategy** | Compressors (`SemanticCompressor` ABC), Reconstructors (`OutputReconstructor` ABC) |
| **Factory** | `create_backend()` in `knowledge/engine.py`, compressor registration |
| **Registry / Plugin** | `MultimodalProcessor.register_compressor`, `MultiFormatTranslator.register`, `DomainLogicManager.register_module` |
| **Abstract Base Class** | `KnowledgeBackend`, `SemanticCompressor`, `OutputReconstructor` |
| **Singleton** | `get_config()` and `get_logger()` |
| **Facade / Orchestrator** | `ISREPipeline` |
| **Data Class (Pydantic)** | All models, config objects |

---

## 4. End-to-End Data Flow

```
raw_input, modality
        │
        ▼
┌─ Stage 0: Resource check ─────────────────────────────────────────┐
│  ResourceMonitor.is_resource_constrained()?  YES → degraded mode   │
│  (returns "SYSTEM BUSY" with concept list, skips full pipeline)    │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ Stage 1: Compression ─────────────────────────────────────────────┐
│  MultimodalProcessor.process(input, modality)                      │
│  └─ routes to ConceptMapper / PhonemeExtractor                     │
│  Output: list[SemanticPrimitive]                                   │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ Stage 2: Intent Graph ────────────────────────────────────────────┐
│  IntentGraphBuilder.build_from_primitives(primitives)              │
│  └─ create IntentNode per primitive                                │
│  └─ link TEMPORAL edges in sequence                                │
│  └─ _detect_conflicts() marks opposition pairs                     │
│  Output: IntentGraph (nodes + edges + conflict_markers)            │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ Stage 3: Reasoning ───────────────────────────────────────────────┐
│  (a) ReasoningPathGenerator.generate_paths(graph)                  │
│        conflicts? → branch: "Prioritize A", "Prioritize B", ...    │
│        no conflicts → "Direct Execution" + "Verification Mode"     │
│  (b) CompetitiveSelector.select(paths)                             │
│        score = w1·Satisfaction + w2·Compliance + w3·Coherence      │
│        Hopf oscillators modulate each score over ≤50 steps         │
│        argmax → ReasoningDecision                                  │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ Stage 4: Knowledge ───────────────────────────────────────────────┐
│  KnowledgeGapDetector.detect_gaps(decision)                        │
│  └─ queries every concept in selected path against KB              │
│  Output: list[str] of missing concepts (NOT hallucinated)          │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ Stage 5: Reconstruction ──────────────────────────────────────────┐
│  MultiFormatTranslator.translate(decision, target_formats)         │
│  └─ LanguageGenerator, CodeGenerator, ActionPlanner, MarkdownGen   │
│  Output: dict {format → output}                                    │
└────────────────────────────────────────────────────────────────────┘
        │
        ▼
{request_id, outputs, knowledge_gaps, decision_metadata}
```

Every stage appends a structured entry to `pipeline.trace_log` via `_log(request_id, stage, data)`,
attached with the current `resource_status`.

---

## 5. Core Data Models

All models are **Pydantic v2 `BaseModel`** classes (validated, serializable via `model_dump()`).

### 5.1 `SemanticPrimitive` — `isre/models/primitives.py`

The base unit of meaning — a compressed, pre-linguistic concept.

```python
class SemanticPrimitive(BaseModel):
    id: str                      # deterministic: "sem_" + sha256(concept)[:12]
    concept: str                 # e.g. "action_move_fast"
    semantic_weight: float = 1.0 # activation seed
    modality: str = "text"       # "text" | "speech"
    compression_metadata: dict   # extensible bag
```

Equality/hash are defined on `id`, so primitives are usable in sets/dicts.

### 5.2 Intent Graph types — `isre/models/intent.py`

```python
class IntentNode(BaseModel):
    id: str
    type: IntentType              # GOAL | CONTEXT | QUERY | CONSTRAINT | EMOTION
    semantic_payload: list[SemanticPrimitive]
    activation_level: float = 1.0
    conflict_markers: list[dict]  # [{type, partner_id, description}]

class IntentEdge(BaseModel):
    source_id: str
    target_id: str
    relationship_type: EdgeType   # CAUSAL | TEMPORAL | LOGICAL | PRIORITY
    weight: float = 1.0
    semantic_label: Optional[str]

class IntentGraph(BaseModel):
    nodes: dict[str, IntentNode]
    edges: list[IntentEdge]
    # API: add_node, add_edge (raises if endpoints missing),
    #      get_nodes_by_type, update_node_payload,
    #      get_neighbors, has_cycles (DFS), check_priority_inversion, clear
```

`has_cycles()` is a classic **DFS with on-path set** (colored DFS). `check_priority_inversion()`
reports when a GOAL has *higher* activation than a CONSTRAINT edge pointing at it.

### 5.3 Reasoning types — `isre/models/reasoning.py`

```python
class ReasoningPath(BaseModel):
    id: str                                   # "path_" + uuid4().hex[:8]
    steps: list[IntentNode]                   # a candidate resolution sequence
    intent_satisfaction_score: float = 0.0
    constraint_compliance_score: float = 0.0
    semantic_coherence_score: float = 0.0
    oscillation_state: dict
    metadata: dict                            # {strategy, scale}

class ReasoningDecision(BaseModel):
    selected_path: ReasoningPath              # the winner
    justification: str                        # why
    confidence: float                         # ∈ [0,1]
    alternative_paths: list[ReasoningPath]
    convergence_metadata: dict                # base/final scores, oscillation steps
```

### 5.4 Shared enums — `isre/types.py`

```python
class IntentType(Enum):   GOAL, CONTEXT, QUERY, CONSTRAINT, EMOTION
class EdgeType(Enum):     CAUSAL, TEMPORAL, LOGICAL, PRIORITY
class SemanticType(Enum): CONCEPT, ACTION, ATTRIBUTE, RELATION
```

---

## 6. Layer 0 — Pipeline Orchestrator

**File:** `isre/pipeline/orchestrator.py` · **Class:** `ISREPipeline`

### 6.1 Construction

```python
def __init__(self, memory_threshold_mb=500.0, config=None):
    self.config = config.model_copy(deep=True) or get_config().model_copy(deep=True)
    self.compression   = MultimodalProcessor()
    self.graph_builder = IntentGraphBuilder(conflict_config=self.config.conflict)
    self.reasoning_gen = ReasoningPathGenerator()
    self.selector      = CompetitiveSelector(reasoning_config=self.config.reasoning)
    self.knowledge_engine = KnowledgeQueryEngine()          # memory backend
    self.gap_detector  = KnowledgeGapDetector(self.knowledge_engine)
    self.translator    = MultiFormatTranslator()
    self.resource_monitor = ResourceMonitor(self.config.memory_threshold_mb)
    self.trace_log = []          # all requests' traces
    self._lock = threading.Lock() # thread-safe trace logging
```

Notable details:
- **Deep copy of config** prevents the global singleton from being mutated.
- **Thread-safety** is implemented only on `trace_log` writes; component instances are shared.
- Config param `memory_threshold_mb` overrides config only when ≠ default `500.0`.

### 6.2 `process()` — the full pipeline

Key pseudo-flow (see §4 for the diagram):

```python
request_id = uuid4()
_log("start", {input, modality})

if resource_monitor.is_resource_constrained():       # graceful degradation
    return {"outputs": {"text": "SYSTEM BUSY ..."}, "degraded": True}

primitives = self.compression.process(raw_input, modality)      # 1
graph      = self.graph_builder.build_from_primitives(primitives) # 2
paths      = self.reasoning_gen.generate_paths(graph)           # 3a
decision   = self.selector.select(paths)                        # 3b
gaps       = self.gap_detector.detect_gaps(decision)            # 4
outputs    = self.translator.translate(decision, target_formats) # 5
```

### 6.3 Public API

| Method | Purpose |
|---|---|
| `process(input, modality="text", target_formats=None) → dict` | Run full pipeline |
| `get_trace(request_id) → list[dict]` | Filter trace log per request |
| `clear()` | Reset the trace log |

---

## 7. Layer 1 — Semantic Compression

The goal: **strip syntax, preserve meaning**. Raw text becomes a flat list of
language-agnostic semantic primitives.

### 7.1 `SemanticCompressor` ABC — `compression/base.py`

```python
class SemanticCompressor(ABC):
    @abstractmethod
    def compress(self, raw_input) -> list[SemanticPrimitive]: ...
    @property
    @abstractmethod
    def modality(self) -> str: ...
```

### 7.2 `ConceptMapper` (text) — `compression/text.py`

Algorithm (`compress()`):

1. **Normalize**: lowercase, strip `,.!?`, split on whitespace.
2. **Map word → concept** using the built-in `_semantic_map` dict (~160 entries).
3. **Fuzzy fallback**: if unmapped and `len(word) > 3`, accept any key with the same 3-char prefix.
4. **Emoji map**: `🍎→fruit`, `🏃→action_move_fast`.
5. **Pass-through**: unknown words keep themselves as the concept (e.g. `but → but`).
6. **Deterministic ID**: `id = "sem_" + sha256(concept.encode()).hexdigest()[:12]`.

The map contains **multilingual entries** (e.g. `pomme`, `manzana` → `fruit`) and groups into
categories: fruits, movement actions, general actions, speed/size/temp/quality/quantity/
state/direction/energy/cost attributes, objects, people, nature, time, emotions, logic.

**Note:** the externalized `compression/semantic_map.json` duplicates this dict but is *not*
actually loaded at runtime — the hardcoded dict is the live source.

### 7.3 `PhonemeExtractor` (speech) — `compression/speech.py`

Simulated speech pipeline. Accepts a string or list of phonemes; maps known phoneme strings
(`"æp.əl" → fruit`, `"rʌn" → action_move_fast`); everything else becomes `audio_cluster_<p>`.
IDs are prefixed `sem_ph_`.

### 7.4 `MultimodalProcessor` (router) — `compression/multimodal.py`

A registry of compressors keyed by modality. Defaults: `text → ConceptMapper`,
`speech → PhonemeExtractor`. `process()` raises `ValueError` for unregistered modalities and is
**fully deterministic** (compressor order fixed, no randomness).

---

## 8. Layer 2 — Intent Graph Construction

**File:** `isre/graph/builder.py` · **Class:** `IntentGraphBuilder`

### 8.1 Build algorithm

1. **Nodes** — one `IntentNode` per primitive; type inferred by `_infer_intent_type()`:

```python
if "action" or "goal" in concept   → GOAL
if "query" or "?" in concept       → QUERY
if "constraint" or "must"/"only"   → CONSTRAINT
if "emotion" in concept            → EMOTION
else                               → CONTEXT
```

2. **Edges** — sequential `TEMPORAL` edges labeled `sequenced_intent` between consecutive nodes
   (`node[i] → node[i+1]`). This is a simplified stand-in for real causal/logical linking.

3. **Conflicts** — `_detect_conflicts(graph)` performs an **O(n²)** pairwise scan.

### 8.2 Conflict detection

`_are_conflicting(n1, n2)` returns `True` if either:

- **(A) Explicit opposition table** (35+ pairs), e.g.:
  - `attribute_fast ↔ attribute_slow`, `action_move_fast ↔ action_move_slow`
  - `attribute_hot ↔ attribute_cold`, `action_create ↔ action_destroy`
  - `action_go ↔ action_stay`, `attribute_on ↔ attribute_off`, ...
- **(B) Heuristic prefix rules** on same `action_*` family:
  - `fast` vs `slow`, `up` vs `down`.

On conflict, **both** nodes get a symmetric `conflict_marker`:

```python
{"type": "semantic_opposition",
 "partner_id": <other node id>,
 "description": f"Conflict between {id1} and {id2}"}
```

---

## 9. Layer 3 — Designed Reasoning Engine

The heart of ISRE. Three components: generator, dynamics, selector.

### 9.1 `ReasoningPathGenerator` — `reasoning/generator.py`

Generates **competing strategies** from one graph:

```
no conflicts:
    → [ "Direct Execution" ]
    → + "Verification Mode" (activation_scale=0.8)   # always ≥2 paths

conflicts found:
    for each unique conflict pair (A, B):
        → "Prioritize A over B"  (sequence without B)
        → "Prioritize B over A"  (sequence without A)
```

- Conflicts are deduplicated with a sorted-pair set (`processed_pairs`).
- Paths deep-copy the node lists, so branches are independent.
- Initial scores are placeholders (`0.5`); the selector re-scores them.

### 9.2 `OscillatoryGate` — `reasoning/dynamics.py`

Implements a **Hopf oscillator** (see §12 for the math):

```python
class OscillatoryGate:
    def step(self):
        r2 = abs(self.z)**2
        dz = self.z * (self.mu - r2) + 1j * self.omega * self.z
        self.z += dz * self.dt          # forward Euler, dt = 0.1

    @property
    def activation(self):              # map Re(z) to [0,1]
        return min(1.0, max(0.0, (self.z.real + 1.0) / 2.0))
```

Exposes `phase` (via `cmath.phase`), `get_state()`, and `reset()`.

### 9.3 `CompetitiveSelector` — `reasoning/selection.py`

**Step 1 — Score every path** on three objectives:

| Objective | Function | Weight |
|---|---|---|
| Intent satisfaction | mean activation of GOAL nodes (`0.1` if none) | `w₁ = 0.4` |
| Constraint compliance | `1.0` if no internal conflicts remain, else `0.2` | `w₂ = 0.4` |
| Semantic coherence | mean of per-adjacent-pair scores | `w₃ = 0.2` |

Coherence pair-score = `0.4·concept_sim + 0.3·type_match + 0.3·activation_smoothness`
where `concept_sim` is **Jaccard similarity** on the concept sets of consecutive nodes.

Base score: `score = 0.4·sat + 0.4·comp + 0.2·coh`.

**Step 2 — Oscillatory modulation.** One `OscillatoryGate` per path, seeded
`z₀ = (0.1 + 0.5·score) + 0.1i`. All oscillators step in lockstep up to
`max_oscillation_steps=50`, breaking early when the max per-path activation delta
falls below `tolerance=0.01` after step 10. Final score =
`0.6·base + 0.4·activation`.

**Step 3 — Argmax.** `best_idx = argmax(final_scores)`; builds a `ReasoningDecision` with
justification, `confidence = final_score`, alternatives, and convergence metadata.

---

## 10. Layer 4 — World Knowledge Integration

Design principle: **"gap detection instead of hallucination."**

### 10.1 `KnowledgeBackend` ABC — `backends/base.py`

Interface: `query(key)`, `query_concepts(keys)`, `update(key, data)`,
`get_all()`, `clear()`, `bulk_update(data)`, `is_modified()`.

### 10.2 Backends

| Backend | Storage | Notes |
|---|---|---|
| `JSONKnowledgeBackend` | `knowledge.json` | Loads on init (merging defaults with file), writes on update; default facts: `apple`, `run`, `physics_gravity` |
| `SQLiteKnowledgeBackend` | `knowledge.db` | `CREATE TABLE knowledge(key TEXT PRIMARY KEY, value TEXT, updated_at REAL)`; **thread-local connections** for thread-safety; `INSERT OR REPLACE` upserts; JSON-encoded values |

Factory `create_backend("memory"|"json"|"sqlite", **kwargs)` — everything non-sqlite falls
back to the JSON backend.

### 10.3 `KnowledgeQueryEngine` — `engine.py`

- Lowercases keys, logs every query with a timestamp.
- **LRU-less dict cache** (config `cache_size` exists but is not used) keyed by concept.
- Returns `KnowledgeQueryResult(source_id, fact_id, content, confidence=1.0, metadata)` or `None`
  when the concept is unknown (this is what makes a *knowledge gap*).
- `update_knowledge()` invalidates the cache on write; `set_backend()` clears the cache.

### 10.4 `KnowledgeGapDetector` — `gaps.py`

`detect_gaps(decision)` collects every concept from the selected path's primitives and batch-queries
the engine; any `None` result is returned as a gap. **The system openly admits ignorance.**

### 10.5 `PhysicsRuleEngine` — `physics.py`

Prototype constraints: flying requires `has_wings` or `has_aircraft`; `object_solid` →
`cannot_pass_through_solids`. (Not wired into the pipeline yet.)

### 10.6 `DomainLogicManager` — `domain.py`

A `Protocol`-based plugin registry: `register_module(name, module)` + `execute_logic(domain, inputs)`.
Raises `ValueError` for unknown domains.

---

## 11. Layer 5 — Semantic Reconstruction

Every generator is a **pure translation** of the selected `ReasoningDecision` — no reasoning here.

### 11.1 `OutputReconstructor` ABC — `reconstruction/base.py`

```python
@abstractmethod
def reconstruct(self, decision) -> Any: ...
@property
def format_type(self) -> str: ...      # "text" | "code" | "action" | "markdown"
```

### 11.2 The four generators

| Format | Generator | Output |
|---|---|---|
| `text` | `LanguageGenerator` | `"Decision: <concepts>. Rationale: <justification>"` — concepts humanized via small map (`action_move_fast → run`) |
| `code` | `CodeGenerator` | `agent.move(speed='fast')`, comments otherwise |
| `action` | `ActionPlanner` | JSON list: `{step, node_id, type, parameters:{prim_id: concept}}` |
| `markdown` | `MarkdownGenerator` | Full document: title, summary, per-step sections, alternatives, knowledge gaps, convergence info |

### 11.3 `MultiFormatTranslator` — `translator.py`

Registry of reconstructors; `translate(decision, formats=None)` returns
`{fmt: output}` for requested formats (unknown formats yield an inline error string).

---

## 12. The Mathematics of ISRE

### 12.1 Deterministic primitive hashing

Every semantic primitive gets an ID that is a **pure function of its concept**:

```
id(concept) = "sem_" + hex(sha256(concept))[0:12]
```

Same input → same primitives → same graph → same paths → same decision. This is the backbone
of the determinism guarantee.

### 12.2 Multi-objective scoring

For each reasoning path *p* with nodes *N(p)*:

**Intent satisfaction** (GOAL nodes *G*):
```
sat(p) = ( Σ_{g ∈ G} activation(g) ) / |G|      if G ≠ ∅, else 0.1
```

**Constraint compliance**:
```
comp(p) = 1.0  if the path retains no internal conflict pair
        = 0.2  otherwise
```

**Semantic coherence** — mean over adjacent pairs (*a*, *b*):

```
concept_sim   = |concepts(a) ∩ concepts(b)| / |concepts(a) ∪ concepts(b)|   (Jaccard)
type_match    = 1.0 if type(a) == type(b) else 0.5
act_smooth    = max(0, 1 − |act(a) − act(b)|)
pair_score    = 0.4·concept_sim + 0.3·type_match + 0.3·act_smooth
coh(p)        = mean(pair_score)      if |N(p)| > 1, else 1.0
```

**Base score:**
```
S(p) = w₁·sat(p) + w₂·comp(p) + w₃·coh(p)
     = 0.4·sat(p) + 0.4·comp(p) + 0.2·coh(p)
```

### 12.3 Hopf oscillator (complex normal form)

The gate evolves a complex state **z** under the normal form of a **supercritical Hopf
bifurcation**:

```
dz/dt = z·( μ − |z|² ) + i·ω·z
```

| Symbol | Meaning | Default |
|---|---|---|
| μ | Bifurcation parameter — μ > 0 ⇒ stable limit cycle at radius √μ | `1.0` |
| ω | Natural angular frequency | `1.0` |
| dt | Euler integration step | `0.1` |

Properties:
- **Bounded:** the cubic term `−|z|²` keeps the trajectory on a limit cycle of radius `√μ`,
  so the oscillator never diverges (no infinite loops).
- **Activation projection:** `a(t) = clip( (Re(z) + 1)/2 , 0, 1 ) ∈ [0,1]`.
- **Phase:** `φ(t) = arg(z)` — captures the oscillatory "state of deliberation."

### 12.4 Oscillatory path competition & convergence

Each path *i* gets an oscillator seeded by its base score:

```
z_i(0) = (0.1 + 0.5·S_i) + 0.1·i
```

Evolve all oscillators synchronously for steps `k = 1…K` (`K = 50`), stopping early when
`max_i |a_i(k) − a_i(k−1)| < ε` (`ε = 0.01`) and `k > 10`. Final path score:

```
S_final(i) = 0.6·S_i + 0.4·a_i(K)
```

Winner: `i* = argmax_i S_final(i)`; `confidence = S_final(i*)`.

The early-stop tolerance bounds the runtime, so **convergence is guaranteed in finite time**
(≤ 50 steps).

### 12.5 Graph theory

- **Cycle detection:** depth-first search maintaining a recursion stack; a back-edge to the
  stack ⇒ cycle (`O(V + E)`).
- **Priority inversion check:** for each `CONSTRAINT → GOAL` edge, flag when
  `activation(GOAL) > activation(CONSTRAINT)`.

---

## 13. Configuration System

**File:** `isre/config.py` — Pydantic models with layered sources.

```
Priority (first source that yields data wins):
  1. explicit config_path argument
  2. $ISRE_CONFIG
  3. ./config.json
  4. ./config.yaml
  5. defaults
then: $ISRE_* environment variables OVERRIDE any loaded values
```

Nested env parsing: `ISRE_REASONING_OSCILLATOR_FREQUENCY=0.5` → `config["reasoning"]["oscillator_frequency"] = 0.5`.
Types auto-parsed: booleans (`true/false`), ints, floats, else strings.

### Full configuration surface

| Key | Type | Default | Meaning |
|---|---|---|---|
| `memory_threshold_mb` | float | 500.0 | Degradation trigger for `ResourceMonitor` |
| `compression.semantic_map_path` | str\|None | None | (unused) custom concept map |
| `compression.fuzzy_match_threshold` | int | 3 | (reserved) fuzzy matching |
| `compression.enable_emoji` | bool | True | emoji support |
| `conflict.custom_opposites` | dict | {} | extendable opposition pairs |
| `conflict.enable_heuristic_detection` | bool | True | prefix heuristics |
| `reasoning.oscillator_frequency` | float | 1.0 | ω |
| `reasoning.oscillator_bifurcation` | float | 1.0 | μ |
| `reasoning.max_oscillation_steps` | int | 50 | K |
| `reasoning.oscillation_tolerance` | float | 0.01 | ε |
| `reasoning.intent_satisfaction_weight` | float | 0.4 | w₁ |
| `reasoning.constraint_compliance_weight` | float | 0.4 | w₂ |
| `reasoning.semantic_coherence_weight` | float | 0.2 | w₃ |
| `knowledge.backend` | str | "memory" | memory/json/sqlite |
| `knowledge.sqlite_path` | str | "knowledge.db" | SQLite file |
| `knowledge.json_path` | str | "knowledge.json" | JSON file |
| `knowledge.cache_size` | int | 1000 | (reserved) |
| `reconstruction.default_formats` | list | [text, code, action] | defaults |
| `reconstruction.enable_markdown` | bool | True | markdown availability |

Global access: `get_config()` (lazy singleton) / `set_config(cfg)`.

---

## 14. Interfaces: CLI, REST API, Docker

### 14.1 CLI — `isre/cli.py`

```
isre [INPUT] [-m MODALITY] [-f FMT ...] [--trace] [--json] [--verbose]
```

- Reads from stdin when no positional arg and stdin isn't a TTY.
- Default formats: text, code, action, markdown.
- `--json` dumps the full result dict; otherwise prints human-readable blocks plus knowledge gaps
  and confidence; `--trace` prints the per-stage log.
- Registered as the `isre` console script in `pyproject.toml`.

### 14.2 REST API — `isre/api/server.py` (FastAPI)

| Endpoint | Method | Behavior |
|---|---|---|
| `/health` | GET | `{status: ok, version: 0.1.0}` |
| `/process` | POST | body `{input, modality?, formats?}` → `ProcessResponse` |
| `/trace/{request_id}` | GET | trace entries or HTTP 404 |

Request/response use Pydantic schemas (`ProcessRequest`, `ProcessResponse`). Server entry point
`main()` runs `uvicorn` on `0.0.0.0:8000`. Registered as `isre-server` console script.

### 14.3 Docker

- `Dockerfile`: multi-stage build (builder installs `build`, `fastapi`, `uvicorn`, then
  `pip install -e .`); final stage copies site-packages + `isre/`, runs as non-root user `isre`,
  serves via uvicorn on port 8000.
- `docker-compose.yml`: single service, port `8000:8000`.

---

## 15. Testing & Validation

**67 tests across 22 files** (`tests/`), configured in `pyproject.toml`
(`--cov=isre --cov-report=term-missing --cov-report=html`).

### Coverage by file

| File | # Tests | Focus |
|---|---|---|
| `test_adversarial.py` | 3 | Malformed/attacker inputs |
| `test_architecture.py` | 2 | Layer separation via AST validator |
| `test_compression.py` | 5 | ConceptMapper determinism, fuzzy/emoji fallback |
| `test_extensibility.py` | 2 | Custom compressors/reconstructors |
| `test_final_coverage.py` | 5 | End-to-end property coverage |
| `test_graph.py` | 3 | Node/edge/conflict building |
| `test_graph_integrity.py` | 3 | Cycle detection, priority inversion, updates |
| `test_integration_scenarios.py` | 2 | Full-pipeline scenarios |
| `test_knowledge.py` | 3 | Query engine, backends |
| `test_knowledge_robustness.py` | 2 | Backend resilience |
| `test_knowledge_timing_updates.py` | 3 | Cache invalidation, update semantics |
| `test_meta.py` | 4 | Ablation studies (remove oscillation / graphs / selector) |
| `test_modalities.py` | 4 | Text + speech modalities |
| `test_models.py` | 3 | Pydantic model behavior |
| `test_performance.py` | 3 | Latency/throughput sanity |
| `test_performance_scaling.py` | 2 | Scaling behavior |
| `test_pipeline.py` | 3 | Sequential flow, traceability, error handling |
| `test_reasoning.py` | 5 | Multi-path, selection, oscillation, property-based |
| `test_reconstruction.py` | 3 | All four output formats |
| `test_robustness.py` | 4 | Resource monitor, degraded mode |
| `test_scalability.py` | 3 | Large input handling |

### Toolchain (`pyproject.toml`, `tox.ini`, `Makefile`)

- **ruff** — `select = E,F,W,I,N,UP,B,SIM`, line length 100, first-party `isre`.
- **mypy** — py3.10, strict-ish (warn_return_any, untyped defs allowed).
- **tox** — matrix `py310..py313` for pytest, plus lint/typecheck/docs envs.
- **Makefile** — `install-all`, `test`, `test-cov`, `lint`, `format`, `typecheck`,
  `clean`, `build`, `run`, `serve`, `docker-build`, `benchmark`.

---

## 16. Determinism & Traceability

### Determinism chain

```
sha256(concept) → primitive id → node id → graph identity → path set → scores → argmax
```

Every link is a pure function. There is **no RNG** and **no probabilistic sampling** anywhere
in the pipeline — the only `uuid` usage is for request/path *identification*, not computation.

### Trace stages

`start → compression → graph_construction → reasoning_generation → reasoning_selection →
[knowledge_gaps] → reconstruction → complete | error`

Each trace entry carries `{request_id, stage, data, resource_status}`.

### Graceful degradation

If RSS memory exceeds `memory_threshold_mb`, the pipeline short-circuits to
`SYSTEM BUSY (Degraded Mode)` with the raw concept list — guaranteeing the server never
crashes under load (Requirement 7.5).

---

## 17. Performance & Scalability

| Concern | Mechanism | Complexity |
|---|---|---|
| Compression | linear scan over words | O(W) |
| Graph building | pairwise conflict scan | **O(n²)** (largest bottleneck) |
| Path generation | per unique conflict pair, two branches | O(C · n) |
| Scoring | per path, per node | O(P · n) |
| Oscillation | 50 steps × P oscillators | O(P·K), early-exit ε |
| Knowledge query | dict/DB lookup, cached | O(1) avg |
| Memory | bounded by input size + trace log | O(W) |

Documented (in docs/) typical figures: decision latency **< 10 ms**, oscillation converges in
**~28 steps avg (73 max)**, 0% timeouts.

---

## 18. Worked Example

Input: **`"run quickly but stay slow"`** (modality `text`, all formats) — captured live output.

### 1. Compression
```
[run]     → action_move_fast   (sem_a60fc45ede0b)
[quickly] → attribute_fast     (sem_c5221f865180)
[but]     → but                (sem_cdc299378871)   ← unknown, passed through
[stay]    → action_stay        (sem_532570df8ab1)
[slow]    → attribute_slow     (sem_0bbeebe643cc)
```

### 2. Graph
5 nodes; `action_move_fast` conflicts with `action_stay` (opposition table) →
`attribute_fast` (sem_c5221f865180) also conflicts with `attribute_slow`
(sem_0bbeebe643cc). Nodes carry symmetric `conflict_markers`.

### 3. Reasoning
Two conflict pairs ⇒ 4 branches generated:
`Prioritize <fast node>` / `Prioritize <stay node>` / `Prioritize <fast-attr> / <slow-attr>`
→ 2 unique paths survive dedup + "Direct Execution". After scoring (Sat 1.0, Comp 1.0, Coh 0.5)
and oscillation, base scores `[0.89, 0.90]` modulate to final `[0.534, 0.54]`. Winner confidence
**0.54**.

### 4. Knowledge
`but`, `action_stay`, `action_move_fast`, `attribute_fast` are all absent from the default KB →
reported honestly as `knowledge_gaps`.

### 5. Reconstruction
- **text:** `Decision: run quickly but action_stay. Rationale: Selected path with highest
  oscillatory score: 0.54 ...`
- **code:** `agent.move(speed='fast')\n# speed set to fast\n# Processing but\n# Processing action_stay`
- **action:** 4-step JSON plan with node ids, types, and parameters.
- **markdown:** full decision document with steps, alternatives, and convergence info.

---

## 19. Extensibility Points

| Extension | How |
|---|---|
| New input modality | Subclass `SemanticCompressor`, `register_compressor()` |
| New output format | Subclass `OutputReconstructor`, `translator.register()` |
| New knowledge store | Subclass `KnowledgeBackend`, pick via `create_backend()` |
| New domain logic | Implement `DomainModule` protocol, `register_module()` |
| Custom opposition pairs | `ConflictConfig.custom_opposites` |
| Tuned reasoning | `ReasoningConfig` weights, frequency, bifurcation, steps |
| New scoring objectives | Extend `CompetitiveSelector` with additional weighted terms |

---

## 20. Known Limitations & Roadmap

### Current limitations (honest assessment)

1. **Toy concept dictionary** — ~160 hardcoded mappings; unknown words pass through unchanged.
2. **`semantic_map.json` is not loaded** at runtime (dead file vs. hardcoded dict).
3. **Conflicts are O(n²)** pairwise; the generator only branches on the *first* conflicts it
   processes (dedup), not a full CSP for multi-conflict graphs.
4. **Coherence/scoring are heuristics** — placeholder-quality, no learning, no embeddings.
5. **Knowledge engine defaults to "memory"** backend (JSON), not SQLite, despite the roadmap.
6. **`PhysicsRuleEngine` / `DomainLogicManager` are not wired into the pipeline.**
7. **Thread-safety is partial** (trace log only); shared components aren't locked.
8. **`KnowledgeQueryEngine` cache ignores `cache_size`.**
9. Some model fields in examples (`metadata=`) don't match the actual `SemanticPrimitive` schema
   (examples may raise until adapted).

### Production roadmap (`roadmapproduction.md` highlights)

- **P0:** fix missing `psutil` dep, duplicate imports, pydantic `.dict()` deprecations.
- **P2:** real semantic-coherence scoring, oscillatory gate truly modulating selection,
  expanded conflict/antonym DB, full thread-safety, robust resource monitor.
- **P3:** externalized config, SQLite default + PostgreSQL option, embeddings/tokenizer
  compression, CSP-based conflict solving.
- **P4:** unit/integration/e2e/security test tiers, property-based expansion, coverage gates.
- **P6/P7:** structured logging, exception hierarchy, caching, OpenTelemetry, security
  hardening, PyPI + Docker release automation.

---

*Document generated from a full source audit of the ISRE repository — v0.1.0.*
