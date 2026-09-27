from typing import Iterator, Optional, Dict
from attacks.base import BaseAttack
from core.candidate_engine import CandidateGenerator

class MaskAttack(BaseAttack):
    def __init__(self, mask: str, custom_charsets: Optional[Dict[str, str]] = None):
        self.mask = mask
        self.custom_charsets = custom_charsets

    def name(self) -> str:
        return "Mask Attack"

    def estimated_total_candidates(self) -> int:
        return CandidateGenerator.calculate_mask_space(self.mask, self.custom_charsets)

    def generate_candidates(self) -> Iterator[str]:
        return CandidateGenerator.mask_attack(self.mask, self.custom_charsets)
