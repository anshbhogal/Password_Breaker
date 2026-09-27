import os
from formats.zip import ZipFormatAdapter

def test_zip_adapter():
    adapter = ZipFormatAdapter()
    zip_path = "tests/fixtures/sample_protected.zip"
    assert adapter.is_supported(zip_path) is True
    
    info = adapter.get_encryption_info(zip_path)
    assert info["is_encrypted"] is True

    assert adapter.verify_password(zip_path, "wrongpass") is False
    assert adapter.verify_password(zip_path, "Ansh@2004") is True
