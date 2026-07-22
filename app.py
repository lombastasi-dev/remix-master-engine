import streamlit as st
from src.intelligence.domains import DomainType, DOMAIN_REGISTRY

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

# Sidebar Domain Selection
st.sidebar.header("🎯 Project Settings")

# Safe Enum mapping with fallback for domain selectbox
domain_choice = st.sidebar.selectbox(
    "Select Manuscript Domain / Niche",
    options=list(DomainType),
    format_func=lambda d: DOMAIN_REGISTRY.get(d, DOMAIN_REGISTRY.get(d.value)).display_name 
    if (d in DOMAIN_REGISTRY or d.value in DOMAIN_REGISTRY) 
    else d.value.replace("_", " ").title()
)

st.sidebar.success(f"Active Domain: **{domain_choice.value}**")

# Main Dashboard Content Area
st.subheader("Overview")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Status", value="Ready")

with col2:
    st.metric(label="Selected Domain", value=domain_choice.value.title())

with col3:
    st.metric(label="Engine Environment", value="Streamlit Cloud")

st.info("System initialized. Select your manuscript files to begin processing.")
