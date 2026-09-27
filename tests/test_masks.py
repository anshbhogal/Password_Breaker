from core.candidate_engine import CandidateGenerator

def test_mask_generation():
    mask = "Ansh?d?d"
    candidates = list(CandidateGenerator.mask_attack(mask))
    assert len(candidates) == 100
    assert "Ansh00" in candidates
    assert "Ansh99" in candidates

def test_mask_space_calculation():
    space = CandidateGenerator.calculate_mask_space("?u?l?d")
    assert space == 26 * 26 * 10
