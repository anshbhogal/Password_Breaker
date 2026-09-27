from typing import List, Optional
from accelerators.base import BaseAccelerator
from formats import get_adapter_for_file

class CPUAccelerator(BaseAccelerator):
    """
    Standard multi-core CPU verification engine.
    """

    def is_available(self) -> bool:
        return True

    def name(self) -> str:
        return "CPU Multiprocessing Core"

    def verify_batch(self, file_path: str, candidates: List[str]) -> Optional[str]:
        adapter = get_adapter_for_file(file_path)
        if not adapter:
            return None
        for pwd in candidates:
            if adapter.verify_password(file_path, pwd):
                return pwd
        return None
