def chunk_text(text: str, size=1800, overlap=250) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        start += max(1, size - overlap)
    return chunks
