from foundry_local_sdk import Configuration, FoundryLocalManager


config = Configuration(app_name="DocuMind")
FoundryLocalManager.initialize(config)

manager = FoundryLocalManager.instance

model = manager.catalog.get_model("qwen3-1.7b")

if not model.is_loaded:
    model.load()

print("Chat modeli hazır!")

chat_client = model.get_chat_client()

print("Teste başlanıyor...")

messages = [
    {
        "role": "user",
        "content": "Merhaba. Kısaca kendini tanıt."
    }
]

response = chat_client.complete_chat(messages)

print("\nMODEL CEVABI:")
print(response.choices[0].message.content)