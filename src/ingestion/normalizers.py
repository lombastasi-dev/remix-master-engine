import io
import re
import pdfplumber
import docx

def normalize_text_content(text: str) -> str:
    """Strips control characters, normalizes line breaks and whitespace sequences."""
    if not text:
        return ""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def extract_text_from_file_bytes(file_bytes: bytes, extension: str) -> str:
    """Extracts raw text from pdf, docx, or txt binary streams."""
    ext = extension.lower().lstrip('.')
    
    if ext == 'txt':
        raw_text = file_bytes.decode('utf-8', errors='ignore')
        return normalize_text_content(raw_text)
        
    elif ext == 'pdf':
        extracted_pages = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)
        return normalize_text_content("\n\n".join(extracted_pages))
        
    elif ext == 'docx':
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return normalize_text_content("\n\n".join(paragraphs))
        
    else:
        raise ValueError(f"Unsupported file format extension: .{ext}")
