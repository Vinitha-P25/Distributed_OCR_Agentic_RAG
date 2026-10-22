from sqlalchemy import text

from database.postgres_db import engine


def add_fingerprint_column():
    with engine.begin() as connection:
        # Add the column without affecting existing documents.
        connection.execute(
            text("""
                ALTER TABLE documents
                ADD COLUMN IF NOT EXISTS sha256_fingerprint VARCHAR(64)
            """)
        )

        # Enforce uniqueness for non-NULL fingerprints.
        connection.execute(
            text("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                ix_documents_sha256_fingerprint
                ON documents (sha256_fingerprint)
                WHERE sha256_fingerprint IS NOT NULL
            """)
        )

    print("SHA-256 fingerprint column and unique index are ready.")


if __name__ == "__main__":
    add_fingerprint_column()