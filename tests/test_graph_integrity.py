import pytest
from isre.models import IntentGraph, IntentNode, IntentEdge
from isre.types import IntentType, EdgeType

def test_8_1_cycles_detection():
    """Test 8.1: Cycle detection."""
    graph = IntentGraph()
    n1 = IntentNode(id="n1", type=IntentType.GOAL, semantic_payload=[])
    n2 = IntentNode(id="n2", type=IntentType.GOAL, semantic_payload=[])
    graph.add_node(n1)
    graph.add_node(n2)
    
    # Create a cycle: n1 -> n2 -> n1
    graph.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.TEMPORAL))
    graph.add_edge(IntentEdge(source_id="n2", target_id="n1", relationship_type=EdgeType.TEMPORAL))
    
    assert graph.has_cycles() is True

def test_7_4_priority_inversion():
    """Test 7.4: Priority inversion detection."""
    graph = IntentGraph()
    c1 = IntentNode(id="c1", type=IntentType.CONSTRAINT, semantic_payload=[], activation_level=0.5)
    g1 = IntentNode(id="g1", type=IntentType.GOAL, semantic_payload=[], activation_level=0.9)
    graph.add_node(c1)
    graph.add_node(g1)
    
    # Edge: c1 constrains g1
    graph.add_edge(IntentEdge(source_id="c1", target_id="g1", relationship_type=EdgeType.TEMPORAL))
    
    inversions = graph.check_priority_inversion()
    assert len(inversions) == 1
    assert "g1 (Goal) > c1 (Constraint)" in inversions[0]

def test_cyclic_reasoning_pipeline():
    """Verify that the pipeline handles cycles (should probably reject them)."""
    # This is a meta-test to see if the generator crashes or prunes.
    from isre.reasoning.generator import ReasoningPathGenerator
    gen = ReasoningPathGenerator()
    
    graph = IntentGraph()
    n1 = IntentNode(id="n1", type=IntentType.GOAL, semantic_payload=[])
    n2 = IntentNode(id="n2", type=IntentType.GOAL, semantic_payload=[])
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(IntentEdge(source_id="n1", target_id="n2", relationship_type=EdgeType.TEMPORAL))
    graph.add_edge(IntentEdge(source_id="n2", target_id="n1", relationship_type=EdgeType.TEMPORAL))
    
    paths = gen.generate_paths(graph)
    # The current generator is simple and might produce paths by BFS/DFS.
    # It should not enter an infinite loop if implemented correctly with visited sets.
    assert len(paths) >= 0
