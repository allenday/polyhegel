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
        description="How well this aligns with strategic mandates and constraints"
    )
    estimated_timeline: str = Field(description="Estimated timeline for execution")
    resource_requirements: List[str] = Field(description="Key resources needed")


class ThemeCategory(str, Enum):
    """Strategic theme categories aligned with Strategic mandates"""
    RESOURCE_ACQUISITION = "resource_acquisition"
    STRATEGIC_SECURITY = "strategic_security"
    VALUE_CATALYSIS = "value_catalysis"
    CROSS_CUTTING = "cross_cutting"  # Themes that span multiple mandates
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
    
    clm_alignment: Dict[str, float] = Field(
        description="Alignment scores with Strategic mandates (2.1, 2.2, 2.3) on 1-5 scale",
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
    
    @validator('clm_alignment')
    def validate_clm_alignment(cls, v):
        """Validate Strategic alignment scores"""
        valid_mandates = {"2.1", "2.2", "2.3"}
        for mandate, score in v.items():
            if mandate not in valid_mandates:
                raise ValueError(f"Invalid Strategic mandate: {mandate}. Must be one of {valid_mandates}")
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
    
    def get_primary_mandate(self) -> Optional[str]:
        """Get the Strategic mandate with highest alignment score"""
        if not self.clm_alignment:
            return None
        return max(self.clm_alignment.items(), key=lambda x: x[1])[0]
    
    def is_cross_cutting(self) -> bool:
        """Check if theme spans multiple Strategic mandates (scores > 3.0 in multiple)"""
        high_scores = [mandate for mandate, score in self.clm_alignment.items() if score > 3.0]
        return len(high_scores) > 1
    
    def get_alignment_summary(self) -> str:
        """Get human-readable alignment summary"""
        if not self.clm_alignment:
            return "No Strategic alignment specified"
        
        mandate_names = {
            "2.1": "Resource Acquisition",
            "2.2": "Strategic Security", 
            "2.3": "Value Catalysis"
        }
        
        summaries = []
        for mandate, score in self.clm_alignment.items():
            name = mandate_names.get(mandate, mandate)
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
    technique_mandate: Optional[str] = None