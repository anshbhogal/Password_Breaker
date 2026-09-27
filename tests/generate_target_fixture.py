import os
import pypdf

def generate_target_pdf():
    os.makedirs("tests/fixtures", exist_ok=True)
    pdf_path = "tests/fixtures/sample_01012345.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("01012345")
    with open(pdf_path, "wb") as f:
        writer.write(f)
    print(f"Generated target PDF: {pdf_path}")

if __name__ == "__main__":
    generate_target_pdf()
