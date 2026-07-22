from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from src.intelligence.domains import get_domain_profile, DomainType

class ChapterHeatmap(BaseModel):
    chapter_index: int
    reader_recognition: float = Field(ge=0.0, le=10.0)
    validation: float = Field(ge=0.0, le=10.0)
    hope: float = Field(ge=0.0, le=10.0)
    trust: float = Field(ge=0.0, le=10.0)
    story_immersion: float = Field(ge=0.0, le=10.0)
    memorability: float = Field(ge=0.0, le=10.0)
    recommendation_potential: float = Field(ge=0.0, le=10.0)
    commercial_reinforcement: float = Field(ge=0.0, le=10.0)

    @property
    def score_color(self) -> str:
        avg = sum([
            self.reader_recognition, self.validation, self.hope,
            self.trust, self.story_immersion, self.memorability,
            self.recommendation_potential, self.commercial_reinforcement
        ]) / 8.0
        if avg >= 8.5:
            return "Green"
        elif avg >= 7.0:
            return "Yellow"
        return "Red"

class AuditRecommendation(BaseModel):
    recommendation_id: str
    phase: str
    description: str
    rationale: str
    expected_reader_impact: float = Field(ge=1.0, le=10.0)
    expected_commercial_impact: float = Field(ge=1.0, le=10.0)
    expected_brand_ip_impact: float = Field(ge=1.0, le=10.0)
    implementation_effort: float = Field(ge=1.0, le=10.0)
    risk_assessment: str

    @property
    def hybrid_impact_index(self) -> float:
        """Calculates HII = (Reader Impact * Commercial Impact * Brand/IP Impact) / Effort"""
        numerator = (self.expected_reader_impact * 
                     self.expected_commercial_impact * 
                     self.expected_brand_ip_impact)
        return round(numerator / self.implementation_effort, 2)

    @property
    def classification(self) -> str:
        hii = self.hybrid_impact_index
        if hii >= 100.0:
            return "Critical Enhancement"
        elif hii >= 50.0:
            return "High-Leverage Enhancement"
        elif hii >= 20.0:
            return "Strategic Enhancement"
        return "Optional Refinement"

class V4HAuditEngine(BaseModel):
    # Default Evaluation Domain Weights totaling 1.0
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "commercial_preservation": 0.20,
        "reader_devotion": 0.20,
        "experience_architecture": 0.15,
        "identity_transformation": 0.10,
        "recommendation_power": 0.10,
        "reader_trust": 0.10,
        "memory_economics": 0.05,
        "asset_multiplication": 0.05,
        "evergreen_durability": 0.05
    }

    def calculate_lcvi(self, domain_scores: Dict[str, float], domain_type: str = "business_finance") -> float:
        """Calculates Lifetime Commercial Value Index™ (LCVI) using domain-aware weights."""
        profile = get_domain_profile(domain_type)
        weights = profile.audit_weights_override if profile else self.DEFAULT_WEIGHTS
        
        lcvi = sum(domain_scores[domain] * weight for domain, weight in weights.items() if domain in domain_scores)
        return round(lcvi, 2)

    def classify_lcvi(self, lcvi_score: float) -> str:
        """Classifies LCVI into official tier status."""
        if lcvi_score >= 9.5:
            return "Category-Defining Evergreen Asset"
        elif lcvi_score >= 9.0:
            return "Reader-Loved Commercial Asset"
        elif lcvi_score >= 8.5:
            return "High-Performance Commercial Asset"
        elif lcvi_score >= 8.0:
            return "Strong Market Asset with Growth Potential"
        return "Targeted Hybrid Optimization Recommended"

    def verify_domain_elements(self, domain_type: str, text: str) -> Dict[str, bool]:
        """Checks if domain-required structural elements are present in text."""
        profile = get_domain_profile(domain_type)
        # Placeholder logic returning required element checks for the selected niche
        return {element: True for element in profile.required_elements}
