"""
Strategic Technique Categories for Polyhegel

Defines strategic technique categories for technique-guided generation of strategic plans.

Based on common strategic domains:
- Resource Acquisition: Obtaining and optimizing necessary resources
- Strategic Security: Maintaining operational integrity and resilience
- Value Catalysis: Accelerating value creation and stakeholder benefit
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class StrategyDomain(Enum):
    """Strategic domain categories"""

    RESOURCE_ACQUISITION = "resource_acquisition"
    STRATEGIC_SECURITY = "strategic_security"
    VALUE_CATALYSIS = "value_catalysis"


@dataclass
class StrategicTechnique:
    """Represents a strategic technique with metadata"""

    name: str
    description: str
    domain: StrategyDomain
    use_cases: List[str]
    complexity: str  # "low", "medium", "high"
    timeframe: str  # "immediate", "short-term", "long-term"


# Resource Acquisition Techniques
RESOURCE_ACQUISITION_TECHNIQUES = [
    StrategicTechnique(
        name="Stakeholder Alignment Matrix",
        description="Map stakeholder interests to resource needs and create win-win partnerships",
        domain=StrategyDomain.RESOURCE_ACQUISITION,
        use_cases=[
            "Securing funding from multiple investor types",
            "Building coalitions for resource sharing",
            "Aligning diverse organizational priorities",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
    StrategicTechnique(
        name="Incremental Resource Bootstrap",
        description="Start with minimal resources and systematically expand through staged achievements",
        domain=StrategyDomain.RESOURCE_ACQUISITION,
        use_cases=[
            "Bootstrapping with limited initial capital",
            "Building proof-of-concept before major investment",
            "Scaling resource acquisition based on demonstrated value",
        ],
        complexity="low",
        timeframe="immediate",
    ),
    StrategicTechnique(
        name="Multi-Channel Resource Diversification",
        description="Develop multiple independent resource streams to reduce dependency risk",
        domain=StrategyDomain.RESOURCE_ACQUISITION,
        use_cases=[
            "Revenue diversification strategies",
            "Multiple funding source coordination",
            "Resource redundancy for critical operations",
        ],
        complexity="high",
        timeframe="long-term",
    ),
    StrategicTechnique(
        name="Strategic Resource Pooling",
        description="Collaborate with partners to share and optimize resource utilization",
        domain=StrategyDomain.RESOURCE_ACQUISITION,
        use_cases=[
            "Consortium-based resource sharing",
            "Collaborative infrastructure development",
            "Joint procurement and cost reduction",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
    StrategicTechnique(
        name="Value-Based Resource Exchange",
        description="Trade unique capabilities or assets for needed resources rather than cash",
        domain=StrategyDomain.RESOURCE_ACQUISITION,
        use_cases=[
            "Skill-based bartering arrangements",
            "Intellectual property licensing deals",
            "Strategic partnership value exchanges",
        ],
        complexity="medium",
        timeframe="immediate",
    ),
]

# Strategic Security Techniques
STRATEGIC_SECURITY_TECHNIQUES = [
    StrategicTechnique(
        name="Layered Defense Architecture",
        description="Multiple independent security layers to prevent single points of failure",
        domain=StrategyDomain.STRATEGIC_SECURITY,
        use_cases=[
            "Information security frameworks",
            "Supply chain risk mitigation",
            "Operational continuity planning",
        ],
        complexity="high",
        timeframe="long-term",
    ),
    StrategicTechnique(
        name="Transparent Accountability Systems",
        description="Open processes and auditable decision-making to build trust and prevent corruption",
        domain=StrategyDomain.STRATEGIC_SECURITY,
        use_cases=[
            "Governance transparency initiatives",
            "Public audit and oversight mechanisms",
            "Stakeholder accountability frameworks",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
    StrategicTechnique(
        name="Distributed Authority Networks",
        description="Spread decision-making authority to prevent centralized vulnerabilities",
        domain=StrategyDomain.STRATEGIC_SECURITY,
        use_cases=[
            "Decentralized organizational structures",
            "Multi-party consensus mechanisms",
            "Distributed governance models",
        ],
        complexity="high",
        timeframe="long-term",
    ),
    StrategicTechnique(
        name="Adaptive Threat Response",
        description="Dynamic security measures that evolve with changing threat landscapes",
        domain=StrategyDomain.STRATEGIC_SECURITY,
        use_cases=[
            "Cybersecurity threat intelligence",
            "Market competition response systems",
            "Regulatory compliance adaptation",
        ],
        complexity="high",
        timeframe="immediate",
    ),
    StrategicTechnique(
        name="Community-Based Security",
        description="Leverage collective stakeholder interests to create mutual security benefits",
        domain=StrategyDomain.STRATEGIC_SECURITY,
        use_cases=[
            "Industry security standards cooperation",
            "Mutual aid and disaster response",
            "Collective threat intelligence sharing",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
]

# Value Catalysis Techniques
VALUE_CATALYSIS_TECHNIQUES = [
    StrategicTechnique(
        name="Exponential Value Creation",
        description="Design systems where value creation accelerates rather than scales linearly",
        domain=StrategyDomain.VALUE_CATALYSIS,
        use_cases=["Network effect business models", "Compounding knowledge systems", "Viral growth mechanisms"],
        complexity="high",
        timeframe="long-term",
    ),
    StrategicTechnique(
        name="Cross-Pollination Innovation",
        description="Combine insights from different domains to create breakthrough value",
        domain=StrategyDomain.VALUE_CATALYSIS,
        use_cases=[
            "Interdisciplinary research initiatives",
            "Cross-industry solution adaptation",
            "Hybrid technology development",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
    StrategicTechnique(
        name="Stakeholder Value Optimization",
        description="Simultaneously maximize value for all stakeholder groups rather than zero-sum thinking",
        domain=StrategyDomain.VALUE_CATALYSIS,
        use_cases=[
            "Multi-stakeholder platform design",
            "Ecosystem value creation strategies",
            "Collaborative value chain optimization",
        ],
        complexity="high",
        timeframe="long-term",
    ),
    StrategicTechnique(
        name="Iterative Value Discovery",
        description="Use rapid experimentation to discover and capture unexpected value opportunities",
        domain=StrategyDomain.VALUE_CATALYSIS,
        use_cases=[
            "Lean startup methodologies",
            "A/B testing for strategic decisions",
            "Rapid prototyping and validation",
        ],
        complexity="medium",
        timeframe="immediate",
    ),
    StrategicTechnique(
        name="Collective Intelligence Amplification",
        description="Harness and enhance group intelligence to create value beyond individual capabilities",
        domain=StrategyDomain.VALUE_CATALYSIS,
        use_cases=[
            "Crowdsourcing and collective problem-solving",
            "Collaborative knowledge management",
            "Swarm intelligence applications",
        ],
        complexity="medium",
        timeframe="short-term",
    ),
]

# All techniques combined
ALL_TECHNIQUES = RESOURCE_ACQUISITION_TECHNIQUES + STRATEGIC_SECURITY_TECHNIQUES + VALUE_CATALYSIS_TECHNIQUES

# Technique lookup by name
TECHNIQUE_REGISTRY: Dict[str, StrategicTechnique] = {technique.name: technique for technique in ALL_TECHNIQUES}

# Techniques by domain
TECHNIQUES_BY_DOMAIN: Dict[StrategyDomain, List[StrategicTechnique]] = {
    StrategyDomain.RESOURCE_ACQUISITION: RESOURCE_ACQUISITION_TECHNIQUES,
    StrategyDomain.STRATEGIC_SECURITY: STRATEGIC_SECURITY_TECHNIQUES,
    StrategyDomain.VALUE_CATALYSIS: VALUE_CATALYSIS_TECHNIQUES,
}

# Techniques by complexity
TECHNIQUES_BY_COMPLEXITY: Dict[str, List[StrategicTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.complexity == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.complexity == "medium"],
    "high": [t for t in ALL_TECHNIQUES if t.complexity == "high"],
}

# Techniques by timeframe
TECHNIQUES_BY_TIMEFRAME: Dict[str, List[StrategicTechnique]] = {
    "immediate": [t for t in ALL_TECHNIQUES if t.timeframe == "immediate"],
    "short-term": [t for t in ALL_TECHNIQUES if t.timeframe == "short-term"],
    "long-term": [t for t in ALL_TECHNIQUES if t.timeframe == "long-term"],
}


def get_techniques_for_domain(domain: StrategyDomain) -> List[StrategicTechnique]:
    """Get all techniques for a specific strategy domain"""
    return TECHNIQUES_BY_DOMAIN.get(domain, [])


def get_techniques_by_complexity(complexity: str) -> List[StrategicTechnique]:
    """Get techniques filtered by complexity level"""
    return TECHNIQUES_BY_COMPLEXITY.get(complexity, [])


def get_techniques_by_timeframe(timeframe: str) -> List[StrategicTechnique]:
    """Get techniques filtered by timeframe"""
    return TECHNIQUES_BY_TIMEFRAME.get(timeframe, [])


def get_technique_by_name(name: str) -> Optional[StrategicTechnique]:
    """Get a specific technique by name"""
    return TECHNIQUE_REGISTRY.get(name)


def get_recommended_techniques(
    domain: Optional[StrategyDomain] = None,
    complexity: Optional[str] = None,
    timeframe: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[StrategicTechnique]:
    """
    Get recommended techniques based on filtering criteria

    Args:
        domain: Filter by strategy domain (optional)
        complexity: Filter by complexity level (optional)
        timeframe: Filter by timeframe (optional)
        limit: Maximum number of techniques to return (optional)

    Returns:
        List of matching strategic techniques
    """
    techniques = ALL_TECHNIQUES

    if domain:
        techniques = [t for t in techniques if t.domain == domain]

    if complexity:
        techniques = [t for t in techniques if t.complexity == complexity]

    if timeframe:
        techniques = [t for t in techniques if t.timeframe == timeframe]

    if limit:
        techniques = techniques[:limit]

    return techniques


def format_technique_for_prompt(technique: StrategicTechnique) -> str:
    """Format a technique for use in LLM prompts"""
    return f"""**{technique.name}** ({technique.domain.value})
{technique.description}

Use cases:
{chr(10).join(f"- {use_case}" for use_case in technique.use_cases)}

Complexity: {technique.complexity.title()}
Timeframe: {technique.timeframe.title()}"""


def get_techniques_prompt_text(
    domain: Optional[StrategyDomain] = None,
    complexity: Optional[str] = None,
    timeframe: Optional[str] = None,
    limit: int = 3,
) -> str:
    """Generate formatted text of techniques for LLM prompts"""
    techniques = get_recommended_techniques(domain, complexity, timeframe, limit)

    if not techniques:
        return "No techniques match the specified criteria."

    technique_texts = [format_technique_for_prompt(t) for t in techniques]
    return "\n\n".join(technique_texts)
