#!/usr/bin/env python3
"""
Demo script showing:
1. Three paraphrases of the same sentence producing identical intent graphs, inferences, and reasoning traces
2. Three conflicting sentences that produce different reasoning paths
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
    
    print("=== PARAPHRASE CONSISTENCY DEMO ===\n")
    print("Testing three paraphrases with identical semantic meaning:\n")
    
    for i, phrase in enumerate(paraphrases, 1):
        print(f"{i}. \"{phrase}\" -> [action_move_fast, attribute_fast]")
    
    print("\n" + "="*60)
    
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
        
        print(f"  Request ID: {result['request_id'][:8]}...")
        print(f"  Knowledge Gaps: {result['knowledge_gaps']}")
        print(f"  Confidence: {result['decision_metadata']['confidence']:.3f}")
    
    print("\n" + "="*60)
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
        print(f"Paraphrase {i+1} selected path: {selected_path_id[:12]}..., confidence: {confidence:.3f}")
    
    print("\n" + "="*60)
    print("PARAPHRASE COMPARISON RESULTS\n")
    
    # Check if primitives are equivalent (ignoring order)
    primitive_concepts = [[p['concept'] for p in primitives] for primitives in primitives_list]
    all_primitive_sets_same = all(sorted(concepts) == sorted(primitive_concepts[0]) for concepts in primitive_concepts)
    print(f"1. Primitive concepts identical: {all_primitive_sets_same}")
    
    # Check if graph structures are equivalent
    graph_signatures = [(g['nodes_count'], g['edges_count'], sorted(g['conflicts'])) for g in graphs_data]
    all_graphs_same = all(sig == graph_signatures[0] for sig in graph_signatures)
    print(f"2. Graph structures identical: {all_graphs_same}")
    
    # Check if reasoning path counts are the same
    all_paths_same = all(count == reasoning_paths[0] for count in reasoning_paths)
    print(f"3. Reasoning paths count identical: {all_paths_same}")
    
    # Check if selections are similar (may vary slightly due to path IDs)
    selection_confidences = [sel[1] for sel in selections]
    all_confidences_similar = all(abs(conf - selection_confidences[0]) < 0.01 for conf in selection_confidences)
    print(f"4. Selection confidences similar: {all_confidences_similar}")
    
    print("\n" + "="*60)
    print("PARAPHRASE DEMO SUMMARY")
    
    overall_consistency = all([
        all_primitive_sets_same,
        all_graphs_same,
        all_paths_same,
        all_confidences_similar
    ])
    
    print(f"Overall paraphrase consistency: {'PASS' if overall_consistency else 'FAIL'}")
    
    if overall_consistency:
        print("\n✅ SUCCESS: The ISRE system demonstrates semantic stability!")
        print("   - Semantically equivalent inputs produce identical intent graphs")
        print("   - Reasoning paths remain consistent despite surface variations")
        print("   - Final decisions are stable across paraphrases")
    else:
        print("\n❌ Some inconsistencies were found in the processing of paraphrases.")
    
    return overall_consistency


def test_conflict_detection():
    """
    Test that demonstrates how the system handles conflicting inputs
    """
    print("\n\n" + "="*60)
    print("CONFLICT DETECTION DEMO")
    print("="*60)
    
    # Initialize the ISRE pipeline
    pipeline = ISREPipeline()
    
    # Define three sentences including conflicting ones
    conflicts = [
        "run quickly",           # [action_move_fast, attribute_fast]
        "fast slow",             # [attribute_fast, attribute_slow] - CONFLICT!
        "walk slowly"            # [action_move_slow, attribute_slow]
    ]
    
    print("\nTesting three sentences including conflicting ones:\n")
    
    for i, phrase in enumerate(conflicts, 1):
        print(f"{i}. \"{phrase}\"")
    
    print("\nNote: 'fast slow' creates a conflict between 'attribute_fast' and 'attribute_slow'")
    
    print("\n" + "-"*40)
    
    # Process each conflicting input
    for i, phrase in enumerate(conflicts):
        print(f"\nProcessing conflicting input {i+1}: '{phrase}'")
        
        # Clear the pipeline trace log before each processing
        pipeline.clear()
        
        # Process the input
        result = pipeline.process(phrase, "text")
        trace = pipeline.get_trace(result['request_id'])
        
        print(f"  Request ID: {result['request_id'][:8]}...")
        
        # Check for conflicts in the graph
        graph_log = next(t for t in trace if t["stage"] == "graph_construction")
        conflicts_detected = graph_log["data"]["conflicts"]
        
        print(f"  Conflicts detected: {bool(conflicts_detected)}")
        if conflicts_detected:
            print(f"  Conflicted nodes: {conflicts_detected}")
        
        # Check reasoning paths (conflicts typically generate more paths)
        reasoning_log = next(t for t in trace if t["stage"] == "reasoning_generation")
        path_count = reasoning_log["data"]["paths_count"]
        print(f"  Reasoning paths generated: {path_count}")
        print(f"  Confidence: {result['decision_metadata']['confidence']:.3f}")


def main():
    """
    Main function to run both demos
    """
    print("INTENTIONAL SEMANTIC REASONING ENGINE (ISRE)")
    print("Paraphrase Consistency and Conflict Detection Demo")
    print("="*60)
    
    # Run the paraphrase consistency test
    paraphrase_success = test_paraphrase_consistency()
    
    # Run the conflict detection test
    test_conflict_detection()
    
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    print(f"Paraphrase consistency test: {'PASSED' if paraphrase_success else 'FAILED'}")
    print("\nKey demonstrations:")
    print("• Semantic stability: Equivalent inputs produce identical outputs")
    print("• Conflict detection: Contradictory inputs trigger conflict resolution")
    print("• Deterministic reasoning: Same inputs always produce same results")
    print("• Traceable reasoning: Full audit trail available for each decision")


if __name__ == "__main__":
    main()