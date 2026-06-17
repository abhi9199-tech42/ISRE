import pytest
from isre.knowledge.engine import KnowledgeQueryEngine
from isre.knowledge.physics import PhysicsRuleEngine

def test_15_3_knowledge_cache():
    """Test 15.3: Verify knowledge caching."""
    engine = KnowledgeQueryEngine()
    
    # First query
    res1 = engine.query("apple")
    assert res1 is not None
    
    # Second query should come from cache
    res2 = engine.query("apple")
    assert res1 is res2 # Identity check for cache

def test_16_1_physical_possibility():
    """Test 16.1: Verify physical impossibility rejection."""
    engine = PhysicsRuleEngine()
    
    # Fly without wings
    context = {"has_wings": False}
    assert engine.check_physical_possibility("fly", context) is False
    
    # Fly with wings
    context = {"has_wings": True}
    assert engine.check_physical_possibility("fly", context) is True
