import pytest
from isre.pipeline import ISREPipeline
from unittest.mock import patch

def test_32_2_remove_oscillation():
    """Test 32.2: What happens if oscillation is bypassed?"""
    pipeline = ISREPipeline()
    
    # Mock _ensure_convergence to do nothing (simulate bypassing oscillation logic)
    with patch.object(ISREPipeline, '_ensure_convergence', return_value=None):
        res = pipeline.process("apple", "text")
        request_id = res["request_id"]
        trace = pipeline.get_trace(request_id)
        # Should NOT have the oscillatory_convergence stage
        stages = [t["stage"] for t in trace]
        assert "oscillatory_convergence" not in stages
        # The system still returns an output because CompetitiveSelector did its job, 
        # but the "Gate Guarantee" is missing.
        assert "outputs" in res

def test_32_3_remove_intent_graphs():
    """Test 32.3: Degradation when intent graphs are bypassed/simplified."""
    pipeline = ISREPipeline()
    from isre.models import IntentGraph, IntentNode
    from isre.types import IntentType
    
    # Create a dummy graph that ignores conflicts
    dummy_graph = IntentGraph()
    dummy_node = IntentNode(id="n1", type=IntentType.GOAL, semantic_payload=[])
    dummy_graph.add_node(dummy_node)
    
    # Shadow the method on the instance
    pipeline.graph_builder.build_from_primitives = lambda x: dummy_graph
    
    # Input with clear conflict: "run quickly slowly"
    res = pipeline.process("run quickly slowly", "text")
    
    trace = pipeline.get_trace(res["request_id"])
    reasoning_gen = next(t for t in trace if t["stage"] == "reasoning_generation")
    
    # The system generated 2 paths (Direct + Verification Mode) because there are no conflicts in dummy_graph.
    # A real graph for "run quickly slowly" would have generated 2 resolution branches (4 paths total).
    assert reasoning_gen["data"]["paths_count"] == 2
    print("\n[Meta 32.3] Loss of Conflict Detection confirmed: Pipeline reduced to default/verification paths.")

def test_32_4_replace_reasoning_engine():
    """Test 32.4: Effect of using a sub-optimal (random/last) selector."""
    pipeline = ISREPipeline()
    from isre.models import ReasoningDecision
    
    # Create a selector that always picks the first (potentially worse) path
    def bad_selector(paths):
        return ReasoningDecision(
            selected_path=paths[0],
            confidence=0.1, # Correct name
            alternative_paths=paths[1:], # Required
            justification="I am a bad selector."
        )
        
    with patch('isre.reasoning.selection.CompetitiveSelector.select', side_effect=bad_selector):
        res = pipeline.process("run quickly slowly", "text")
        decision = next(t for t in pipeline.get_trace(res["request_id"]) if t["stage"] == "reasoning_selection")
        assert decision["data"]["confidence"] == 0.1
        print(f"\n[Meta 32.4] Quality Degradation confirmed: Selected path with score {decision['data']['confidence']}")

def test_32_5_violate_core_assumptions_stress():
    """Test 32.5: Stress test with extreme conflict density."""
    pipeline = ISREPipeline()
    # 50 overlapping conflicts in a single prompt
    extreme_conflict = "run quickly slowly walk fast stay still " * 10
    res = pipeline.process(extreme_conflict, "text")
    # The system should handle it via path capping or graceful degradation
    assert "outputs" in res
    print("\n[Meta 32.5] Stress Test confirmed: System survived extreme conflict density.")
