from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services.embedding_service import generate_embedding


def chunk_text(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[dict]:

    chunks = []

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        if not text.strip():
            continue

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append({
                    "page_number": page_number,
                    "content": chunk
                })

            start += chunk_size - chunk_overlap

    return chunks


def save_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[dict]
):
    for index, chunk_data in enumerate(chunks):

        content = chunk_data["content"]
        page_number = chunk_data["page_number"]

        embedding = generate_embedding(content)

        document_chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            page_number=page_number,
            content=content,
            embedding=embedding
        )

        db.add(document_chunk)

    db.commit()


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.35
):
    query_embedding = generate_embedding(query)

    results = (
        db.query(
            DocumentChunk,
            Document,
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            ).label("distance")
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.embedding.isnot(None)
        )
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(top_k)
        .all()
    )

    filtered_results = []

    for chunk, document, distance in results:

        similarity = 1 - distance

        if similarity >= similarity_threshold:
            filtered_results.append(
                (
                    chunk,
                    document,
                    similarity
                )
            )

    return filtered_results