import itertools
from typing import Iterator, List
from attacks.base import BaseAttack

class PatternAttack(BaseAttack):
    """
    Template pattern attack for custom structured formats like:
    [Word] + [Special] + [Digits]
    """
    def __init__(self, words: List[str], symbols: List[str], min_digits: int = 1, max_digits: int = 4):
        self.words = words
        self.symbols = symbols
        self.min_digits = min_digits
        self.max_digits = max_digits

    def name(self) -> str:
        return "Pattern-Based Attack"

    def estimated_total_candidates(self) -> int:
        digit_count = sum(10**d for d in range(self.min_digits, self.max_digits + 1))
        return len(self.words) * len(self.symbols) * digit_count

    def generate_candidates(self) -> Iterator[str]:
        for w in self.words:
            for sym in self.symbols:
                for d_len in range(self.min_digits, self.max_digits + 1):
                    for digits in itertools.product("0123456789", repeat=d_len):
                        d_str = "".join(digits)
                        yield f"{w}{sym}{d_str}"
                        yield f"{d_str}{sym}{w}"
