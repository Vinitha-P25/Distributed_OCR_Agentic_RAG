import os
import requests

from dotenv import load_dotenv

load_dotenv()

from rag.llm_service import generate_answer
from rag.reranker import retrieve_and_rerank
from rag.web_search import search_web


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

MODEL_NAME = "llama3.2:1b"

MIN_RERANKER_SCORE = float(
    os.getenv("RERANKER_MIN_SCORE", "0.0")
)

def classify_question(question: str) -> str:
    """Classify a question as document-related or general."""

    prompt = f"""
Classify the question into one category.

DOCUMENT: The question asks about uploaded documents,
OCR, RAG, machine learning, or technical information
that may be available in stored documents.

GENERAL: Greetings or general conversational questions.

Return only one word: DOCUMENT or GENERAL.

Question: {question}

Category:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=60
        )

        response.raise_for_status()

        category = (
            response.json()
            .get("response", "")
            .strip()
            .upper()
        )

        if "DOCUMENT" in category:
            return "DOCUMENT"

        return "GENERAL"

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Ollama timed out while classifying the question."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Question classification failed: {error}"
        ) from error


def generate_web_answer(question: str, web_results: list[dict]) -> str:
    """Generate an answer using retrieved web-search snippets."""

    if not web_results:
        return (
            "I couldn't find a relevant answer in the uploaded "
            "documents or through web search."
        )

    web_context = "\n\n".join(
        (
            f"Title: {result.get('title', '')}\n"
            f"URL: {result.get('url', '')}\n"
            f"Snippet: {result.get('snippet', '')}"
        )
        for result in web_results
    )

    prompt = f"""
Answer the question using the web-search results below.

Rules:
- Use only information supported by the supplied search results.
- If the results do not contain enough information, say so.
- Do not invent facts.
- Give a clear, concise answer.

Question:
{question}

Web-search results:
{web_context}

Answer:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=120
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        return answer or "The model did not generate an answer."

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running."
        ) from error

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Ollama timed out while generating the web-based answer."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Web-based answer generation failed: {error}"
        ) from error


def run_agent(question: str) -> dict:
    """Route questions through document RAG or web-search fallback."""

    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    category = classify_question(question)

    # Route general conversation directly to the LLM.
    if category == "GENERAL":
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": question,
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=120
        )

        response.raise_for_status()

        answer = response.json().get("response", "").strip()

        return {
            "question": question,
            "agent_decision": "general_answer",
            "answer": answer,
            "sources": []
        }

    # Retrieve and rerank relevant document chunks.
    ranked_chunks = retrieve_and_rerank(
        question,
        candidate_k=20,
        top_k=5
    )

    best_score = (
        ranked_chunks[0].get("reranker_score", float("-inf"))
        if ranked_chunks
        else float("-inf")
    )

    # If the documents appear relevant, use the existing RAG pipeline.
    if ranked_chunks and best_score >= MIN_RERANKER_SCORE:
        result = generate_answer(question)

        return {
            "question": question,
            "agent_decision": "retrieve_documents",
            "answer": result["answer"],
            "sources": result["sources"]
        }

    # No sufficiently relevant document chunks: use web search.
    web_results = search_web(question, max_results=5)

    answer = generate_web_answer(question, web_results)

    return {
        "question": question,
        "agent_decision": "web_search_fallback",
        "answer": answer,
        "sources": [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", "")
            }
            for result in web_results
        ]
    }


def main():
    question = input("Enter your question: ")

    try:
        result = run_agent(question)

        print("\nAgent decision:", result["agent_decision"])
        print("\nAnswer:\n", result["answer"])

        print("\nSources:")

        for source in result["sources"]:
            if "url" in source:
                print("-", source.get("title", "Web source"))
                print("  URL:", source["url"])
            else:
                print("-", source)

    except Exception as error:
        print(f"\nAgent failed: {error}")


if __name__ == "__main__":
    main()