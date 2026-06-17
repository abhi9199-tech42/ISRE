import pytest
import math
from hypothesis import given, strategies as st
from isre.models import SemanticPrimitive, IntentGraph, IntentNode, ReasoningPath
from isre.types import IntentType
from isre.reasoning import ReasoningPathGenerator, CompetitiveSelector, OscillatoryGate

# --- Test Data Generation ---
def create_test_node(id, type=IntentType.GOAL, conflict_with=None):
    node = IntentNode(
        id=id,
        type=type,
        semantic_payload=[SemanticPrimitive(id=f"prim_{id}", concept=f"concept_{id}", modality="text")]
    )
    if conflict_with:
        node.conflict_markers.append({"partner_id": conflict_with, "type": "semantic_opposition"})
    return node

def create_conflicting_graph():
    graph = IntentGraph()
    # Node A and B conflict
    n1 = create_test_node("A", conflict_with="B")
    n2 = create_test_node("B", conflict_with="A")
    n1.conflict_markers[0]["partner_id"] = "B"
    n2.conflict_markers[0]["partner_id"] = "A"
    
    graph.add_node(n1)
    graph.add_node(n2)
    return graph

# --- Property Tests ---

def test_property_6_multi_path_generation():
    """
    Property 6: Multi-Path Reasoning Generation (Requirement 3.1)
    Logic: If conflicts exist, generator must produce > 1 path.
    """
    graph = create_conflicting_graph()
    generator = ReasoningPathGenerator()
    
    paths = generator.generate_paths(graph)
    
    assert len(paths) > 1
    # Verify paths are distinct strategies
    path_ids = {p.id for p in paths}
    assert len(path_ids) == len(paths)
    
    # Check that at least one path excluded A and one excluded B
    has_path_without_A = any("A" not in [n.id for n in p.steps] for p in paths)
    has_path_without_B = any("B" not in [n.id for n in p.steps] for p in paths)
    
    assert has_path_without_A
    assert has_path_without_B

def test_property_7_competitive_selection():
    """
    Property 7: Competitive Path Selection (Requirement 3.2)
    Logic: Selector must modify scores and choose the best one.
    """
    selector = CompetitiveSelector()
    
    # Path 1: Good (Goals exist, no internal conflicts)
    p1 = ReasoningPath(id="good", steps=[create_test_node("G1", IntentType.GOAL)])
    
    # Path 2: Bad (Constraint conflict internally)
    n_a = create_test_node("A", IntentType.CONSTRAINT, conflict_with="B")
    n_b = create_test_node("B", IntentType.CONSTRAINT, conflict_with="A")
    p2 = ReasoningPath(id="bad", steps=[n_a, n_b])
    
    decision = selector.select([p1, p2])
    
    assert decision.selected_path.id == "good"
    assert decision.selected_path.intent_satisfaction_score > 0
    assert decision.selected_path.constraint_compliance_score >= p2.constraint_compliance_score

def test_property_8_oscillatory_dynamics():
    """
    Property 8: Oscillatory Path Dynamics (Requirements 3.3, 3.4)
    Logic: Gate state must change over time and stay bounded.
    """
    gate = OscillatoryGate(frequency=2.0)
    initial_act = gate.activation
    
    # Evolve
    activations = []
    for _ in range(50):
        gate.step()
        activations.append(gate.activation)
        
    # Check for change (dynamics)
    assert len(set(activations)) > 1
    # Check bounds [0, 1]
    assert all(0.0 <= a <= 1.0 for a in activations)

def test_property_9_non_token_reasoning():
    """
    Property 9: Non-Token Reasoning (Requirement 3.6)
    Logic: Reasoning process operates on IntentNodes/Paths, not strings/tokens.
    """
    graph = create_conflicting_graph()
    generator = ReasoningPathGenerator()
    paths = generator.generate_paths(graph)
    
    # Inspect internals to ensure no string manipulation of content happens
    # (By proxy: verify we are working with our object types)
    for path in paths:
        assert isinstance(path, ReasoningPath)
        for step in path.steps:
            assert isinstance(step, IntentNode)
            # Ensure we haven't degenerated into text
            assert not isinstance(step, str)

@given(st.integers(min_value=1, max_value=10))
def test_oscillator_convergence(steps):
    """
    Verify oscillator simulation stability.
    """
    gate = OscillatoryGate()
    for _ in range(steps):
        gate.step()
        assert not math.isnan(gate.z.real)
        assert not math.isinf(gate.z.real)
