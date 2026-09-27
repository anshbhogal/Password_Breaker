from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseFormatAdapter(ABC):
    """
    Abstract base class for all file format adapters.
    """
    
    @abstractmethod
    def is_supported(self, file_path: str) -> bool:
        """
        Check if the file path is supported by this adapter.
        """
        pass

    @abstractmethod
    def get_encryption_info(self, file_path: str) -> Dict[str, Any]:
        """
        Extract encryption metadata (e.g. is_encrypted, algorithm, permissions, password_type).
        """
        pass

    @abstractmethod
    def verify_password(self, file_path: str, password: str) -> bool:
        """
        Verify if the given password opens/decrypts the target file.
        Returns True if password is valid, False otherwise.
        """
        pass
