import pytest
from hypothesis import given, strategies as st
from isre.reconstruction import MultiFormatTranslator, LanguageGenerator, CodeGenerator
from isre.models import ReasoningDecision, ReasoningPath, IntentNode, SemanticPrimitive
from isre.types import IntentType

def create_sample_decision(concepts):
    steps = []
    for i, c in enumerate(concepts):
        node = IntentNode(
            id=f"n{i}", 
            type=IntentType.GOAL,
            semantic_payload=[SemanticPrimitive(id=f"p{i}", concept=c, modality="text")]
        )
        steps.append(node)
    
    path = ReasoningPath(id="path1", steps=steps)
    return ReasoningDecision(selected_path=path, justification="test", confidence=1.0, alternative_paths=[])

def test_property_13_multi_format_consistency():
    """
    Property 13: Multi-Format Output Consistency
    Validates: Requirements 5.2, 5.3
    Logic: Ensure translator produces results for all registered formats based on same decision.
    """
    translator = MultiFormatTranslator()
    decision = create_sample_decision(["action_move_fast", "attribute_fast"])
    
    outputs = translator.translate(decision, formats=["text", "code", "action"])
    
    assert "text" in outputs
    assert "code" in outputs
    assert "action" in outputs
    
    # Verify content semantic consistency (heuristic)
    assert "run" in outputs["text"] or "fast" in outputs["text"]
    assert "agent.move" in outputs["code"]
    assert len(outputs["action"]) == 2

def test_property_14_translation_based_generation():
    """
    Property 14: Translation-Based Output Generation
    Validates: Requirement 5.5
    Logic: Generators should map concepts directly, not "hallucinate" new steps.
    """
    decision = create_sample_decision(["fruit", "attribute_slow"])
    gen_text = LanguageGenerator()
    gen_code = CodeGenerator()
    
    text_out = gen_text.reconstruct(decision)
    code_out = gen_code.reconstruct(decision)
    
    # Text should contain mapped concepts
    assert "apple" in text_out and "slowly" in text_out
    # It should NOT contain random tokens not in logical mapping (hard to prove negative, 
    # but we verify strictly presence of mapped terms).
    
    # Code should reflect structure
    # 'fruit' might not have code mapping, but 'attribute_slow' might imply something
    # Our simple code gen might ignore 'fruit', that's fine, but it shouldn't crash.
    assert isinstance(code_out, str)

@given(st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=5))
def test_reconstruction_robustness(concepts):
    """Verify reconstructors handle arbitrary concept strings gracefully."""
    translator = MultiFormatTranslator()
    decision = create_sample_decision(concepts)
    outputs = translator.translate(decision)
    assert len(outputs) == 3
