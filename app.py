import streamlit as st
import asyncio
from uuid import uuid4
from src.ingestion.chunkers import ingest_document_payload
from src.analysis.gateway import execute_quality_audit_async
from src.planning.blueprints import create_blueprint_from_report
from src.execution.workers import execute_blueprint_batch_async
from src.publishing.assembly import assemble_publishing_bundle, compile_master_text

st.set_page_config(page_title="V4H Publishing Engine", layout="wide", page_icon="📚")

st.title("📚 V4H Publishing Engine — Human-in-the-Loop IDE")
st.caption("REMIX-MASTER-ARCH-V3 | 5-Layer AI-Accelerated Document Optimization System")

# Initialize Session State Variables
if "manuscript" not in st.session_state:
    st.session_state.manuscript = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "audit_report" not in st.session_state:
    st.session_state.audit_report = None
if "blueprint" not in st.session_state:
    st.session_state.blueprint = None
if "rewrite_units" not in st.session_state:
    st.session_state.rewrite_units = {}

tab0, tab1, tab2, tab3 = st.tabs([
    "📥 Layer 0: Ingestion & Provenance",
    "🔍 Layer 1: Quality Audit Heatmap",
    "🛠️ Layer 2 & 3: Blueprint & Diff Review",
    "📦 Layer 4: Master Assembly Export"
])

# -----------------------------------------------------------------------------
# TAB 0: LAYER 0 INGESTION
# -----------------------------------------------------------------------------
with tab0:
    st.header("Document Intake & Cryptographic Provenance")
    uploaded_file = st.file_uploader("Upload Manuscript (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_ext = uploaded_file.name.split(".")[-1]
        
        if st.button("Process & Chunk Document", type="primary"):
            manuscript, chunks = ingest_document_payload(
                file_bytes=file_bytes,
                file_extension=file_ext,
                title=uploaded_file.name
            )
            st.session_state.manuscript = manuscript
            st.session_state.chunks = chunks
            st.success(f"✓ Ingested '{manuscript.title}' successfully!")

    if st.session_state.manuscript:
        st.subheader("Provenance Integrity Tracking")
        st.json({
            "Manuscript ID": str(st.session_state.manuscript.manuscript_id),
            "Master SHA-256": st.session_state.manuscript.raw_sha256,
            "Total Extracted Chunks": len(st.session_state.chunks),
            "Lifecycle State": st.session_state.manuscript.current_state
        })

# -----------------------------------------------------------------------------
# TAB 1: LAYER 1 QUALITY AUDIT
# -----------------------------------------------------------------------------
with tab1:
    st.header("Quality Kernel Audit & Heatmap")
    
    if not st.session_state.chunks:
        st.warning("Please upload and process a document in Layer 0 first.")
    else:
        if st.button("Run Layer 1 Audit Sweep", type="primary"):
            with st.spinner("Auditing manuscript chunks across dimension rubrics..."):
                playbook_id = uuid4()
                report = asyncio.run(execute_quality_audit_async(
                    manuscript_id=st.session_state.manuscript.manuscript_id,
                    playbook_id=playbook_id,
                    chunks=st.session_state.chunks
                ))
                st.session_state.audit_report = report
                st.success(f"✓ Audit Complete! Global LCVI Score: {report.global_lcvi_score}/10.0")

    if st.session_state.audit_report:
        st.metric("Global LCVI Score", f"{st.session_state.audit_report.global_lcvi_score} / 10.0")
        st.write("### Executive Summary")
        st.info(st.session_state.audit_report.executive_summary)

# -----------------------------------------------------------------------------
# TAB 2: LAYER 2 & 3 BLUEPRINT & DIFF REVIEW
# -----------------------------------------------------------------------------
with tab2:
    st.header("Blueprint Synthesis & Human Sign-off Gates")
    
    if not st.session_state.audit_report:
        st.warning("Please complete the Layer 1 Audit first.")
    else:
        if st.button("Generate Transformation Blueprint", type="primary"):
            blueprint = create_blueprint_from_report(
                st.session_state.audit_report,
                st.session_state.chunks
            )
            st.session_state.blueprint = blueprint
            
            chunks_map = {str(c.chunk_id): c for c in st.session_state.chunks}
            units = asyncio.run(execute_blueprint_batch_async(
                nodes=blueprint.ordered_nodes,
                chunks_map=chunks_map,
                blueprint_id=blueprint.blueprint_id,
                auto_sign_off=False
            ))
            st.session_state.rewrite_units = {str(u.source_chunk_id): u for u in units}
            st.success(f"✓ Generated Blueprint with {len(blueprint.ordered_nodes)} execution nodes!")

    if st.session_state.rewrite_units:
        st.subheader("Dual-Pane Diff & Human Sign-off Editor")
        chunk_options = [f"Chunk {c.chunk_index} ({c.chunk_id})" for c in st.session_state.chunks]
        selected_chunk_str = st.selectbox("Select Chunk to Review:", chunk_options)
        
        idx = int(selected_chunk_str.split()[1])
        target_chunk = st.session_state.chunks[idx]
        unit = st.session_state.rewrite_units.get(str(target_chunk.chunk_id))
        
        if unit:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original Baseline Text (Read-Only)**")
                st.text_area("Baseline", target_chunk.raw_text_content, height=200, disabled=True, key=f"orig_{idx}")
            with col2:
                st.markdown("**Remediated Draft Patch**")
                edited_text = st.text_area("Proposed Edit", unit.current_approved_text, height=200, key=f"edit_{idx}")
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("✅ Approve Patch", key=f"app_{idx}"):
                unit.current_approved_text = edited_text
                unit.is_human_signed_off = True
                st.success("✓ Chunk signed off!")
            if c_btn2.button("❌ Reject / Reset", key=f"rej_{idx}"):
                unit.current_approved_text = target_chunk.raw_text_content
                unit.is_human_signed_off = False
                st.info("Reset to baseline text.")
                
            st.write(f"**Sign-off Status:** {'✅ Signed Off' if unit.is_human_signed_off else '⏳ Pending Review'}")

# -----------------------------------------------------------------------------
# TAB 3: LAYER 4 MASTER PUBLISHING EXPORT
# -----------------------------------------------------------------------------
with tab3:
    st.header("Master Assembly & Publishing Bundle Export")
    
    if not st.session_state.rewrite_units:
        st.warning("Please complete Blueprint & Diff Review steps first.")
    else:
        signed_off_units = [u for u in st.session_state.rewrite_units.values() if u.is_human_signed_off]
        total_units = len(st.session_state.rewrite_units)
        
        st.write(f"**Human Sign-off Progress:** {len(signed_off_units)} / {total_units} Chunks Signed Off")
        
        if len(signed_off_units) < total_units:
            st.info("💡 You can compile with current sign-offs or sign off remaining chunks in Tab 3.")
            
        if st.button("Compile & Build Publishing Bundle (.zip)", type="primary"):
            bundle_zip = assemble_publishing_bundle(
                manuscript=st.session_state.manuscript,
                chunks=st.session_state.chunks,
                units=list(st.session_state.rewrite_units.values())
            )
            
            st.download_button(
                label="📥 Download Complete Publishing Bundle (.zip)",
                data=bundle_zip,
                file_name=f"{st.session_state.manuscript.title.replace(' ', '_')}_Publishing_Bundle.zip",
                mime="application/zip"
            )
            st.balloons()
