import pytest
from isre.pipeline import ISREPipeline

def test_property_15_sequential_pipeline_processing():
    """
    Property 15: Sequential Pipeline Processing
    Validates: Requirements 6.1
    Logic: Ensure a single input flows through all layers and produces consistent multimodal output.
    """
    pipeline = ISREPipeline()
    raw_input = "Run quickly but stay slow."
    
    result = pipeline.process(raw_input, "text")
    
    # Check outputs exist
    assert "outputs" in result
    assert "text" in result["outputs"]
    assert "code" in result["outputs"]
    assert "action" in result["outputs"]
    
    # Check knowledge gaps were detected (since 'but' and 'stay' might be missing in mock KB)
    assert "knowledge_gaps" in result
    
    # Check request ID
    assert "request_id" in result

def test_property_17_processing_traceability():
    """
    Property 17: Processing Traceability
    Validates: Requirements 6.4
    Logic: Ensure every stage of processing is logged and inspectable.
    """
    pipeline = ISREPipeline()
    raw_input = "apple"
    
    result = pipeline.process(raw_input, "text")
    request_id = result["request_id"]
    
    trace = pipeline.get_trace(request_id)
    
    # Expected stages
    stages = [t["stage"] for t in trace]
    assert "start" in stages
    assert "compression" in stages
    assert "graph_construction" in stages
    assert "reasoning_generation" in stages
    assert "reasoning_selection" in stages
    assert "reconstruction" in stages
    assert "complete" in stages
    
    # Verify data is logged
    compression_log = next(t for t in trace if t["stage"] == "compression")
    assert "primitives_count" in compression_log["data"]

def test_pipeline_error_handling():
    """Verify that errors are caught and logged."""
    pipeline = ISREPipeline()
    
    # Passing invalid input to trigger an error in compression
    with pytest.raises(Exception):
        pipeline.process(None, "text")
        
    # Check if error was logged
    assert any(t["stage"] == "error" for t in pipeline.trace_log)
