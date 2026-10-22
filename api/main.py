import hashlib
import logging
from pathlib import Path
from uuid import uuid4

from celery.result import AsyncResult
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError

from database.document_repository import (
    create_document,
    get_document_by_fingerprint,
)
from rag.agent import run_agent
from storage.vector_store import get_collection
from worker.celery_app import celery_app
from worker.tasks import process_document


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# Project configuration
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = PROJECT_DIR / "uploads"

MAX_FILE_SIZE = 20 * 1024 * 1024


# --------------------------------------------------
# SHA-256 fingerprint
# --------------------------------------------------

def calculate_content_fingerprint(content: bytes) -> str:
    """Calculate a SHA-256 fingerprint from PDF bytes."""
    return hashlib.sha256(content).hexdigest()


# --------------------------------------------------
# ChromaDB indexed chunk count
# --------------------------------------------------

def get_indexed_chunk_count(document_id: str, filename: str) -> int:
    """Return the number of chunks indexed for a document."""

    try:
        collection = get_collection()

        document_name = f"{document_id}_{filename}"

        result = collection.get(
            where={"document_name": document_name},
            include=["metadatas"],
        )

        return len(result.get("ids", []))

    except Exception:
        logger.exception(
            "Could not retrieve indexed chunk count for document %s",
            document_id,
        )
        return 0


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Distributed OCR + RAG API",
    description=(
        "API for document upload, asynchronous OCR, "
        "RAG-based question answering, and web-search fallback."
    ),
    version="1.0.0",
)


# --------------------------------------------------
# Request models
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to answer using documents or web search.",
    )


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Distributed OCR + RAG API",
    }


# --------------------------------------------------
# Agentic RAG question endpoint
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = run_agent(question)

        return {
            "question": result["question"],
            "agent_decision": result["agent_decision"],
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Question answering failed")

        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {error}",
        ) from error


# --------------------------------------------------
# Duplicate document response helper
# --------------------------------------------------

def build_duplicate_response(existing_document, fingerprint: str):
    """Build a response containing the existing document's status."""

    document_id = str(existing_document.document_id)
    filename = existing_document.filename

    indexed_chunks = get_indexed_chunk_count(
        document_id,
        filename,
    )

    return {
        "status": "duplicate",
        "document_id": document_id,
        "filename": filename,
        "fingerprint": fingerprint,
        "document_status": getattr(
            existing_document,
            "status",
            "unknown",
        ),
        "indexed_chunks": indexed_chunks,
        "message": (
            "This PDF has already been uploaded. "
            "The existing document record is being returned."
        ),
    }


# --------------------------------------------------
# Asynchronous document upload with duplicate detection
# --------------------------------------------------

@app.post("/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    original_filename = Path(file.filename).name

    if Path(original_filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the 20 MB limit.",
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty.",
            )

        # Calculate SHA-256 from the actual PDF bytes.
        fingerprint = calculate_content_fingerprint(content)

        logger.info(
            "Calculated SHA-256 fingerprint: %s",
            fingerprint,
        )

        # Check PostgreSQL before creating a new document.
        existing_document = get_document_by_fingerprint(fingerprint)

        if existing_document:
            logger.info(
                "Duplicate PDF detected. Existing document ID: %s",
                existing_document.document_id,
            )

            return build_duplicate_response(
                existing_document,
                fingerprint,
            )

        # --------------------------------------------------
        # Save the new PDF
        # --------------------------------------------------

        UPLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        document_id = str(uuid4())

        saved_filename = f"{document_id}_{original_filename}"
        file_path = UPLOADS_DIR / saved_filename

        file_path.write_bytes(content)

        # --------------------------------------------------
        # Create PostgreSQL metadata
        # --------------------------------------------------

        try:
            create_document(
                document_id=document_id,
                filename=original_filename,
                storage_path=str(file_path.resolve()),
                status="pending",
                sha256_fingerprint=fingerprint,
            )

        except ValueError as error:
            file_path.unlink(missing_ok=True)

            if "Duplicate document detected" in str(error):
                existing_document = get_document_by_fingerprint(
                    fingerprint
                )

                if existing_document:
                    return build_duplicate_response(
                        existing_document,
                        fingerprint,
                    )

            raise

        except IntegrityError as error:
            file_path.unlink(missing_ok=True)

            existing_document = get_document_by_fingerprint(
                fingerprint
            )

            if existing_document:
                return build_duplicate_response(
                    existing_document,
                    fingerprint,
                )

            logger.exception("PostgreSQL integrity error")

            raise HTTPException(
                status_code=409,
                detail=(
                    "Document metadata conflicts with an existing record."
                ),
            ) from error

        except Exception:
            file_path.unlink(missing_ok=True)
            raise

        logger.info(
            "Document metadata created: %s",
            document_id,
        )

        # --------------------------------------------------
        # Queue OCR and indexing using Celery
        # --------------------------------------------------

        try:
            task = process_document.delay(
                document_id=document_id,
                file_path=str(file_path.resolve()),
                original_filename=original_filename,
            )

        except Exception as error:
            logger.exception("Could not submit document to Celery")

            from database.document_repository import (
                update_document_status,
            )

            update_document_status(
                document_id=document_id,
                status="failed",
                error_message="Could not submit document to Celery.",
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "Document metadata was saved, but Celery could not "
                    "accept the task. Check Redis and the Celery worker."
                ),
            ) from error

        logger.info("Celery task submitted: %s", task.id)

        return {
            "status": "accepted",
            "document_id": document_id,
            "task_id": task.id,
            "filename": original_filename,
            "fingerprint": fingerprint,
            "document_status": "pending",
            "indexed_chunks": 0,
            "message": (
                "PDF uploaded successfully. "
                "OCR and indexing are running in the background."
            ),
        }

    finally:
        await file.close()


# --------------------------------------------------
# Celery task status
# --------------------------------------------------

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):

    task = AsyncResult(
        task_id,
        app=celery_app,
    )

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result

    elif task.failed():
        response["error"] = str(task.result)

    return response