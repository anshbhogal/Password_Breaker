import os
from core.recovery_engine import RecoveryEngine

def test_full_recovery_workflow(tmp_path):
    db_file = tmp_path / "test_recovery.db"
    engine = RecoveryEngine(db_path=str(db_file))
    
    target_pdf = "tests/fixtures/sample_protected.pdf"
    
    # Run dictionary attack
    result = engine.start_recovery(
        file_path=target_pdf,
        attack_type="dictionary",
        config={
            "wordlists": ["resources/wordlists/default.txt"],
            "custom_words": ["wrong1", "wrong2"]
        }
    )
    assert result == "ansh2004"

def test_mask_recovery_workflow(tmp_path):
    db_file = tmp_path / "test_recovery.db"
    engine = RecoveryEngine(db_path=str(db_file))
    
    target_pdf = "tests/fixtures/sample_protected.pdf"
    
    result = engine.start_recovery(
        file_path=target_pdf,
        attack_type="mask",
        config={
            "mask": "ansh200?d"
        }
    )
    assert result == "ansh2004"
