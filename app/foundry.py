from foundry_local_sdk import (
    Configuration,
    FoundryLocalManager
)


CHAT_MODEL = "qwen3-1.7b"


_manager = None
_model = None
_client = None


def get_chat_client():

    global _manager
    global _model
    global _client

    if _client is not None:
        return _client

    print(
        "Foundry Local hazırlanıyor..."
    )

    if _manager is None:

        FoundryLocalManager.initialize(
            Configuration(
                app_name="DocuMind"
            )
        )

        _manager = FoundryLocalManager.instance

    print(
        "Foundry Local hazır!"
    )

    _model = _manager.catalog.get_model(
        CHAT_MODEL
    )

    if _model is None:
        raise RuntimeError(
            f"Chat modeli bulunamadı: "
            f"{CHAT_MODEL}"
        )

    # Chat modeli için cached GPU/CPU varyantı bul
    selected_variant = None

    for variant in _model.variants:

        print(
            "Chat varyantı:",
            variant.id,
            "| cached:",
            variant.info.cached
        )

        if variant.info.cached:
            selected_variant = variant
            break

    if selected_variant is None:
        raise RuntimeError(
            "Chat modeli için "
            "indirilmiş bir varyant bulunamadı."
        )

    print(
        "Chat varyantı seçiliyor:",
        selected_variant.id
    )

    _model.select_variant(
        selected_variant
    )

    print(
        "Chat modeli yükleniyor..."
    )

    _model.load()

    print(
        "Chat modeli hazır!"
    )

    _client = _model.get_chat_client()

    return _client