import logging
from typing import List
from uuid import uuid4
from src.models.schemas import AuditReport, Blueprint, BlueprintNode, Finding

logger = logging.getLogger("BlueprintEngine")

def map_finding_to_action(finding: Finding) -> str:
    """Routes finding severity/target_dimension to a blueprint action type."""
    dimension = getattr(finding, "target_dimension", "").lower()
    severity = getattr(finding, "severity", "").lower()
    critique = getattr(finding, "diagnostic_critique", "").lower()
    
    if severity == "high" or "structure" in dimension:
        return "rewrite"
    elif "brevity" in dimension or "wordy" in critique:
        return "condense"
    elif "clarity" in dimension or "expand" in critique:
        return "expand"
    else:
        return "revise"

def generate_transformation_blueprint(audit_report: AuditReport) -> Blueprint:
    """
    Parses an AuditReport and constructs an ordered execution Blueprint 
    mapping chunk-level issues to targeted rewrite actions.
    """
    blueprint_id = uuid4()
    ordered_nodes: List[BlueprintNode] = []
    
    # Collect findings across prioritized map categories
    all_findings: List[Finding] = []
    for severity_key, findings_list in audit_report.prioritized_issues_map.items():
        if isinstance(findings_list, list):
            all_findings.extend(findings_list)
            
    # Sort findings by chunk_id to maintain deterministic ordering
    all_findings.sort(key=lambda f: str(f.chunk_id))
    
    for idx, finding in enumerate(all_findings):
        action_type = map_finding_to_action(finding)
        
        node = BlueprintNode(
            node_id=uuid4(),
            blueprint_id=blueprint_id,
            chunk_id=finding.chunk_id,
            chronological_execution_order=idx + 1,
            assigned_action_type=action_type,
            remediation_instruction_payload=f"[{action_type.upper()}] {finding.diagnostic_critique} Guideline: {finding.proposed_remediation_guideline}"
        )
        ordered_nodes.append(node)
        
    blueprint = Blueprint(
        blueprint_id=blueprint_id,
        manuscript_id=audit_report.manuscript_id,
        associated_report_id=audit_report.report_id,
        ordered_nodes=ordered_nodes
    )
    
    logger.info(f"Generated Blueprint {blueprint_id} with {len(ordered_nodes)} execution nodes.")
    return blueprint
