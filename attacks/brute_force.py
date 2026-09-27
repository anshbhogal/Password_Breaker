from typing import Iterator, Optional, List
from attacks.base import BaseAttack
from core.candidate_engine import CandidateGenerator

class BruteForceAttack(BaseAttack):
    def __init__(self, charset: str, min_len: int, max_len: int, prefixes: Optional[List[str]] = None, suffixes: Optional[List[str]] = None):
        self.charset = charset
        self.min_len = min_len
        self.max_len = max_len
        self.prefixes = prefixes
        self.suffixes = suffixes

    def name(self) -> str:
        return "Bounded Brute-Force Attack"

    def estimated_total_candidates(self) -> int:
        return CandidateGenerator.calculate_brute_force_space(
            len(self.charset), self.min_len, self.max_len, self.prefixes, self.suffixes
        )

    def generate_candidates(self) -> Iterator[str]:
        return CandidateGenerator.brute_force_attack(
            self.charset, self.min_len, self.max_len, self.prefixes, self.suffixes
        )
