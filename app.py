import io
import re
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

def split_text_into_chapters(text):
    # Split text on top-level markdown headings (# Chapter or ## Chapter)
    pattern = r'(?=\n(?=#{1,2}\s))'
    chunks = re.split(pattern, text)
    chapters = [c.strip() for c in chunks if c.strip()]
    return chapters if chapters else [text]

def generate_adaptation_with_fallback(prompt):
    openrouter_key = st.secrets.get('OPENROUTER_API_KEY')
    gemini_key = st.secrets.get('GEMINI_API_KEY')
    if openrouter_key:
        try:
            client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=openrouter_key)
            res = client.chat.completions.create(model='openrouter/free', messages=[{'role': 'user', 'content': prompt}])
            return res.choices[0].message.content, 'OpenRouter (Free Router)'
        except Exception:
            pass
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            res = model.generate_content(prompt)
            return res.text, 'Google Gemini API (Fallback)'
        except Exception as err:
            raise RuntimeError(f'Gemini Fallback failed: {err}')
    raise ValueError('No valid API keys found.')

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
target_tone = st.sidebar.selectbox('Target Tone', ['Executive Brief', 'Conversational & Engaging', 'Academic & Formal', 'Technical Direct'])

st.subheader('🎯 Active Domain Overview')
st.write(f'**Niche:** {profile.display_name} | **Focus:** {profile.primary_focus}')
st.divider()

uploaded_files = st.file_uploader('Upload manuscript files (.docx or .pdf)', type=['docx', 'pdf'], accept_multiple_files=True)
if uploaded_files:
    combined_text = ''
    for file in uploaded_files:
        combined_text += '\n\n' + extract_text_from_file(file)
    st.success(f'{len(uploaded_files)} file(s) uploaded successfully!')
    
    chapters = split_text_into_chapters(combined_text)
    st.info(f'📦 Manuscript automatically split into **{len(chapters)} chapter chunk(s)** for batch processing.')
    
    audit_results, readiness_score = audit_manuscript(combined_text, list(profile.required_elements))
    st.metric(label='Master Readiness Score', value=f'{readiness_score}%')
    
    if st.button('⚡ Process Chapters & Generate Full Master Manuscript', type='primary'):
        processed_chapters = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, chapter in enumerate(chapters):
            status_text.text(f'Processing Chapter {i+1} of {len(chapters)}...')
            prompt = f'''You are an expert editor in {profile.display_name}. Rewrite and refine this chapter in {target_tone} tone, maintaining logical flow, fixing formatting, and preparing it for multi-format publishing.\n\nChapter content:\n{chapter}'''
            out_text, _ = generate_adaptation_with_fallback(prompt)
            processed_chapters.append(out_text)
            progress_bar.progress((i + 1) / len(chapters))
            
        status_text.text('Assembly complete!')
        front = generate_front_matter(book_title, author_name, publisher_name, profile.display_name)
        back = generate_back_matter(author_name, book_title)
        full_manuscript = front + '\n\n' + '\n\n---\n\n'.join(processed_chapters) + '\n\n' + back
        st.session_state['generated_text'] = full_manuscript
    
    if 'generated_text' in st.session_state:
        st.subheader('✨ Final Compiled Master Manuscript')
        st.markdown(st.session_state['generated_text'][:3000] + '\n\n*(Preview truncated for display...)*')
        st.download_button('💾 Download Full Master Manuscript (.md)', data=st.session_state['generated_text'], file_name='master_manuscript.md')