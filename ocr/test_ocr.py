from pathlib import Path
from ocr.ocr_service import extract_text_from_pdf

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = PROJECT_DIR / "uploads"

pdf_files = list(UPLOAD_DIR.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found in uploads folder.")
else:
    pdf_path = pdf_files[0]
    print(f"Testing OCR with: {pdf_path.name}")

    try:
        extracted_text = extract_text_from_pdf(str(pdf_path))

        print("\n========== EXTRACTED TEXT ==========\n")
        print(extracted_text)

        output_path = PROJECT_DIR / "extracted_text.txt"
        output_path.write_text(extracted_text, encoding="utf-8")

        print(f"\nExtracted text saved to: {output_path}")

    except Exception as error:
        print(f"OCR failed: {error}")