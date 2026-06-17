import json
from isre.compression.multimodal import MultimodalProcessor
from isre.graph.builder import IntentGraphBuilder

def run_pipeline_demo():
    print("=== ISRE Semantic Pipeline Demo ===\n")
    
    # 1. Initialize components
    processor = MultimodalProcessor()
    builder = IntentGraphBuilder()
    
    # 2. Input: A phrase with a conflict
    raw_input = "Run quickly but stay slow."
    print(f"Input: '{raw_input}'")
    
    # 3. Compression Layer
    # Based on our map, 'run' -> 'action_move_fast', 'quickly' -> 'attribute_fast', 'slow' -> 'attribute_slow'
    primitives = processor.process(raw_input, "text")
    print(f"\n1. Compression Layer Output ({len(primitives)} primitives):")
    for p in primitives:
        print(f"  - [{p.id}] Concept: {p.concept}")
        
    # 4. Intent Graph Layer
    graph = builder.build_from_primitives(primitives)
    print(f"\n2. Intent Graph Layer Output:")
    print(f"  - Nodes: {len(graph.nodes)}")
    print(f"  - Edges: {len(graph.edges)}")
    
    # 5. Conflict Detection Check
    print("\n3. Conflict Detection:")
    conflicted_nodes = [n for n in graph.nodes.values() if n.conflict_markers]
    if conflicted_nodes:
        for node in conflicted_nodes:
            for marker in node.conflict_markers:
                print(f"  - [CONFLICT] {node.id} ({[p.concept for p in node.semantic_payload]}) "
                      f"<--{marker['type']}--> {marker['partner_id']}")
    else:
        print("  - No conflicts detected.")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    run_pipeline_demo()
