from pydantic import BaseModel
from typing import Optional, Dict, Any

class Manuscript(BaseModel):
    manuscript_id: Optional[str] = None
    user_id: str
    title: str
    raw_sha256: Optional[str] = None
    metadata_bible: Optional[Dict[str, Any]] = None
    current_state: str = "Ingested"

class Chunk(BaseModel):
    chunk_id: Optional[str] = None
    manuscript_id: str
    chunk_index: int
    raw_text_content: str
    chunk_sha256: str
