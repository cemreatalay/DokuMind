import chromadb

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "documents"

_client = None
_collection = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        _collection = get_client().get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def add_documents(documents, embeddings, metadatas, ids):
    get_collection().add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )


def delete_document(source_filename):
    try:
        get_collection().delete(where={"source": source_filename})
    except Exception as e:
        print(f"Eski kayıtlar silinirken hata (önemli değil): {e}")


def list_sources():
    collection = get_collection()

    if collection.count() == 0:
        return []

    data = collection.get(include=["metadatas"])

    sources = set()
    for metadata in data.get("metadatas", []):
        if metadata and "source" in metadata:
            sources.add(metadata["source"])

    return sorted(sources)