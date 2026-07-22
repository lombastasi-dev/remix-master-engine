import streamlit as st
from src.intelligence.domains import DomainType, DOMAIN_REGISTRY, get_domain_profile

# Page Configuration
st.set_page_config(
    page_title="REMIX-MASTER Control Room",
    page_icon="📚",
    layout="wide"
)

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
    st.tags = st.write(" ".join([f"`{elem}`" for elem in profile.required_elements]))

st.divider()

# Main Dashboard - Ingestion Setup
st.subheader("📄 Manuscript Ingestion")

uploaded_file = st.file_uploader(
    "Upload manuscript file (.docx or .pdf)",
    type=["docx", "pdf"],
    help="Upload your document to begin ingestion and domain-adaptive auditing."
)

if uploaded_file is not None:
    st.success(f"File **{uploaded_file.name}** uploaded successfully ({uploaded_file.size / 1024:.1f} KB).")
    st.info("Ready for Phase 2: Ingestion & Parsing.")
else:
    st.warning("Please upload a `.docx` or `.pdf` manuscript file to proceed.")
