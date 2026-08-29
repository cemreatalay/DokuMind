import chromadb

client = chromadb.PersistentClient(path="data/chroma")
collection = client.get_or_create_collection(name="documents")

print("=" * 70)
print("DOCUMIND VERITABANI KONTROL")
print("=" * 70)

print("\nToplam chunk:", collection.count())

if collection.count() == 0:
    print("Veritabanı boş.")
    raise SystemExit

data = collection.get(
    limit=20,
    include=["documents", "metadatas"]
)

print("\nKAYITLAR:")
print("=" * 70)

for i, (doc, metadata) in enumerate(
    zip(data["documents"], data["metadatas"]),
    1
):
    print(f"\n[{i}]")
    print("METADATA:", metadata)
    print("METIN:", doc[:300].replace("\n", " "))
    print("-" * 70)
