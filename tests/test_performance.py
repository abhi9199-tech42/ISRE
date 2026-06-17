import pytest
import threading
import time
from isre.pipeline import ISREPipeline

def test_property_18_oscillatory_convergence():
    """
    Property 18: Oscillatory Convergence
    Validates: Requirement 7.3
    Logic: Ensure the pipeline reaches a decision convergence in finite time.
    """
    pipeline = ISREPipeline()
    result = pipeline.process("apple", "text")
    request_id = result["request_id"]
    
    trace = pipeline.get_trace(request_id)
    convergence_log = next(t for t in trace if t["stage"] == "oscillatory_convergence")
    
    assert convergence_log["data"]["steps_to_converge"] > 0
    assert convergence_log["data"]["steps_to_converge"] <= 100

def test_property_19_concurrent_request_isolation():
    """
    Property 19: Concurrent Request Isolation
    Validates: Requirement 7.4
    Logic: Multiple simultaneous requests must maintain distinct trace logs.
    """
    pipeline = ISREPipeline()
    
    def worker(input_str, out_list):
        res = pipeline.process(input_str, "text")
        out_list.append(res)
        
    results = []
    threads = []
    inputs = ["apple", "run", "quickly"]
    
    for i in inputs:
        t = threading.Thread(target=worker, args=(i, results))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert len(results) == 3
    # Check each has a unique request ID
    ids = {r["request_id"] for r in results}
    assert len(ids) == 3
    
    # Check isolation in trace log
    for rid in ids:
        trace = pipeline.get_trace(rid)
        assert len(trace) > 1

def test_property_20_graceful_resource_degradation():
    """
    Property 20: Graceful Resource Degradation
    Validates: Requirement 7.5
    Logic: If memory exceeds threshold, system switches to a low-resource mode.
    """
    # Initialize with a tiny threshold to force degradation
    pipeline = ISREPipeline(memory_threshold_mb=1.0) 
    
    result = pipeline.process("Complex reasoning request", "text")
    
    assert result.get("degraded") is True
    assert "SYSTEM BUSY" in result["outputs"]["text"]
    
    # Verify it was logged
    trace = pipeline.get_trace(result["request_id"])
    assert any(t["stage"] == "degradation" for t in trace)
