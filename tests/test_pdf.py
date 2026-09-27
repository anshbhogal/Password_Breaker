import os
from formats.pdf import PDFFormatAdapter

def test_pdf_adapter():
    adapter = PDFFormatAdapter()
    pdf_path = "tests/fixtures/sample_protected.pdf"
    assert adapter.is_supported(pdf_path) is True
    
    info = adapter.get_encryption_info(pdf_path)
    assert info["is_encrypted"] is True

    # Test verification
    assert adapter.verify_password(pdf_path, "wrongpass") is False
    assert adapter.verify_password(pdf_path, "ansh2004") is True

def test_pdf_unicode():
    adapter = PDFFormatAdapter()
    pdf_path = "tests/fixtures/sample_unicode.pdf"
    assert adapter.verify_password(pdf_path, "₹ansh2004") is True
