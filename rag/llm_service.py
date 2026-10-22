import os
import requests

from dotenv import load_dotenv
from rag.reranker import retrieve_and_rerank

# Load environment variables from the project root .env file.
load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

MODEL_NAME = "llama3.2:1b"
def generate_answer(
    question: str,
    top_k: int = 3,
) -> dict:

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    # Step 1: Hybrid retrieval + cross-encoder reranking.
    chunks = retrieve_and_rerank(
        question=question,
        candidate_k=20,
        top_k=top_k,
    )

    if not chunks:
        return {
            "question": question,
            "answer": (
                "I could not find relevant information "
                "in the stored documents."
            ),
            "sources": [],
        }

    # Step 2: Prepare context for the LLM.
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks
    )

    # Step 3: Construct the grounded prompt.
    prompt = (
        "Answer the question using only the context below.\n"
        "Ignore minor OCR spelling mistakes when the meaning is clear.\n"
        "Do not invent facts that are not supported by the context.\n"
        "If the answer is missing, say you could not find it "
        "in the documents.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )

    # Step 4: Generate the answer using Ollama.
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

        result = response.json()

        answer = result.get(
            "response",
            "",
        ).strip()

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty answer."
            )

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check that Ollama "
            f"is running at {OLLAMA_URL}"
        ) from error

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Ollama response timed out."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Ollama request failed: {error}"
        ) from error

    # Step 5: Return source information.
    sources = []

    for chunk in chunks:
        metadata = chunk.get("metadata") or {}

        sources.append({
            "document_name": metadata.get(
                "document_name",
                "unknown",
            ),
            "chunk_index": metadata.get(
                "chunk_index",
                -1,
            ),
            "reranker_score": chunk.get(
                "reranker_score",
            ),
            "rrf_score": chunk.get(
                "rrf_score",
            ),
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    ).strip()

    print("\nGenerating answer...\n")

    result = generate_answer(question)

    print("Answer:")
    print(result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(source)