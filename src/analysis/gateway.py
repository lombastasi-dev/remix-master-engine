import json
import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from src.analysis.local_rules import run_local_syntax_audit
from src.models.schemas import ManuscriptChunk, Finding

def execute_chunk_diagnostic(chunk: ManuscriptChunk, report_id, dimension_prompt: str) -> tuple[list[Finding], str]:
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    
    prompt = f"""Act as a publishing editor. Analyze this text chunk against the following criteria:
{dimension_prompt}

Chunk Content:
{chunk.raw_text_content}

If issues exist, return a valid JSON list of objects with fields:
- target_dimension (str)
- severity_rating ("Green", "Yellow", "Red")
- exact_passage_excerpt (str)
- diagnostic_critique (str)
- proposed_remediation_guideline (str)

If clean, return an empty array [].
Respond ONLY with raw valid JSON.
"""

    # Primary: OpenRouter
    if openrouter_key:
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
            res = client.chat.completions.create(model="openrouter/free", messages=[{"role": "user", "content": prompt}])
            data = json.loads(res.choices[0].message.content)
            findings = [Finding(report_id=report_id, chunk_id=chunk.chunk_id, **item) for item in data]
            return findings, "OpenRouter Gateway"
        except Exception:
            pass

    # Secondary Fallback: Gemini API
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            res = model.generate_content(prompt)
            clean_json = re.sub(r'```json|```', '', res.text).strip()
            data = json.loads(clean_json)
            findings = [Finding(report_id=report_id, chunk_id=chunk.chunk_id, **item) for item in data]
            return findings, "Google Gemini Fallback"
        except Exception:
            pass

    # Local Rule-Based Fallback Engine
    local_findings = run_local_syntax_audit(chunk, report_id)
    return local_findings, "Local Syntax Rules (Offline Fallback)"
