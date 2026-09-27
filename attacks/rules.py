from typing import Iterator, List, Dict, Any
from attacks.base import BaseAttack
from core.candidate_engine import CandidateGenerator

class RulesAttack(BaseAttack):
    def __init__(self, base_words: List[str], rules_config: Dict[str, Any]):
        self.base_words = base_words
        self.rules_config = rules_config

    def name(self) -> str:
        return "Rule / Mutation Attack"

    def estimated_total_candidates(self) -> int:
        # Approximate search size based on rules
        num_words = len(self.base_words)
        multiplier = 5  # case transformations
        if self.rules_config.get("append_digits"):
            multiplier += 10
        if self.rules_config.get("prepend_digits"):
            multiplier += 10
        if self.rules_config.get("years"):
            multiplier += len(self.rules_config["years"]) * 2
        return num_words * multiplier

    def generate_candidates(self) -> Iterator[str]:
        return CandidateGenerator.rule_mutation_attack(self.base_words, self.rules_config)
