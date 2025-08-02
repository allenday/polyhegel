"""
Common Cross-Domain Techniques for Polyhegel

This module provides broadly applicable analytical techniques that work across
multiple domains (strategic, technical, product, etc.) providing immediate value
while maintaining extensibility for domain-specific implementations.

Available techniques:
- Stakeholder Analysis: Identify and analyze stakeholders across any domain
- SWOT Analysis: Strengths, weaknesses, opportunities, threats analysis
- Trade-off Analysis: Systematic evaluation of competing options
- Risk Assessment: Identify and evaluate risks across domains
- Consensus Building: Multi-party agreement and alignment techniques
- Scenario Planning: Explore multiple future scenarios and outcomes
"""

from .techniques import (
    # Core technique classes and enums
    CommonTechnique,
    TechniqueType,
    TechniqueComplexity,
    TechniqueTimeframe,
    StakeholderAnalysisTechnique,
    SWOTAnalysisTechnique,
    TradeoffAnalysisTechnique,
    RiskAssessmentTechnique,
    ConsensusBuildingTechnique,
    ScenarioPlanningTechnique,
    # Technique registry
    ALL_COMMON_TECHNIQUES,
    ALL_TECHNIQUES,  # Alias for compatibility
    COMMON_TECHNIQUE_REGISTRY,
    TECHNIQUE_REGISTRY,  # Alias for compatibility
    get_common_technique,
    get_common_techniques_by_type,
)

__all__ = [
    "CommonTechnique",
    "TechniqueType",
    "TechniqueComplexity",
    "TechniqueTimeframe",
    "StakeholderAnalysisTechnique",
    "SWOTAnalysisTechnique",
    "TradeoffAnalysisTechnique",
    "RiskAssessmentTechnique",
    "ConsensusBuildingTechnique",
    "ScenarioPlanningTechnique",
    "ALL_COMMON_TECHNIQUES",
    "ALL_TECHNIQUES",  # Alias for compatibility
    "COMMON_TECHNIQUE_REGISTRY",
    "TECHNIQUE_REGISTRY",  # Alias for compatibility
    "get_common_technique",
    "get_common_techniques_by_type",
]
