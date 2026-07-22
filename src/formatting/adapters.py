import re

def adapt_for_kindle(text: str) -> str:
    """
    Optimizes for Reading Momentum.
    Breaks long paragraphs into shorter visual units (1-3 sentences)
    to reduce cognitive friction on small screens.
    """
    paragraphs = text.split("\n\n")
    kindle_paragraphs = []
    
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?]) +', p.strip())
        if len(sentences) <= 2:
            kindle_paragraphs.append(p.strip())
        else:
            for i in range(0, len(sentences), 2):
                kindle_paragraphs.append(" ".join(sentences[i:i+2]))
                
    return "\n\n".join([kp for kp in kindle_paragraphs if kp])

def adapt_for_paperback(text: str) -> str:
    """
    Optimizes for Value and Authority.
    Combines overly short/fragmented paragraphs into more substantial narrative blocks.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paperback_paragraphs = []
    buffer = ""

    for p in paragraphs:
        if len(buffer.split()) + len(p.split()) < 120:
            buffer = f"{buffer} {p}".strip()
        else:
            if buffer:
                paperback_paragraphs.append(buffer)
            buffer = p

    if buffer:
        paperback_paragraphs.append(buffer)

    return "\n\n".join(paperback_paragraphs)

def adapt_for_audiobook(text: str) -> str:
    """
    Adapts for Conversation, Not Narration.
    Removes visual references ('see diagram below', 'page X')
    and smooths bullet-heavy or fragmented text for spoken rhythm.
    """
    # 1. Strip visual references
    adapted = re.sub(r'(?i)\s*\(see (the )?diagram below\)', '', text)
    adapted = re.sub(r'(?i)\s*\(refer to page \d+\)', '', adapted)
    adapted = re.sub(r'(?i)see figure \d+', 'as described', adapted)

    # 2. Smooth exercise headers into natural conversational transitions
    adapted = re.sub(
        r'(?i)Exercise Number (\d+)(?:\s+will\s+help\s+you|\s*:)?',
        r'Let’s pause for a moment and try Exercise \1 together to',
        adapted
    )

    # 3. Clean up double spaces caused by regex stripping
    adapted = re.sub(r'[ \t]+', ' ', adapted)
    
    return adapted.strip()

def adapt_for_pdf(text: str) -> str:
    """
    Optimizes for Reference and Structured Learning.
    Ensures clear section spacing and preserves structured layout blocks.
    """
    cleaned = re.sub(r'\n\s*\n', '\n\n', text)
    return cleaned.strip()
