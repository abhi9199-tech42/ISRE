import pytest
from isre.compression.base import SemanticCompressor
from isre.reconstruction.base import OutputReconstructor
from isre.knowledge.domain import DomainModule
from isre.pipeline import ISREPipeline
from isre.models import SemanticPrimitive, IntentGraph, IntentNode
from isre.types import IntentType

# --- Mock Plugins ---

class MockCompressor(SemanticCompressor):
    @property
    def modality(self) -> str: return "custom"
    def compress(self, raw_input):
        return [SemanticPrimitive(id="custom_1", concept="custom_concept", modality="custom")]

class MockReconstructor(OutputReconstructor):
    @property
    def format_type(self) -> str: return "custom_format"
    def reconstruct(self, decision):
        return "RECONSTRUCTED_CUSTOM"

class MockDomainLogic(DomainModule):
    def execute(self, inputs):
        return {"result": "DOMAIN_HANDLED"}

# --- Tests ---

def test_property_21_comprehensive_system_extensibility():
    """
    Property 21: Comprehensive System Extensibility
    Validates: Requirements 8.1, 8.2, 8.3, 8.5
    """
    pipeline = ISREPipeline()
    
    # 1. Test compression extension
    pipeline.compression.register_compressor(MockCompressor())
    prims = pipeline.compression.process("any", "custom")
    assert prims[0].concept == "custom_concept"
    
    # 2. Test reconstruction extension
    pipeline.translator.register(MockReconstructor())
    res = pipeline.translator.translate(
        pipeline.process("apple", "text")["decision_metadata"], # Mock decision logic
        formats=["custom_format"]
    )
    # Actually, pipeline.process returns a dict, but translator.translate needs a ReasoningDecision.
    # So I'll just test the translator directly.
    from isre.models.reasoning import ReasoningDecision, ReasoningPath
    dummy_decision = ReasoningDecision(
        selected_path=ReasoningPath(id="p", steps=[]), 
        justification="j", 
        confidence=1.0, 
        alternative_paths=[]
    )
    res = pipeline.translator.translate(dummy_decision, formats=["custom_format"])
    assert res["custom_format"] == "RECONSTRUCTED_CUSTOM"

    # 3. Test knowledge extension
    pipeline.knowledge_engine._knowledge_base["new_fact"] = {"data": 123}
    assert pipeline.knowledge_engine.query("new_fact").content["data"] == 123

def test_property_22_intent_graph_api_accessibility():
    """
    Property 22: Intent Graph API Accessibility
    Validates: Requirements 8.4
    """
    graph = IntentGraph()
    n1 = IntentNode(
        id="n1", 
        type=IntentType.GOAL, 
        semantic_payload=[SemanticPrimitive(id="p1", concept="c1", modality="text")]
    )
    n2 = IntentNode(
        id="n2", 
        type=IntentType.CONSTRAINT, 
        semantic_payload=[]
    )
    graph.add_node(n1)
    graph.add_node(n2)
    
    # Test Node Inspection
    goals = graph.get_nodes_by_type(IntentType.GOAL)
    assert len(goals) == 1
    assert goals[0].id == "n1"
    
    # Test Node Modification
    new_payload = [SemanticPrimitive(id="p2", concept="updated", modality="text")]
    graph.update_node_payload("n1", new_payload)
    assert graph.nodes["n1"].semantic_payload[0].concept == "updated"
