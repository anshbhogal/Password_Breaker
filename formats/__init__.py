from typing import List, Optional, Dict, Any
from formats.base import BaseFormatAdapter
from formats.pdf import PDFFormatAdapter
from formats.office import OfficeFormatAdapter
from formats.zip import ZipFormatAdapter
from formats.sevenzip import SevenZipFormatAdapter

ALL_ADAPTERS: List[BaseFormatAdapter] = [
    PDFFormatAdapter(),
    OfficeFormatAdapter(),
    ZipFormatAdapter(),
    SevenZipFormatAdapter()
]

def get_adapter_for_file(file_path: str) -> Optional[BaseFormatAdapter]:
    """
    Find matching format adapter for a target file path.
    """
    for adapter in ALL_ADAPTERS:
        if adapter.is_supported(file_path):
            return adapter
    return None

def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze file format and encryption metadata.
    """
    adapter = get_adapter_for_file(file_path)
    if not adapter:
        return {
            "format": "Unknown / Unsupported",
            "file_name": file_path,
            "file_size": 0,
            "is_encrypted": False,
            "algorithm": "N/A",
            "password_type": "N/A",
            "is_supported": False,
            "error": "No matching format adapter found for this file extension or structure."
        }
    return adapter.get_encryption_info(file_path)
