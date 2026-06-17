import pytest
from isre.models import SemanticPrimitive, IntentNode, IntentEdge, ReasoningPath
from isre.types import SemanticType, IntentType, EdgeType

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
