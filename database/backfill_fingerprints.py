from pathlib import Path

from database.postgres_db import SessionLocal
from database.postgres_models import Document
from storage.fingerprint import calculate_sha256


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = PROJECT_ROOT / "uploads"


def backfill_fingerprints():
    db = SessionLocal()
    updated = 0
    skipped = 0
    duplicates = 0

    try:
        documents = (
            db.query(Document)
            .filter(Document.sha256_fingerprint.is_(None))
            .all()
        )

        for document in documents:
            stored_filename = Path(document.storage_path or "").name

            if not stored_filename:
                skipped += 1
                print(f"Skipped {document.document_id}: no stored filename.")
                continue

            file_path = UPLOAD_DIR / stored_filename

            if not file_path.is_file():
                skipped += 1
                print(f"Skipped {document.document_id}: PDF not found at {file_path}.")
                continue

            fingerprint = calculate_sha256(file_path)

            existing = (
                db.query(Document)
                .filter(
                    Document.sha256_fingerprint == fingerprint
                )
                .first()
            )

            if existing is not None:
                duplicates += 1
                print(
                    f"Duplicate content: {document.filename} matches "
                    f"{existing.filename}. Existing record retained."
                )
                continue

            document.sha256_fingerprint = fingerprint
            db.commit()

            updated += 1
            print(
                f"Updated {document.filename}: "
                f"SHA-256 = {fingerprint}"
            )

        print("\nBackfill completed.")
        print(f"Fingerprints added: {updated}")
        print(f"Skipped: {skipped}")
        print(f"Duplicate contents found: {duplicates}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    backfill_fingerprints()