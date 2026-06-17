import pytest
from isre.compression.text import ConceptMapper
from isre.compression.speech import PhonemeExtractor
from isre.compression.multimodal import MultimodalProcessor
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property_2_compression_determinism(text):
    """
    Property 2: Semantic Compression Determinism
    Validates: Requirements 1.4, 7.1
    """
    mapper = ConceptMapper()
    res1 = mapper.compress(text)
    res2 = mapper.compress(text)
    assert res1 == res2

@given(st.sampled_from([
    ("apple run", "pomme run"),  # Mix of mapping and pass-through
    ("run quickly", "run quickly"),
    ("manzana run", "apple run")
]))
def test_property_1_multi_word_consistency(pair):
    """
    Property 1: Cross-Language Semantic Consistency (Multi-word)
    Validates: Requirements 1.3
    """
    phrase1, phrase2 = pair
    mapper = ConceptMapper()
    
    res1 = mapper.compress(phrase1)
    res2 = mapper.compress(phrase2)
    
    assert len(res1) == len(res2)
    for p1, p2 in zip(res1, res2):
        assert p1.concept == p2.concept

def test_concept_mapper_basic():
    mapper = ConceptMapper()
    input_text = "apple run"
    result = mapper.compress(input_text)
    assert result[0].concept == "fruit"
    assert result[1].concept == "action_move_fast"

def test_multimodal_routing():
    processor = MultimodalProcessor()
    
    text_result = processor.process("apple", "text")
    speech_result = processor.process("æp.əl", "speech")
    
    assert text_result[0].concept == "fruit"
    assert speech_result[0].concept == "fruit"

def test_grammar_removal():
    """Property 3: Grammar-Free Semantic Extraction (Requirement 1.2)"""
    mapper = ConceptMapper()
    
    # Simple demonstration: mapping doesn't care about extra noise or grammar if we filter it
    # For now, our simple mapper treats unknown words as their Own concepts, 
    # but filters punctuation and casing.
    res1 = mapper.compress("Apple.")
    res2 = mapper.compress("apple")
    
    assert res1[0].concept == res2[0].concept == "fruit"
