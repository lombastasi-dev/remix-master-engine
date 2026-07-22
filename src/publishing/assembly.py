import io
import json
import zipfile
from src.models.schemas import Manuscript, RewriteUnit

def assemble_master_manuscript(manuscript: Manuscript, approved_units: list[RewriteUnit]) -> tuple[str, bool]:
    # Strictly enforce the compile gate: non-signed-off units block compilation
    unapproved = [u for u in approved_units if not u.is_human_signed_off]
    if unapproved:
        return f"Compilation Blocked: {len(unapproved)} chunk(s) pending human sign-off.", False

    # Sort and stitch text
    compiled_text = "\n\n".join([u.current_approved_text for u in approved_units])
    return compiled_text, True

def build_publishing_bundle(manuscript: Manuscript, compiled_text: str, metadata_json: str, cover_bytes: bytes = None) -> bytes:
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Master Compiled Manuscript
        clean_title = manuscript.title.lower().replace(" ", "_")
        zip_file.writestr(f"{clean_title}_manuscript.md", compiled_text)
        
        # 2. Metadata Package
        zip_file.writestr("kdp_metadata.json", metadata_json)
        
        # 3. Provenance Certificate
        provenance = {
            "manuscript_id": str(manuscript.manuscript_id),
            "raw_sha256": manuscript.raw_sha256,
            "title": manuscript.title,
            "state": manuscript.current_state,
            "created_at": str(manuscript.created_at)
        }
        zip_file.writestr("provenance_certificate.json", json.dumps(provenance, indent=2))
        
        # 4. Cover image blueprint if provided
        if cover_bytes:
            zip_file.writestr("cover_blueprint.png", cover_bytes)
            
    return zip_buffer.getvalue()
