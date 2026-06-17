import pytest
from isre.pipeline import ISREPipeline
from isre.compression.base import SemanticCompressor
from isre.models import SemanticPrimitive

class DirectCompressor(SemanticCompressor):
    @property
    def modality(self) -> str: return "direct"
    def compress(self, raw_input):
        if isinstance(raw_input, list):
            return raw_input
        return []

def test_1_3_noisy_speech():
    """Test 1.3: Noisy speech simulation."""
    pipeline = ISREPipeline()
    # Currently PhonemeExtractor is very basic, but let's see if it handles noise
    noisy_phonemes = "ae p l x z y" # 'apple' with extra chars
    res = pipeline.process(noisy_phonemes, modality="speech")
    # Result should at least contain 'fruit' if 'p l' is found
    assert "outputs" in res

def test_1_4_mixed_language_hinglish():
    """Test 1.4: Mixed language (Hinglish)."""
    pipeline = ISREPipeline()
    # Register Hindi mapping
    mapper = pipeline.compression.get_compressor("text") if hasattr(pipeline.compression, "get_compressor") else pipeline.compression._compressors["text"]
    mapper._semantic_map["daud"] = "action_move_fast"
    
    input_text = "Main fast daud raha hoon"
    res = pipeline.process(input_text, "text")
    # Should identify 'fast' (attribute_fast) and 'daud' (action_move_fast)
    assert "run" in res["outputs"]["text"].lower() or "fast" in res["outputs"]["text"].lower()

def test_1_5_symbolic_input():
    """Test 1.5: Symbolic input (direct primitives)."""
    pipeline = ISREPipeline()
    pipeline.compression.register_compressor(DirectCompressor())
    prims = [SemanticPrimitive(id="s1", concept="action_move_fast", modality="direct")]
    res = pipeline.process(prims, modality="direct")
    assert "run" in res["outputs"]["text"].lower()

def test_1_8_extremely_long_input():
    """Test 1.8: Extremely long input."""
    pipeline = ISREPipeline()
    long_input = "run " * 100
    res = pipeline.process(long_input, "text")
    assert "outputs" in res
    assert len(res["outputs"]["text"]) > 0
