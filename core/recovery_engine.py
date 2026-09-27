import os
from typing import Dict, Any, Optional, Callable
from core.detector import FileDetector
from core.checkpoint import CheckpointDatabase
from core.scheduler import RecoveryScheduler
from attacks import (
    DictionaryAttack,
    RulesAttack,
    MaskAttack,
    HybridAttack,
    BruteForceAttack,
    PatternAttack
)

class RecoveryEngine:
    """
    High-level facade for managing recovery tasks, creating attack instances,
    and managing active scheduler sessions.
    """

    def __init__(self, db_path: str = "database/recovery.db"):
        self.db = CheckpointDatabase(db_path)
        self.active_scheduler: Optional[RecoveryScheduler] = None

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        return FileDetector.analyze(file_path)

    def create_attack(self, attack_type: str, config: Dict[str, Any]):
        atype = attack_type.lower()
        if atype == "dictionary":
            return DictionaryAttack(
                wordlists=config.get("wordlists", []),
                custom_words=config.get("custom_words", [])
            )
        elif atype == "rules" or atype == "mutation":
            return RulesAttack(
                base_words=config.get("base_words", []),
                rules_config=config.get("rules", {})
            )
        elif atype == "mask":
            return MaskAttack(
                mask=config.get("mask", "?u?l?l?l?d?d?d?d"),
                custom_charsets=config.get("custom_charsets")
            )
        elif atype == "hybrid":
            return HybridAttack(
                base_words=config.get("base_words", []),
                prefixes=config.get("prefixes", []),
                suffixes=config.get("suffixes", []),
                add_years=config.get("add_years", True),
                add_symbols=config.get("add_symbols", True)
            )
        elif atype == "brute_force":
            return BruteForceAttack(
                charset=config.get("charset", "abcdefghijklmnopqrstuvwxyz0123456789"),
                min_len=config.get("min_len", 1),
                max_len=config.get("max_len", 6),
                prefixes=config.get("prefixes"),
                suffixes=config.get("suffixes")
            )
        elif atype == "pattern":
            return PatternAttack(
                words=config.get("words", []),
                symbols=config.get("symbols", ["@", "!", "#"]),
                min_digits=config.get("min_digits", 1),
                max_digits=config.get("max_digits", 4)
            )
        else:
            raise ValueError(f"Unknown attack type: {attack_type}")

    def start_recovery(
        self,
        file_path: str,
        attack_type: str,
        config: Dict[str, Any],
        worker_count: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Optional[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_info = FileDetector.analyze(file_path)
        file_hash = file_info.get("fingerprint", "")
        file_name = os.path.basename(file_path)

        attack = self.create_attack(attack_type, config)
        total = attack.estimated_total_candidates()
        candidates_gen = attack.generate_candidates()

        session_id = self.db.create_session(
            file_hash=file_hash,
            file_name=file_name,
            file_path=file_path,
            attack_type=attack_type,
            config=config
        )

        self.active_scheduler = RecoveryScheduler(
            file_path=file_path,
            candidates_generator=candidates_gen,
            total_candidates=total,
            worker_count=worker_count,
            checkpoint_db=self.db,
            session_id=session_id
        )

        return self.active_scheduler.run(progress_callback=progress_callback)

    def resume_session(
        self,
        session_id: int,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Optional[str]:
        session = self.db.get_session(session_id)
        if not session:
            raise ValueError(f"Session ID {session_id} not found.")

        file_path = session["file_path"]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target file no longer exists at: {file_path}")

        attack_type = session["attack_type"]
        config = session["config"]
        pos = session["candidate_position"]
        elapsed = session["elapsed_seconds"]

        attack = self.create_attack(attack_type, config)
        total = attack.estimated_total_candidates()
        candidates_gen = attack.generate_candidates()

        self.active_scheduler = RecoveryScheduler(
            file_path=file_path,
            candidates_generator=candidates_gen,
            total_candidates=total,
            checkpoint_db=self.db,
            session_id=session_id,
            resume_position=pos,
            resume_elapsed=elapsed
        )

        return self.active_scheduler.run(progress_callback=progress_callback)
