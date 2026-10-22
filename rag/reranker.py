from sentence_transformers import CrossEncoder

from rag.hybrid_retriever import hybrid_search


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Load the reranking model once.
_reranker = None


def get_reranker():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(MODEL_NAME)

    return _reranker


def rerank_results(
    question: str,
    results: list[dict],
    top_k: int = 5,
) -> list[dict]:
    """
    Rerank hybrid-search results using a cross-encoder.

    The cross-encoder evaluates each question and document chunk
    together and assigns a relevance score.
    """

    if not results:
        return []

    model = get_reranker()

    pairs = [
        (question, result["text"])
        for result in results
    ]

    scores = model.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):
        updated_result = result.copy()
        updated_result["reranker_score"] = float(score)

        reranked_results.append(updated_result)

    reranked_results.sort(
        key=lambda item: item["reranker_score"],
        reverse=True,
    )

    return reranked_results[:top_k]


def retrieve_and_rerank(
    question: str,
    candidate_k: int = 20,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve candidate chunks through hybrid search,
    then rerank them using a cross-encoder.
    """

    candidates = hybrid_search(
        question=question,
        top_k=candidate_k,
    )

    return rerank_results(
        question=question,
        results=candidates,
        top_k=top_k,
    )


if __name__ == "__main__":

    question = input(
        "Enter a question to test hybrid retrieval and reranking: "
    ).strip()

    results = retrieve_and_rerank(
        question=question,
        candidate_k=20,
        top_k=5,
    )

    print("\nHybrid Search + Cross-Encoder Reranking")
    print("=" * 60)

    if not results:
        print("No relevant chunks found.")
    else:
        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(
                f"Reranker Score: "
                f"{result['reranker_score']:.4f}"
            )
            print(f"Metadata: {result['metadata']}")
            print(f"Text: {result['text'][:500]}")
            print("-" * 60)