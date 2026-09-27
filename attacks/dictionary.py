import os
from typing import Iterator, List, Optional
from attacks.base import BaseAttack
from core.candidate_engine import CandidateGenerator

class DictionaryAttack(BaseAttack):
    def __init__(self, wordlists: List[str], custom_words: Optional[List[str]] = None):
        self.wordlists = wordlists
        self.custom_words = custom_words or []

    def name(self) -> str:
        return "Dictionary Attack"

    def estimated_total_candidates(self) -> int:
        total = len(self.custom_words)
        for w_path in self.wordlists:
            if os.path.exists(w_path):
                try:
                    with open(w_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total += sum(1 for line in f if line.strip())
                except Exception:
                    pass
        return total

    def generate_candidates(self) -> Iterator[str]:
        return CandidateGenerator.dictionary_attack(self.wordlists, self.custom_words)
