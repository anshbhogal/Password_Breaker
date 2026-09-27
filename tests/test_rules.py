from core.candidate_engine import CandidateGenerator

def test_rule_mutation():
    base = ["ansh"]
    rules = {
        "append_digits": True,
        "years": ["2004"]
    }
    candidates = list(CandidateGenerator.rule_mutation_attack(base, rules))
    assert "ansh" in candidates
    assert "Ansh" in candidates
    assert "ANSH" in candidates
    assert "ansh2004" in candidates
    assert "Ansh2004" in candidates
    assert "2004ansh" in candidates
