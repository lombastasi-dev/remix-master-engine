from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, List, Literal

class Manuscript(BaseModel):
    manuscript_id: UUID = Field(default_factory=uuid4)
    user_id: str
    title: str = Field(..., min_length=1, max_length=255)
    current_state: str = Field("Concept")
    raw_sha256: str = Field(..., min_length=64, max_length=64)
    metadata_bible: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ManuscriptChunk(BaseModel):
    chunk_id: UUID = Field(default_factory=uuid4)
    manuscript_id: UUID
    chunk_index: int = Field(..., ge=0)
    raw_text_content: str
    chunk_sha256: str = Field(..., min_length=64, max_length=64)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PlaybookDimension(BaseModel):
    dimension_name: str = Field(..., min_length=1, max_length=100)
    weight_percentage: float = Field(..., ge=0.0, le=1.0)
    evaluation_criteria_prompt: str

class Playbook(BaseModel):
    playbook_id: UUID = Field(default_factory=uuid4)
    niche_domain_name: str
    dimensions: Dict[str, PlaybookDimension]
    is_active_baseline: bool = Field(False)

class Finding(BaseModel):
    finding_id: UUID = Field(default_factory=uuid4)
    report_id: UUID
    chunk_id: UUID
    target_dimension: str
    severity_rating: Literal["Green", "Yellow", "Red"] = Field("Yellow")
    exact_passage_excerpt: str
    diagnostic_critique: str
    proposed_remediation_guideline: str

class AuditReport(BaseModel):
    report_id: UUID = Field(default_factory=uuid4)
    manuscript_id: UUID
    global_lcvi_score: float = Field(..., ge=0.0, le=10.0)
    domain_scores: Dict[str, float]
    executive_summary: str
    prioritized_issues_map: Dict[str, list]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BlueprintNode(BaseModel):
    node_id: UUID = Field(default_factory=uuid4)
    chunk_id: UUID
    chronological_execution_order: int = Field(..., ge=0)
    assigned_action_type: Literal["keep", "revise", "rewrite", "cut"] = Field("keep")
    remediation_instruction_payload: str

class Blueprint(BaseModel):
    blueprint_id: UUID = Field(default_factory=uuid4)
    manuscript_id: UUID
    associated_report_id: UUID
    ordered_nodes: List[BlueprintNode] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RewriteUnit(BaseModel):
    unit_id: UUID = Field(default_factory=uuid4)
    blueprint_id: UUID
    node_id: UUID
    source_chunk_id: UUID
    version_history_array: List[Dict[str, str]] = Field(default_factory=list)
    current_approved_text: str
    differential_patch_data: str
    is_human_signed_off: bool = Field(False)

class GateDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    manuscript_id: UUID
    gate_identifier_code: str
    operator_user_id: str
    action_committed: str
    historical_trail_payload: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
