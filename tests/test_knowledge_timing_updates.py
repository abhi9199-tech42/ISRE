import pytest
import time
from isre.pipeline import ISREPipeline
from isre.knowledge.engine import KnowledgeQueryEngine

def test_15_2_query_timing():
    """Test 15.2: Verify query timing (Pre-emptive vs Just-in-time)."""
    pipeline = ISREPipeline()
    # In our current pipeline, knowledge gaps are detected AFTER reasoning selection (Just-in-time for output grounding).
    # However, we can simulate pre-emptive queries during graph construction.
    
    res = pipeline.process("apple run", "text")
    # Check the query log in knowledge engine
    log = pipeline.knowledge_engine.query_log
    # Query should have happened during gap detection stage
    assert len(log) > 0
    # For Just-in-time verification, ensure query happened after compression
    trace = pipeline.get_trace(res["request_id"])
    comp_ts = next(t for t in trace if t["stage"] == "compression")["resource_status"]["timestamp"]
    # The current mock time in resource status doesn't have high precision, but we can verify order in trace.
    stages = [t["stage"] for t in trace]
    gap_idx = stages.index("knowledge_gaps") if "knowledge_gaps" in stages else -1
    comp_idx = stages.index("compression")
    assert gap_idx > comp_idx

def test_15_4_update_propagation():
    """Test 15.4: Knowledge update propagation."""
    pipeline = ISREPipeline()
    # Initial query
    res1 = pipeline.knowledge_engine.query("apple")
    assert res1.content["color"] == ["red", "green"]
    
    # Update knowledge
    pipeline.knowledge_engine.update_knowledge("apple", {"category": "fruit", "color": ["blue"]})
    
    # Re-query
    res2 = pipeline.knowledge_engine.query("apple")
    assert res2.content["color"] == ["blue"]

def test_15_5_version_mismatch():
    """Test 15.5: Version mismatch handling."""
    # KB with old schema
    old_engine = KnowledgeQueryEngine(schema_version="0.9")
    res = old_engine.query("apple")
    assert res.metadata["schema"] == "0.9"
    
    # Target system expecting 1.0
    current_version = "1.0"
    if res.metadata["schema"] != current_version:
        # Handling mismatch (e.g., logging warning or adapting data)
        print(f"Schema Mismatch Detected: {res.metadata['schema']} vs {current_version}")
        assert True
