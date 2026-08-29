from search import search_documents


question = "staj süresi kaç iş günüdür"

print("=" * 60)
print("SORU:", question)
print("=" * 60)

results = search_documents(
    question,
    n_results=5
)

print("\n")
print("=" * 60)
print("SONUÇLAR")
print("=" * 60)

for i, result in enumerate(results, 1):

    print(
        f"\n[{i}] "
        f"SKOR: {result['score']:.3f}"
    )

    print(
        f"Semantic: "
        f"{result['semantic_score']:.3f}"
    )

    print(
        f"Keyword: "
        f"{result['keyword_score']:.3f}"
    )

    print("-" * 60)

    print(result["text"])