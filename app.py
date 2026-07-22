import io
import re
import json
import zipfile
import asyncio
import streamlit as st
import docx
from docx import Document
import pypdf
import google.generativeai as genai
from openai import OpenAI
from fpdf import FPDF
import ebooklib
from ebooklib import epub
import edge_tts
from PIL import Image, ImageDraw, ImageFont
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

def compute_readability_metrics(text):
    words = re.findall(r'\w+', text)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    word_count = len(words)
    sentence_count = max(1, len(sentences))
    avg_sentence_len = round(word_count / sentence_count, 1)
    est_reading_time_min = max(1, round(word_count / 200))
    return {
        'total_words': word_count,
        'total_sentences': sentence_count,
        'avg_sentence_len': avg_sentence_len,
        'est_reading_time_min': est_reading_time_min
    }

def generate_front_matter(book_title, author_name, publisher_name, domain_name):
    return f'''# {book_title}\n\n**By {author_name}**  \n*Published by {publisher_name}*\n\n---\n\n### Title & Copyright Page\n**{book_title}**  \nCopyright © 2026 by {author_name}. All rights reserved.\n\nNo part of this publication may be reproduced, distributed, or transmitted in any form or by any means without prior written permission of the publisher.\n\n*Category:* {domain_name}  \n*First Edition:* 2026\n\n---\n\n### Preface\nWelcome to **{book_title}**. This work was created to offer practical, structured guidance in {domain_name}. Modern readers digest information in different ways—whether in short visual bursts on a screen, structured study on paper, or dynamic listening on the go. This edition was tailored to respect your time and provide actionable clarity from start to finish.\n'''

def generate_back_matter(author_name, book_title):
    return f'''\n\n---\n\n### About the Author\n**{author_name}** is an author and domain practitioner dedicated to transforming complex ideas into clear, actionable frameworks.\n\n### Reader Call to Action\nThank you for reading **{book_title}**! If you found value in this work, please consider leaving an honest review on Amazon or GoodReads. Your feedback helps other readers discover this book.\n\n### Recommended Next Steps\n* Connect with the author for additional resources and updates.\n* Join the community newsletter for upcoming releases and exclusive bonus materials.\n'''

def split_text_into_chapters(text):
    pattern = r'(?=\n(?=#{1,2}\s))'
    chunks = re.split(pattern, text)
    chapters = [c.strip() for c in chunks if c.strip()]
    return chapters if chapters else [text]

def create_cover_image(title, subtitle, author, domain_name):
    width, height = 800, 1200
    img = Image.new('RGB', (width, height), color='#1a252c')
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, width - 20, height - 20], outline='#2c5282', width=5)
    draw.text((width / 2, 120), domain_name.upper(), fill='#63b3ed', anchor='mm')
    draw.text((width / 2, 350), title, fill='#ffffff', anchor='mm')
    draw.text((width / 2, 450), subtitle, fill='#cbd5e0', anchor='mm')
    draw.line([(150, 700), (650, 700)], fill='#2c5282', width=3)
    draw.text((width / 2, 950), f'BY {author.upper()}', fill='#ffffff', anchor='mm')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def build_zip_package(manuscript_text, metadata_dict, cover_bytes):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('master_manuscript.md', manuscript_text)
        zip_file.writestr('kdp_metadata.json', json.dumps(metadata_dict, indent=2))
        zip_file.writestr('cover_blueprint.png', cover_bytes)
    zip_buffer.seek(0)
    return zip_buffer

async def generate_audio_preview(text_sample, voice='en-US-ChristopherNeural'):
    communicate = edge_tts.Communicate(text_sample, voice)
    audio_data = b''
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            audio_data += chunk['data']
    return audio_data

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
book_subtitle = st.sidebar.text_input('Book Subtitle', value='A Complete Guide to Mastery')
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
        
        st.divider()
        st.subheader('📊 Interactive Quality & Readability Review')
        read_metrics = compute_readability_metrics(st.session_state['generated_text'])
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric('Total Word Count', f"{read_metrics['total_words']:,}")
        with m2:
            st.metric('Sentence Count', f"{read_metrics['total_sentences']:,}")
        with m3:
            st.metric('Avg Sentence Length', f"{read_metrics['avg_sentence_len']} words")
        with m4:
            st.metric('Est. Reading Time', f"~{read_metrics['est_reading_time_min']} mins")
            
        if st.button('🔍 Run AI Editorial Compliance Audit'):
            with st.spinner('Performing deep editorial audit...'):
                eval_prompt = f'''Act as a senior publisher in {profile.display_name}. Audit this excerpt against the {target_tone} tone and provide 3 key strengths, 3 recommendations for polish, and a publication recommendation.\n\nExcerpt:\n{st.session_state['generated_text'][:3000]}'''
                audit_report, _ = generate_adaptation_with_fallback(eval_prompt)
                st.markdown(audit_report)
        
        st.divider()
        st.subheader('🎨 Cover Blueprint & KDP Metadata Package')
        col_cov1, col_cov2 = st.columns([1, 2])
        cover_buf = create_cover_image(book_title, book_subtitle, author_name, profile.display_name)
        metadata_pkg = {
            'title': book_title,
            'subtitle': book_subtitle,
            'author': author_name,
            'publisher': publisher_name,
            'domain_niche': profile.display_name,
            'primary_focus': profile.primary_focus,
            'target_tone': target_tone,
            'suggested_keywords': [profile.display_name, 'Guide', 'Handbook', 'Mastery', 'Strategy'],
            'language': 'English'
        }
        
        with col_cov1:
            st.image(cover_buf, caption='Generated Front Cover Blueprint', use_container_width=True)
        with col_cov2:
            st.json(metadata_pkg)
        
        st.divider()
        st.subheader('📦 Download Publishing Bundle')
        zip_buf = build_zip_package(st.session_state['generated_text'], metadata_pkg, cover_buf.getvalue())
        st.download_button('📦 Download Complete Publishing Bundle (.zip)', data=zip_buf.getvalue(), file_name='publishing_package.zip', mime='application/zip', type='primary')
        
        st.divider()
        st.subheader('🎙️ Audiobook Sample Preview (TTS)')
        voice_option = st.selectbox('Select Narrator Voice', ['en-US-ChristopherNeural', 'en-US-JennyNeural', 'en-GB-SoniaNeural', 'en-AU-WilliamNeural'])
        clean_sample = re.sub(r'[#\*\-_]', '', st.session_state['generated_text'][:500])
        if st.button('🎧 Generate & Play Audio Sample'):
            with st.spinner('Synthesizing speech sample...'):
                try:
                    audio_bytes = asyncio.run(generate_audio_preview(clean_sample, voice=voice_option))
                    st.audio(audio_bytes, format='audio/mp3')
                    st.success('✓ Audio preview ready!')
                except Exception as tts_err:
                    st.error(f'Audio generation failed: {tts_err}')