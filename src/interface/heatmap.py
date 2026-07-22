import streamlit as st
from src.models.schemas import ManuscriptChunk, Finding

def render_chunk_heatmap(chunks: list[ManuscriptChunk], findings: list[Finding]) -> ManuscriptChunk:
    st.subheader("📊 Manuscript Chunk Heatmap")
    
    # Map findings by chunk_id to determine status
    chunk_status = {}
    for c in chunks:
        chunk_status[c.chunk_id] = "Green"
        
    for f in findings:
        if f.severity_rating == "Red":
            chunk_status[f.chunk_id] = "Red"
        elif f.severity_rating == "Yellow" and chunk_status[f.chunk_id] != "Red":
            chunk_status[f.chunk_id] = "Yellow"
            
    cols_per_row = 10
    selected_chunk = None
    
    for i in range(0, len(chunks), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(chunks):
                chunk = chunks[idx]
                status = chunk_status[chunk.chunk_id]
                color_emoji = "🟢" if status == "Green" else ("🟡" if status == "Yellow" else "🔴")
                
                if col.button(f"{color_emoji} #{chunk.chunk_index + 1}", key=f"btn_chunk_{chunk.chunk_id}"):
                    st.session_state["active_chunk_id"] = chunk.chunk_id

    active_id = st.session_state.get("active_chunk_id")
    if active_id:
        selected_chunk = next((c for c in chunks if c.chunk_id == active_id), chunks[0])
    else:
        selected_chunk = chunks[0] if chunks else None
        
    return selected_chunk
