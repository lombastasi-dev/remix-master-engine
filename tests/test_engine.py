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
    
    compiled_text, is_complete = assemble_master_manuscript(manuscript, [unit])
    assert is_complete is True
    assert "Revised and polished text." in compiled_text
    
    metadata = {
        "title": manuscript.title,
        "domain_profile": "Tech Non-Fiction",
        "baseline_raw_sha256": manuscript.raw_sha256
    }
    metadata_json = json.dumps(metadata, indent=2)
    
    zip_bytes = build_publishing_bundle(
        manuscript=manuscript,
        compiled_text=compiled_text,
        metadata_json=metadata_json
    )
    
    output_zip_path = os.path.join(tmp_path, "test_bundle.zip")
    with open(output_zip_path, "wb") as f:
        f.write(zip_bytes)
        
    assert os.path.exists(output_zip_path)
    
    with zipfile.ZipFile(output_zip_path, 'r') as z:
        file_list = z.namelist()
        assert any(f.endswith(".md") for f in file_list)
        assert any("metadata" in f or "provenance" in f for f in file_list)

@pytest.mark.asyncio
async def test_async_batch_processing():
    """Test parallel chunk processing in Layer 1 Quality Kernel Gateway."""
    from src.analysis.gateway import process_manuscript_chunks_async
    
    manuscript_id = uuid4()
    chunks = [
        ManuscriptChunk(
            manuscript_id=manuscript_id,
            chunk_index=i,
            raw_text_content=f"Sample sentence {i} with passive voice." if i % 2 == 0 else f"Active sentence {i}.",
            chunk_sha256="a" * 64
        )
        for i in range(20)
    ]
    
    report = await process_manuscript_chunks_async(chunks, max_concurrency=5)
    
    assert report is not None
    assert len(report.prioritized_issues_map["medium"]) == 10


@pytest.mark.asyncio
async def test_blueprint_generation():
    """Test Layer 2 Blueprint Engine generation from AuditReport."""
    from src.analysis.gateway import process_manuscript_chunks_async
    from src.planning.blueprints import generate_transformation_blueprint
    
    manuscript_id = uuid4()
    chunks = [
        ManuscriptChunk(
            manuscript_id=manuscript_id,
            chunk_index=i,
            raw_text_content=f"Sample sentence {i} with passive voice." if i % 2 == 0 else f"Active sentence {i}.",
            chunk_sha256="b" * 64
        )
        for i in range(10)
    ]
    
    audit_report = await process_manuscript_chunks_async(chunks)
    blueprint = generate_transformation_blueprint(audit_report)
    
    assert blueprint is not None
    assert blueprint.manuscript_id == manuscript_id
    assert len(blueprint.ordered_nodes) == 5  # 5 chunks with passive voice findings
    assert blueprint.ordered_nodes[0].chronological_execution_order == 1
    assert "REVISE" in blueprint.ordered_nodes[0].remediation_instruction_payload


@pytest.mark.asyncio
async def test_worker_execution_and_diffs():
    """Test Layer 3 execution worker rewriting and differential patch generation."""
    from src.execution.workers import execute_blueprint_batch_async, generate_differential_patch
    
    # Test diff generator
    diff = generate_differential_patch("Sample with passive voice.", "Sample actively reframed.")
    assert "baseline_chunk.txt" in diff
    assert "-Sample with passive voice." in diff
    assert "+Sample actively reframed." in diff
    
    # Setup test entities
    manuscript_id = uuid4()
    blueprint_id = uuid4()
    chunk = ManuscriptChunk(
        manuscript_id=manuscript_id,
        chunk_index=0,
        raw_text_content="Sample sentence 0 with passive voice.",
        chunk_sha256="c" * 64
    )
    
    node = BlueprintNode(
        node_id=uuid4(),
        blueprint_id=blueprint_id,
        chunk_id=chunk.chunk_id,
        chronological_execution_order=1,
        assigned_action_type="revise",
        remediation_instruction_payload="[REVISE] Passive voice detected."
    )
    
    chunks_map = {str(chunk.chunk_id): chunk}
    units = await execute_blueprint_batch_async([node], chunks_map, auto_sign_off=True)
    
    assert len(units) == 1
    assert units[0].is_human_signed_off is True
    assert "actively reframed" in units[0].current_approved_text
    assert len(units[0].differential_patch_data) > 0


def test_layer0_ingestion_and_provenance():
    """Test Layer 0 extraction, normalization, boundary chunking, and SHA-256 provenance."""
    from src.ingestion.chunkers import ingest_document_payload, compute_sha256
    
    sample_text = "Paragraph 1 baseline content.\n\nParagraph 2 baseline content."
    raw_bytes = sample_text.encode('utf-8')
    
    manuscript, chunks = ingest_document_payload(
        file_bytes=raw_bytes,
        file_extension="txt",
        title="Test Manuscript Title"
    )
    
    assert manuscript is not None
    assert manuscript.title == "Test Manuscript Title"
    assert manuscript.raw_sha256 == compute_sha256(sample_text)
    assert len(chunks) == 1
    assert chunks[0].chunk_sha256 == compute_sha256(sample_text)
