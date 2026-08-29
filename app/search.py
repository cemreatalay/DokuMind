import re

from embedding import create_embedding
from vector_store import get_collection


def normalize(text):
    if not text:
        return ""

    text = text.lower()

    replacements = {
        "ı": "i", "ğ": "g", "ü": "u",
        "ş": "s", "ö": "o", "ç": "c",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_keywords(text):
    words = normalize(text).split()

    stop_words = {
        "ve", "veya", "bir", "bu", "su",
        "ne", "nedir", "nasil", "olan",
        "icin", "ile", "mi", "mu",
        "mudur", "midir", "kac",
        "olarak", "en", "the"
    }

    return {w for w in words if len(w) >= 3 and w not in stop_words}


def word_matches(query_word, document_words):
    if query_word in document_words:
        return True

    for word in document_words:
        if word.startswith(query_word) or query_word.startswith(word):
            return True

    return False


def keyword_score(query, text):
    query_words = get_keywords(query)
    document_words = set(normalize(text).split())

    if not query_words:
        return 0.0

    matched = sum(1 for w in query_words if word_matches(w, document_words))
    return matched / len(query_words)


def exact_phrase_bonus(query, text):
    """Kelime sınırı (\\b) kullanır — 'staj sure' artık 'staj suresince' içine
    yanlışlıkla sızmaz."""

    q = normalize(query)
    t = normalize(text)

    bonus = 0.0

    phrases = [
        "staj suresi", "is gun",
        "ders icerigi", "dersin amaci", "ders adi", "ders kodu"
    ]

    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, q) and re.search(pattern, t):
            bonus += 0.20

    return min(bonus, 0.40)


def answer_type_bonus(query, text):
    """Soru bir miktar/sayı soruyorsa ('süresi', 'kaç gün' vb.) ve metinde
    rakam varsa bonus verir. Kök eşleşmesi kullanır ('suresi' -> 'sure')."""

    q = normalize(query)
    t = normalize(text)

    quantity_roots = ["kac", "nekadar", "sayi", "sure", "yil", "gun", "kredi", "akts"]

    q_words = q.split()

    asks_quantity = any(
        any(root in word or word in root for root in quantity_roots)
        for word in q_words
    )

    if asks_quantity and re.search(r"\b\d+\b", t):
        return 0.20

    return 0.0


def source_bonus(query, text, metadata):
    source = metadata.get("source", "") if metadata else ""

    source_words = get_keywords(source)
    query_words = get_keywords(query)

    if source_words and query_words and source_words.intersection(query_words):
        return 0.10

    return 0.0


def search_documents(query, n_results=5):
    print(f"\nArama: {query}")

    collection = get_collection()
    total = collection.count()

    if total == 0:
        print("Veritabanında belge bulunamadı.")
        return []

    query_embedding = create_embedding(query)
    candidate_count = min(max(n_results * 6, 20), total)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_count,
        include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    scored = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        semantic_score = 1 / (1 + max(distance, 0))
        keyword = keyword_score(query, document)
        phrase_bonus = exact_phrase_bonus(query, document)
        type_bonus = answer_type_bonus(query, document)
        source_bonus_value = source_bonus(query, document, metadata)

        final_score = (
            semantic_score * 0.30
            + keyword * 0.40
            + phrase_bonus
            + type_bonus
            + source_bonus_value
        )

        scored.append({
            "text": document,
            "metadata": metadata or {},
            "semantic_score": semantic_score,
            "keyword_score": keyword,
            "phrase_bonus": phrase_bonus,
            "type_bonus": type_bonus,
            "source_bonus": source_bonus_value,
            "score": final_score
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    if scored:
        best_score = scored[0]["score"]
        scored = [item for item in scored if item["score"] >= best_score * 0.55]

    print("\nEN İYİ SONUÇLAR:")
    for i, item in enumerate(scored[:n_results], 1):
        source = item["metadata"].get("source", "Bilinmeyen")
        print(
            f"{i}. Skor={item['score']:.3f} "
            f"Sem={item['semantic_score']:.3f} "
            f"Kw={item['keyword_score']:.3f} "
            f"Phrase={item['phrase_bonus']:.3f} "
            f"Type={item['type_bonus']:.3f} "
            f"Kaynak={source}"
        )

    return scored[:n_results]


if __name__ == "__main__":
    soru = input("Sorunuzu yazın: ")
    results = search_documents(soru)

    print("\n" + "=" * 60)
    for i, result in enumerate(results, 1):
        source = result["metadata"].get("source", "Bilinmeyen")
        print(f"\n[{i}] SKOR={result['score']:.3f} KAYNAK={source}")
        print("-" * 60)
        print(result["text"])