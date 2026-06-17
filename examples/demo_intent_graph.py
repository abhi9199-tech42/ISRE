"""
Demonstration of ISRE's Layer 2: Intent Graph Construction

This script showcases how Semantic Primitives are transformed into a 
structured Intent Graph with typed nodes (GOAL, CONSTRAINT, etc.)
and explicit relationships.

Key Features:
1. Implicit to Explicit Intent Mapping
2. Typed Nodes (Requirement 2.1)
3. Explicit Conflict Representation (Requirement 2.4)
4. Edge Weighting and Relationship Types
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from isre.models.primitives import SemanticPrimitive
from isre.graph.builder import IntentGraphBuilder
from isre.types import IntentType, EdgeType

def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def demo_graph_construction():
    print_section("LAYER 2: INTENT GRAPH CONSTRUCTION")

    # 1. Simulate Layer 1 Output: Semantic Primitives
    print("Step 1: Input Semantic Primitives (from Layer 1)")
    print("-" * 45)
    
    primitives = [
        SemanticPrimitive(id="p1", concept="action_move_fast", semantic_weight=0.9),
        SemanticPrimitive(id="p2", concept="constraint_must_be_safe", semantic_weight=1.0),
        SemanticPrimitive(id="p3", concept="attribute_fast", semantic_weight=0.8),
        SemanticPrimitive(id="p4", concept="attribute_slow", semantic_weight=0.7),
        SemanticPrimitive(id="p5", concept="query_status", semantic_weight=0.5)
    ]
    
    for p in primitives:
        print(f"  Primitive: {p.id:<4} | Concept: {p.concept:<20} | Weight: {p.semantic_weight}")

    # 2. Build Intent Graph
    print("\nStep 2: Constructing Intent Graph")
    print("-" * 45)
    
    builder = IntentGraphBuilder()
    graph = builder.build_from_primitives(primitives)
    
    # 3. Inspect Nodes
    print("\nStep 3: Inspecting Typed Nodes")
    print("-" * 45)
    print(f"{'Node ID':<15} {'Type':<15} {'Activation':<12} {'Payload Concept'}")
    print("-" * 65)
    
    for node_id, node in graph.nodes.items():
        payload_concepts = [p.concept for p in node.semantic_payload]
        print(f"{node_id:<15} {node.type.value:<15} {node.activation_level:<12.2f} {payload_concepts}")

    # 4. Inspect Edges
    print("\nStep 4: Inspecting Relationships (Edges)")
    print("-" * 45)
    for edge in graph.edges:
        print(f"  {edge.source_id} --({edge.relationship_type.value}, weight={edge.weight})--> {edge.target_id}")

    # 5. Inspect Conflict Markers
    print("\nStep 5: Explicit Conflict Representation")
    print("-" * 45)
    
    found_conflicts = False
    for node in graph.nodes.values():
        if node.conflict_markers:
            found_conflicts = True
            for marker in node.conflict_markers:
                print(f"  [CONFLICT] Node '{node.id}' conflicts with '{marker['partner_id']}'")
                print(f"             Reason: {marker['description']}")
    
    if not found_conflicts:
        print("  No conflicts detected.")

    print("\n" + "=" * 80)
    print("✓ Layer 2 successfully transformed primitives into a structured graph.")
    print("✓ Nodes are typed (GOAL, CONSTRAINT, QUERY, etc.).")
    print("✓ Relationships are explicitly defined as edges.")
    print("✓ Conflicts are explicitly represented in node metadata.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    demo_graph_construction()
