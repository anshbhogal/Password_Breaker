import os
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Iterator, Callable, Optional, Dict, Any
from core.worker import worker_verify_chunk
from core.statistics import RecoveryStatistics
from core.checkpoint import CheckpointDatabase
from core.detector import FileDetector

class RecoveryScheduler:
    """
    Multiprocess execution manager for password recovery attacks.
    Provides batch processing, pause/resume, checkpointing, and live stats.
    """

    def __init__(
        self,
        file_path: str,
        candidates_generator: Iterator[str],
        total_candidates: int = 0,
        worker_count: Optional[int] = None,
        chunk_size: int = 1000,
        checkpoint_db: Optional[CheckpointDatabase] = None,
        session_id: Optional[int] = None,
        resume_position: int = 0,
        resume_elapsed: float = 0.0
    ):
        self.file_path = file_path
        self.candidates_generator = candidates_generator
        self.total_candidates = total_candidates
        self.worker_count = worker_count or max(1, multiprocessing.cpu_count())
        self.chunk_size = chunk_size
        self.checkpoint_db = checkpoint_db
        self.session_id = session_id
        
        self.stats = RecoveryStatistics(
            total_candidates=total_candidates,
            initial_tested=resume_position,
            initial_elapsed=resume_elapsed
        )

        self._is_paused = False
        self._is_stopped = False
        self._found_password: Optional[str] = None
        self.current_position = resume_position

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._is_stopped = True

    def run(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Optional[str]:
        """
        Main execution loop.
        Submits candidate chunks to ProcessPoolExecutor.
        """
        # Fast direct test first if position == 0
        from formats import get_adapter_for_file
        adapter = get_adapter_for_file(self.file_path)
        if not adapter:
            raise ValueError(f"No adapter available for file: {self.file_path}")

        # Skip candidates prior to resume position
        generator = self.candidates_generator
        if self.current_position > 0:
            skipped = 0
            while skipped < self.current_position:
                try:
                    next(generator)
                    skipped += 1
                except StopIteration:
                    break

        executor = ProcessPoolExecutor(max_workers=self.worker_count)
        futures = {}
        batch = []

        try:
            last_checkpoint_time = time.time()

            for cand in generator:
                if self._is_stopped:
                    break

                while self._is_paused:
                    time.sleep(0.2)
                    if self._is_stopped:
                        break

                batch.append(cand)

                if len(batch) >= self.chunk_size:
                    chunk_args = (self.file_path, list(batch))
                    fut = executor.submit(worker_verify_chunk, chunk_args)
                    futures[fut] = len(batch)
                    batch = []

                # Limit in-flight futures buffer (e.g., 2x worker count)
                if len(futures) >= self.worker_count * 2:
                    done = []
                    for fut in as_completed(list(futures.keys())):
                        cnt = futures.pop(fut)
                        result = fut.result()
                        self.current_position += cnt
                        self.stats.update(cnt)

                        if progress_callback:
                            progress_callback(self.stats.format_stats())

                        if result is not None:
                            self._found_password = result
                            self._is_stopped = True
                            break

                    if self._is_stopped:
                        break

                # Periodic Checkpoint
                if self.checkpoint_db and self.session_id and (time.time() - last_checkpoint_time > 3.0):
                    self.checkpoint_db.update_checkpoint(
                        session_id=self.session_id,
                        candidate_position=self.current_position,
                        elapsed_seconds=self.stats.get_elapsed_seconds(),
                        status="PAUSED" if self._is_paused else "RUNNING"
                    )
                    last_checkpoint_time = time.time()

            # Process remaining batch
            if batch and not self._is_stopped:
                chunk_args = (self.file_path, list(batch))
                fut = executor.submit(worker_verify_chunk, chunk_args)
                futures[fut] = len(batch)

            # Gather remaining futures
            for fut in as_completed(list(futures.keys())):
                cnt = futures.pop(fut)
                result = fut.result()
                self.current_position += cnt
                self.stats.update(cnt)

                if progress_callback:
                    progress_callback(self.stats.format_stats())

                if result is not None:
                    self._found_password = result
                    break

        finally:
            executor.shutdown(wait=False)

        # Final checkpoint update
        if self.checkpoint_db and self.session_id:
            final_status = "SUCCESS" if self._found_password else ("STOPPED" if self._is_stopped else "FINISHED")
            self.checkpoint_db.update_checkpoint(
                session_id=self.session_id,
                candidate_position=self.current_position,
                elapsed_seconds=self.stats.get_elapsed_seconds(),
                status=final_status,
                recovered_password=self._found_password
            )

        return self._found_password
