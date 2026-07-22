import streamlit as st
import json
from uuid import uuid4
from src.models.schemas import Manuscript, Playbook, PlaybookDimension
from src.ingestion.pipeline import extract_text, chunk_manuscript, compute_sha256
from src.analysis.gateway import execute_chunk_diagnostic
from src.planning.blueprints import generate_blueprint_from_findings, generate_rewrite_unit
from src.interface.heatmap import render_chunk_heatmap
from src.interface.diff_viewer import render_dual_pane_diff
from src.publishing.assembly import assemble_master_manuscript, build_publishing_bundle

st.set_page_config(page_title="REMIX MASTER ENGINE V3", layout="wide")

st.title("⚡ REMIX MASTER ENGINE V3")
st.caption("Human-Gated, AI-Accelerated Publishing Engine")

# Session state initialization
if "manuscript" not in st.session_state:
    st.session_state["manuscript"] = None
if "chunks" not in st.session_state:
    st.session_state["chunks"] = []
if "findings" not in st.session_state:
    st.session_state["findings"] = []
if "rewrite_units" not in st.session_state:
    st.session_state["rewrite_units"] = {}

# Sidebar Domain Config
st.sidebar.header("🎯 Domain Profile Setup")
domain_niche = st.sidebar.selectbox("Niche Profile", ["Self-Help / Non-Fiction", "Technical / Academic", "Fiction / Narrative"])
target_tone = st.sidebar.selectbox("Target Tone", ["Authoritative & Professional", "Conversational & Engaging", "Academic & Precise"])

# Step 1: Upload & Ingest (Layer 0)
st.header("1. Ingestion & Provenance (Layer 0)")
uploaded_file = st.file_uploader("Upload Manuscript (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])

if uploaded_file and st.button("🚀 Ingest & Process Manuscript"):
    with st.spinner("Extracting text and computing cryptographic SHA-256 hashes..."):
        raw_text = extract_text(uploaded_file, uploaded_file.name)
        raw_sha256 = compute_sha256(raw_text)
        
        manuscript = Manuscript(
            user_id="operator_01",
            title=uploaded_file.name.split(".")[0].title(),
            current_state="Draft",
            raw_sha256=raw_sha256
        )
        chunks = chunk_manuscript(manuscript.manuscript_id, raw_text)
        
        st.session_state["manuscript"] = manuscript
        st.session_state["chunks"] = chunks
        st.session_state["findings"] = []
        st.session_state["rewrite_units"] = {}
        st.success(f"✓ Ingested '{manuscript.title}' into {len(chunks)} chunk(s). Master Hash: {raw_sha256[:16]}...")

# Step 2: Audit & Quality Kernel (Layer 1)
if st.session_state["chunks"]:
    st.divider()
    st.header("2. Diagnostic Audit (Layer 1)")
    
    if st.button("🔍 Run Quality Kernel Audit"):
        report_id = uuid4()
        all_findings = []
        
        progress = st.progress(0)
        for idx, chunk in enumerate(st.session_state["chunks"]):
            findings, source = execute_chunk_diagnostic(chunk, report_id, f"Target Tone: {target_tone}")
            all_findings.extend(findings)
            progress.progress((idx + 1) / len(st.session_state["chunks"]))
            
        st.session_state["findings"] = all_findings
        st.success(f"✓ Audit Complete! Evaluated via {source}. Total Findings: {len(all_findings)}")

# Step 3: Heatmap & Patch Management (Layers 2 & 3)
if st.session_state["chunks"] and "findings" in st.session_state:
    st.divider()
    st.header("3. Human Approval Gate (Layers 2 & 3)")
    
    selected_chunk = render_chunk_heatmap(st.session_state["chunks"], st.session_state["findings"])
    
    if selected_chunk:
        # Generate or retrieve rewrite unit for active chunk
        if selected_chunk.chunk_id not in st.session_state["rewrite_units"]:
            # Mock node generation for active chunk
            blueprint = generate_blueprint_from_findings(
                st.session_state["manuscript"].manuscript_id,
                uuid4(),
                st.session_state["chunks"],
                st.session_state["findings"]
            )
            node = next((n for n in blueprint.ordered_nodes if n.chunk_id == selected_chunk.chunk_id), blueprint.ordered_nodes[0])
            unit = generate_rewrite_unit(blueprint.blueprint_id, node, selected_chunk, target_tone)
            st.session_state["rewrite_units"][selected_chunk.chunk_id] = unit
            
        active_unit = st.session_state["rewrite_units"][selected_chunk.chunk_id]
        updated_unit = render_dual_pane_diff(selected_chunk, active_unit)
        st.session_state["rewrite_units"][selected_chunk.chunk_id] = updated_unit

# Step 4: Master Assembly & Export (Layer 4)
if st.session_state["rewrite_units"]:
    st.divider()
    st.header("4. Master Assembly & Distribution Bundle (Layer 4)")
    
    all_units = list(st.session_state["rewrite_units"].values())
    compiled_text, is_ready = assemble_master_manuscript(st.session_state["manuscript"], all_units)
    
    if is_ready:
        st.success("🟢 All active units human-verified! Ready for compilation.")
        
        metadata_json = json.dumps({
            "title": st.session_state["manuscript"].title,
            "domain": domain_niche,
            "tone": target_tone,
            "hash": st.session_state["manuscript"].raw_sha256
        }, indent=2)
        
        bundle_bytes = build_publishing_bundle(st.session_state["manuscript"], compiled_text, metadata_json)
        
        st.download_button(
            label="📦 Download Complete Publishing Bundle (.zip)",
            data=bundle_bytes,
            file_name=f"{st.session_state['manuscript'].title.lower().replace(' ', '_')}_bundle.zip",
            mime="application/zip"
        )
    else:
        st.warning(f"⚠️ {compiled_text}")
