import io
import streamlit as st
import docx
from docx import Document
import pypdf
import google.generativeai as genai
from openai import OpenAI
from fpdf import FPDF
from src.intelligence.domains import DomainType, DOMAIN_REGISTRY, get_domain_profile

# Page Configuration
st.set_page_config(
    page_title="REMIX-MASTER Control Room",
    page_icon="📚",
    layout="wide"
)

def extract_text_from_file(file):
    """Extract raw text from uploaded DOCX or PDF file."""
    text = ""
    file_type = file.name.split(".")[-1].lower()
    
    if file_type == "docx":
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    elif file_type == "pdf":
        reader = pypdf.PdfReader(file)
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

class PublicationPDF(FPDF):
    def __init__(self, domain_name):
        super().__init__()
        self.domain_name = domain_name

    def header(self):
        self.set_fill_color(26, 37, 44)
        self.rect(0, 0, 210, 22, 'F')
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, f"REMIX-MASTER Remastered Manuscript | Niche: {self.domain_name}", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

def create_pdf_from_markdown(text, domain_name):
    """Convert generated markdown into a publication PDF using FPDF2."""
    pdf = PublicationPDF(domain_name)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for line in text.split("\n"):
        line_s = line.strip()
        if not line_s:
            pdf.ln(3)
            continue
            
        # Clean non-latin characters for standard PDF fonts
        line_clean = line_s.encode('latin-1', 'replace').decode('latin-1')

        if line_clean.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(26, 37, 44)
            pdf.ln(4)
            pdf.multi_cell(0, 8, line_clean[2:])
            pdf.ln(2)
        elif line_clean.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(44, 82, 130)
            pdf.ln(3)
            pdf.multi_cell(0, 7, line_clean[3:])
            pdf.ln(1)
        elif line_clean.startswith("### "):
            pdf.set_font("Helvetica", "I", 11)
            pdf.set_text_color(74, 85, 104)
            pdf.multi_cell(0, 6, line_clean[4:])
        elif line_clean.startswith("- ") or line_clean.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 6, f"   • {line_clean[2:]}")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 6, line_clean)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def generate_adaptation_with_fallback(prompt):
    """Attempts OpenRouter free-tier generation first, falls back to Gemini API."""
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    
    if openrouter_key:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
            )
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-lite-preview-02-05:free",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content, "OpenRouter (Free Tier)"
        except Exception as openrouter_err:
            st.warning(f"⚠️ OpenRouter Free Tier failed ({openrouter_err}). Switching to Gemini Fallback...")

    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text, "Google Gemini API (Fallback)"
        except Exception as gemini_err:
            raise RuntimeError(f"Gemini Fallback failed: {gemini_err}")

    raise ValueError("No valid API keys found. Please set OPENROUTER_API_KEY or GEMINI_API_KEY in Streamlit Secrets.")

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

st.sidebar.divider()
st.sidebar.header("⚙️ Custom Audit Rules & Style")

target_word_count = st.sidebar.number_input(
    "Target Word Count Threshold",
    min_value=100,
    max_value=100000,
    value=1500,
    step=250,
    help="Set the minimum target word count for compliance check."
)

target_tone = st.sidebar.selectbox(
    "Target Writing Tone & Style",
    options=["Executive Brief", "Conversational & Engaging", "Academic & Formal", "Technical Direct", "Authoritative Guide"],
    index=0
)

custom_elements_input = st.sidebar.text_input(
    "Custom Structural Elements (Comma-separated)",
    value="",
    placeholder="e.g., Key Takeaways, Action Steps, FAQs",
    help="Add additional custom section headings to check for in the audit."
)

all_required_elements = list(profile.required_elements)
if custom_elements_input.strip():
    user_customs = [e.strip() for e in custom_elements_input.split(",") if e.strip()]
    for c_elem in user_customs:
        if c_elem not in all_required_elements:
            all_required_elements.append(c_elem)

# Main Dashboard - Domain Overview
st.subheader("🎯 Active Domain Overview")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Selected Niche", value=profile.display_name)
    st.metric(label="Selected Writing Tone", value=target_tone)

with col2:
    st.markdown(f"**Primary Focus:** {profile.primary_focus}")
    st.markdown(f"**Target Word Count:** `{target_word_count:,} words`")
    st.markdown("**Active Audit Elements:**")
    st.markdown(" ".join([f"`{elem}`" for elem in all_required_elements]))

st.divider()

# Main Dashboard - Batch Ingestion Setup
st.subheader("📦 Batch Manuscript Ingestion & Parsing")

uploaded_files = st.file_uploader(
    "Upload manuscript files (.docx or .pdf)",
    type=["docx", "pdf"],
    accept_multiple_files=True,
    help="Upload single or multiple chapter files to analyze in batch."
)

if uploaded_files:
    st.success(f"**{len(uploaded_files)} file(s)** uploaded for batch processing.")
    
    combined_text = ""
    file_summaries = []

    with st.spinner("Extracting and aggregating batch texts..."):
        for file in uploaded_files:
            file_text = extract_text_from_file(file)
            f_words = len(file_text.split())
            f_chars = len(file_text)
            file_summaries.append({"filename": file.name, "words": f_words, "chars": f_chars})
            combined_text += f"\n\n--- FILE: {file.name} ---\n\n" + file_text

        total_char_count = len(combined_text)
        total_word_count = len(combined_text.split())

    # Batch Metrics
    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.metric("Total Batch Files", len(uploaded_files))
    with ic2:
        st.metric("Aggregate Word Count", f"{total_word_count:,}")
    with ic3:
        word_pct = min(100, int((total_word_count / target_word_count) * 100))
        st.metric("Word Count Progress", f"{word_pct}%")
    with ic4:
        st.metric("Batch Status", "Aggregated & Ready")

    # File Breakdown Expander
    with st.expander("📂 Batch Files Breakdown & Preview", expanded=False):
        for f_info in file_summaries:
            st.write(f"📄 **{f_info['filename']}** — {f_info['words']:,} words ({f_info['chars']:,} chars)")
        st.text_area("Aggregated Batch Text Sample", combined_text[:2000] + ("..." if len(combined_text) > 2000 else ""), height=200)

    st.divider()

    # Structural Audit
    st.subheader(f"📊 Structural Audit — {profile.display_name}")
    
    audit_results, readiness_score = audit_manuscript(combined_text, all_required_elements)
    
    ac1, ac2 = st.columns([1, 2])
    
    with ac1:
        st.metric(label="Batch Compliance Score", value=f"{readiness_score}%")
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

    # Live Generation Engine
    st.subheader("🚀 Autonomous Adaptation Engine")
    st.write(f"Generate missing structural components in **{target_tone}** tone.")

    if st.button("⚡ Run Domain-Adaptive Remastering", type="primary"):
        prompt = f"""You are an expert publishing editor specializing in {profile.display_name}.
        
The target focus is: {profile.primary_focus}
The required tone and style is: {target_tone}
The required target word count threshold is: {target_word_count} words
The required structural elements for this niche are: {', '.join(all_required_elements)}
The following elements were flagged as MISSING across the batch: {', '.join(missing_elements) if missing_elements else 'None'}

Here is the aggregated text from {len(uploaded_files)} manuscript files:
---
{combined_text[:5000]}
---

Please generate an adapted executive summary in the requested tone ({target_tone}), harmonize chapter transitions, and draft any missing structural components formatted in clean Markdown.
"""

        with st.spinner("AI Engine generating batch domain adaptation..."):
            try:
                output_text, provider_used = generate_adaptation_with_fallback(prompt)
                st.session_state['generated_text'] = output_text
                st.session_state['provider_used'] = provider_used
            except Exception as e:
                st.error(f"Execution Error: {e}")

    if 'generated_text' in st.session_state:
        st.info(f"Generated via: **{st.session_state.get('provider_used', 'Unknown Provider')}**")
        st.subheader("✨ Generated Domain Adaptation")
        st.markdown(st.session_state['generated_text'])
        
        st.divider()
        st.subheader("💾 Export Multi-Pack")
        
        ec1, ec2, ec3 = st.columns(3)
        
        with ec1:
            docx_buffer = create_docx_from_markdown(st.session_state['generated_text'], profile.display_name)
            st.download_button(
                label="📄 Download as Word (.docx)",
                data=docx_buffer,
                file_name=f"remastered_{domain_choice.value}_batch.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        with ec2:
            st.download_button(
                label="📝 Download as Markdown (.md)",
                data=st.session_state['generated_text'],
                file_name=f"remastered_{domain_choice.value}_batch.md",
                mime="text/markdown",
                use_container_width=True
            )

        with ec3:
            try:
                pdf_buffer = create_pdf_from_markdown(st.session_state['generated_text'], profile.display_name)
                st.download_button(
                    label="📕 Download as PDF (.pdf)",
                    data=pdf_buffer,
                    file_name=f"remastered_{domain_choice.value}_batch.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as pdf_err:
                st.warning(f"PDF generation failed: {pdf_err}")

else:
    st.info("Please upload one or more `.docx` / `.pdf` manuscript files to proceed.")
