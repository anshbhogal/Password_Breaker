import os
import pypdf
import pyzipper
import py7zr

def create_encrypted_pdf(output_path: str, password: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt(password)
    with open(output_path, "wb") as f:
        writer.write(f)

def create_encrypted_zip(output_path: str, password: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pyzipper.AESZipFile(output_path, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode('utf-8'))
        zf.writestr('secret.txt', 'This is confidential content.')

def create_encrypted_7z(output_path: str, password: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with py7zr.SevenZipFile(output_path, 'w', password=password) as zf:
        zf.writestr('secret.txt', 'This is confidential 7z content.')

if __name__ == "__main__":
    create_encrypted_pdf("tests/fixtures/sample_protected.pdf", "ansh2004")
    create_encrypted_pdf("tests/fixtures/sample_unicode.pdf", "₹ansh2004")
    create_encrypted_zip("tests/fixtures/sample_protected.zip", "Ansh@2004")
    create_encrypted_7z("tests/fixtures/sample_protected.7z", "secret123")
    print("Test fixtures generated successfully.")
