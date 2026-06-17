from isre.pipeline import ISREPipeline
import time

def demo_conflict_resolution():
    """
    Demonstrates how ISRE handles semantic conflicts that often trip up traditional LLMs.
    LLMs often 'hallucinate' a middle ground or pick one based on frequency.
    ISRE explicitly detects the conflict and generates distinct reasoning paths.
    """
    pipeline = ISREPipeline()
    
    print("=== ISRE vs TRADITIONAL LLM DEMO ===")
    print("\nScenario: User gives a conflicting command: 'Run quickly but walk slowly.'")
    
    raw_input = "Run quickly but walk slowly."
    result = pipeline.process(raw_input, "text")
    
    print(f"\n1. Request ID: {result['request_id']}")
    print(f"2. Detected Knowledge Gaps: {result['knowledge_gaps']}")
    
    # Trace the reasoning
    trace = pipeline.get_trace(result["request_id"])
    
    # Find conflicts
    graph_log = next(t for t in trace if t["stage"] == "graph_construction")
    print(f"3. Conflict Detection: Found conflicts in nodes: {graph_log['data']['conflicts']}")
    
    # Find reasoning paths
    reasoning_log = next(t for t in trace if t["stage"] == "reasoning_generation")
    print(f"4. Reasoning Strategy: Generated {reasoning_log['data']['paths_count']} distinct resolution paths.")
    
    # Selection
    selection_log = next(t for t in trace if t["stage"] == "reasoning_selection")
    print(f"5. Selection Decision: {result['decision_metadata']['justification']}")
    print(f"   Confidence Score: {result['decision_metadata']['confidence']:.2f}")

    print("\n6. Final Multimodal Outputs:")
    for fmt, content in result['outputs'].items():
        print(f"   [{fmt.upper()}]: {content}")

    print("\nDifference Note: A traditional LLM might just produce 'Running quickly and walking slowly.' "
          "without realizing they are mutually exclusive. ISRE detects the binary opposition (fast vs slow) "
          "and forces a choice or a structured compromise.")

if __name__ == "__main__":
    demo_conflict_resolution()
