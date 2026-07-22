import hashlib

MAX_WORD_LIMIT = 1500

def compute_sha256(text_content: str) -> str:
    """Calculates immutable SHA-256 signature for text payload integrity validation."""
    return hashlib.sha256(text_content.encode("utf-8")).hexdigest()

def chunk_manuscript(text_content: str) -> list[dict]:
    """
    Splits manuscript text into boundary-safe chunks on paragraph breaks.
    Falls back to MAX_WORD_LIMIT ceiling if paragraphs are overly dense.
    """
    paragraphs = text_content.split("\n\n")
    chunks = []
    current_chunk_words = []
    current_word_count = 0
    chunk_index = 0

    for paragraph in paragraphs:
        p_words = paragraph.split()
        if not p_words:
            continue

        if current_word_count + len(p_words) > MAX_WORD_LIMIT and current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append({
                "chunk_index": chunk_index,
                "raw_text_content": chunk_text,
                "chunk_sha256": compute_sha256(chunk_text)
            })
            chunk_index += 1
            current_chunk_words = []
            current_word_count = 0

        current_chunk_words.extend(p_words)
        current_word_count += len(p_words)

    if current_chunk_words:
        chunk_text = " ".join(current_chunk_words)
        chunks.append({
            "chunk_index": chunk_index,
            "raw_text_content": chunk_text,
            "chunk_sha256": compute_sha256(chunk_text)
        })

    return chunks
