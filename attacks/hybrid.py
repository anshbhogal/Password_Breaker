from typing import Iterator, List
from attacks.base import BaseAttack
from core.candidate_engine import CandidateGenerator

class HybridAttack(BaseAttack):
    def __init__(self, base_words: List[str], prefixes: List[str], suffixes: List[str], add_years: bool = True, add_symbols: bool = True):
        self.base_words = base_words
        self.prefixes = prefixes
        self.suffixes = suffixes
        self.add_years = add_years
        self.add_symbols = add_symbols

    def name(self) -> str:
        return "Hybrid / Combined Attack"

    def estimated_total_candidates(self) -> int:
        p_len = max(1, len(self.prefixes))
        s_len = max(1, len(self.suffixes))
        yr_len = 9 if self.add_years else 1
        sym_len = 6 if self.add_symbols else 1
        return len(self.base_words) * p_len * s_len * yr_len * sym_len * 2

    def generate_candidates(self) -> Iterator[str]:
        return CandidateGenerator.hybrid_attack(
            self.base_words, self.prefixes, self.suffixes, self.add_years, self.add_symbols
        )
