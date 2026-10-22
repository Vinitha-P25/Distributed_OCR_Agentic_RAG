from pathlib import Path

from sentence_transformers import SentenceTransformer

from rag.text_chunker import split_text_into_chunks
from storage.vector_store import store_chunks


PROJECT_DIR = Path(__file__).resolve().parent.parent
TEXT_FILE = PROJECT_DIR / "extracted_text.txt"

MODEL_NAME = "all-MiniLM-L6-v2"

# Reuse the model instead of loading it for every document.
_embedding_model = None


def get_embedding_model():
    """Load the embedding model once and reuse it."""

    global _embedding_model

    if _embedding_model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _embedding_model = SentenceTransformer(MODEL_NAME)

    return _embedding_model


def index_document(text: str, document_name: str) -> int:
    """Chunk document text, generate embeddings, and store them."""

    if not text or not text.strip():
        raise ValueError("Document text is empty.")

    chunks = split_text_into_chunks(
        text,
        chunk_size=300,
        overlap=50
    )

    if not chunks:
        print("No chunks were created.")
        return 0

    print(f"Total chunks: {len(chunks)}")

    model = get_embedding_model()

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print(f"Embeddings shape: {embeddings.shape}")

    store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_name=document_name
    )

    print("Document indexed successfully!")

    return len(chunks)


def main() -> None:
    """Create embeddings for the existing extracted_text.txt file."""

    if not TEXT_FILE.exists():
        raise FileNotFoundError(
            f"Extracted text file not found: {TEXT_FILE}"
        )

    text = TEXT_FILE.read_text(encoding="utf-8")

    count = index_document(
        text=text,
        document_name=TEXT_FILE.name
    )

    print(f"Successfully indexed {count} chunks.")


if __name__ == "__main__":
    main()