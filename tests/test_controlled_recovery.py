import os
import pytest
from core.recovery_engine import RecoveryEngine
from formats.pdf import PDFFormatAdapter
from core.candidate_engine import CandidateGenerator

TARGET_FILE = "tests/fixtures/sample_01012345.pdf"
TARGET_PWD = "01012345"

def test_direct_verification():
    adapter = PDFFormatAdapter()
    assert adapter.is_supported(TARGET_FILE) is True
    info = adapter.get_encryption_info(TARGET_FILE)
    assert info["is_encrypted"] is True

    # Check incorrect passwords
    assert adapter.verify_password(TARGET_FILE, "01000000") is False
    assert adapter.verify_password(TARGET_FILE, "01012344") is False
    assert adapter.verify_password(TARGET_FILE, "01012346") is False
    
    # Check correct password
    assert adapter.verify_password(TARGET_FILE, TARGET_PWD) is True

def test_candidate_generation_010():
    # 010 + 5 digits (length 5)
    candidates = list(CandidateGenerator.brute_force_attack(
        charset="0123456789",
        min_len=5,
        max_len=5,
        prefixes=["010"]
    ))
    assert len(candidates) == 100000
    assert "01000000" in candidates
    assert "01000001" in candidates
    assert "01012345" in candidates
    assert "01099999" in candidates
    assert all(len(c) == 8 and c.startswith("010") and c.isdigit() for c in candidates)

def test_full_controlled_recovery_single_worker(tmp_path):
    db_file = tmp_path / "test_controlled.db"
    engine = RecoveryEngine(db_path=str(db_file))
    
    result = engine.start_recovery(
        file_path=TARGET_FILE,
        attack_type="brute_force",
        config={
            "charset": "0123456789",
            "min_len": 5,
            "max_len": 5,
            "prefixes": ["010"]
        },
        worker_count=1
    )
    assert result == TARGET_PWD

def test_full_controlled_recovery_multiprocess(tmp_path):
    db_file = tmp_path / "test_controlled_mp.db"
    engine = RecoveryEngine(db_path=str(db_file))
    
    result = engine.start_recovery(
        file_path=TARGET_FILE,
        attack_type="brute_force",
        config={
            "charset": "0123456789",
            "min_len": 5,
            "max_len": 5,
            "prefixes": ["010"]
        },
        worker_count=4
    )
    assert result == TARGET_PWD
