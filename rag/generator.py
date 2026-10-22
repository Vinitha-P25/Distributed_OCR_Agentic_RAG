import ollama
from rag.retriever import retrieve_relevant_chunks

MODEL_NAME = "llama3.2:1b"


def generate_answer(question: str, top_k: int = 3) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    chunks = retrieve_relevant_chunks(question, top_k=top_k)

    if not chunks:
        return {
            "question": question,
            "answer": "No relevant information was found in the documents.",
            "sources": []
        }

    context = "\n\n".join(chunk["text"] for chunk in chunks)

    prompt = f"""
Answer the question using the context below.

Context:
{context}

Question: {question}

Give a short, direct answer based on the context.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0}
    )

    answer = response["message"]["content"]

    sources = [
        {
            "document_name": chunk["document_name"],
            "chunk_index": chunk["chunk_index"],
            "distance": chunk["distance"]
        }
        for chunk in chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


def main():
    question = "What does OCR mean?"

    print("Question:", question)
    print("\nGenerating answer...")

    result = generate_answer(question)

    print("\nGenerated Answer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(
            f"Document: {source['document_name']} | "
            f"Chunk: {source['chunk_index']} | "
            f"Distance: {source['distance']:.4f}"
        )


if __name__ == "__main__":
    main()