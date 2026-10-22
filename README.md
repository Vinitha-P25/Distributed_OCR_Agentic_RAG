# Distributed OCR + Agentic RAG

An AI-powered document processing and question-answering system that extracts text from PDF documents, indexes the extracted content, and answers questions using Retrieval-Augmented Generation (RAG).

## Project Overview

This project combines Optical Character Recognition (OCR), asynchronous task processing, document metadata storage, semantic search, hybrid retrieval, reranking, and Large Language Models (LLMs).

Users can upload PDF documents through a Streamlit interface and ask questions about their content.

## Features

* **PDF Upload:** Upload and process PDF documents.
* **OCR:** Extract text from scanned PDFs using Tesseract and Poppler.
* **Asynchronous Processing:** Process document tasks using Celery and Redis.
* **Document Metadata:** Store document information and processing status in PostgreSQL.
* **Duplicate Detection:** Use SHA-256 fingerprints to identify duplicate documents.
* **Text Chunking:** Divide extracted text into smaller passages for retrieval.
* **Embeddings:** Generate semantic embeddings using Sentence Transformers.
* **Vector Database:** Store and retrieve document chunks using ChromaDB.
* **Hybrid Search:** Combine BM25 keyword search and semantic vector search using Reciprocal Rank Fusion (RRF).
* **Reranking:** Improve search relevance using a CrossEncoder model.
* **RAG Answers:** Generate answers using retrieved document context and Ollama.
* **Agentic RAG:** Route questions through document retrieval or web-search fallback.
* **Web Interface:** Interact with the application using Streamlit.
* **API:** Expose document processing and question-answering endpoints through FastAPI.
* **Containerization:** Include Docker and Docker Compose configuration.

## Architecture

1. Upload a PDF through the Streamlit frontend.
2. Validate the uploaded document.
3. Record document metadata in PostgreSQL.
4. Process OCR tasks using the background task workflow.
5. Extract text and divide it into chunks.
6. Generate embeddings and index chunks in ChromaDB.
7. Retrieve candidate passages using BM25 and semantic search.
8. Combine search rankings using Reciprocal Rank Fusion.
9. Rerank candidate passages using a CrossEncoder.
10. Generate answers using the language model and relevant context.
11. Use the web-search fallback when document retrieval is insufficient.

## Technology Stack

| Component           | Technology                              |
| ------------------- | --------------------------------------- |
| Backend API         | FastAPI                                 |
| Frontend            | Streamlit                               |
| OCR                 | Tesseract OCR, Poppler, Pytesseract     |
| Background Tasks    | Celery, Redis                           |
| Metadata Database   | PostgreSQL, SQLAlchemy                  |
| Vector Database     | ChromaDB                                |
| Embeddings          | Sentence Transformers                   |
| Keyword Search      | BM25                                    |
| Hybrid Ranking      | Reciprocal Rank Fusion                  |
| Reranking           | CrossEncoder                            |
| Language Model      | Ollama                                  |
| Object Storage Code | MinIO and S3-compatible storage modules |
| Containerization    | Docker, Docker Compose                  |

## Prerequisites

* Python 3.12 or a compatible Python version
* Tesseract OCR
* Poppler
* PostgreSQL
* Redis
* Ollama with a compatible model
* Docker Desktop, if running the containerized setup

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Distributed_OCR_Agentic_RAG
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Update database, object-storage, and Ollama settings for your environment. Never commit actual credentials.

### 5. Start the API

From the project root:

```bash
python -m uvicorn api.main:app --reload --port 8001
```

Open the interactive API documentation at:

`http://127.0.0.1:8001/docs`

### 6. Start the frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py --server.port 8503
```

Open the frontend at:

`http://localhost:8503`

Ensure the frontend API URL matches the address and port used by FastAPI.

### 7. Start supporting services

PostgreSQL, Redis, and Ollama must be configured and running as required by the application. Configure their connection settings before testing document processing.

## Docker Setup

The repository includes a Dockerfile and `compose.yaml`.

Review the Compose environment variables and service configuration before starting the stack. In particular, configure database credentials, object storage, persistent volumes, and the API URL appropriately.

After validating the configuration, build and start the services with:

```bash
docker compose up --build
```

The configured container ports may differ from the local development ports.

## API Endpoints

The application includes endpoints for:

* `GET /health` — Check API health.
* `POST /upload` — Upload a document for processing.
* `POST /ask` — Ask a question using the RAG workflow.
* `GET /tasks/{task_id}` — Check the status of a background task.

Use `/docs` to inspect the actual request and response schemas.

## Project Structure

```text
Distributed_OCR_Agentic_RAG/
├── api/
├── database/
├── frontend/
├── ocr/
├── rag/
├── storage/
├── worker/
├── tests/
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Security

* Keep `.env` and real credentials private.
* Do not commit uploaded documents or extracted private content.
* Do not commit virtual environments, local databases, or model caches.
* Replace development passwords with environment variables before deployment.
* Review the files staged for Git before every commit.

## Project Status

This project is being developed as a practical implementation of document intelligence, OCR pipelines, hybrid retrieval, reranking, and Agentic RAG. Validate each external service and the complete Docker workflow in the target environment before production deployment.

## Future Improvements

* Automated integration tests for the complete pipeline.
* More robust duplicate-document handling.
* Improved retrieval evaluation and relevance thresholds.
* Production-ready configuration and deployment.
* Monitoring and structured logging.
