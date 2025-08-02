"""
Strategic techniques and domain classification for Polyhegel framework.

This module provides enum-based domain classification for strategic operations.
"""

from enum import Enum, auto
from typing import List, Optional
from dataclasses import dataclass


class StrategyDomain(Enum):
    """
    Enumeration of strategic domains for specialized agent configurations.
    """

    RESOURCE_ACQUISITION = auto()
    STRATEGIC_SECURITY = auto()
    VALUE_CATALYSIS = auto()
    GENERAL = auto()
    BUSINESS = auto()
    TECHNOLOGY = auto()
    COMPETITIVE_ANALYSIS = auto()
    MARKET_ENTRY = auto()

    def __str__(self):
        return self.name.lower()


@dataclass
class StrategicTechnique:
    """Represents a strategic planning technique"""

    name: str
    domain: StrategyDomain
    description: str
    complexity: str = "medium"
    timeframe: str = "medium"
    prerequisites: List[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


# Technique registry
ALL_TECHNIQUES = [
    StrategicTechnique("systems_thinking", StrategyDomain.GENERAL, "Holistic approach to complex problems"),
    StrategicTechnique("scenario_planning", StrategyDomain.GENERAL, "Planning for multiple future scenarios"),
    StrategicTechnique("risk_assessment", StrategyDomain.GENERAL, "Systematic risk identification and analysis"),
    StrategicTechnique(
        "swot_analysis", StrategyDomain.BUSINESS, "Strengths, Weaknesses, Opportunities, Threats analysis"
    ),
    StrategicTechnique("market_research", StrategyDomain.BUSINESS, "Market analysis and customer research"),
    StrategicTechnique("value_proposition", StrategyDomain.BUSINESS, "Defining unique value offerings"),
    StrategicTechnique("technology_roadmap", StrategyDomain.TECHNOLOGY, "Strategic technology planning"),
    StrategicTechnique("architecture_design", StrategyDomain.TECHNOLOGY, "System architecture planning"),
    StrategicTechnique("testing_strategy", StrategyDomain.TECHNOLOGY, "Comprehensive testing approach"),
    StrategicTechnique(
        "resource_optimization", StrategyDomain.RESOURCE_ACQUISITION, "Optimal resource allocation strategies"
    ),
    StrategicTechnique(
        "stakeholder_mapping", StrategyDomain.RESOURCE_ACQUISITION, "Identifying key resource stakeholders"
    ),
]

TECHNIQUE_REGISTRY = {tech.name: tech for tech in ALL_TECHNIQUES}

# Domain-specific technique collections
RESOURCE_ACQUISITION_TECHNIQUES = [
    tech for tech in ALL_TECHNIQUES if tech.domain == StrategyDomain.RESOURCE_ACQUISITION
]

# Placeholder for compatibility
strategic_techniques = {
    "general": ["systems_thinking", "scenario_planning", "risk_assessment"],
    "business": ["swot_analysis", "market_research", "value_proposition"],
    "technology": ["technology_roadmap", "architecture_design", "testing_strategy"],
}


def get_techniques_for_domain(domain: StrategyDomain) -> List[StrategicTechnique]:
    """Get all techniques for a specific domain"""
    return [tech for tech in ALL_TECHNIQUES if tech.domain == domain]


def get_techniques_by_complexity(complexity: str) -> List[StrategicTechnique]:
    """Get techniques by complexity level"""
    return [tech for tech in ALL_TECHNIQUES if tech.complexity == complexity]


def get_techniques_by_timeframe(timeframe: str) -> List[StrategicTechnique]:
    """Get techniques by timeframe"""
    return [tech for tech in ALL_TECHNIQUES if tech.timeframe == timeframe]


def get_technique_by_name(name: str) -> Optional[StrategicTechnique]:
    """Get a technique by name"""
    return TECHNIQUE_REGISTRY.get(name)


def get_recommended_techniques(domain: StrategyDomain, complexity: str = None) -> List[StrategicTechnique]:
    """Get recommended techniques for domain and complexity"""
    techniques = get_techniques_for_domain(domain)
    if complexity:
        techniques = [tech for tech in techniques if tech.complexity == complexity]
    return techniques


def get_techniques_prompt_text(techniques: List[StrategicTechnique]) -> str:
    """Generate prompt text for techniques"""
    lines = ["Available strategic techniques:"]
    for tech in techniques:
        lines.append(f"- {tech.name}: {tech.description}")
    return "\n".join(lines)


def format_technique_for_prompt(technique: StrategicTechnique) -> str:
    """Format a single technique for prompt inclusion"""
    return f"{technique.name}: {technique.description} (Domain: {technique.domain.name.lower()}, Complexity: {technique.complexity})"


__all__ = [
    "StrategyDomain",
    "StrategicTechnique",
    "ALL_TECHNIQUES",
    "TECHNIQUE_REGISTRY",
    "RESOURCE_ACQUISITION_TECHNIQUES",
    "strategic_techniques",
    "get_techniques_for_domain",
    "get_techniques_by_complexity",
    "get_techniques_by_timeframe",
    "get_technique_by_name",
    "get_recommended_techniques",
    "get_techniques_prompt_text",
    "format_technique_for_prompt",
]
