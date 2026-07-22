import re
import difflib
from uuid import uuid4
import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from src.models.schemas import Blueprint, BlueprintNode, RewriteUnit, ManuscriptChunk, Finding

def generate_blueprint_from_findings(manuscript_id, report_id, chunks: list[ManuscriptChunk], findings: list[Finding]) -> Blueprint:
    # Group findings by chunk_id
    findings_by_chunk = {}
    for f in findings:
        findings_by_chunk.setdefault(f.chunk_id, []).append(f)
        
    ordered_nodes = []
    for idx, chunk in enumerate(chunks):
        chunk_findings = findings_by_chunk.get(chunk.chunk_id, [])
        
        # Determine node action type
        if not chunk_findings:
            action_type = "keep"
            remediation_payload = "No operational defects found. Retain original chunk."
        else:
            has_red = any(f.severity_rating == "Red" for f in chunk_findings)
            action_type = "rewrite" if has_red else "revise"
            remediation_payload = " | ".join([f.proposed_remediation_guideline for f in chunk_findings])
            
        ordered_nodes.append(
            BlueprintNode(
                node_id=uuid4(),
                chunk_id=chunk.chunk_id,
                chronological_execution_order=idx,
                assigned_action_type=action_type,
                remediation_instruction_payload=remediation_payload
            )
        )
        
    return Blueprint(
        blueprint_id=uuid4(),
        manuscript_id=manuscript_id,
        associated_report_id=report_id,
        ordered_nodes=ordered_nodes
    )

def compute_git_diff(original_text: str, revised_text: str) -> str:
    diff = difflib.unified_diff(
        original_text.splitlines(keepends=True),
        revised_text.splitlines(keepends=True),
        fromfile='original',
        tofile='revised'
    )
    return "".join(diff)

def generate_rewrite_unit(blueprint_id, node: BlueprintNode, chunk: ManuscriptChunk, target_tone: str) -> RewriteUnit:
    if node.assigned_action_type == "keep":
        return RewriteUnit(
            blueprint_id=blueprint_id,
            node_id=node.node_id,
            source_chunk_id=chunk.chunk_id,
            version_history_array=[{"v1_original": chunk.raw_text_content}],
            current_approved_text=chunk.raw_text_content,
            differential_patch_data="",
            is_human_signed_off=True
        )
        
    prompt = f"""You are an expert editorial writer. Revise the following text according to these guidelines:
Guidance: {node.remediation_instruction_payload}
Target Tone: {target_tone}

Original Text:
{chunk.raw_text_content}

Return ONLY the revised text string without explanation.
"""
    
    revised_text = chunk.raw_text_content
    openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    
    if openrouter_key:
        try:
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key)
            res = client.chat.completions.create(model="openrouter/free", messages=[{"role": "user", "content": prompt}])
            revised_text = res.choices[0].message.content.strip()
        except Exception:
            pass
    elif gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            res = model.generate_content(prompt)
            revised_text = res.text.strip()
        except Exception:
            pass
            
    patch_diff = compute_git_diff(chunk.raw_text_content, revised_text)
    
    return RewriteUnit(
        blueprint_id=blueprint_id,
        node_id=node.node_id,
        source_chunk_id=chunk.chunk_id,
        version_history_array=[
            {"version": "1", "type": "ai_draft", "content": revised_text}
        ],
        current_approved_text=revised_text,
        differential_patch_data=patch_diff,
        is_human_signed_off=False
    )
