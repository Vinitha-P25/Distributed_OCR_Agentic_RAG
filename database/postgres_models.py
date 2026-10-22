from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.postgres_db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    storage_path = Column(
        Text,
        nullable=True,
    )

    sha256_fingerprint = Column(
        String(64),
        nullable=True
        
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )