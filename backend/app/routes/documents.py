from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import Document, DocumentType, User, UserRole


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = PUPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(
    document_type: DocumentType,
    file: UploadFile = File(...),
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

    document = Document(
        filename=file.filename,
        document_type=document_type,
        uploaded_by=current_user.id,
        file_path=str(file_path)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "document_type": document.document_type.value
    }