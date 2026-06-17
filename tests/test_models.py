import pytest
from hypothesis import given, strategies as st
from isre.models import SemanticPrimitive, IntentNode, IntentEdge, ReasoningPath, ReasoningDecision
from isre.types import IntentType, EdgeType

# Strategies for generating test data
semantic_primitive_st = st.builds(
    SemanticPrimitive,
    id=st.uuids().map(str),
    concept=st.text(min_size=1),
    semantic_weight=st.floats(min_value=0, max_value=1),
    modality=st.just("text"),
)

intent_node_st = st.builds(
    IntentNode,
    id=st.uuids().map(str),
    type=st.sampled_from(IntentType),
    semantic_payload=st.lists(semantic_primitive_st, min_size=1, max_size=5),
    activation_level=st.floats(min_value=0, max_value=1),
)

def test_basic_model_instantiation(sample_primitive, sample_node, sample_edge):
    """Verify that models can be instantiated with sample data."""
    assert sample_primitive.concept == "apple"
    assert sample_node.semantic_payload[0] == sample_primitive
    assert sample_edge.relationship_type == EdgeType.CAUSAL

@given(intent_node_st)
def test_property_16_semantic_consistency_preservation(node):
    """
    Property 16: Semantic Consistency Preservation
    Validates: Requirements 6.3
    
    Ensures that semantic meaning (payload) is preserved within the IntentNode.
    """
    assert len(node.semantic_payload) > 0
    for primitive in node.semantic_payload:
        assert isinstance(primitive, SemanticPrimitive)
        assert len(primitive.concept) > 0

@given(st.lists(intent_node_st, min_size=1, max_size=5))
def test_property_16_full_chain_consistency(nodes):
    """
    Property 16: Semantic Consistency Preservation (Full Chain)
    Validates: Requirements 6.3
    
    Verifies that semantic primitives are preserved across the entire model hierarchy:
    Primitive -> Node -> Path -> Decision
    """
    # 1. Create Path
    path = ReasoningPath(
        id="path_test",
        steps=nodes,
        intent_satisfaction_score=0.9
    )
    
    # 2. Create Decision
    decision = ReasoningDecision(
        selected_path=path,
        justification="Highest coherence",
        confidence=0.95,
        alternative_paths=[]
    )
    
    # 3. Verify top-level consistency
    assert decision.selected_path.id == path.id
    assert len(decision.selected_path.steps) == len(nodes)
    
    # 4. Deep verify semantic preservation
    for i, original_node in enumerate(nodes):
        result_node = decision.selected_path.steps[i]
        assert result_node.id == original_node.id
        assert result_node.type == original_node.type
        
        # Check that semantic payloads match exactly
        assert len(result_node.semantic_payload) == len(original_node.semantic_payload)
        for j, original_primitive in enumerate(original_node.semantic_payload):
            result_primitive = result_node.semantic_payload[j]
            assert result_primitive.id == original_primitive.id
            assert result_primitive.concept == original_primitive.concept
            assert result_primitive.semantic_weight == original_primitive.semantic_weight
