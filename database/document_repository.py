import hashlib

from sqlalchemy.orm import Session

from database.postgres_db import SessionLocal
from database.postgres_models import Document


def calculate_sha256(file_path: str) -> str:
    """Calculate the SHA-256 fingerprint of a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def get_document_by_id(document_id: str):
    """Retrieve document metadata from PostgreSQL."""

    db: Session = SessionLocal()

    try:
        return (
            db.query(Document)
            .filter(Document.document_id == document_id)
            .first()
        )
    finally:
        db.close()


def get_document_by_fingerprint(fingerprint: str):
    """Find an existing document using its SHA-256 fingerprint."""

    db: Session = SessionLocal()

    try:
        return (
            db.query(Document)
            .filter(
                Document.sha256_fingerprint == fingerprint
            )
            .first()
        )
    finally:
        db.close()


def create_document(
    document_id: str,
    filename: str,
    storage_path: str,
    status: str = "pending",
    sha256_fingerprint: str | None = None,
):
    """Create a document record with its SHA-256 fingerprint."""

    db: Session = SessionLocal()

    try:
        if sha256_fingerprint:
            existing = (
                db.query(Document)
                .filter(
                    Document.sha256_fingerprint
                    == sha256_fingerprint
                )
                .first()
            )

            if existing:
                raise ValueError(
                    "Duplicate document detected. "
                    f"Existing document ID: {existing.document_id}"
                )

        document = Document(
            document_id=document_id,
            filename=filename,
            storage_path=storage_path,
            status=status,
            sha256_fingerprint=sha256_fingerprint,
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def update_document_status(
    document_id: str,
    status: str,
    error_message: str | None = None,
):
    """Update the processing status of a document."""

    db: Session = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.document_id == document_id)
            .first()
        )

        if document is None:
            return False

        document.status = status
        document.error_message = error_message

        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()