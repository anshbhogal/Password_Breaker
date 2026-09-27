import time
import os
import sys
import psutil
import multiprocessing
from typing import Dict, Any

from formats import get_adapter_for_file
from core.candidate_engine import CandidateGenerator
from core.recovery_engine import RecoveryEngine

def benchmark_candidate_generation(count: int = 100000) -> float:
    """Measure raw candidate generation throughput."""
    gen = CandidateGenerator.mask_attack("Ansh?d?d?d?d")
    start = time.perf_counter()
    i = 0
    for _ in gen:
        i += 1
        if i >= count:
            break
    elapsed = time.perf_counter() - start
    speed = i / elapsed if elapsed > 0 else 0
    return speed

def benchmark_format_verification(file_path: str, candidate_count: int = 1000, workers: int = 1) -> Dict[str, Any]:
    """Measure single-process or multi-process password verification throughput."""
    adapter = get_adapter_for_file(file_path)
    if not adapter:
        return {"error": f"No adapter found for {file_path}"}

    candidates = [f"wrong_pass_{i}" for i in range(candidate_count)]
    
    start_mem = psutil.Process().memory_info().rss / (1024 * 1024)
    start_time = time.perf_counter()

    if workers == 1:
        tested = 0
        for pwd in candidates:
            adapter.verify_password(file_path, pwd)
            tested += 1
    else:
        from core.scheduler import RecoveryScheduler
        scheduler = RecoveryScheduler(
            file_path=file_path,
            candidates_generator=iter(candidates),
            total_candidates=candidate_count,
            worker_count=workers,
            chunk_size=100
        )
        scheduler.run()
        tested = candidate_count

    elapsed = time.perf_counter() - start_time
    end_mem = psutil.Process().memory_info().rss / (1024 * 1024)
    speed = tested / elapsed if elapsed > 0 else 0

    return {
        "file": os.path.basename(file_path),
        "candidates": tested,
        "elapsed_sec": elapsed,
        "speed_cps": speed,
        "workers": workers,
        "ram_mb": end_mem - start_mem
    }

def run_full_benchmark():
    print("=========================================================", flush=True)
    print("  LOCAL DOCUMENT PASSWORD RECOVERY BENCHMARK SUITE", flush=True)
    print("=========================================================", flush=True)
    print(f"System CPU Cores : {multiprocessing.cpu_count()}", flush=True)
    print(f"Python Version   : {sys.version.split()[0]}", flush=True)
    print("---------------------------------------------------------", flush=True)

    gen_speed = benchmark_candidate_generation(100000)
    print(f"[+] Candidate Generation Speed : {gen_speed:,.0f} candidates/sec", flush=True)
    print("---------------------------------------------------------", flush=True)

    fixtures = [
        "tests/fixtures/sample_protected.pdf",
        "tests/fixtures/sample_protected.zip",
    ]

    for fix in fixtures:
        if not os.path.exists(fix):
            print(f"[!] Fixture not found: {fix}", flush=True)
            continue

        print(f"\n[*] Benchmarking Format: {os.path.basename(fix)}", flush=True)
        for w in [1, 2, 4, multiprocessing.cpu_count()]:
            res = benchmark_format_verification(fix, candidate_count=500, workers=w)
            print(f"   Workers: {w:<2} | Tested: {res['candidates']:<5} | Time: {res['elapsed_sec']:.3f}s | Speed: {res['speed_cps']:,.0f} cand/sec", flush=True)

if __name__ == "__main__":
    run_full_benchmark()
