from enum import Enum
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Integer, String, Enum as SQLEnum, Text

from app.database import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class DocumentType(str, Enum):
    HR = "hr"
    HEALTH_INSURANCE = "health_insurance"
    LEAVE = "leave"
    BENEFITS = "benefits"
    GENERAL = "general"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)

    document_type = Column(
        SQLEnum(DocumentType),
        nullable=False
    )

    uploaded_by = Column(Integer, nullable=False)

    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    file_path = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )
    page_number = Column(

        Integer,

        nullable=True

    )

    content = Column(
        Text,
        nullable=False
    )

    embedding = Column(
        Vector(384),
        nullable=True
    )