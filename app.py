import streamlit as st
import os
import sys

# Ensure project modules are importable
sys.path.insert(0, os.path.abspath("."))

from src.intelligence.v4h_audit import V4HAuditEngine, AuditRecommendation
from src.intelligence.domains import DOMAIN_REGISTRY, get_domain_profile, DomainType
from src.intelligence.bible import BibleGenerator
from src.formatting.adapters import adapt_for_kindle, adapt_for_paperback, adapt_for_audiobook, adapt_for_pdf

# Set Page Config
st.set_page_config(
    page_title="REMIX-MASTER | Human Gatekeeper Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 REMIX-MASTER: Autonomous Publishing Control Room")
st.caption("Domain-Adaptive Intelligence & Multi-Format Adaptation Stack")

# Sidebar Configuration
st.sidebar.header("🎯 Project Settings")

domain_choice = st.sidebar.selectbox(
    "Select Manuscript Domain / Niche",
    options=[d.value for d in DomainType],
    format_func=lambda x: DOMAIN_REGISTRY[DomainType(x)].display_name
)

current_profile = get_domain_profile(domain_choice)
st.sidebar.info(f"**Primary Focus:** {current_profile.primary_focus}")

# Navigation Tabs
tab_ingest, tab_audit, tab_bible, tab_formats = st.tabs([
    "📥 Ingestion & Raw Text", 
    "📊 V4-H Audit Engine", 
    "📖 Manuscript Bible", 
    "🚀 Multi-Format Publisher"
])

# ---------------------------------------------------------
# TAB 1: INGESTION & RAW TEXT
# ---------------------------------------------------------
with tab_ingest:
    st.header("Manuscript Ingestion")
    uploaded_file = st.file_uploader("Upload Manuscript File (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])
    
    default_text = """Most business relationships and enterprise architectures repeat familiar patterns. The Lifetime Value Matrix is a method for measuring recurring customer impact. Exercise Number 1 will help you identify them. Case Study: Acme Corp scaled revenue by 40% after implementing the framework."""
    
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        raw_text = st.text_area("Or paste sample text for testing:", value=default_text, height=200)

    st.session_state["raw_text"] = raw_text

# ---------------------------------------------------------
# TAB 2: V4-H AUDIT ENGINE
# ---------------------------------------------------------
with tab_audit:
    st.header(f"V4-H Autonomous Audit ({current_profile.display_name})")
    
    audit_engine = V4HAuditEngine()
    
    # Mock evaluation domain scores for preview
    mock_scores = {
        "commercial_preservation": 9.2,
        "reader_devotion": 8.8,
        "experience_architecture": 8.5,
        "identity_transformation": 9.0,
        "recommendation_power": 8.5,
        "reader_trust": 9.1,
        "memory_economics": 8.5,
        "asset_multiplication": 8.8,
        "evergreen_durability": 9.0
    }
    
    lcvi_score = audit_engine.calculate_lcvi(mock_scores, domain_type=domain_choice)
    tier = audit_engine.classify_lcvi(lcvi_score)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Lifetime Commercial Value Index™ (LCVI)", f"{lcvi_score} / 10.0")
    with col2:
        st.subheader(f"Status: **{tier}**")

    st.divider()
    st.subheader("Domain Required Elements Checklist")
    req_checks = audit_engine.verify_domain_elements(domain_choice, raw_text)
    for element, present in req_checks.items():
        st.checkbox(element, value=present, disabled=True)

# ---------------------------------------------------------
# TAB 3: MANUSCRIPT BIBLE
# ---------------------------------------------------------
with tab_bible:
    st.header("Extracted Manuscript Bible")
    generator = BibleGenerator()
    bible = generator.generate_bible_from_text(raw_text, domain=domain_choice, title="Uploaded Manuscript")
    
    col_fw, col_glo = st.columns(2)
    with col_fw:
        st.subheader("Extracted Frameworks")
        for fw in bible.core_frameworks:
            st.success(f"**{fw.name}**\n\n*{fw.description}*")
            
    with col_glo:
        st.subheader("Glossary / Terms")
        for g in bible.glossary:
            st.info(f"**{g.term}**: {g.definition}")

    if bible.identity_map:
        st.subheader("Psychology Identity Map")
        st.write(f"**Before State:** {bible.identity_map.before_state}")
        st.write(f"**After State:** {bible.identity_map.after_state}")

# ---------------------------------------------------------
# TAB 4: MULTI-FORMAT PUBLISHER
# ---------------------------------------------------------
with tab_formats:
    st.header("One Manuscript, Four Reading Experiences")
    
    format_choice = st.radio(
        "Select Format Target to Preview",
        options=["Kindle Edition", "Paperback Edition", "PDF Reference", "Audiobook Script"],
        horizontal=True
    )
    
    if format_choice == "Kindle Edition":
        adapted = adapt_for_kindle(raw_text)
        st.caption("Kindle: Short units optimized for reading momentum on small screens.")
    elif format_choice == "Paperback Edition":
        adapted = adapt_for_paperback(raw_text)
        st.caption("Paperback: Substantial narrative blocks that convey authority and value.")
    elif format_choice == "PDF Reference":
        adapted = adapt_for_pdf(raw_text)
        st.caption("PDF: Clean section spacing for structured reference.")
    else:
        adapted = adapt_for_audiobook(raw_text)
        st.caption("Audiobook: Conversational phrasing, visual references removed.")

    st.text_area("Transformed Output Preview", value=adapted, height=300)
    
    st.download_button(
        label=f"Export {format_choice}",
        data=adapted,
        file_name=f"manuscript_{format_choice.lower().replace(' ', '_')}.txt",
        mime="text/plain"
    )
