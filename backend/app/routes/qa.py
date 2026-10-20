from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import User, UserRole
from app.services.chunk_service import search_similar_chunks
from app.services.llmservice import generate_policy_answer


router = APIRouter(
    prefix="/qa",
    tags=["Question Answering"]
)


@router.post("/search")
def search_policy(
    question: str,
    current_user: User = Depends(
        require_role(UserRole.USER)
    ),
    db: Session = Depends(get_db)
):
    results = search_similar_chunks(
        db=db,
        query=question,
        top_k=5
    )

    return {
        "question": question,
        "results": [
            {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "document": document.filename,
                "document_type": document.document_type.value,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "similarity": round(
                    similarity,
                    4
                ),
                "content": chunk.content
            }
            for chunk, document, similarity in results
        ]
    }


@router.post("/ask")
def ask_policy_question(
    question: str,
    current_user: User = Depends(
        require_role(UserRole.USER)
    ),
    db: Session = Depends(get_db)
):
    results = search_similar_chunks(
        db=db,
        query=question,
        top_k=5
    )

    if not results:
        return {
            "question": question,
            "answer": (
                "I could not find this information "
                "in the available company policies."
            ),
            "sources": []
        }


    context_parts = []

    for chunk, document, similarity in results:

        context_parts.append(
            f"""
SOURCE:
Document: {document.filename}
Document Type: {document.document_type.value}
Page: {chunk.page_number}
Chunk: {chunk.chunk_index}
Similarity: {similarity:.4f}

Content:
{chunk.content}
"""
        )


    context = "\n".join(
        context_parts
    )


    answer = generate_policy_answer(
        question=question,
        context=context
    )


    sources = [
        {
            "document_id": document.id,
            "document": document.filename,
            "document_type": document.document_type.value,
            "page_number": chunk.page_number,
            "chunk_id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "similarity": round(
                similarity,
                4
            ),
            "content_preview": chunk.content[:300]
        }
        for chunk, document, similarity in results
    ]


    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }