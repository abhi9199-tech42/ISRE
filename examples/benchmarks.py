import time
from isre.pipeline import ISREPipeline

def run_benchmarks():
    print("=== ISRE PERFORMANCE BENCHMARKS ===\n")
    pipeline = ISREPipeline()
    
    scenarios = [
        ("Simple", "apple"),
        ("Conflict", "run fast but stay slow"),
        ("Medium", "I want to eat a fruit and then run quickly to the park."),
        ("Long", "Apple, pomme, manzana, fruit. Quickly, fast. Run, walk. But. Only.")
    ]
    
    for name, text in scenarios:
        start_time = time.perf_counter()
        result = pipeline.process(text, "text")
        end_time = time.perf_counter()
        
        duration = (end_time - start_time) * 1000
        trace = pipeline.get_trace(result["request_id"])
        conv_step = next((t for t in trace if t["stage"] == "oscillatory_convergence"), {"data": {"steps_to_converge": 0}})
        
        print(f"Scenario: {name}")
        print(f"  Input: '{text}'")
        print(f"  Latency: {duration:.2f} ms")
        print(f"  Convergence Steps: {conv_step['data']['steps_to_converge']}")
        print(f"  Outputs Generated: {list(result['outputs'].keys())}")
        print("-" * 30)

if __name__ == "__main__":
    run_benchmarks()
