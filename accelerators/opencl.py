from typing import List, Optional
from accelerators.base import BaseAccelerator

class OpenCLAccelerator(BaseAccelerator):
    """
    OpenCL GPU Acceleration module.
    Falls back gracefully if PyOpenCL is unavailable.
    """

    def __init__(self):
        self._available = False
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            if platforms:
                self._available = True
        except Exception:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def name(self) -> str:
        return "OpenCL GPU Accelerator"

    def verify_batch(self, file_path: str, candidates: List[str]) -> Optional[str]:
        from accelerators.cpu import CPUAccelerator
        return CPUAccelerator().verify_batch(file_path, candidates)
