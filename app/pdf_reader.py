import pymupdf


def read_pdf(pdf_path):
    """PDF'deki tüm metni sayfa sayfa okur."""

    document = pymupdf.open(pdf_path)

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")

            if text and text.strip():
                pages.append({
                    "page": page_number,
                    "text": text.strip()
                })
    finally:
        document.close()

    return pages


def extract_text(pdf_path):
    pages = read_pdf(pdf_path)
    return "\n\n".join(page["text"] for page in pages)


if __name__ == "__main__":
    print("PDF Reader hazır.")