from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


# Configure paths for Windows and Docker
if Path("/.dockerenv").exists():
    TESSERACT_PATH = "tesseract"
    POPPLER_PATH = None
else:
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\Users\Aadi Rhythm\Downloads\Release-26.09.0-0\poppler-26.09.0\Library\bin"


pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_text_from_pdf(pdf_path: str) -> str:
    pdf_file = Path(pdf_path)

    if not pdf_file.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_file}")

    if POPPLER_PATH:
        pages = convert_from_path(
            str(pdf_file),
            dpi=300,
            poppler_path=POPPLER_PATH,
        )
    else:
        pages = convert_from_path(
            str(pdf_file),
            dpi=300,
        )

    extracted_pages = []

    for page_number, page_image in enumerate(pages, start=1):
        page_text = pytesseract.image_to_string(page_image)

        extracted_pages.append(
            f"--- Page {page_number} ---\n{page_text}"
        )

    return "\n\n".join(extracted_pages)