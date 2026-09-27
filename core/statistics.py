import time
from typing import Dict, Any

class RecoveryStatistics:
    """
    Tracks and computes real-time performance statistics.
    """

    def __init__(self, total_candidates: int = 0, initial_tested: int = 0, initial_elapsed: float = 0.0):
        self.total_candidates = total_candidates
        self.tested_count = initial_tested
        self.initial_elapsed = initial_elapsed
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.candidates_sec = 0.0

    def update(self, newly_tested: int):
        self.tested_count += newly_tested
        now = time.time()
        elapsed_delta = now - self.last_update_time
        if elapsed_delta >= 0.5:
            # Recalculate current rate
            total_elapsed = self.get_elapsed_seconds()
            if total_elapsed > 0:
                self.candidates_sec = self.tested_count / total_elapsed
            self.last_update_time = now

    def get_elapsed_seconds(self) -> float:
        return self.initial_elapsed + (time.time() - self.start_time)

    def get_eta_seconds(self) -> float:
        if self.total_candidates <= 0 or self.candidates_sec <= 0:
            return 0.0
        remaining = self.total_candidates - self.tested_count
        if remaining <= 0:
            return 0.0
        return remaining / self.candidates_sec

    def get_progress_percentage(self) -> float:
        if self.total_candidates <= 0:
            return 0.0
        pct = (self.tested_count / self.total_candidates) * 100.0
        return min(100.0, max(0.0, pct))

    def format_stats(self) -> Dict[str, Any]:
        elapsed = self.get_elapsed_seconds()
        eta = self.get_eta_seconds()
        return {
            "tested_count": self.tested_count,
            "total_candidates": self.total_candidates,
            "progress_pct": self.get_progress_percentage(),
            "speed_cps": self.candidates_sec,
            "elapsed_formatted": self._format_time(elapsed),
            "eta_formatted": self._format_time(eta) if eta > 0 else "Calculating..."
        }

    @staticmethod
    def _format_time(seconds: float) -> str:
        sec = int(seconds)
        hrs = sec // 3600
        mins = (sec % 3600) // 60
        secs = sec % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
