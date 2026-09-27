import pytest
from core.candidate_engine import CandidateGenerator

def test_dictionary_attack(tmp_path):
    wfile = tmp_path / "words.txt"
    wfile.write_text("apple\nbanana\ncherry\n", encoding="utf-8")
    
    candidates = list(CandidateGenerator.dictionary_attack([str(wfile)], custom_words=["dragon"]))
    assert "dragon" in candidates
    assert "apple" in candidates
    assert "banana" in candidates
    assert "cherry" in candidates

def test_unicode_candidates():
    custom_words = ["₹", "é", "ü", "中"]
    candidates = list(CandidateGenerator.dictionary_attack([], custom_words=custom_words))
    assert candidates == custom_words
