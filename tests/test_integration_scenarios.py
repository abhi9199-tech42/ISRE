import pytest
from isre.pipeline import ISREPipeline

@pytest.mark.parametrize("input_text, expected_outcome", [
    ("apple", "contains_fruit"),
    ("run fast but stay slow", "contains_conflict"),
    ("fly to the moon", "contains_knowledge_gap"),
])
def test_end_to_end_scenarios(input_text, expected_outcome):
    """
    Comprehensive end-to-end integration test for various input scenarios.
    """
    pipeline = ISREPipeline()
    result = pipeline.process(input_text, "text")
    
    assert "outputs" in result
    assert "request_id" in result
    
    if expected_outcome == "contains_fruit":
        # Check if 'apple' was mapped to 'fruit' and then back to 'apple' in text or 'fruit' in semantics
        assert "apple" in result["outputs"]["text"].lower() or "fruit" in result["outputs"]["text"].lower()
        
    elif expected_outcome == "contains_conflict":
        trace = pipeline.get_trace(result["request_id"])
        graph_log = next(t for t in trace if t["stage"] == "graph_construction")
        assert len(graph_log["data"]["conflicts"]) > 0
        
    elif expected_outcome == "contains_knowledge_gap":
        # 'moon' and 'fly' (without context) should trigger gaps or physics rules
        # Our mock KB doesn't have 'moon'
        assert "moon" in result["knowledge_gaps"] or "fly" in result["knowledge_gaps"]

def test_full_multimodal_integration():
    """Verify that DIFFERENT inputs produce SIMILAR semantic traces if they mean the same thing."""
    pipeline = ISREPipeline()
    
    res_en = pipeline.process("apple", "text")
    res_fr = pipeline.process("pomme", "text")
    
    # Both should have 1 primitive
    trace_en = pipeline.get_trace(res_en["request_id"])
    trace_fr = pipeline.get_trace(res_fr["request_id"])
    
    comp_en = next(t for t in trace_en if t["stage"] == "compression")
    comp_fr = next(t for t in trace_fr if t["stage"] == "compression")
    
    assert comp_en["data"]["primitives_count"] == comp_fr["data"]["primitives_count"]
    # In a perfect system, the outputs would also be identical or equivalent
