import fitz


def extract_pages_from_pdf(file_path: str) -> list[dict]:
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

    document.close()

    return pages