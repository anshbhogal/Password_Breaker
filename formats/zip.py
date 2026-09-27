import os
import zipfile
from typing import Dict, Any
from formats.base import BaseFormatAdapter

try:
    import pyzipper
except ImportError:
    pyzipper = None

class ZipFormatAdapter(BaseFormatAdapter):
    """
    Adapter for ZIP archives (Standard PKWARE and AES-128/256 encrypted zip).
    """

    def is_supported(self, file_path: str) -> bool:
        if not file_path or not os.path.exists(file_path):
            return False
        return file_path.lower().endswith(".zip")

    def get_encryption_info(self, file_path: str) -> Dict[str, Any]:
        info = {
            "format": "ZIP Archive",
            "file_name": os.path.basename(file_path),
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "is_encrypted": False,
            "algorithm": "Unknown",
            "password_type": "Archive Encryption Password",
            "is_supported": True,
            "error": None
        }

        try:
            if pyzipper:
                with pyzipper.AESZipFile(file_path, 'r') as zf:
                    # Check if any file inside has flag_bits indicating encryption
                    for zinfo in zf.infolist():
                        if zinfo.flag_bits & 0x1:
                            info["is_encrypted"] = True
                            if zinfo.encryption:
                                info["algorithm"] = f"ZIP Encryption ({zinfo.encryption})"
                            else:
                                info["algorithm"] = "ZIP Encryption (AES/PKWARE)"
                            break
            else:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for zinfo in zf.infolist():
                        if zinfo.flag_bits & 0x1:
                            info["is_encrypted"] = True
                            info["algorithm"] = "PKWARE ZipCrypto"
                            break
        except Exception as e:
            info["error"] = str(e)

        return info

    def verify_password(self, file_path: str, password: str) -> bool:
        if not os.path.exists(file_path):
            return False

        pwd_bytes = password.encode('utf-8')

        # Try pyzipper first (supports AES & ZipCrypto)
        if pyzipper:
            try:
                with pyzipper.AESZipFile(file_path, 'r') as zf:
                    zf.pwd = pwd_bytes
                    # Pick first encrypted file entry to test password
                    for member in zf.infolist():
                        if member.flag_bits & 0x1 and not member.is_dir():
                            # read first few bytes to verify CRC/decryption
                            with zf.open(member, 'r') as member_file:
                                _ = member_file.read(128)
                            return True
                    return True  # No encrypted files found
            except Exception:
                pass

        # Fallback to standard zipfile (standard ZipCrypto)
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.setpassword(pwd_bytes)
                for member in zf.infolist():
                    if member.flag_bits & 0x1 and not member.is_dir():
                        with zf.open(member, 'r') as member_file:
                            _ = member_file.read(128)
                        return True
                return True
        except Exception:
            return False
