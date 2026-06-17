import pytest
from isre.pipeline import ISREPipeline

def test_2_1_misspellings():
    """Test 2.1: Misspellings."""
    pipeline = ISREPipeline()
    # "appl" instead of "apple"
    res = pipeline.process("appl", "text")
    assert "apple" in res["outputs"]["text"].lower() or "fruit" in res["outputs"]["text"].lower()

def test_2_2_broken_grammar():
    """Test 2.2: Broken grammar."""
    pipeline = ISREPipeline()
    # "run quickly slow" shouldn't confuse it
    res = pipeline.process("run quickly slow", "text")
    assert "outputs" in res

def test_2_4_emoji_only():
    """Test 2.4: Emoji-only input."""
    pipeline = ISREPipeline()
    res = pipeline.process("🍎 🏃", "text")
    assert "apple" in res["outputs"]["text"].lower() or "run" in res["outputs"]["text"].lower()

def test_2_6_incomplete_sentences():
    """Test 2.6: Incomplete sentences."""
    pipeline = ISREPipeline()
    res = pipeline.process("apple run", "text") # Fragment
    assert "outputs" in res
