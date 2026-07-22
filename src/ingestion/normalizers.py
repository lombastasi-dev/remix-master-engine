import io
import re
import docx
import pdfplumber

def normalize_text(raw_text: str) -> str:
    """Strips hidden control characters and normalizes whitespace sequences."""
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', raw_text)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()

def extract_text_from_file(file_bytes: bytes, file_extension: str) -> str:
    """Extracts raw text payload from supported binary byte streams."""
    ext = file_extension.lower().replace(".", "")
    extracted_text = ""

    if ext == "docx":
        doc = docx.Document(io.BytesIO(file_bytes))
        extracted_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    elif ext == "pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
            extracted_text = "\n\n".join(pages_text)

    elif ext == "txt":
        extracted_text = file_bytes.decode("utf-8", errors="ignore")

    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    return normalize_text(extracted_text)
