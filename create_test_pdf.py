from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


output_path = Path.home() / "Documents" / "OCR_RAG_Test.pdf"

document = SimpleDocTemplate(str(output_path), pagesize=A4)
styles = getSampleStyleSheet()

content = [
    Paragraph("OCR and RAG Test Document", styles["Title"]),
    Spacer(1, 20),
]

paragraphs = [
    "OCR means Optical Character Recognition.",
    "RAG means Retrieval-Augmented Generation.",
    "The embedding model used in this project is all-MiniLM-L6-v2.",
    "ChromaDB stores document chunks and their embeddings.",
    "The retriever finds relevant information before Ollama generates an answer.",
]

for text in paragraphs:
    content.append(Paragraph(text, styles["BodyText"]))
    content.append(Spacer(1, 12))

document.build(content)

print(f"PDF created successfully: {output_path}")