"""
Data models for Polyhegel
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np
import networkx as nx
from pydantic import BaseModel, Field


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