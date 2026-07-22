import streamlit as st
import docx
import pypdf
from src.intelligence.domains import DomainType, DOMAIN_REGISTRY, get_domain_profile

# Page Configuration
st.set_page_config(
    page_title="REMIX-MASTER Control Room",
    page_icon="📚",
    layout="wide"
)

def extract_text_from_file(uploaded_file):
    """Extract raw text from uploaded DOCX or PDF file."""
    text = ""
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    if file_type == "docx":
        doc = docx.Document(uploaded_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    elif file_type == "pdf":
        reader = pypdf.PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        
    return text

# Header Section
st.title("📚 REMIX-MASTER: Autonomous Publishing Control Room")
st.caption("Domain-Adaptive Intelligence & Multi-Format Adaptation Stack")

st.divider()

# Sidebar Settings
st.sidebar.header("🎯 Project Settings")

# Domain Selection
domain_choice = st.sidebar.selectbox(
    "Select Manuscript Domain / Niche",
    options=list(DomainType),
    format_func=lambda d: DOMAIN_REGISTRY.get(d, DOMAIN_REGISTRY.get(d.value)).display_name 
    if (d in DOMAIN_REGISTRY or d.value in DOMAIN_REGISTRY) 
    else d.value.replace("_", " ").title()
)

# Retrieve selected profile
profile = get_domain_profile(domain_choice)

st.sidebar.success(f"Active Domain: **{profile.display_name}**")

# Main Dashboard - Domain Overview
st.subheader("🎯 Active Domain Overview")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Selected Niche", value=profile.display_name)
    st.metric(label="Engine Environment", value="Streamlit Cloud")

with col2:
    st.markdown(f"**Primary Focus:** {profile.primary_focus}")
    st.markdown("**Required Structural Elements:**")
    st.markdown(" ".join([f"`{elem}`" for elem in profile.required_elements]))

st.divider()

# Main Dashboard - Ingestion Setup
st.subheader("📄 Manuscript Ingestion & Parsing")

uploaded_file = st.file_uploader(
    "Upload manuscript file (.docx or .pdf)",
    type=["docx", "pdf"],
    help="Upload your document to begin ingestion and domain-adaptive auditing."
)

if uploaded_file is not None:
    st.success(f"File **{uploaded_file.name}** uploaded successfully ({uploaded_file.size / 1024:.1f} KB).")
    
    with st.spinner("Extracting and normalizing manuscript text..."):
        raw_text = extract_text_from_file(uploaded_file)
        char_count = len(raw_text)
        word_count = len(raw_text.split())

    # Ingestion Stats
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.metric("Total Character Count", f"{char_count:,}")
    with ic2:
        st.metric("Total Word Count", f"{word_count:,}")
    with ic3:
        st.metric("Ingestion Status", "Parsed & Ready")

    # Text Preview Expander
    with st.expander("📖 Manuscript Text Preview (First 1,500 characters)", expanded=False):
        st.text_area("Raw Text Sample", raw_text[:1500] + ("..." if len(raw_text) > 1500 else ""), height=200)

else:
    st.info("Please upload a `.docx` or `.pdf` manuscript file to proceed.")
