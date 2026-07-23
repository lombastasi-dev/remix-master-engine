import hashlib
from typing import List
from uuid import UUID, uuid4
from src.models.schemas import Manuscript, ManuscriptChunk
from src.ingestion.normalizers import extract_text_from_file_bytes, normalize_text_content

def compute_sha256(content: str) -> str:
    """Calculates deterministic SHA-256 hash string from input text."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def split_text_into_chunks(full_text: str, max_words: int = 1500) -> List[str]:
    """Boundary-safe paragraph chunking with max_words fallback ceiling."""
    paragraphs = full_text.split('\n\n')
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for para in paragraphs:
        para_words = len(para.split())
        if current_word_count + para_words > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_word_count = para_words
        else:
            current_chunk.append(para)
            current_word_count += para_words
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks if chunks else [full_text]

def ingest_document_payload(
    file_bytes: bytes,
    file_extension: str,
    title: str,
    user_id: str = "usr_system_default"
) -> tuple[Manuscript, List[ManuscriptChunk]]:
    """
    Layer 0 Master Ingestion Pipeline:
    1. Extracts and normalizes text from binary payload.
    2. Computes master raw_sha256 provenance hash.
    3. Segments into boundary-safe ManuscriptChunk objects with isolated chunk_sha256 hashes.
    """
    raw_text = extract_text_from_file_bytes(file_bytes, file_extension)
    master_hash = compute_sha256(raw_text)
    manuscript_id = uuid4()
    
    manuscript = Manuscript(
        manuscript_id=manuscript_id,
        user_id=user_id,
        title=title,
        current_state="Concept",
        raw_sha256=master_hash
    )
    
    raw_chunks = split_text_into_chunks(raw_text)
    chunk_objects = []
    
    for idx, chunk_str in enumerate(raw_chunks):
        chunk_hash = compute_sha256(chunk_str)
        chunk_obj = ManuscriptChunk(
            chunk_id=uuid4(),
            manuscript_id=manuscript_id,
            chunk_index=idx,
            raw_text_content=chunk_str,
            chunk_sha256=chunk_hash
        )
        chunk_objects.append(chunk_obj)
        
    return manuscript, chunk_objects
