import argparse
import sys
import os
import time
import itertools
from core.recovery_engine import RecoveryEngine

def print_banner():
    print("=" * 60)
    print("   LOCAL DOCUMENT PASSWORD RECOVERY SYSTEM v1.0")
    print("   Secure, Local & High-Performance Password Recovery")
    print("=" * 60)

def cmd_analyze(args, engine: RecoveryEngine):
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)

    print(f"\nAnalyzing file: {file_path}...")
    info = engine.analyze_file(file_path)
    
    print("-" * 50)
    print(f"File Name      : {info.get('file_name')}")
    print(f"Format         : {info.get('format')}")
    print(f"File Size      : {info.get('file_size')} bytes")
    print(f"Encrypted      : {'YES' if info.get('is_encrypted') else 'NO'}")
    print(f"Algorithm      : {info.get('algorithm')}")
    print(f"Protection Type: {info.get('password_type')}")
    print(f"Fingerprint    : {info.get('fingerprint')}")
    if info.get('error'):
        print(f"Warning/Error  : {info.get('error')}")
    print("-" * 50)

def cmd_recover(args, engine: RecoveryEngine):
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: Target file '{file_path}' does not exist.")
        sys.exit(1)

    mode = args.mode.lower()
    config = {}

    if mode == "dictionary":
        wordlist = args.wordlist or "resources/wordlists/default.txt"
        if not os.path.exists(wordlist):
            print(f"Error: Wordlist file '{wordlist}' not found.")
            sys.exit(1)
        config["wordlists"] = [wordlist]
        if args.custom_word:
            config["custom_words"] = args.custom_word
    elif mode == "mask":
        mask_str = args.mask or "Ansh?d?d?d?d"
        config["mask"] = mask_str
    elif mode == "rules" or mode == "mutation":
        words = args.words.split(",") if args.words else ["ansh"]
        config["base_words"] = words
        config["rules"] = {"append_digits": True, "years": ["2024", "2004"]}
    elif mode == "brute_force":
        config["charset"] = args.charset or "0123456789"
        config["min_len"] = args.min_len if args.min_len is not None else 1
        config["max_len"] = args.max_len if args.max_len is not None else 5
        if args.prefix:
            config["prefixes"] = [args.prefix]
        if args.suffix:
            config["suffixes"] = [args.suffix]
    elif mode == "hybrid":
        config["base_words"] = args.words.split(",") if args.words else ["ansh"]
        config["prefixes"] = args.prefix.split(",") if args.prefix else []
        config["suffixes"] = args.suffix.split(",") if args.suffix else []
    else:
        print(f"Error: Unsupported mode '{mode}'. Choose dictionary, mask, rules, hybrid, or brute_force.")
        sys.exit(1)

    if getattr(args, "debug", False):
        print("\n--- DEBUG DIAGNOSTICS MODE ---")
        print(f"Target File     : {file_path}")
        file_info = engine.analyze_file(file_path)
        print(f"Format & Enc    : {file_info.get('format')} ({file_info.get('algorithm')})")
        print(f"Attack Mode     : {mode}")
        print(f"Config          : {config}")
        attack_obj = engine.create_attack(mode, config)
        print(f"Calculated Space: {attack_obj.estimated_total_candidates():,} candidates")
        cands_gen = list(itertools.islice(attack_obj.generate_candidates(), 5))
        print(f"First 5 Samples : {cands_gen}")
        print("-------------------------------\n")

    print(f"\n[+] Starting {mode.upper()} recovery attack on '{file_path}'...")
    print(f"[+] Workers: {args.workers or 'Auto (all CPU cores)'}\n")

    def progress_cb(stats):
        sys.stdout.write(
            f"\rCandidates: {stats['tested_count']:,} / {stats['total_candidates']:,} "
            f"({stats['progress_pct']:.1f}%) | "
            f"Speed: {stats['speed_cps']:,.0f} cand/sec | "
            f"Elapsed: {stats['elapsed_formatted']} | "
            f"ETA: {stats['eta_formatted']}     "
        )
        sys.stdout.flush()

    start_t = time.time()
    result = engine.start_recovery(
        file_path=file_path,
        attack_type=mode,
        config=config,
        worker_count=args.workers,
        progress_callback=progress_cb
    )
    sys.stdout.write("\n")

    print("=" * 60)
    if result:
        print(f" SUCCESS! PASSWORD RECOVERED: {result}")
    else:
        print(" RECOVERY FINISHED: Password not found in search space.")
    print(f" Time elapsed: {time.time() - start_t:.2f} seconds")
    print("=" * 60)

def cmd_resume(args, engine: RecoveryEngine):
    session_id = args.session_id
    print(f"\n[+] Resuming recovery session #{session_id}...")

    def progress_cb(stats):
        sys.stdout.write(
            f"\rCandidates: {stats['tested_count']:,} / {stats['total_candidates']:,} "
            f"({stats['progress_pct']:.1f}%) | "
            f"Speed: {stats['speed_cps']:,.0f} cand/sec | "
            f"Elapsed: {stats['elapsed_formatted']}     "
        )
        sys.stdout.flush()

    start_t = time.time()
    try:
        result = engine.resume_session(session_id, progress_callback=progress_cb)
        sys.stdout.write("\n")
        print("=" * 60)
        if result:
            print(f" SUCCESS! PASSWORD RECOVERED: {result}")
        else:
            print(" RECOVERY FINISHED: Password not found.")
        print("=" * 60)
    except Exception as e:
        print(f"Error resuming session: {e}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Document Password Recovery CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # analyze command
    p_analyze = subparsers.add_parser("analyze", help="Analyze document encryption")
    p_analyze.add_argument("file", help="Path to document file")

    # recover command
    p_recover = subparsers.add_parser("recover", help="Start password recovery attack")
    p_recover.add_argument("--file", "-f", required=True, help="Path to document file")
    p_recover.add_argument("--mode", "-m", default="dictionary", help="Attack mode (dictionary, mask, rules, hybrid, brute_force)")
    p_recover.add_argument("--wordlist", "-w", help="Path to wordlist file")
    p_recover.add_argument("--custom-word", action="append", help="Custom base words")
    p_recover.add_argument("--mask", help="Mask pattern e.g. Ansh?d?d?d?d")
    p_recover.add_argument("--words", help="Comma-separated base words for rules/hybrid")
    p_recover.add_argument("--charset", help="Charset for brute force")
    p_recover.add_argument("--min-len", type=int, help="Min length for brute force")
    p_recover.add_argument("--max-len", type=int, help="Max length for brute force")
    p_recover.add_argument("--prefix", help="Prefixes for hybrid attack")
    p_recover.add_argument("--suffix", help="Suffixes for hybrid attack")
    p_recover.add_argument("--workers", type=int, help="Number of CPU worker processes")
    p_recover.add_argument("--debug", action="store_true", help="Enable verbose debug mode")

    # resume command
    p_resume = subparsers.add_parser("resume", help="Resume previous recovery session")
    p_resume.add_argument("session_id", type=int, help="Session ID from database")

    args = parser.parse_args()
    engine = RecoveryEngine()

    if args.command == "analyze":
        cmd_analyze(args, engine)
    elif args.command == "recover":
        cmd_recover(args, engine)
    elif args.command == "resume":
        cmd_resume(args, engine)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
