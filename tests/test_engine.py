import os
import zipfile
import json
import pytest
from uuid import uuid4
from src.models.schemas import Manuscript, ManuscriptChunk, Blueprint, BlueprintNode, RewriteUnit
from src.publishing.assembly import assemble_master_manuscript, build_publishing_bundle

def test_schema_validations():
    """Test Pydantic model constraints and default values."""
    manuscript = Manuscript(
        user_id="user_123",
        title="Test Book",
        raw_sha256="a" * 64
    )
    assert manuscript.title == "Test Book"
    assert manuscript.current_state == "Concept"
    
    node = BlueprintNode(
        chunk_id=uuid4(),
        chronological_execution_order=1,
        assigned_action_type="revise",
        remediation_instruction_payload="Fix passive voice"
    )
    assert node.assigned_action_type == "revise"

def test_bundle_assembly(tmp_path):
    """Test Layer 4 publishing bundle zip generation and internal contents."""
    manuscript = Manuscript(
        user_id="user_test",
        title="Sample Bundle Manuscript",
        raw_sha256="f" * 64
    )
    
    chunk = ManuscriptChunk(
        manuscript_id=manuscript.manuscript_id,
        chunk_index=0,
        raw_text_content="Original baseline text.",
        chunk_sha256="e" * 64
    )
    
    node = BlueprintNode(
        chunk_id=chunk.chunk_id,
        chronological_execution_order=0,
        assigned_action_type="rewrite",
        remediation_instruction_payload="Enhance style"
    )
    
    blueprint = Blueprint(
        manuscript_id=manuscript.manuscript_id,
        associated_report_id=uuid4(),
        ordered_nodes=[node]
    )
    
    unit = RewriteUnit(
        blueprint_id=blueprint.blueprint_id,
        node_id=node.node_id,
        source_chunk_id=chunk.chunk_id,
        current_approved_text="Revised and polished text.",
        differential_patch_data="Diff info",
        is_human_signed_off=True
    )
    
    # 1. Assemble text
    compiled_text, is_complete = assemble_master_manuscript(manuscript, [unit])
    assert is_complete is True
    assert "Revised and polished text." in compiled_text
    
    # 2. Build metadata JSON string
    metadata = {
        "title": manuscript.title,
        "domain_profile": "Tech Non-Fiction",
        "baseline_raw_sha256": manuscript.raw_sha256
    }
    metadata_json = json.dumps(metadata, indent=2)
    
    # 3. Compile Zip bytes
    zip_bytes = build_publishing_bundle(
        manuscript=manuscript,
        compiled_text=compiled_text,
        metadata_json=metadata_json
    )
    
    # 4. Save and inspect zip file
    output_zip_path = os.path.join(tmp_path, "test_bundle.zip")
    with open(output_zip_path, "wb") as f:
        f.write(zip_bytes)
        
    assert os.path.exists(output_zip_path)
    
    with zipfile.ZipFile(output_zip_path, 'r') as z:
        file_list = z.namelist()
        assert any(f.endswith(".md") for f in file_list)
        assert any("metadata" in f or "provenance" in f for f in file_list)
