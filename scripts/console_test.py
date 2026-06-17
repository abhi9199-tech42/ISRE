#!/usr/bin/env python3
"""
Console test that takes 3 paraphrases of the same sentence and outputs:
- identical intent graph
- same inference
- printed reasoning trace
"""

from isre.pipeline.orchestrator import ISREPipeline


def main():
    # Initialize pipeline
    pipeline = ISREPipeline()
    
    # Three paraphrases of the same sentence
    paraphrases = [
        "run quickly",
        "run fast", 
        "quickly run"
    ]
    
    print("Input: 3 paraphrases of the same sentence")
    for i, p in enumerate(paraphrases, 1):
        print(f"  {i}. {p}")
    
    print("\nProcessing...\n")
    
    # Process each paraphrase
    results = []
    traces = []
    
    for phrase in paraphrases:
        pipeline.clear()  # Clear previous trace
        result = pipeline.process(phrase, "text")
        trace = pipeline.get_trace(result['request_id'])
        
        results.append(result)
        traces.append(trace)
    
    print("Output:\n")
    
    # Show identical intent graphs
    print("Identical intent graph:")
    graph_data = next(t for t in traces[0] if t["stage"] == "graph_construction")["data"]
    print(f"  - Nodes: {graph_data['nodes_count']}")
    print(f"  - Edges: {graph_data['edges_count']}")
    print(f"  - Conflicts: {graph_data['conflicts']}")
    
    # Show same inference (confidence and selected path)
    print("\nSame inference:")
    for i, result in enumerate(results, 1):
        print(f"  Paraphrase {i}: confidence = {result['decision_metadata']['confidence']:.3f}")
    
    # Show reasoning trace (first one as example)
    print("\nPrinted reasoning trace:")
    for log_entry in traces[0]:  # Show trace for first paraphrase
        stage = log_entry["stage"]
        data = log_entry["data"]
        print(f"  {stage}: {data}")


if __name__ == "__main__":
    main()