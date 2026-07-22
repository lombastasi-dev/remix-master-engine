import io
import streamlit as st
import docx
from docx import Document
import pypdf
import google.generativeai as genai
from openai import OpenAI
from fpdf import FPDF
import ebooklib
from ebooklib import epub
from src.intelligence.domains import DomainType, DOMAIN_REGISTRY, get_domain_profile

st.set_page_config(page_title='REMIX-MASTER Control Room', page_icon='📚', layout='wide')

def extract_text_from_file(file):
    text = ''
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'docx':
        doc = docx.Document(file)
        text = '\n'.join([p.text for p in doc.paragraphs if p.text.strip()])
    elif file_type == 'pdf':
        reader = pypdf.PdfReader(file)
        text = '\n'.join([page.extract_text() or '' for page in reader.pages])
    return text

def audit_manuscript(text, required_elements):
    results = {}
    text_lower = text.lower()
    for element in required_elements:
        results[element] = element.lower() in text_lower
    found_count = sum(results.values())
    score = int((found_count / len(required_elements)) * 100) if required_elements else 100
    return results, score

def generate_front_matter(book_title, author_name, publisher_name, domain_name):
    return f'''# {book_title}\n\n**By {author_name}**  \n*Published by {publisher_name}*\n\n---\n\n### Title & Copyright Page\n**{book_title}**  \nCopyright © 2026 by {author_name}. All rights reserved.\n\nNo part of this publication may be reproduced, distributed, or transmitted in any form or by any means without prior written permission of the publisher.\n\n*Category:* {domain_name}  \n*First Edition:* 2026\n\n---\n\n### Preface\nWelcome to **{book_title}**. This work was created to offer practical, structured guidance in {domain_name}. Modern readers digest information in different ways—whether in short visual bursts on a screen, structured study on paper, or dynamic listening on the go. This edition was tailored to respect your time and provide actionable clarity from start to finish.\n'''

def generate_back_matter(author_name, book_title):
    return f'''\n\n---\n\n### About the Author\n**{author_name}** is an author and domain practitioner dedicated to transforming complex ideas into clear, actionable frameworks.\n\n### Reader Call to Action\nThank you for reading **{book_title}**! If you found value in this work, please consider leaving an honest review on Amazon or GoodReads. Your feedback helps other readers discover this book.\n\n### Recommended Next Steps\n* Connect with the author for additional resources and updates.\n* Join the community newsletter for upcoming releases and exclusive bonus materials.\n'''

st.title('📚 REMIX-MASTER: Autonomous Publishing Control Room')
st.caption('One Master Manuscript → Four Distinct Reading Experiences')
st.divider()

st.sidebar.header('🎯 Project Settings')
domain_choice = st.sidebar.selectbox('Select Manuscript Domain / Niche', options=list(DomainType))
profile = get_domain_profile(domain_choice)
st.sidebar.success(f'Active Domain: **{profile.display_name}**')

st.sidebar.divider()
st.sidebar.header('📖 Publishing Metadata')
book_title = st.sidebar.text_input('Book Title', value='The Master Blueprint')
author_name = st.sidebar.text_input('Author Name', value='Alex Vance')
publisher_name = st.sidebar.text_input('Publisher Name', value='Apex Press')

st.subheader('🎯 Active Domain Overview')
st.write(f'**Niche:** {profile.display_name} | **Focus:** {profile.primary_focus}')
st.divider()

uploaded_files = st.file_uploader('Upload manuscript files (.docx or .pdf)', type=['docx', 'pdf'], accept_multiple_files=True)
if uploaded_files:
    combined_text = ''
    for file in uploaded_files:
        combined_text += '\n\n' + extract_text_from_file(file)
    st.success(f'{len(uploaded_files)} file(s) uploaded successfully!')
    
    audit_results, readiness_score = audit_manuscript(combined_text, list(profile.required_elements))
    st.metric(label='Master Readiness Score', value=f'{readiness_score}%')
    
    if st.button('⚡ Generate Full Manuscript with Front & Back Matter'):
        front = generate_front_matter(book_title, author_name, publisher_name, profile.display_name)
        back = generate_back_matter(author_name, book_title)
        st.session_state['generated_text'] = front + '\n\n' + combined_text + '\n\n' + back
    
    if 'generated_text' in st.session_state:
        st.subheader('✨ Final Compiled Manuscript')
        st.markdown(st.session_state['generated_text'][:3000] + '\n\n*(Preview truncated for display...)*')
        st.download_button('💾 Download Full Manuscript (.md)', data=st.session_state['generated_text'], file_name='full_manuscript.md')