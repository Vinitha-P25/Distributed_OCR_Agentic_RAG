from pathlib import Path

import pytesseract
from pdf2image import convert_from_path

# Tesseract executable path

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Poppler binary directory

POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_pdf(pdf_path: str) -> str:
"""Extract text from every page of a PDF using OCR."""

```
pdf_file = Path(pdf_path)

if not pdf_file.is_file():
    raise FileNotFoundError(f"PDF not found: {pdf_file}")

pages = convert_from_path(
    str(pdf_file),
    dpi=300,
    poppler_path=POPPLER_PATH,
)

extracted_pages = []

for page_number, page_image in enumerate(pages, start=1):
    page_text = pytesseract.image_to_string(page_image)

    extracted_pages.append(
        f"--- Page {page_number} ---\n{page_text}"
    )

return "\n\n".join(extracted_pages)
```
