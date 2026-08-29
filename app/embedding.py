from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model

    if _model is None:
        print("Embedding modeli yükleniyor...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Embedding modeli hazır! (boyut:", _model.get_sentence_embedding_dimension(), ")")

    return _model


def create_embeddings(texts):
    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32
    )

    return embeddings.tolist()


def create_embedding(text):
    return create_embeddings([text])[0]


if __name__ == "__main__":
    result = create_embedding("Merhaba DocuMind")
    print("EMBEDDING OK — Boyut:", len(result))