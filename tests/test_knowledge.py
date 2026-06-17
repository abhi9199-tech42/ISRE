import pytest
from hypothesis import given, strategies as st
from isre.knowledge import KnowledgeQueryEngine, KnowledgeGapDetector
from isre.models import ReasoningDecision, ReasoningPath, IntentNode, SemanticPrimitive
from isre.types import IntentType

def test_property_10_external_knowledge_integration():
    """
    Property 10: External Knowledge Integration
    Validates: Requirements 4.1, 4.2
    Logic: Ensure known concepts return structured results.
    """
    engine = KnowledgeQueryEngine()
    
    # Test known concept
    res_apple = engine.query("apple")
    assert res_apple is not None
    assert res_apple.content["category"] == "fruit"
    
    # Test unknown concept
    res_unknown = engine.query("xyz_nonexistent")
    assert res_unknown is None

def test_property_11_knowledge_gap_detection():
    """
    Property 11: Knowledge Gap Detection
    Validates: Requirements 4.3
    Logic: Reasoning about unknown concepts should trigger gap detection.
    """
    engine = KnowledgeQueryEngine()
    detector = KnowledgeGapDetector(engine)
    
    # Create path with mixed known/unknown concepts
    # 'apple' is known in mock DB, 'unicorn' is not.
    node_known = IntentNode(
        id="n1",
        type=IntentType.GOAL,
        semantic_payload=[SemanticPrimitive(id="p1", concept="apple", modality="text")]
    )
    node_unknown = IntentNode(
        id="n2",
        type=IntentType.GOAL,
        semantic_payload=[SemanticPrimitive(id="p2", concept="unicorn", modality="text")]
    )
    
    path = ReasoningPath(id="path1", steps=[node_known, node_unknown])
    decision = ReasoningDecision(selected_path=path, justification="test", confidence=1.0, alternative_paths=[])
    
    gaps = detector.detect_gaps(decision)
    
    assert "unicorn" in gaps
    assert "apple" not in gaps
    assert len(gaps) == 1

@given(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=20))
def test_batch_query_robustness(concepts):
    """Verify engine handles batch queries without crashing."""
    engine = KnowledgeQueryEngine()
    results = engine.query_concepts(concepts)
    assert len(results) == len(set(concepts)) # Dict keys are unique
