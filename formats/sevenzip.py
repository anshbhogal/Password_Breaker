import os
from typing import Dict, Any
from formats.base import BaseFormatAdapter

try:
    import py7zr
except ImportError:
    py7zr = None

class SevenZipFormatAdapter(BaseFormatAdapter):
    """
    Adapter for 7z archives using py7zr.
    """

    def is_supported(self, file_path: str) -> bool:
        if not file_path or not os.path.exists(file_path):
            return False
        return file_path.lower().endswith(".7z")

    def get_encryption_info(self, file_path: str) -> Dict[str, Any]:
        info = {
            "format": "7z Archive",
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "is_encrypted": False,
            "algorithm": "AES-256",
            "password_type": "Archive Encryption Password",
            "is_supported": True,
            "error": None
        }

        if not py7zr:
            info["is_supported"] = False
            info["error"] = "py7zr library not installed"
            return info

        try:
            is_enc = py7zr.is_7zfile(file_path)
            # Check if encrypted by trying to inspect without password
            info["is_encrypted"] = False
            try:
                with py7zr.SevenZipFile(file_path, mode='r') as archive:
                    if archive.needs_password():
                        info["is_encrypted"] = True
            except py7zr.PasswordRequired:
                info["is_encrypted"] = True
            except Exception:
                pass
        except Exception as e:
            info["error"] = str(e)

        return info

    def verify_password(self, file_path: str, password: str) -> bool:
        if not py7zr or not os.path.exists(file_path):
            return False
        try:
            with py7zr.SevenZipFile(file_path, mode='r', password=password) as archive:
                # Test reading / checking password header
                if archive.testzip() is None:
                    return True
                return True
        except py7zr.PasswordRequired:
            return False
        except py7zr.Bad7zFile:
            return False
        except Exception:
            return False
