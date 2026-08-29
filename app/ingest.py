import os
import sys
import hashlib

from pdf_reader import read_pdf
from chunker import chunk_text
from embedding import create_embeddings
from vector_store import add_documents, delete_document


def ingest_pdf(pdf_path):
    filename = os.path.basename(pdf_path)
    print(f"\nPDF işleniyor: {filename}")

    pages = read_pdf(pdf_path)

    if not pages:
        print("PDF'den metin çıkarılamadı.")
        return 0

    all_chunks, metadatas, ids = [], [], []

    for page in pages:
        for chunk_index, chunk in enumerate(chunk_text(page["text"])):
            all_chunks.append(chunk)
            metadatas.append({
                "source": filename,
                "page": page["page"],
                "chunk": chunk_index
            })
            raw_id = f"{filename}-{page['page']}-{chunk_index}"
            ids.append(hashlib.md5(raw_id.encode("utf-8")).hexdigest())

    print("Oluşturulan chunk sayısı:", len(all_chunks))

    if not all_chunks:
        return 0

    print("Embedding'ler oluşturuluyor...")
    embeddings = create_embeddings(all_chunks)
    print("Embedding'ler hazır.")

    delete_document(filename)
    add_documents(documents=all_chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)

    print(f"PDF başarıyla eklendi: {filename}")
    return len(all_chunks)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım:\npython app\\ingest.py dosya.pdf")
        sys.exit()

    ingest_pdf(sys.argv[1])