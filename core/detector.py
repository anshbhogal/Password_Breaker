import os
import hashlib
from typing import Dict, Any
from formats import analyze_file, get_adapter_for_file

class FileDetector:
    """
    Analyzes document file attributes, calculates file fingerprints,
    and detects format encryption capabilities.
    """

    @staticmethod
    def get_file_fingerprint(file_path: str) -> str:
        """
        Generate SHA256 fingerprint for session tracking.
        Reads first 64KB for rapid hashing.
        """
        if not os.path.exists(file_path):
            return ""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            chunk = f.read(65536)
            hasher.update(chunk)
            hasher.update(str(os.path.getsize(file_path)).encode('utf-8'))
        return hasher.hexdigest()

    @staticmethod
    def analyze(file_path: str) -> Dict[str, Any]:
        info = analyze_file(file_path)
        info["fingerprint"] = FileDetector.get_file_fingerprint(file_path)
        return info
