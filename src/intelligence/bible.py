from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import re

class FrameworkEntity(BaseModel):
    name: str
    description: str
    domain_relevance: str

class TerminologyEntry(BaseModel):
    term: str
    definition: str
    niche_context: str

class IdentityTransformationMap(BaseModel):
    before_state: str
    after_state: str
    key_catalyst: str

class ManuscriptBible(BaseModel):
    domain: str
    title: str
    core_frameworks: List[FrameworkEntity] = Field(default_factory=list)
    glossary: List[TerminologyEntry] = Field(default_factory=list)
    identity_map: Optional[IdentityTransformationMap] = None
    key_entities_or_case_studies: List[str] = Field(default_factory=list)
    chapter_beats: Dict[int, str] = Field(default_factory=dict)

class BibleGenerator:
    """
    Extracts and manages domain-aware Bible metadata from manuscript text.
    """

    def generate_bible_from_text(self, text: str, domain: str, title: str) -> ManuscriptBible:
        bible = ManuscriptBible(domain=domain, title=title)
        
        # 1. Extract Glossaries/Terminology (Naive extraction pattern for key terms)
        term_matches = re.findall(r'(?i)([A-Z][a-zA-Z\s]{2,20})\s*:\s*([^.\n]+)', text)
        for term, desc in term_matches[:5]:
            bible.glossary.append(
                TerminologyEntry(
                    term=term.strip(),
                    definition=desc.strip(),
                    niche_context=domain
                )
            )

        # 2. Extract Frameworks (Looks for terms like "Model", "Framework", "System")
        framework_matches = re.findall(r'(?i)([A-Z][a-zA-Z0-9\s]+(?:Framework|Model|System|Matrix|Engine))', text)
        for fw in list(set(framework_matches))[:3]:
            bible.core_frameworks.append(
                FrameworkEntity(
                    name=fw.strip(),
                    description=f"Core proprietary asset extracted for {title}.",
                    domain_relevance=domain
                )
            )

        # 3. Handle Domain-Specific Behavioral Extraction
        if domain == "psychology":
            bible.identity_map = IdentityTransformationMap(
                before_state="Unconscious habit repetition / reactive mindset",
                after_state="Autonomous self-mastery and intentional agency",
                key_catalyst="Cognitive reframing and identity shifts"
            )

        # 4. Extract Case Studies / Entity Anchors
        case_matches = re.findall(r'(?i)(?:case study|example|instance):\s*([^.\n]+)', text)
        for cs in case_matches[:3]:
            bible.key_entities_or_case_studies.append(cs.strip())

        return bible
