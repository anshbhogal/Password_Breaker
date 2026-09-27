import os
from typing import Dict, Any
from formats.base import BaseFormatAdapter

try:
    import pypdf
except ImportError:
    pypdf = None

class PDFFormatAdapter(BaseFormatAdapter):
    """
    Adapter for PDF document password verification and analysis using pypdf.
    """

    def is_supported(self, file_path: str) -> bool:
        if not file_path or not os.path.exists(file_path):
            return False
        return file_path.lower().endswith(".pdf")

    def get_encryption_info(self, file_path: str) -> Dict[str, Any]:
        info = {
            "format": "PDF",
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "is_encrypted": False,
            "algorithm": "Unknown",
            "password_type": "Unknown",
            "is_supported": True,
            "error": None
        }

        if not pypdf:
            info["is_supported"] = False
            info["error"] = "pypdf library not installed"
            return info

        try:
            reader = pypdf.PdfReader(file_path)
            info["is_encrypted"] = reader.is_encrypted
            if reader.is_encrypted:
                info["password_type"] = "File Open / User Password"
                # Extract algorithm detail if available in trailer / encrypt object
                if hasattr(reader, "_encryption") and reader._encryption:
                    enc = reader._encryption
                    if hasattr(enc, "v"):
                        if enc.v == 5:
                            info["algorithm"] = "AES-256 (PDF 2.0 / R6)"
                        elif enc.v == 4:
                            info["algorithm"] = "AES-128 / RC4 (R4)"
                        else:
                            info["algorithm"] = f"Standard PDF Security (V={enc.v})"
                    else:
                        info["algorithm"] = "Standard PDF Security"
                else:
                    info["algorithm"] = "Standard PDF Security"
        except Exception as e:
            info["error"] = str(e)

        return info

    def verify_password(self, file_path: str, password: str) -> bool:
        if not pypdf or not os.path.exists(file_path):
            return False
        try:
            reader = pypdf.PdfReader(file_path)
            if not reader.is_encrypted:
                return True
            res = reader.decrypt(password)
            if res != 0:
                # Extra check to ensure page structure can be read cleanly
                try:
                    _ = len(reader.pages)
                    return True
                except Exception:
                    return False
            return False
        except Exception:
            return False
