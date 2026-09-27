from formats import get_adapter_for_file

def worker_verify_chunk(args):
    """
    Multiprocessing top-level target function.
    args: (file_path, chunk_candidates)
    """
    file_path, candidates = args
    adapter = get_adapter_for_file(file_path)
    if not adapter:
        return None
    for pwd in candidates:
        if adapter.verify_password(file_path, pwd):
            return pwd
    return None
