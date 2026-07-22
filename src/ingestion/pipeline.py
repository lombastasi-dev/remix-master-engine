import hashlib
import re
import docx
import pypdf
from uuid import uuid4
from src.models.schemas import Manuscript, ManuscriptChunk

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def extract_text(file_obj, filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    text = ""
    if ext == 'docx':
        doc = docx.Document(file_obj)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == 'pdf':
        reader = pypdf.PdfReader(file_obj)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    elif ext in ['txt', 'md']:
        text = file_obj.read().decode('utf-8')
    return text.strip()

def chunk_manuscript(manuscript_id, full_text: str, max_words: int = 1500) -> list[ManuscriptChunk]:
    # Split on structural headers or fallback to word boundary limits
    raw_chunks = re.split(r'(?=\n(?=#{1,2}\s))', full_text)
    processed_chunks = []
    
    chunk_index = 0
    for rc in raw_chunks:
        clean_rc = rc.strip()
        if not clean_rc:
            continue
            
        words = clean_rc.split()
        if len(words) > max_words:
            # Word-ceiling fallback chunking
            for i in range(0, len(words), max_words):
                sub_text = " ".join(words[i:i + max_words])
                chunk_hash = compute_sha256(sub_text)
                processed_chunks.append(
                    ManuscriptChunk(
                        manuscript_id=manuscript_id,
                        chunk_index=chunk_index,
                        raw_text_content=sub_text,
                        chunk_sha256=chunk_hash
                    )
                )
                chunk_index += 1
        else:
            chunk_hash = compute_sha256(clean_rc)
            processed_chunks.append(
                ManuscriptChunk(
                    manuscript_id=manuscript_id,
                    chunk_index=chunk_index,
                    raw_text_content=clean_rc,
                    chunk_sha256=chunk_hash
                )
            )
            chunk_index += 1
            
    return processed_chunks
