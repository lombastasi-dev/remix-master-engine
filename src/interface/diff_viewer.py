import streamlit as st
from src.models.schemas import ManuscriptChunk, RewriteUnit

def render_dual_pane_diff(chunk: ManuscriptChunk, unit: RewriteUnit) -> RewriteUnit:
    st.subheader(f"🔍 Dual-Pane Diff Editor — Chunk #{chunk.chunk_index + 1}")
    
    col_orig, col_rev = st.columns(2)
    
    with col_orig:
        st.markdown("**Original Source Context (Read-Only)**")
        st.text_area("Source Text", value=chunk.raw_text_content, height=250, disabled=True, key=f"orig_{chunk.chunk_id}")
        st.caption(f"SHA-256 Hash: `{chunk.chunk_sha256[:16]}...`")
        
    with col_rev:
        st.markdown("**AI Proposed Patch / Edit Target**")
        edited_text = st.text_area("Active Draft String", value=unit.current_approved_text, height=250, key=f"rev_{chunk.chunk_id}")
        
    st.markdown("### 🛡️ Human Gate Action Controls")
    c1, c2, c3 = st.columns([1, 1, 2])
    
    with c1:
        if st.button("✅ Accept Patch & Approve", type="primary", key=f"approve_{chunk.chunk_id}"):
            unit.current_approved_text = edited_text
            unit.is_human_signed_off = True
            unit.version_history_array.append({"action": "human_approved", "content": edited_text})
            st.success("✓ Patch approved and signed off!")
            
    with c2:
        if st.button("❌ Reject & Restore Original", key=f"reject_{chunk.chunk_id}"):
            unit.current_approved_text = chunk.raw_text_content
            unit.is_human_signed_off = True
            unit.version_history_array.append({"action": "human_rejected_restored_original"})
            st.warning("Original text restored and signed off.")
            
    with c3:
        status_badge = "🟢 Approved & Locked" if unit.is_human_signed_off else "🔴 Pending Sign-off"
        st.info(f"Gate Status: **{status_badge}**")
        
    return unit
