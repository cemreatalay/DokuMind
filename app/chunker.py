import re


def clean_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_blocks(text):
    text = clean_text(text)

    text = re.sub(
        r"\s+(Madde\s+\d+\s*[-–—])",
        r"\n\n\1",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s+(\(\d+\))", r"\n\1", text)

    blocks = []

    for block in text.split("\n\n"):
        block = block.strip()
        if len(block) >= 80:
            blocks.append(block)

    return blocks


def chunk_text(text, max_chars=1400, overlap=250):
    blocks = split_into_blocks(text)
    chunks = []

    for block in blocks:
        if len(block) <= max_chars:
            chunks.append(block)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", block)
        current = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current) + len(sentence) + 1 <= max_chars:
                current = (current + " " + sentence).strip()
            else:
                if current:
                    chunks.append(current)

                if len(sentence) > max_chars:
                    start = 0
                    while start < len(sentence):
                        end = start + max_chars
                        part = sentence[start:end].strip()
                        if part:
                            chunks.append(part)
                        start = end - overlap
                    current = ""
                else:
                    current = sentence

        if current:
            chunks.append(current)

    final_chunks = []
    seen = set()

    for chunk in chunks:
        chunk = clean_text(chunk)

        if len(chunk) < 80:
            continue

        key = chunk.lower()
        if key in seen:
            continue

        seen.add(key)
        final_chunks.append(chunk)

    return final_chunks