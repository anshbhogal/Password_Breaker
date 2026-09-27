from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any

class BaseAttack(ABC):
    @abstractmethod
    def name(self) -> str:
        """Return attack name."""
        pass

    @abstractmethod
    def generate_candidates(self) -> Iterator[str]:
        """Return an iterator of candidate strings."""
        pass

    @abstractmethod
    def estimated_total_candidates(self) -> int:
        """Return estimated candidate space size (0 if unknown)."""
        pass
