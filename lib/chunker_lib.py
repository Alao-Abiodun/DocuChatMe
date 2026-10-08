import math


def split_into_chunks(text: str, max_words_per_chunk: int = 500) -> list[str]:
    words = text.split()
    chunks: list[str] = []

    for i in range(0, len(words), max_words_per_chunk):
        chunk = " ".join(words[i : i + max_words_per_chunk])
        if chunk.strip():
            chunks.append(chunk)

    return chunks if chunks else [text]


def estimate_tokens(text: str) -> int:
    # Rough estimate: 1 token ~= 0.75 words
    return math.ceil(len(text.split()) * 1.33)