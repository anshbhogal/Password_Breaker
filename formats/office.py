import os
import io
from typing import Dict, Any
from formats.base import BaseFormatAdapter

try:
    import msoffcrypto
except ImportError:
    msoffcrypto = None

class OfficeFormatAdapter(BaseFormatAdapter):
    """
    Adapter for Microsoft Office formats (.doc, .docx, .xls, .xlsx, .ppt, .pptx)
    using msoffcrypto-tool.
    """

    SUPPORTED_EXTENSIONS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"}

    def is_supported(self, file_path: str) -> bool:
        if not file_path or not os.path.exists(file_path):
            return False
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def get_encryption_info(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        info = {
            "format": f"MS Office ({ext.upper()[1:]})",
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "is_encrypted": False,
            "algorithm": "Unknown",
            "password_type": "Unknown",
            "is_supported": True,
            "error": None
        }

        if not msoffcrypto:
            info["is_supported"] = False
            info["error"] = "msoffcrypto-tool library not installed"
            return info

        try:
            with open(file_path, "rb") as f:
                office_file = msoffcrypto.OfficeFile(f)
                info["is_encrypted"] = office_file.is_encrypted()
                if info["is_encrypted"]:
                    info["password_type"] = "File Open / Storage Encryption Password"
                    # Attempt to extract format/cipher detail
                    if hasattr(office_file, "format"):
                        info["algorithm"] = f"Office Crypto ({office_file.format})"
                    else:
                        info["algorithm"] = "Agile / Standard Encryption"
        except Exception as e:
            # File might be plain Office XML or unencrypted binary
            info["is_encrypted"] = False
            info["error"] = None

        return info

    def verify_password(self, file_path: str, password: str) -> bool:
        if not msoffcrypto or not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "rb") as f:
                office_file = msoffcrypto.OfficeFile(f)
                if not office_file.is_encrypted():
                    return True
                office_file.load_key(password=password)
                # Verify key by writing to dummy buffer
                out = io.BytesIO()
                office_file.decrypt(out)
                return True
        except Exception:
            return False
