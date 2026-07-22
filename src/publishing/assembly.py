import zipfile
import io
import json
from datetime import datetime
from src.models.schemas import Manuscript, RewriteUnit

def generate_front_matter(manuscript: Manuscript, domain_profile: str = "Standard Non-Fiction") -> str:
    """Generates standard front matter including title, metadata, and ToC placeholders."""
    now_str = datetime.utcnow().strftime("%Y-%m-%d")
    return f"""# {manuscript.title.upper()}

**Domain Profile:** {domain_profile}  
**Compilation Date:** {now_str}  
**Master Hash (SHA-256):** `{manuscript.raw_sha256[:16]}...`

---

## Table of Contents
1. [Manuscript Body](#manuscript-body)
2. [Provenance & Verification Summary](#provenance--verification-summary)

---

## Manuscript Body

"""

def generate_back_matter(manuscript: Manuscript) -> str:
    """Generates back matter including copyright, provenance disclaimer, and publisher sign-off."""
    return f"""

---

## Provenance & Verification Summary

* **Engine:** REMIX Master Engine V3 (Human-Gated, AI-Accelerated)
* **User ID:** `{manuscript.user_id}`
* **State:** Approved & Signed Off
* **Copyright Notice:** All rights reserved by the original author and human gatekeeper.

*Generated automatically via Layer 4 Assembly Pipeline.*
"""

def assemble_master_manuscript(
    manuscript: Manuscript, 
    approved_units: list[RewriteUnit],
    domain_profile: str = "Standard Non-Fiction"
) -> tuple[str, bool]:
    """Assembles all approved units into a complete manuscript string with front and back matter."""
    all_signed_off = all(unit.is_human_signed_off for unit in approved_units) if approved_units else False
    
    body_content = "\n\n".join([unit.current_approved_text for unit in approved_units])
    
    front_matter = generate_front_matter(manuscript, domain_profile)
    back_matter = generate_back_matter(manuscript)
    
    full_manuscript = front_matter + body_content + back_matter
    return full_manuscript, all_signed_off

def build_publishing_bundle(
    manuscript: Manuscript, 
    compiled_text: str, 
    metadata_json: str, 
    cover_bytes: bytes = None
) -> bytes:
    """Packages the compiled manuscript, provenance certificate, and metadata into a zip bundle."""
    zip_buffer = io.BytesIO()
    
    slug_title = manuscript.title.lower().replace(" ", "_")
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{slug_title}_manuscript.md", compiled_text)
        zip_file.writestr("kdp_metadata.json", metadata_json)
        
        prov_cert = {
            "manuscript_id": str(manuscript.manuscript_id),
            "title": manuscript.title,
            "baseline_raw_sha256": manuscript.raw_sha256,
            "user_id": manuscript.user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        zip_file.writestr("provenance_certificate.json", json.dumps(prov_cert, indent=2))
        
        if cover_bytes:
            zip_file.writestr("cover.jpg", cover_bytes)
            
    return zip_buffer.getvalue()
