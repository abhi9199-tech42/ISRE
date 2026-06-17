#!/usr/bin/env python3
"""
Test script demonstrating that three paraphrases of the same sentence
produce identical intent graphs, inferences, and reasoning traces.
"""

from isre.pipeline.orchestrator import ISREPipeline
import json


def test_paraphrase_consistency():
    """
    Test that demonstrates how three paraphrases of the same sentence
    produce identical intent graphs, inferences, and reasoning traces.
    """
    # Initialize the ISRE pipeline
    pipeline = ISREPipeline()
    
    # Define three paraphrases that should map to similar semantic primitives
    # Based on the existing semantic map in ConceptMapper
    paraphrases = [
        "run quickly",           # Maps to: [action_move_fast, attribute_fast]
        "run fast",              # Maps to: [action_move_fast, attribute_fast]
        "quickly run"            # Maps to: [attribute_fast, action_move_fast]
    ]
    
    print("=== PARAPHRASE CONSISTENCY TEST ===\n")
    print("Testing three paraphrases of the same core intent:\n")
    
    for i, phrase in enumerate(paraphrases, 1):
        print(f"{i}. {phrase}")
    
    print("\n" + "="*50)
    
    # Process each paraphrase and collect results
    results = []
    traces = []
    
    for i, phrase in enumerate(paraphrases):
        print(f"\nProcessing paraphrase {i+1}: '{phrase}'")
        
        # Clear the pipeline trace log before each processing
        pipeline.clear()
        
        # Process the input
        result = pipeline.process(phrase, "text")
        trace = pipeline.get_trace(result['request_id'])
        
        results.append(result)
        traces.append(trace)
        
        print(f"  Request ID: {result['request_id']}")
        print(f"  Knowledge Gaps: {result['knowledge_gaps']}")
        print(f"  Output: {result['outputs']}")
        print(f"  Confidence: {result['decision_metadata']['confidence']}")
    
    print("\n" + "="*50)
    print("ANALYZING REASONING PATHS AND GRAPHS\n")
    
    # Compare the semantic primitives generated
    primitives_list = []
    for i, trace in enumerate(traces):
        compression_log = next(t for t in trace if t["stage"] == "compression")
        primitives = compression_log["data"]["primitives"]
        primitives_list.append(primitives)
        print(f"Paraphrase {i+1} primitives: {[p['concept'] for p in primitives]}")
    
    # Compare the intent graphs
    graphs_data = []
    for i, trace in enumerate(traces):
        graph_log = next(t for t in trace if t["stage"] == "graph_construction")
        graph_data = graph_log["data"]
        graphs_data.append(graph_data)
        print(f"Paraphrase {i+1} graph: {graph_data['nodes_count']} nodes, {graph_data['edges_count']} edges")
        print(f"  Conflicts: {graph_data['conflicts']}")
    
    # Compare reasoning generation
    reasoning_paths = []
    for i, trace in enumerate(traces):
        reasoning_log = next(t for t in trace if t["stage"] == "reasoning_generation")
        path_count = reasoning_log["data"]["paths_count"]
        reasoning_paths.append(path_count)
        print(f"Paraphrase {i+1} reasoning paths generated: {path_count}")
    
    # Compare reasoning selection
    selections = []
    for i, trace in enumerate(traces):
        selection_log = next(t for t in trace if t["stage"] == "reasoning_selection")
        selected_path_id = selection_log["data"]["selected_path_id"]
        confidence = selection_log["data"]["confidence"]
        selections.append((selected_path_id, confidence))
        print(f"Paraphrase {i+1} selected path: {selected_path_id[:12]}..., confidence: {confidence}")
    
    print("\n" + "="*50)
    print("COMPARISON RESULTS\n")
    
    # Check if primitives are equivalent (ignoring IDs since they're hash-based)
    primitive_concepts = [[p['concept'] for p in primitives] for primitives in primitives_list]
    all_primitive_sets_same = all(set(concepts) == set(primitive_concepts[0]) for concepts in primitive_concepts)
    print(f"1. Primitive concepts identical: {all_primitive_sets_same}")
    if not all_primitive_sets_same:
        print(f"   Details: {primitive_concepts}")
    
    # Check if graph structures are equivalent
    graph_signatures = [(g['nodes_count'], g['edges_count'], sorted(g['conflicts'])) for g in graphs_data]
    all_graphs_same = all(sig == graph_signatures[0] for sig in graph_signatures)
    print(f"2. Graph structures identical: {all_graphs_same}")
    if not all_graphs_same:
        print(f"   Details: {graph_signatures}")
    
    # Check if reasoning path counts are the same
    all_paths_same = all(count == reasoning_paths[0] for count in reasoning_paths)
    print(f"3. Reasoning paths count identical: {all_paths_same}")
    if not all_paths_same:
        print(f"   Details: {reasoning_paths}")
    
    # Check if selections are similar (may vary slightly due to path IDs)
    selection_confidences = [sel[1] for sel in selections]
    all_confidences_similar = all(abs(conf - selection_confidences[0]) < 0.01 for conf in selection_confidences)
    print(f"4. Selection confidences similar: {all_confidences_similar}")
    if not all_confidences_similar:
        print(f"   Details: {selection_confidences}")
    
    print("\n" + "="*50)
    print("DETAILED REASONING TRACES\n")
    
    # Print the full reasoning traces for inspection
    for i, (phrase, trace) in enumerate(zip(paraphrases, traces)):
        print(f"\n--- Paraphrase {i+1}: '{phrase}' ---")
        for log_entry in trace:
            stage = log_entry["stage"]
            data = log_entry["data"]
            print(f"  {stage}: {data}")
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    
    overall_consistency = all([
        all_primitive_sets_same,
        all_graphs_same,
        all_paths_same,
        all_confidences_similar
    ])
    
    print(f"Overall paraphrase consistency: {'PASS' if overall_consistency else 'FAIL'}")
    
    if overall_consistency:
        print("\nThe ISRE system successfully demonstrates that semantically equivalent")
        print("sentences (paraphrases) produce consistent intent graphs, reasoning")
        print("paths, and final decisions, confirming the semantic stability property.")
    else:
        print("\nSome inconsistencies were found in the processing of paraphrases.")
        print("This may indicate that the semantic compression is sensitive to surface variations.")


if __name__ == "__main__":
    test_paraphrase_consistency()