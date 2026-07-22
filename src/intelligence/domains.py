from enum import Enum
from pydantic import BaseModel, Field

class DomainType(str, Enum):
    ACADEMIC = "academic"
    AGROTECH = "agrotech"
    BUSINESS_FINANCE = "business_finance"
    FEEDBACK_PROMPTS = "feedback_prompts"
    FICTION = "fiction"
    HISTORY = "history"
    LEGAL = "legal"
    NON_FICTION = "non_fiction"
    PSYCHOLOGY = "psychology"
    SOCIOLOGY = "sociology"

class DomainProfile(BaseModel):
    display_name: str
    primary_focus: str
    required_elements: list[str] = Field(default_factory=list)

DOMAIN_REGISTRY: dict[DomainType, DomainProfile] = {
    DomainType.ACADEMIC: DomainProfile(
        display_name="Academic Publishing",
        primary_focus="Rigorous methodology, citations, peer review standards, and formal discourse.",
        required_elements=["Abstract", "Literature Review", "Methodology", "References"]
    ),
    DomainType.AGROTECH: DomainProfile(
        display_name="Agrotech Publishing",
        primary_focus="Agricultural technologies, smart farming practices, sustainability, and technical specs.",
        required_elements=["Technical Data", "Case Studies", "Implementation Framework"]
    ),
    DomainType.BUSINESS_FINANCE: DomainProfile(
        display_name="Business & Financial",
        primary_focus="Market analysis, revenue models, executive strategy, and actionable insights.",
        required_elements=["Executive Summary", "Financial Models", "Key Takeaways"]
    ),
    DomainType.FEEDBACK_PROMPTS: DomainProfile(
        display_name="Feedback & Prompt Engineering",
        primary_focus="Prompt evaluation, instruction refinement, model feedback loops, and optimization.",
        required_elements=["Prompt Architecture", "Evaluation Criteria", "Feedback Loops"]
    ),
    DomainType.FICTION: DomainProfile(
        display_name="Fiction Publishing",
        primary_focus="Narrative arc, character development, world-building, and thematic pacing.",
        required_elements=["Character Profiles", "Plot Outline", "Scene Breakdown"]
    ),
    DomainType.HISTORY: DomainProfile(
        display_name="History Manuscript",
        primary_focus="Chronological narrative, primary sources, historical context, and archivist rigor.",
        required_elements=["Timeline", "Primary Sources", "Historical Context"]
    ),
    DomainType.LEGAL: DomainProfile(
        display_name="Legal Manuscript",
        primary_focus="Statutory analysis, case law citations, jurisdictional precision, and legal logic.",
        required_elements=["Statutory References", "Case Law Analysis", "Legal Arguments"]
    ),
    DomainType.NON_FICTION: DomainProfile(
        display_name="Non-Fiction Publishing",
        primary_focus="General audience engagement, clear taxonomy, practical application, and narrative flow.",
        required_elements=["Table of Contents", "Chapter Overviews", "Action Steps"]
    ),
    DomainType.PSYCHOLOGY: DomainProfile(
        display_name="Psychology Manuscript",
        primary_focus="Behavioral analysis, psychological frameworks, evidence-based research, and case examples.",
        required_elements=["Theoretical Framework", "Case Studies", "Empirical Data"]
    ),
    DomainType.SOCIOLOGY: DomainProfile(
        display_name="Sociology Manuscript",
        primary_focus="Social structures, demographic trends, qualitative/quantitative research, and cultural analysis.",
        required_elements=["Demographic Data", "Social Theory", "Field Findings"]
    )
}

def get_domain_profile(domain: DomainType) -> DomainProfile:
    return DOMAIN_REGISTRY.get(domain, DOMAIN_REGISTRY[DomainType.NON_FICTION])
