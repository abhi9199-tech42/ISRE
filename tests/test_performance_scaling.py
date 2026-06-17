import pytest
import time
import concurrent.futures
from isre.pipeline import ISREPipeline

def test_24_3_burst_traffic():
    """Test 24.3: Burst traffic handling via concurrent requests."""
    pipeline = ISREPipeline()
    
    def run_request(i):
        return pipeline.process(f"burst request {i}", "text")

    # Simulate 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_request, i) for i in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    assert len(results) == 20
    for res in results:
        assert "outputs" in res
    
    # Verify trace log captured all concurrent requests
    # Each request should have multiple stages. 
    # Since they share the same pipeline instance, the log should be large.
    assert len(pipeline.trace_log) >= 20 * 5 # Approx 5-7 stages per request

def test_24_4_sustained_load():
    """Test 24.4: Sustained load stability."""
    pipeline = ISREPipeline()
    load_duration_requests = 50
    
    start_time = time.time()
    for i in range(load_duration_requests):
        res = pipeline.process(f"load test {i}", "text")
        assert "outputs" in res
        # Optional: clear trace periodically to prevent memory bloating in a real sustained environment
        if i % 10 == 0:
            pipeline.clear()
            
    end_time = time.time()
    avg_latency = (end_time - start_time) / load_duration_requests
    print(f"\n[Performance] Average latency under sustained load: {avg_latency:.4f}s")
    
    # Stability check: ensure latency doesn't spike exponentially
    # (Simple check: latency should be reasonably low for the prototype)
    assert avg_latency < 0.1 # Should be very fast for simple text
