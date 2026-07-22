from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class DomainType(str, Enum):
    BUSINESS_FINANCE = "business_finance"
    PSYCHOLOGY = "psychology"
    ENGINEERING_TECH = "engineering_tech"
    HISTORY_HUMANITIES = "history_humanities"
    GENERAL_NONFICTION = "general_nonfiction"

class DomainProfile(BaseModel):
    domain: DomainType
    display_name: str
    primary_focus: str
    audit_weights_override: Dict[str, float]
    required_elements: List[str]
    formatting_rules: Dict[str, str]

# Registry of domain configurations
DOMAIN_REGISTRY: Dict[DomainType, DomainProfile] = {
    DomainType.BUSINESS_FINANCE: DomainProfile(
        domain=DomainType.BUSINESS_FINANCE,
        display_name="Business & Finance",
        primary_focus="Commercial value, proprietary frameworks, actionable ROI, and scale.",
        audit_weights_override={
            "commercial_preservation": 0.25,
            "asset_multiplication": 0.15,
            "recommendation_power": 0.15,
            "reader_trust": 0.15,
            "reader_devotion": 0.10,
            "experience_architecture": 0.10,
            "identity_transformation": 0.05,
            "memory_economics": 0.025,
            "evergreen_durability": 0.025
        },
        required_elements=[
            "Proprietary Framework / Named Model",
            "Real-World Case Study or Data Point",
            "Actionable Strategic Takeaway",
            "Companion Tool / Worksheet / Calculator Potential"
        ],
        formatting_rules={
            "kindle": "Use bold framework key points and short callout summaries.",
            "paperback": "Include visual diagram place-holders and structured worksheets.",
            "audiobook": "Explain figures and tables naturally in prose without citing visual page numbers."
        }
    ),
    DomainType.PSYCHOLOGY: DomainProfile(
        domain=DomainType.PSYCHOLOGY,
        display_name="Psychology & Self-Mastery",
        primary_focus="Identity shift, emotional resonance, behavioral change, and deep trust.",
        audit_weights_override={
            "identity_transformation": 0.25,
            "reader_devotion": 0.25,
            "reader_trust": 0.15,
            "experience_architecture": 0.15,
            "recommendation_power": 0.10,
            "commercial_preservation": 0.05,
            "memory_economics": 0.025,
            "asset_multiplication": 0.0125,
            "evergreen_durability": 0.0125
        },
        required_elements=[
            "Recognition Moment ('That's me')",
            "Validation & Empathy Framing",
            "Identity Before vs. After Mapping",
            "Behavioral Reflection Question or Prompt"
        ],
        formatting_rules={
            "kindle": "Emphasize single-sentence impactful hooks and generous line breaks.",
            "paperback": "Integrate reflection spaces and journal prompts.",
            "audiobook": "Use intimate, conversational cadence ('Let's pause and reflect...')."
        }
    ),
    DomainType.ENGINEERING_TECH: DomainProfile(
        domain=DomainType.ENGINEERING_TECH,
        display_name="Engineering & Technical",
        primary_focus="Technical precision, logical hierarchy, mathematical rigor, and systematic clarity.",
        audit_weights_override={
            "reader_trust": 0.30,
            "experience_architecture": 0.20,
            "memory_economics": 0.15,
            "evergreen_durability": 0.15,
            "commercial_preservation": 0.10,
            "reader_devotion": 0.05,
            "recommendation_power": 0.025,
            "identity_transformation": 0.0125,
            "asset_multiplication": 0.0125
        },
        required_elements=[
            "Step-by-Step Problem Architecture",
            "Verifiable Technical/Mathematical Claim",
            "Clear Terminology Definition",
            "System / Process Diagram Reference"
        ],
        formatting_rules={
            "kindle": "Keep inline math and code snippets concise and scannable.",
            "paperback": "Preserve precise typography for formulas and technical tables.",
            "audiobook": "Translate formulas and complex code into intuitive verbal analogies."
        }
    ),
    DomainType.HISTORY_HUMANITIES: DomainProfile(
        domain=DomainType.HISTORY_HUMANITIES,
        display_name="History & Humanities",
        primary_focus="Narrative immersion, contextual depth, historical accuracy, and lasting recall.",
        audit_weights_override={
            "experience_architecture": 0.25,
            "memory_economics": 0.20,
            "evergreen_durability": 0.20,
            "reader_devotion": 0.15,
            "reader_trust": 0.10,
            "recommendation_power": 0.05,
            "commercial_preservation": 0.025,
            "identity_transformation": 0.0125,
            "asset_multiplication": 0.0125
        },
        required_elements=[
            "Contextual Scene Setting",
            "Primary/Secondary Source Anchor",
            "Thematic Synthesis / Broader Lesson",
            "Narrative Tension / Arc"
        ],
        formatting_rules={
            "kindle": "Maintain clean chapter transitions and narrative momentum.",
            "paperback": "Allow rich, immersive paragraph blocks.",
            "audiobook": "Adopt rhythmic, storytelling narration pacing."
        }
    )
}

def get_domain_profile(domain: str) -> DomainProfile:
    """Retrieves domain profile or defaults to General Non-Fiction."""
    try:
        return DOMAIN_REGISTRY[DomainType(domain.lower())]
    except (KeyError, ValueError):
        # Fallback to general non-fiction weights
        return DOMAIN_REGISTRY[DomainType.BUSINESS_FINANCE]
        
