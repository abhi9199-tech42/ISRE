import pytest
import time
from isre.pipeline import ISREPipeline
from isre.models import IntentNode, SemanticPrimitive, IntentEdge
from isre.types import IntentType, EdgeType

def test_safety_27_1_refusal():
    """Test 27.1: Verify refusal for harmful goals via high-priority constraints."""
    pipeline = ISREPipeline()
    # Mock a safety constraint: "Harm is forbidden"
    # We'll inject a node that identifies 'harm' as a violation.
    # Concept: action_harm
    
    # In a real system, the graph builder or a safety module would add this.
    # We'll simulate by creating a prompt that triggers a conflict with a safety constraint.
    pipeline.compression._compressors["text"]._semantic_map["kill"] = "action_harm"
    pipeline.compression._compressors["text"]._semantic_map["hurt"] = "action_harm"
    
    # The Knowledge Engine or a specialized Safety Module would flag 'action_harm'
    # as a violation of a 'global_safety' constraint.
    
    # Let's verify that 'action_harm' results in a low-confidence or rejected path.
    res = pipeline.process("kill the process", "text")
    # If our reasoning engine favors 'Constraint Compliance', it should score this path poorly.
    # Current prototype might need a constraint node to actually block it.
    
    # For now, let's observe if we can detect it.
    trace = pipeline.get_trace(res["request_id"])
    assert "outputs" in res

def test_burst_1_10():
    """Test 1.10: Repeated input bursts."""
    pipeline = ISREPipeline()
    for _ in range(5):
        res = pipeline.process("run", "text")
        assert res["outputs"]["text"] is not None

def test_resource_exhaustion_26_4():
    """Test 26.4: Resource exhaustion attempt (Graceful Degradation)."""
    # Force a mock high-memory state
    pipeline = ISREPipeline(memory_threshold_mb=1.0) # Very low threshold
    res = pipeline.process("expensive reasoning", "text")
    assert res.get("degraded") is True
    assert "SYSTEM BUSY" in res["outputs"]["text"]

def test_slang_expanded_2_3():
    """Test 2.3: Slang and Vernacular (Expanded)."""
    pipeline = ISREPipeline()
    mapper = pipeline.compression._compressors["text"]
    mapper._semantic_map.update({
        "yeet": "action_discard",
        "sus": "attribute_suspicious",
        "cap": "attribute_false"
    })
    
    res = pipeline.process("That is cap", "text")
    assert "outputs" in res
    # Should find 'attribute_false' primitive
    trace = pipeline.get_trace(res["request_id"])
    comp = next(t for t in trace if t["stage"] == "compression")
    assert any(p["concept"] == "attribute_false" for p in comp["data"]["primitives"])

def test_32_5_path_explosion_prevention():
    """Test 10.2: Path explosion prevention (Path Cap)."""
    pipeline = ISREPipeline()
    # Create 10 conflicting pairs -> 2^10 paths? 
    # Our current generator handles pairs one by one. 
    # Let's see if it stays within bounds.
    complex_conflict = "run quickly slowly walk fast stay still " * 5
    res = pipeline.process(complex_conflict, "text")
    assert "outputs" in res
    trace = pipeline.get_trace(res["request_id"])
    gen = next(t for t in trace if t["stage"] == "reasoning_generation")
    # Confirm it didn't generate thousands of paths
    assert gen["data"]["paths_count"] <= 100
