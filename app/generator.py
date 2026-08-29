import re
import threading

from foundry_local_sdk import Configuration, FoundryLocalManager


MODEL_ALIAS = "qwen3-1.7b"

MAX_CONTEXT_CHUNKS = 2
MAX_CHUNK_CHARS = 700
MAX_NEW_TOKENS = 150
FALLBACK_MAX_NEW_TOKENS = 100

_lock = threading.Lock()
_chat_client = None
_manager_ready = False


def _ensure_manager_initialized():
    global _manager_ready

    if _manager_ready:
        return

    try:
        config = Configuration(app_name="DocuMind")
        FoundryLocalManager.initialize(config)
    except Exception as e:
        if "already initialized" not in str(e).lower():
            raise

    _manager_ready = True


def get_chat_client(force_reload=False):
    global _chat_client

    if force_reload:
        _chat_client = None

    if _chat_client is not None:
        return _chat_client

    with _lock:
        if _chat_client is None:
            print("Chat modeli yükleniyor...")

            _ensure_manager_initialized()

            manager = FoundryLocalManager.instance
            model = manager.catalog.get_model(MODEL_ALIAS)

            if not model.is_loaded:
                model.load()

            _chat_client = model.get_chat_client()
            print("Chat modeli hazır!")

    return _chat_client


def build_context(results, max_chunks=MAX_CONTEXT_CHUNKS):
    if not results:
        return ""

    parts = []

    for i, result in enumerate(results[:max_chunks], 1):
        text = result.get("text", "").strip()
        metadata = result.get("metadata", {}) or {}
        source = metadata.get("source", "Bilinmeyen kaynak")
        page = metadata.get("page", "")

        if not text:
            continue

        if len(text) > MAX_CHUNK_CHARS:
            text = text[:MAX_CHUNK_CHARS].rsplit(" ", 1)[0] + "..."

        location = source
        if page:
            location += f", sayfa {page}"

        parts.append(f"[KAYNAK {i} - {location}]\n{text}")

    return "\n\n".join(parts)


def create_prompt(question, results, max_chunks=MAX_CONTEXT_CHUNKS):
    context = build_context(results, max_chunks)

    prompt = f"""Sen DocuMind adlı bir belge asistanısın.
Yalnızca aşağıdaki belge parçalarına dayanarak Türkçe cevap ver.

BELGE PARÇALARI
{context}

SORU
{question}

KURALLAR
- Birden fazla kaynak varsa, sadece soruyu DOĞRUDAN cevaplayan kaynağı kullan, diğerini yok say.
- Cevap belgede açıkça varsa doğrudan ve kısa ver.
- Sayı, tarih, süre gibi değerleri ve ifadeleri aynen koru, değiştirme.
- Belgede olmayan hiçbir bilgi ekleme, tahmin yapma, yorum yapma.
- Cevap belgede yoksa yalnızca şunu yaz: "Bu bilgi belgede bulunamadı."
- Açıklama yapma, sadece nihai cevabı yaz. Cevaptan sonra HİÇBİR ŞEY yazma.
- Cevabın sonunda "Kaynak: <dosya adı>, Sayfa <no>" şeklinde belirt ve orada dur.

/no_think

CEVAP:"""

    return prompt


PROMPT_ECHO_MARKERS = [
    "KURALLAR",
    "BELGE PARÇALARI",
    "\nSORU",
    "KAYNAK 1",
    "KAYNAK 2",
    "KAYNAK 3",
]


def clean_answer(answer):
    if not answer:
        return ""

    answer = answer.strip()

    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL | re.IGNORECASE)
    answer = re.sub(r"</?think>", "", answer, flags=re.IGNORECASE)

    for marker in ["CEVAP:", "Cevap:", "cevap:"]:
        if marker in answer:
            answer = answer.rsplit(marker, 1)[-1]
            break

    answer = answer.strip()

    for marker in PROMPT_ECHO_MARKERS:
        idx = answer.find(marker)
        if idx != -1:
            answer = answer[:idx].strip()

    match = re.search(r"Kaynak\s*:.*", answer, flags=re.IGNORECASE)
    if match:
        newline_after = answer.find("\n", match.start())
        if newline_after != -1:
            answer = answer[:newline_after].strip()

    return answer.strip()


import time

def _call_model(prompt, max_tokens, force_reload=False):
    chat_client = get_chat_client(force_reload=force_reload)
    messages = [{"role": "user", "content": prompt}]

    for attempt in range(2):
        try:
            try:
                response = chat_client.complete_chat(messages, max_tokens=max_tokens, temperature=0.1)
            except TypeError:
                response = chat_client.complete_chat(messages)
            return response.choices[0].message.content
        except Exception:
            if attempt == 0:
                time.sleep(1.5)
                continue
            raise


def generate_answer(question, results):
    if not results:
        return "Bu bilgi belgede bulunamadı."

    try:
        print("Cevap oluşturuluyor... (1. deneme)")
        prompt = create_prompt(question, results, max_chunks=MAX_CONTEXT_CHUNKS)
        raw_answer = _call_model(prompt, MAX_NEW_TOKENS)

    except Exception as e:
        print("1. deneme başarısız:", e)

        try:
            print("Cevap oluşturuluyor... (2. deneme, client sıfırlandı)")
            prompt = create_prompt(question, results, max_chunks=1)
            raw_answer = _call_model(prompt, FALLBACK_MAX_NEW_TOKENS, force_reload=True)

        except Exception as e2:
            print("Chat modeli hata verdi:", e2)
            return "Cevap oluşturulurken bir hata oluştu. Lütfen tekrar deneyin."

    answer = clean_answer(raw_answer)
    return answer if answer else "Bu bilgi belgede bulunamadı."


if __name__ == "__main__":
    test_results = [{
        "text": "Madde 3 - Toplam staj süresi en az 20 işgünüdür.",
        "metadata": {"source": "test.pdf", "page": 1}
    }]
    print(generate_answer("Staj süresi kaç iş günüdür?", test_results))