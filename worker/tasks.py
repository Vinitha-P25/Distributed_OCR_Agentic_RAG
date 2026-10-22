import logging
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from worker.celery_app import celery_app

logger = logging.getLogger(__name__)

EXTRACTED_TEXT_DIR = PROJECT_DIR / "extracted_text"


@celery_app.task(name="worker.tasks.test_celery")
def test_celery(message: str = "Celery is working") -> dict:
    """Verify that Celery and Redis are connected."""

    logger.info("Test Celery task received: %s", message)

    return {
        "status": "success",
        "message": f"Celery task completed successfully: {message}",
    }


@celery_app.task(
    bind=True,
    name="worker.tasks.process_document",
    max_retries=3,
    default_retry_delay=10,
)
def process_document(
    self,
    document_id: str,
    file_path: str,
    original_filename: str,
) -> dict:
    """Process a PDF asynchronously using OCR and RAG."""

    from database.document_repository import (
        get_document_by_id,
        update_document_status,
    )

    try:
        logger.info(
            "Starting document processing: %s",
            original_filename,
        )

        # 1. Validate the uploaded PDF.
        pdf_path = Path(file_path)

        if not pdf_path.is_file():
            raise FileNotFoundError(
                f"Uploaded document not found: {pdf_path}"
            )

        # 2. Verify the document exists in PostgreSQL.
        document = get_document_by_id(document_id)

        if document is None:
            raise ValueError(
                f"Document metadata not found: {document_id}"
            )

        update_document_status(document_id, "processing")

        # 3. Extract text using the existing OCR service.
        from ocr.ocr_service import extract_text_from_pdf

        extracted_text = extract_text_from_pdf(str(pdf_path))

        if not extracted_text or not extracted_text.strip():
            raise ValueError(
                f"No text could be extracted from {original_filename}"
            )

        # 4. Save extracted text.
        EXTRACTED_TEXT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        extracted_path = (
            EXTRACTED_TEXT_DIR / f"{document_id}.txt"
        )

        extracted_path.write_text(
            extracted_text,
            encoding="utf-8",
        )

        # 5. Chunk and index using the existing RAG service.
        from rag.embedding_service import index_document

        chunk_count = index_document(
            text=extracted_text,
            document_name=f"{document_id}_{original_filename}",
        )

        if chunk_count == 0:
            raise ValueError(
                f"No chunks generated for {original_filename}"
            )

        # 6. Record successful processing in PostgreSQL.
        update_document_status(document_id, "completed")

        logger.info(
            "Document processing completed: %s",
            document_id,
        )

        return {
            "status": "success",
            "document_id": document_id,
            "original_filename": original_filename,
            "extracted_text_path": str(extracted_path),
            "chunks_created": chunk_count,
            "message": "Document processed and indexed successfully.",
        }

    except (FileNotFoundError, ValueError) as exc:
        logger.error(
            "Document processing failed: %s",
            exc,
        )

        try:
            update_document_status(
                document_id,
                "failed",
                str(exc),
            )
        except Exception:
            logger.exception("Could not update document failure status")

        raise

    except Exception as exc:
        logger.exception(
            "Unexpected error processing document %s",
            document_id,
        )

        # Record the error before retrying.
        try:
            update_document_status(
                document_id,
                "retrying",
                str(exc),
            )
        except Exception:
            logger.exception("Could not update retry status")

        raise self.retry(exc=exc)