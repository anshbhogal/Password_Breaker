from abc import ABC, abstractmethod
from typing import List, Optional

class BaseAccelerator(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if accelerator hardware/framework is available."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return human readable accelerator name."""
        pass

    @abstractmethod
    def verify_batch(self, file_path: str, candidates: List[str]) -> Optional[str]:
        """
        Verify a batch of candidate passwords against the file.
        Returns the matching password if found, else None.
        """
        pass
