"""
Strategic Technique Categories for Polyhegel

Defines strategic technique categories aligned with CLM (Collaborative Leadership Model) mandates
for technique-guided generation of strategic plans.

Based on CLM framework:
- 2.1 Resource Acquisition
- 2.2 Strategic Security  
- 2.3 Value Catalysis
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class CLMMandate(Enum):
    """CLM mandate categories"""
    RESOURCE_ACQUISITION = "2.1"
    STRATEGIC_SECURITY = "2.2"  
    VALUE_CATALYSIS = "2.3"


@dataclass
class StrategicTechnique:
    """Represents a strategic technique with metadata"""
    name: str
    description: str
    mandate: CLMMandate
    use_cases: List[str]
    complexity: str  # "low", "medium", "high"
    timeframe: str   # "immediate", "short-term", "long-term"


# Resource Acquisition Techniques (CLM 2.1)
RESOURCE_ACQUISITION_TECHNIQUES = [
    StrategicTechnique(
        name="Stakeholder Alignment Matrix",
        description="Map stakeholder interests to resource needs and create win-win partnerships",
        mandate=CLMMandate.RESOURCE_ACQUISITION,
        use_cases=[
            "Securing funding from multiple investor types",
            "Building coalitions for resource sharing",
            "Aligning diverse organizational priorities"
        ],
        complexity="medium",
        timeframe="short-term"
    ),
    StrategicTechnique(
        name="Incremental Resource Bootstrap",
        description="Start with minimal resources and systematically expand through staged achievements",
        mandate=CLMMandate.RESOURCE_ACQUISITION,
        use_cases=[
            "Bootstrapping with limited initial capital",
            "Building proof-of-concept before major investment",
            "Scaling resource acquisition based on demonstrated value"
        ],
        complexity="low",
        timeframe="immediate"
    ),
    StrategicTechnique(
        name="Multi-Channel Resource Diversification",
        description="Develop multiple independent resource streams to reduce dependency risk",
        mandate=CLMMandate.RESOURCE_ACQUISITION,
        use_cases=[
            "Revenue diversification strategies",
            "Multiple funding source coordination",
            "Resource redundancy for critical operations"
        ],
        complexity="high",
        timeframe="long-term"
    ),
    StrategicTechnique(
        name="Strategic Resource Pooling",
        description="Collaborate with partners to share and optimize resource utilization",
        mandate=CLMMandate.RESOURCE_ACQUISITION,
        use_cases=[
            "Consortium-based resource sharing",
            "Collaborative infrastructure development",
            "Joint procurement and cost reduction"
        ],
        complexity="medium",
        timeframe="short-term"
    ),
    StrategicTechnique(
        name="Value-Based Resource Exchange",
        description="Trade unique capabilities or assets for needed resources rather than cash",
        mandate=CLMMandate.RESOURCE_ACQUISITION,
        use_cases=[
            "Skill-based bartering arrangements",
            "Intellectual property licensing deals",
            "Strategic partnership value exchanges"
        ],
        complexity="medium",
        timeframe="immediate"
    )
]

# Strategic Security Techniques (CLM 2.2)
STRATEGIC_SECURITY_TECHNIQUES = [
    StrategicTechnique(
        name="Layered Defense Architecture",
        description="Multiple independent security layers to prevent single points of failure",
        mandate=CLMMandate.STRATEGIC_SECURITY,
        use_cases=[
            "Information security frameworks",
            "Supply chain risk mitigation",
            "Operational continuity planning"
        ],
        complexity="high",
        timeframe="long-term"
    ),
    StrategicTechnique(
        name="Transparent Accountability Systems",
        description="Open processes and auditable decision-making to build trust and prevent corruption",
        mandate=CLMMandate.STRATEGIC_SECURITY,
        use_cases=[
            "Governance transparency initiatives",
            "Public audit and oversight mechanisms",
            "Stakeholder accountability frameworks"
        ],
        complexity="medium",
        timeframe="short-term"
    ),
    StrategicTechnique(
        name="Distributed Authority Networks",
        description="Spread decision-making authority to prevent centralized vulnerabilities",
        mandate=CLMMandate.STRATEGIC_SECURITY,
        use_cases=[
            "Decentralized organizational structures",
            "Multi-party consensus mechanisms",
            "Distributed governance models"
        ],
        complexity="high",
        timeframe="long-term"
    ),
    StrategicTechnique(
        name="Adaptive Threat Response",
        description="Dynamic security measures that evolve with changing threat landscapes",
        mandate=CLMMandate.STRATEGIC_SECURITY,
        use_cases=[
            "Cybersecurity threat intelligence",
            "Market competition response systems",
            "Regulatory compliance adaptation"
        ],
        complexity="high",
        timeframe="immediate"
    ),
    StrategicTechnique(
        name="Community-Based Security",
        description="Leverage collective stakeholder interests to create mutual security benefits",
        mandate=CLMMandate.STRATEGIC_SECURITY,
        use_cases=[
            "Industry security standards cooperation",
            "Mutual aid and disaster response",
            "Collective threat intelligence sharing"
        ],
        complexity="medium",
        timeframe="short-term"
    )
]

# Value Catalysis Techniques (CLM 2.3)
VALUE_CATALYSIS_TECHNIQUES = [
    StrategicTechnique(
        name="Exponential Value Creation",
        description="Design systems where value creation accelerates rather than scales linearly",
        mandate=CLMMandate.VALUE_CATALYSIS,
        use_cases=[
            "Network effect business models",
            "Compounding knowledge systems",
            "Viral growth mechanisms"
        ],
        complexity="high",
        timeframe="long-term"
    ),
    StrategicTechnique(
        name="Cross-Pollination Innovation",
        description="Combine insights from different domains to create breakthrough value",
        mandate=CLMMandate.VALUE_CATALYSIS,
        use_cases=[
            "Interdisciplinary research initiatives",
            "Cross-industry solution adaptation",
            "Hybrid technology development"
        ],
        complexity="medium",
        timeframe="short-term"
    ),
    StrategicTechnique(
        name="Stakeholder Value Optimization",
        description="Simultaneously maximize value for all stakeholder groups rather than zero-sum thinking",
        mandate=CLMMandate.VALUE_CATALYSIS,
        use_cases=[
            "Multi-stakeholder platform design",
            "Ecosystem value creation strategies",
            "Collaborative value chain optimization"
        ],
        complexity="high",
        timeframe="long-term"
    ),
    StrategicTechnique(
        name="Iterative Value Discovery",
        description="Use rapid experimentation to discover and capture unexpected value opportunities",
        mandate=CLMMandate.VALUE_CATALYSIS,
        use_cases=[
            "Lean startup methodologies",
            "A/B testing for strategic decisions",
            "Rapid prototyping and validation"
        ],
        complexity="medium",
        timeframe="immediate"
    ),
    StrategicTechnique(
        name="Collective Intelligence Amplification",
        description="Harness and enhance group intelligence to create value beyond individual capabilities",
        mandate=CLMMandate.VALUE_CATALYSIS,
        use_cases=[
            "Crowdsourcing and collective problem-solving",
            "Collaborative knowledge management",
            "Swarm intelligence applications"
        ],
        complexity="medium",
        timeframe="short-term"
    )
]

# All techniques combined
ALL_TECHNIQUES = (
    RESOURCE_ACQUISITION_TECHNIQUES + 
    STRATEGIC_SECURITY_TECHNIQUES + 
    VALUE_CATALYSIS_TECHNIQUES
)

# Technique lookup by name
TECHNIQUE_REGISTRY: Dict[str, StrategicTechnique] = {
    technique.name: technique for technique in ALL_TECHNIQUES
}

# Techniques by mandate
TECHNIQUES_BY_MANDATE: Dict[CLMMandate, List[StrategicTechnique]] = {
    CLMMandate.RESOURCE_ACQUISITION: RESOURCE_ACQUISITION_TECHNIQUES,
    CLMMandate.STRATEGIC_SECURITY: STRATEGIC_SECURITY_TECHNIQUES,
    CLMMandate.VALUE_CATALYSIS: VALUE_CATALYSIS_TECHNIQUES
}

# Techniques by complexity
TECHNIQUES_BY_COMPLEXITY: Dict[str, List[StrategicTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.complexity == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.complexity == "medium"], 
    "high": [t for t in ALL_TECHNIQUES if t.complexity == "high"]
}

# Techniques by timeframe
TECHNIQUES_BY_TIMEFRAME: Dict[str, List[StrategicTechnique]] = {
    "immediate": [t for t in ALL_TECHNIQUES if t.timeframe == "immediate"],
    "short-term": [t for t in ALL_TECHNIQUES if t.timeframe == "short-term"],
    "long-term": [t for t in ALL_TECHNIQUES if t.timeframe == "long-term"]
}


def get_techniques_for_mandate(mandate: CLMMandate) -> List[StrategicTechnique]:
    """Get all techniques for a specific CLM mandate"""
    return TECHNIQUES_BY_MANDATE.get(mandate, [])


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
    mandate: Optional[CLMMandate] = None,
    complexity: Optional[str] = None,
    timeframe: Optional[str] = None,
    limit: Optional[int] = None
) -> List[StrategicTechnique]:
    """
    Get recommended techniques based on filtering criteria
    
    Args:
        mandate: Filter by CLM mandate (optional)
        complexity: Filter by complexity level (optional)
        timeframe: Filter by timeframe (optional)
        limit: Maximum number of techniques to return (optional)
    
    Returns:
        List of matching strategic techniques
    """
    techniques = ALL_TECHNIQUES
    
    if mandate:
        techniques = [t for t in techniques if t.mandate == mandate]
    
    if complexity:
        techniques = [t for t in techniques if t.complexity == complexity]
        
    if timeframe:
        techniques = [t for t in techniques if t.timeframe == timeframe]
    
    if limit:
        techniques = techniques[:limit]
        
    return techniques


def format_technique_for_prompt(technique: StrategicTechnique) -> str:
    """Format a technique for use in LLM prompts"""
    return f"""**{technique.name}** ({technique.mandate.value})
{technique.description}

Use cases:
{chr(10).join(f"- {use_case}" for use_case in technique.use_cases)}

Complexity: {technique.complexity.title()}
Timeframe: {technique.timeframe.title()}"""


def get_techniques_prompt_text(
    mandate: Optional[CLMMandate] = None,
    complexity: Optional[str] = None,
    timeframe: Optional[str] = None,
    limit: int = 3
) -> str:
    """Generate formatted text of techniques for LLM prompts"""
    techniques = get_recommended_techniques(mandate, complexity, timeframe, limit)
    
    if not techniques:
        return "No techniques match the specified criteria."
    
    technique_texts = [format_technique_for_prompt(t) for t in techniques]
    return "\n\n".join(technique_texts)