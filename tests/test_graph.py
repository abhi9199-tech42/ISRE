import pytest
from hypothesis import given, strategies as st
from isre.models.primitives import SemanticPrimitive
from isre.graph.builder import IntentGraphBuilder
from isre.types import IntentType, EdgeType

# We can reuse the semantic_primitive_st if we import it, or redefine it.
# Let's redefine a simpler version for graph testing.
semantic_primitive_st = st.builds(
    SemanticPrimitive,
    id=st.uuids().map(str),
    concept=st.sampled_from(["fruit", "action_move_fast", "attribute_fast", "attribute_slow", "must_be_cold"]),
    semantic_weight=st.floats(min_value=0, max_value=1),
    modality=st.just("text"),
)

def test_property_4_intent_graph_completeness():
    """
    Property 4: Intent Graph Completeness
    Validates: Requirements 2.2, 2.3
    """
    builder = IntentGraphBuilder()
    primitives = [
        SemanticPrimitive(id="1", concept="action_goal", modality="text"),
        SemanticPrimitive(id="2", concept="must_be_fast", modality="text"),
        SemanticPrimitive(id="3", concept="apple", modality="text"),
    ]
    
    graph = builder.build_from_primitives(primitives)
    
    # Check that allPrimitives were processed into nodes
    assert len(graph.nodes) == 3
    
    # Check for expected node types based on our builder's heuristics
    node_types = [n.type for n in graph.nodes.values()]
    assert IntentType.GOAL in node_types
    assert IntentType.CONSTRAINT in node_types or IntentType.CONTEXT in node_types

    # Check that edges exist
    assert len(graph.edges) >= 2
    edge_types = [e.relationship_type for e in graph.edges]
    assert EdgeType.TEMPORAL in edge_types

def test_property_5_conflict_representation():
    """
    Property 5: Conflict Explicit Representation
    Validates: Requirements 2.4
    """
    builder = IntentGraphBuilder()
    # Create conflicting primitives
    primitives = [
        SemanticPrimitive(id="fast", concept="action_move_fast", modality="text"),
        SemanticPrimitive(id="slow", concept="action_move_slow", modality="text"),
    ]
    
    graph = builder.build_from_primitives(primitives)
    
    # Find the nodes
    node_fast = graph.nodes["node_fast"]
    node_slow = graph.nodes["node_slow"]
    
    # Verify conflict markers exist
    assert len(node_fast.conflict_markers) > 0
    assert any(m["partner_id"] == node_slow.id for m in node_fast.conflict_markers)
    
    assert len(node_slow.conflict_markers) > 0
    assert any(m["partner_id"] == node_fast.id for m in node_slow.conflict_markers)

@given(st.lists(semantic_primitive_st, min_size=1, max_size=10))
def test_graph_builder_robustness(primitives):
    """Verify that graph builder handles various primitive combinations without failing."""
    builder = IntentGraphBuilder()
    graph = builder.build_from_primitives(primitives)
    assert len(graph.nodes) == len(primitives)
    if len(primitives) > 1:
        assert len(graph.edges) >= len(primitives) - 1
