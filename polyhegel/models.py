"""
Data models for Polyhegel
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Literal
from enum import Enum
import numpy as np
import networkx as nx
from pydantic import BaseModel, Field, validator


class StrategyStep(BaseModel):
    """Represents a single step in a strategy chain"""
    action: str = Field(description="The specific action to take")
    prerequisites: List[str] = Field(description="Prerequisites that must be met before this action")
    outcome: str = Field(description="Expected outcome of this action")
    risks: List[str] = Field(description="Potential risks or failure modes")
    confidence: float = Field(default=0.8, description="Confidence level in this step (0-1)")


class GenesisStrategy(BaseModel):
    """Complete Genesis strategy output from LLM"""
    title: str = Field(description="Short title for this strategy approach")
    steps: List[StrategyStep] = Field(description="Sequential steps to execute the strategy")
    alignment_score: Dict[str, float] = Field(
        description="How well this aligns with strategic domains and constraints"
    )
    estimated_timeline: str = Field(description="Estimated timeline for execution")
    resource_requirements: List[str] = Field(description="Key resources needed")


class ThemeCategory(str, Enum):
    """Strategic theme categories aligned with strategic domains"""
    RESOURCE_ACQUISITION = "resource_acquisition"
    STRATEGIC_SECURITY = "strategic_security"
    VALUE_CATALYSIS = "value_catalysis"
    CROSS_CUTTING = "cross_cutting"  # Themes that span multiple domains
    FOUNDATIONAL = "foundational"    # Core infrastructure themes


class StrategicTheme(BaseModel):
    """
    High-level strategic theme that leader agents generate
    
    Strategic themes are the conceptual building blocks that leader agents
    identify before follower agents develop them into detailed strategies.
    """
    title: str = Field(
        description="Clear, concise title for the strategic theme",
        min_length=5,
        max_length=100
    )
    
    category: ThemeCategory = Field(
        description="Primary category this theme belongs to"
    )
    
    description: str = Field(
        description="Detailed description of the strategic theme and its purpose",
        min_length=50,
        max_length=500
    )
    
    domain_alignment: Dict[str, float] = Field(
        description="Alignment scores with strategic domains (2.1, 2.2, 2.3) on 1-5 scale",
        default_factory=dict
    )
    
    priority_level: Literal["critical", "high", "medium", "low"] = Field(
        default="medium",
        description="Priority level for theme implementation"
    )
    
    complexity_estimate: Literal["simple", "moderate", "complex", "highly_complex"] = Field(
        default="moderate", 
        description="Estimated complexity of implementing this theme"
    )
    
    key_concepts: List[str] = Field(
        description="Core concepts and keywords associated with this theme",
        max_items=10
    )
    
    success_criteria: List[str] = Field(
        description="High-level success criteria for this theme",
        max_items=5
    )
    
    potential_risks: List[str] = Field(
        description="Major risks or challenges associated with this theme",
        max_items=5,
        default_factory=list
    )
    
    strategic_context: Optional[str] = Field(
        default=None,
        description="Additional context about why this theme is strategically important"
    )
    
    @validator('domain_alignment')
    def validate_domain_alignment(cls, v):
        """Validate Strategic domain alignment scores"""
        valid_domains = {"2.1", "2.2", "2.3"}
        for domain, score in v.items():
            if domain not in valid_domains:
                raise ValueError(f"Invalid strategic domain: {domain}. Must be one of {valid_domains}")
            if not (1.0 <= score <= 5.0):
                raise ValueError(f"Strategic alignment score must be between 1.0 and 5.0, got {score}")
        return v
    
    @validator('key_concepts')
    def validate_key_concepts(cls, v):
        """Validate key concepts are not empty"""
        if not v:
            raise ValueError("At least one key concept is required")
        return [concept.strip() for concept in v if concept.strip()]
    
    @validator('success_criteria')
    def validate_success_criteria(cls, v):
        """Validate success criteria are meaningful"""
        if not v:
            raise ValueError("At least one success criterion is required")
        return [criterion.strip() for criterion in v if criterion.strip()]
    
    def get_primary_domain(self) -> Optional[str]:
        """Get the strategic domain with highest alignment score"""
        if not self.domain_alignment:
            return None
        return max(self.domain_alignment.items(), key=lambda x: x[1])[0]
    
    def is_cross_cutting(self) -> bool:
        """Check if theme spans multiple strategic domains (scores > 3.0 in multiple)"""
        high_scores = [domain for domain, score in self.domain_alignment.items() if score > 3.0]
        return len(high_scores) > 1
    
    def get_alignment_summary(self) -> str:
        """Get human-readable alignment summary"""
        if not self.domain_alignment:
            return "No strategic alignment specified"
        
        domain_names = {
            "2.1": "Resource Acquisition",
            "2.2": "Strategic Security", 
            "2.3": "Value Catalysis"
        }
        
        summaries = []
        for domain, score in self.domain_alignment.items():
            name = domain_names.get(domain, domain)
            summaries.append(f"{name}: {score}/5.0")
        
        return " | ".join(summaries)


@dataclass
class StrategyChain:
    """Internal representation of a strategy chain with metadata"""
    strategy: GenesisStrategy
    source_sample: int
    temperature: float
    embedding: Optional[np.ndarray] = None
    cluster_label: int = -1
    is_trunk: bool = False
    is_twig: bool = False
    graph: Optional[nx.DiGraph] = None
    # Technique-guided generation metadata
    technique_name: Optional[str] = None
    technique_domain: Optional[str] = None


class StrategyEvaluationResponse(BaseModel):
    """Structured response for strategy evaluation and comparison"""
    
    preferred_strategy_index: int = Field(
        description="Index of preferred strategy (1 or 2)",
        ge=1, le=2
    )
    
    confidence_score: float = Field(
        description="Confidence in the evaluation (0.0 to 1.0)",
        ge=0.0, le=1.0
    )
    
    reasoning: str = Field(
        description="Brief explanation of why this strategy was preferred",
        min_length=10, max_length=500
    )
    
    coherence_comparison: Dict[str, float] = Field(
        description="Coherence scores for both strategies (1-10 scale)",
        default_factory=dict
    )
    
    feasibility_comparison: Dict[str, float] = Field(
        description="Feasibility scores for both strategies (1-10 scale)", 
        default_factory=dict
    )
    
    risk_management_comparison: Dict[str, float] = Field(
        description="Risk management scores for both strategies (1-10 scale)",
        default_factory=dict
    )


class StrategyAnalysisResponse(BaseModel):
    """Structured response for single strategy analysis"""
    
    overall_score: float = Field(
        description="Overall strategy effectiveness score (1-10 scale)",
        ge=1.0, le=10.0
    )
    
    coherence_score: float = Field(
        description="Logical flow and consistency score (1-10 scale)",
        ge=1.0, le=10.0
    )
    
    feasibility_score: float = Field(
        description="Implementation feasibility score (1-10 scale)",
        ge=1.0, le=10.0
    )
    
    risk_management_score: float = Field(
        description="Risk identification and mitigation score (1-10 scale)",
        ge=1.0, le=10.0
    )
    
    strategic_alignment_score: float = Field(
        description="Alignment with strategic objectives score (1-10 scale)",
        ge=1.0, le=10.0
    )
    
    strengths: List[str] = Field(
        description="Key strengths of the strategy",
        min_items=1, max_items=5
    )
    
    weaknesses: List[str] = Field(
        description="Key weaknesses or areas for improvement",
        max_items=5, default_factory=list
    )
    
    recommendations: List[str] = Field(
        description="Specific recommendations for improvement",
        max_items=3, default_factory=list
    )