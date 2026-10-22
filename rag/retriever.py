from sentence_transformers import SentenceTransformer

from storage.vector_store import get_collection


MODEL_NAME = "all-MiniLM-L6-v2"

# Load the embedding model only once.
_model = None


def get_embedding_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 3
) -> list[dict]:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    collection = get_collection()

    if collection.count() == 0:
        print("No documents are stored in ChromaDB.")
        return []

    model = get_embedding_model()

    question_embedding = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=min(top_k, collection.count()),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_chunks = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        metadata = metadata or {}

        retrieved_chunks.append({
            "text": document,
            "document_name": metadata.get(
                "document_name",
                "unknown"
            ),
            "chunk_index": metadata.get("chunk_index"),
            "distance": distance
        })

    return retrieved_chunks


def main():

    question = "What does OCR mean?"

    print("Question:", question)
    print("\nSearching ChromaDB...")

    chunks = retrieve_relevant_chunks(
        question,
        top_k=3
    )

    if not chunks:
        print("No relevant text found.")
        return

    print("\nRetrieved text and sources:")

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n--- Result {index} ---")
        print("Source:", chunk["document_name"])
        print("Chunk index:", chunk["chunk_index"])
        print(f"Distance: {chunk['distance']:.4f}")
        print("Text:", chunk["text"])


if __name__ == "__main__":
    main()