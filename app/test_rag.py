from search import search_documents
from generator import generate_answer


print("=" * 60)
print("DOCUMIND RAG TESTİ")
print("=" * 60)


question = input("\nSorunuzu yazın: ")


print("\nArama yapılıyor...")

results = search_documents(
    question,
    n_results=5
)


if not results:

    print("\nBelge bulunamadı.")

    raise SystemExit


print("\nCevap oluşturuluyor...")

answer = generate_answer(
    question,
    results
)


print("\n" + "=" * 60)
print("DOCUMIND CEVABI")
print("=" * 60)

print(answer)
