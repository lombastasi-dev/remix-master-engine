import io
import streamlit as st
import docx
from docx import Document
import pypdf
import google.generativeai as genai
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

def audit_manuscript(text, required_elements):
    """Perform a preliminary keyword/heading check for required structural elements."""
    results = {}
    text_lower = text.lower()
    
    for element in required_elements:
        present = element.lower() in text_lower
        results[element] = present
        
    found_count = sum(results.values())
    score = int((found_count / len(required_elements)) * 100) if required_elements else 100
    return results, score

def create_docx_from_markdown(text, domain_name):
    """Convert generated markdown-like response into a clean Word document."""
    doc = Document()
    doc.add_heading(f"Remastered Output — {domain_name}", level=0)
    
    for line in text.split("\n"):
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith("# "):
            doc.add_heading(line_strip[2:], level=1)
        elif line_strip.startswith("## "):
            doc.add_heading(line_strip[3:], level=2)
        elif line_strip.startswith("### "):
            doc.add_heading(line_strip[4:], level=3)
        elif line_strip.startswith("- ") or line_strip.startswith("* "):
            doc.add_paragraph(line_strip[2:], style='List Bullet')
        else:
            doc.add_paragraph(line_strip)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Header Section
st.title("📚 REMIX-MASTER: Autonomous Publishing Control Room")
st.caption("Domain-Adaptive Intelligence & Multi-Format Adaptation Stack")

st.divider()

# Sidebar Settings
st.sidebar.header("🎯 Project Settings")

domain_choice = st.sidebar.selectbox(
    "Select Manuscript Domain / Niche",
    options=list(DomainType),
    format_func=lambda d: DOMAIN_REGISTRY.get(d, DOMAIN_REGISTRY.get(d.value)).display_name 
    if (d in DOMAIN_REGISTRY or d.value in DOMAIN_REGISTRY) 
    else d.value.replace("_", " ").title()
)

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

    st.divider()

    # Structural Audit
    st.subheader(f"📊 Structural Audit — {profile.display_name}")
    
    audit_results, readiness_score = audit_manuscript(raw_text, profile.required_elements)
    
    ac1, ac2 = st.columns([1, 2])
    
    with ac1:
        st.metric(label="Domain Compliance Score", value=f"{readiness_score}%")
        st.progress(readiness_score / 100)
        
    with ac2:
        st.markdown("**Element Check:**")
        missing_elements = []
        for elem, detected in audit_results.items():
            if detected:
                st.write(f"✅ **{elem}** — Detected")
            else:
                st.write(f"❌ **{elem}** — Missing / Not Detected")
                missing_elements.append(elem)

    st.divider()

    # Live Generation & Export Engine
    st.subheader("🚀 Autonomous Adaptation Engine")
    st.write("Generate missing structural components and domain-specific publishing outputs.")

    if st.button("⚡ Run Domain-Adaptive Remastering", type="primary"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            st.error("⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Please add it to your app settings.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = f"""You are an expert publishing editor specializing in {profile.display_name}.
                
The target focus is: {profile.primary_focus}
The required structural elements for this niche are: {', '.join(profile.required_elements)}
The following elements were flagged as MISSING: {', '.join(missing_elements) if missing_elements else 'None'}

Here is the raw manuscript draft:
---
{raw_text[:4000]}
---

Please generate an adapted executive summary and draft the missing structural components formatted in clean Markdown for immediate publishing preparation.
"""

                with st.spinner("AI Engine generating domain adaptation..."):
                    response = model.generate_content(prompt)
                    st.session_state['generated_text'] = response.text
                    
            except Exception as e:
                st.error(f"Error during AI generation: {e}")

    if 'generated_text' in st.session_state:
        st.subheader("✨ Generated Domain Adaptation")
        st.markdown(st.session_state['generated_text'])
        
        st.divider()
        st.subheader("💾 Export Multi-Pack")
        
        ec1, ec2 = st.columns(2)
        
        with ec1:
            # Word Document Download
            docx_buffer = create_docx_from_markdown(st.session_state['generated_text'], profile.display_name)
            st.download_button(
                label="📄 Download as Word Document (.docx)",
                data=docx_buffer,
                file_name=f"remastered_{domain_choice.value}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        with ec2:
            # Markdown Download
            st.download_button(
                label="📝 Download as Markdown (.md)",
                data=st.session_state['generated_text'],
                file_name=f"remastered_{domain_choice.value}.md",
                mime="text/markdown",
                use_container_width=True
            )

else:
    st.info("Please upload a `.docx` or `.pdf` manuscript file to proceed.")
