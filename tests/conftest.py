import pytest
from pathlib import Path
from isre.models import SemanticPrimitive, IntentNode, IntentEdge, ReasoningPath, ReasoningDecision
from isre.types import SemanticType, IntentType, EdgeType
from isre.pipeline import ISREPipeline

# ---------------------------------------------------------------------------
# Clean up persistent state between test runs
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _cleanup_knowledge():
    """Remove knowledge.json before each test to avoid state leakage."""
    kf = Path("knowledge.json")
    if kf.exists():
        kf.unlink()
    yield
    if kf.exists():
        kf.unlink()


# ---------------------------------------------------------------------------
# Model fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_primitive():
    return SemanticPrimitive(
        id="prim_1",
        concept="apple",
        modality="text"
    )

@pytest.fixture
def sample_node(sample_primitive):
    return IntentNode(
        id="node_1",
        type=IntentType.GOAL,
        semantic_payload=[sample_primitive]
    )

@pytest.fixture
def sample_edge():
    return IntentEdge(
        source_id="node_1",
        target_id="node_2",
        relationship_type=EdgeType.CAUSAL
    )

@pytest.fixture
def sample_decision():
    """A minimal ReasoningDecision for reconstruction tests."""
    node = IntentNode(
        id="n0", type=IntentType.GOAL,
        semantic_payload=[SemanticPrimitive(id="p0", concept="fruit", modality="text")]
    )
    path = ReasoningPath(id="path1", steps=[node])
    return ReasoningDecision(
        selected_path=path,
        justification="test",
        confidence=1.0,
        alternative_paths=[]
    )


# ---------------------------------------------------------------------------
# Pipeline fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def pipeline():
    """Fresh ISREPipeline instance with high memory threshold."""
    return ISREPipeline(memory_threshold_mb=2000.0)
