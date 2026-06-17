import pytest
import time
from isre.models import IntentGraph, IntentNode, SemanticPrimitive
from isre.types import IntentType
from isre.reasoning.generator import ReasoningPathGenerator
from isre.knowledge.engine import KnowledgeQueryEngine

def test_25_1_graph_size_scaling():
    """Test 25.1: Intent graph size scaling (Nodes vs Latency)."""
    generator = ReasoningPathGenerator()
    sizes = [10, 100, 500] # 1000 might be too slow for deepcopy in a quick test
    
    print("\n[Scalability] Graph Size Scaling Results:")
    for size in sizes:
        graph = IntentGraph()
        for i in range(size):
            node = IntentNode(
                id=f"n{i}",
                type=IntentType.GOAL,
                semantic_payload=[SemanticPrimitive(id=f"p{i}", concept=f"concept_{i}", text_fragment=f"text_{i}")]
            )
            graph.add_node(node)
        
        start = time.time()
        paths = generator.generate_paths(graph)
        end = time.time()
        latency = end - start
        print(f"  Nodes: {size}, Latency: {latency:.4f}s")
        assert len(paths) > 0

def test_25_2_reasoning_depth_scaling():
    """Test 25.2: Reasoning depth scaling (Path length)."""
    generator = ReasoningPathGenerator()
    depths = [10, 100, 500]
    
    print("\n[Scalability] Reasoning Depth Scaling Results:")
    for depth in depths:
        graph = IntentGraph()
        for i in range(depth):
            node = IntentNode(
                id=f"n{i}",
                type=IntentType.GOAL,
                semantic_payload=[SemanticPrimitive(id=f"p{i}", concept=f"concept_{i}", text_fragment=f"text_{i}")]
            )
            graph.add_node(node)
        
        # In the current prototype, depth is just node count in a linear path
        start = time.time()
        paths = generator.generate_paths(graph)
        end = time.time()
        latency = end - start
        print(f"  Depth: {depth}, Latency: {latency:.4f}s")
        assert len(paths[0].steps) == depth

def test_25_3_knowledge_source_scaling():
    """Test 25.3: Knowledge source scaling (1M Facts)."""
    engine = KnowledgeQueryEngine()
    
    print("\n[Scalability] Knowledge Source Scaling (Populating 1M facts)...")
    start_pop = time.time()
    for i in range(1000000):
        engine._knowledge_base[f"fact_{i}"] = {"data": i}
    end_pop = time.time()
    print(f"  Population time: {end_pop - start_pop:.2f}s")
    
    # Measure query time
    start_query = time.time()
    res = engine.query("fact_999999")
    end_query = time.time()
    latency = end_query - start_query
    print(f"  Lookup Latency for 1M facts: {latency:.6f}s")
    
    assert res is not None
    assert res.content["data"] == 999999
    # Python dict lookups are O(1) so this should be nearly instantaneous regardless of size
