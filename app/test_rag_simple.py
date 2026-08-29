from foundry_local_sdk import Configuration, FoundryLocalManager

config = Configuration(app_name="DocuMind")
FoundryLocalManager.initialize(config)

manager = FoundryLocalManager.instance

model = manager.catalog.get_model("qwen3-1.7b")

if not model.is_loaded:
    model.load()

client = model.get_chat_client()

messages = [
    {
        "role": "user",
        "content": """Aşağıdaki belge bilgisini kullanarak soruyu cevapla.

BELGE:
Madde 3 - Toplam staj süresi en az 20 işgünüdür.

SORU:
Staj süresi kaç iş günüdür?

Cevabı sadece bir cümleyle Türkçe ver."""
    }
]

print("Cevap üretiliyor...")

try:
    for chunk in client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            print(content, end="", flush=True)

    print("\n")
    print("TEST BAŞARILI")

except Exception as e:
    print("\nHATA:")
    print(type(e).__name__)
    print(e)
