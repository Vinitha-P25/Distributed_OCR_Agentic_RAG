from pathlib import Path

import chromadb


PROJECT_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = PROJECT_DIR / "database" / "chroma_db"

COLLECTION_NAME = "ocr_documents"


def get_collection():
    """Create or retrieve the persistent ChromaDB collection."""

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def store_chunks(
    chunks: list[str],
    embeddings,
    document_name: str = "sample_document.pdf"
) -> None:
    """Store text chunks, embeddings, and document metadata."""

    if not chunks:
        print("No chunks to store.")
        return

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    collection = get_collection()

    ids = [
        f"{document_name}_chunk_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "document_name": document_name,
            "chunk_index": index
        }
        for index in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Database location: {VECTOR_DB_DIR}")


def main() -> None:
    """Check that the persistent vector store is accessible."""

    collection = get_collection()

    print("ChromaDB initialized successfully.")
    print(f"Collection name: {collection.name}")
    print(f"Existing stored chunks: {collection.count()}")


if __name__ == "__main__":
    main()
