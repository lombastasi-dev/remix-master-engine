import re
from src.models.schemas import Finding, ManuscriptChunk

def run_local_syntax_audit(chunk: ManuscriptChunk, report_id) -> list[Finding]:
    findings = []
    text = chunk.raw_text_content
    
    # Example Rule 1: Passive voice check
    passive_matches = re.findall(r'\b(?:am|is|are|was|were|be|been|being)\s+\w+ed\b', text, re.I)
    if len(passive_matches) > 3:
        findings.append(Finding(
            report_id=report_id,
            chunk_id=chunk.chunk_id,
            target_dimension="Readability & Tone",
            severity_rating="Yellow",
            exact_passage_excerpt=passive_matches[0],
            diagnostic_critique="High density of passive voice constructs detected.",
            proposed_remediation_guideline="Convert passive constructs into active, direct statements."
        ))
        
    # Example Rule 2: Overly long sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    for s in sentences:
        if len(s.split()) > 35:
            findings.append(Finding(
                report_id=report_id,
                chunk_id=chunk.chunk_id,
                target_dimension="Pacing & Flow",
                severity_rating="Red",
                exact_passage_excerpt=s[:60] + "...",
                diagnostic_critique="Sentence length exceeds 35-word threshold, impacting readability.",
                proposed_remediation_guideline="Split this sentence into two concise clauses."
            ))
            
    return findings
