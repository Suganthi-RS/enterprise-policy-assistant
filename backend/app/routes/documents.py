from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import Document, DocumentType, User, UserRole
from app.services.doc_service import extract_pages_from_pdf
from app.services.chunk_service import chunk_text, save_document_chunks
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from app.models import Document, DocumentType, User, UserRole, DocumentChunk
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = PUPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    pages = extract_pages_from_pdf(str(file_path))
    extracted_text = "\n".join(

    page["text"]

    for page in pages

)
    document = Document(
        filename=file.filename,
        document_type=document_type,
        uploaded_by=current_user.id,
        file_path=str(file_path),
        extracted_text=extracted_text
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    chunks = chunk_text(pages)

    save_document_chunks(
    db=db,
    document_id=document.id,
    chunks=chunks)

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "document_type": document.document_type.value
    }

@router.get("/")
def list_documents(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    documents = (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return {
        "documents": [
            {
                "id": document.id,
                "filename": document.filename,
                "document_type": document.document_type.value,
                "uploaded_by": document.uploaded_by,
                "uploaded_at": document.uploaded_at
            }
            for document in documents
        ]
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete(
        synchronize_session=False
    )

    file_path = Path(document.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "filename": document.filename
    }