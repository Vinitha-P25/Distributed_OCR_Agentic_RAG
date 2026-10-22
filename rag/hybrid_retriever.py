from rank_bm25 import BM25Okapi

from rag.embedding_service import get_embedding_model
from storage.vector_store import get_collection


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]],
    k: int = 60,
) -> list[dict]:
    """
    Combine multiple ranked result lists using Reciprocal Rank Fusion.
    """

    fused_results = {}

    for ranked_list in ranked_lists:
        for rank, result in enumerate(ranked_list, start=1):

            chunk_id = result["id"]

            if chunk_id not in fused_results:
                fused_results[chunk_id] = {
                    **result,
                    "rrf_score": 0.0,
                }

            fused_results[chunk_id]["rrf_score"] += 1 / (k + rank)

    return sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )


def hybrid_search(
    question: str,
    top_k: int = 5,
    candidate_k: int = 20,
) -> list[dict]:
    """
    Retrieve relevant chunks using both:
    1. BM25 keyword retrieval.
    2. ChromaDB semantic retrieval.

    Combine their rankings using Reciprocal Rank Fusion.
    """

    question = question.strip()

    if not question:
        return []

    collection = get_collection()

    # Retrieve all indexed chunks for the BM25 corpus.
    stored_data = collection.get(
        include=["documents", "metadatas"]
    )

    documents = stored_data.get("documents") or []
    metadatas = stored_data.get("metadatas") or []
    ids = stored_data.get("ids") or []

    if not documents:
        print("No indexed document chunks found.")
        return []

    # Build the keyword-search corpus.
    tokenized_corpus = [
        document.lower().split()
        for document in documents
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_question = question.lower().split()

    # BM25 keyword retrieval.
    bm25_scores = bm25.get_scores(tokenized_question)

    bm25_indices = sorted(
        range(len(bm25_scores)),
        key=lambda index: bm25_scores[index],
        reverse=True,
    )[:candidate_k]

    bm25_results = []

    for index in bm25_indices:

        if bm25_scores[index] <= 0:
            continue

        bm25_results.append(
            {
                "id": ids[index],
                "text": documents[index],
                "metadata": metadatas[index] or {},
                "bm25_score": float(bm25_scores[index]),
            }
        )

    # Semantic retrieval using the existing embedding model.
    embedding_model = get_embedding_model()

    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    semantic_data = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(candidate_k, len(documents)),
        include=["documents", "metadatas", "distances"],
    )

    semantic_results = []

    semantic_ids = (semantic_data.get("ids") or [[]])[0]
    semantic_documents = (
        semantic_data.get("documents") or [[]]
    )[0]
    semantic_metadatas = (
        semantic_data.get("metadatas") or [[]]
    )[0]
    semantic_distances = (
        semantic_data.get("distances") or [[]]
    )[0]

    for chunk_id, text, metadata, distance in zip(
        semantic_ids,
        semantic_documents,
        semantic_metadatas,
        semantic_distances,
    ):
        semantic_results.append(
            {
                "id": chunk_id,
                "text": text,
                "metadata": metadata or {},
                "semantic_distance": float(distance),
            }
        )

    # Combine keyword and semantic rankings.
    fused_results = reciprocal_rank_fusion(
        [bm25_results, semantic_results]
    )

    return fused_results[:top_k]


if __name__ == "__main__":

    test_question = input(
        "Enter a question to test hybrid retrieval: "
    ).strip()

    results = hybrid_search(
        question=test_question,
        top_k=5,
    )

    print("\nHybrid Search Results")
    print("=" * 60)

    if not results:
        print("No relevant chunks found.")
    else:
        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"RRF Score: {result['rrf_score']:.6f}")
            print(f"Metadata: {result['metadata']}")
            print(f"Text: {result['text'][:500]}")
            print("-" * 60)