"""
Common Cross-Domain Techniques for Polyhegel

Provides broadly applicable analytical techniques that work across multiple domains.
These techniques form the foundation that domain-specific techniques can build upon.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class TechniqueType(Enum):
    """Categories of common techniques"""

    ANALYSIS = "analysis"
    PLANNING = "planning"
    EVALUATION = "evaluation"
    COORDINATION = "coordination"


class TechniqueComplexity(Enum):
    """Complexity levels for techniques"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TechniqueTimeframe(Enum):
    """Expected timeframes for technique execution"""

    IMMEDIATE = "immediate"  # Minutes to hours
    SHORT_TERM = "short-term"  # Days to weeks
    LONG_TERM = "long-term"  # Weeks to months


@dataclass
class CommonTechnique:
    """Base class for common cross-domain techniques"""

    name: str
    description: str
    technique_type: TechniqueType
    use_cases: List[str]
    complexity: TechniqueComplexity
    timeframe: TechniqueTimeframe
    inputs_required: List[str]
    outputs_provided: List[str]
    applicable_domains: List[str]  # Empty list means applicable to all domains


# Stakeholder Analysis Technique
StakeholderAnalysisTechnique = CommonTechnique(
    name="Stakeholder Analysis",
    description="Systematically identify, analyze, and prioritize stakeholders across any domain or project context",
    technique_type=TechniqueType.ANALYSIS,
    use_cases=[
        "Identify key decision makers for strategic initiatives",
        "Map stakeholder interests in technical architecture decisions",
        "Analyze user groups for product roadmap planning",
        "Assess stakeholder impact for organizational changes",
        "Build coalition support for cross-functional projects",
    ],
    complexity=TechniqueComplexity.MEDIUM,
    timeframe=TechniqueTimeframe.SHORT_TERM,
    inputs_required=[
        "Project or initiative description",
        "Organizational context",
        "Scope of analysis (internal/external/both)",
    ],
    outputs_provided=[
        "Stakeholder identification matrix",
        "Interest and influence mapping",
        "Engagement strategy recommendations",
        "Communication plan outline",
    ],
    applicable_domains=[],  # Universal - applies to all domains
)


# SWOT Analysis Technique
SWOTAnalysisTechnique = CommonTechnique(
    name="SWOT Analysis",
    description="Evaluate Strengths, Weaknesses, Opportunities, and Threats for any situation or decision context",
    technique_type=TechniqueType.EVALUATION,
    use_cases=[
        "Assess competitive position for strategic planning",
        "Evaluate technology choices in architecture decisions",
        "Analyze market position for product planning",
        "Review organizational capabilities for change initiatives",
        "Assess project readiness and risk factors",
    ],
    complexity=TechniqueComplexity.LOW,
    timeframe=TechniqueTimeframe.IMMEDIATE,
    inputs_required=[
        "Subject of analysis (organization, project, product, etc.)",
        "Relevant context and constraints",
        "Timeframe for analysis",
    ],
    outputs_provided=[
        "Comprehensive SWOT matrix",
        "Strategic implications analysis",
        "Action priorities based on SWOT findings",
        "Risk and opportunity prioritization",
    ],
    applicable_domains=[],  # Universal
)


# Trade-off Analysis Technique
TradeoffAnalysisTechnique = CommonTechnique(
    name="Trade-off Analysis",
    description="Systematically evaluate competing options by analyzing benefits, costs, and trade-offs across multiple criteria",
    technique_type=TechniqueType.EVALUATION,
    use_cases=[
        "Compare strategic alternatives with different resource requirements",
        "Evaluate architecture patterns with different performance characteristics",
        "Assess product features with competing user value propositions",
        "Choose between implementation approaches with different risk profiles",
        "Balance competing organizational priorities and constraints",
    ],
    complexity=TechniqueComplexity.MEDIUM,
    timeframe=TechniqueTimeframe.SHORT_TERM,
    inputs_required=[
        "List of options to evaluate",
        "Evaluation criteria and their relative importance",
        "Available data and constraints for each option",
    ],
    outputs_provided=[
        "Multi-criteria decision matrix",
        "Trade-off visualization and analysis",
        "Recommendation with supporting rationale",
        "Sensitivity analysis for key assumptions",
    ],
    applicable_domains=[],  # Universal
)


# Risk Assessment Technique
RiskAssessmentTechnique = CommonTechnique(
    name="Risk Assessment",
    description="Identify, analyze, and prioritize risks across any domain with mitigation strategies",
    technique_type=TechniqueType.ANALYSIS,
    use_cases=[
        "Assess strategic risks for business planning",
        "Identify technical risks in architecture decisions",
        "Evaluate market risks for product launches",
        "Analyze operational risks for process changes",
        "Review compliance and regulatory risks",
    ],
    complexity=TechniqueComplexity.MEDIUM,
    timeframe=TechniqueTimeframe.SHORT_TERM,
    inputs_required=[
        "Scope and context of risk assessment",
        "Relevant historical data and precedents",
        "Risk tolerance and acceptance criteria",
    ],
    outputs_provided=[
        "Risk identification and categorization",
        "Risk probability and impact assessment",
        "Risk prioritization matrix",
        "Mitigation strategies and contingency plans",
    ],
    applicable_domains=[],  # Universal
)


# Consensus Building Technique
ConsensusBuildingTechnique = CommonTechnique(
    name="Consensus Building",
    description="Facilitate multi-party agreement and alignment through structured negotiation and collaboration",
    technique_type=TechniqueType.COORDINATION,
    use_cases=[
        "Build alignment on strategic direction across leadership",
        "Achieve consensus on technical standards across teams",
        "Align stakeholders on product priorities and roadmap",
        "Resolve conflicts in cross-functional project decisions",
        "Build support for organizational change initiatives",
    ],
    complexity=TechniqueComplexity.HIGH,
    timeframe=TechniqueTimeframe.LONG_TERM,
    inputs_required=[
        "Stakeholder positions and interests",
        "Areas of agreement and disagreement",
        "Constraints and non-negotiable requirements",
    ],
    outputs_provided=[
        "Consensus building process design",
        "Facilitated agreement framework",
        "Conflict resolution strategies",
        "Implementation and monitoring plan",
    ],
    applicable_domains=[],  # Universal
)


# Scenario Planning Technique
ScenarioPlanningTechnique = CommonTechnique(
    name="Scenario Planning",
    description="Explore multiple future scenarios and outcomes to improve decision-making under uncertainty",
    technique_type=TechniqueType.PLANNING,
    use_cases=[
        "Plan strategic responses to different market conditions",
        "Design resilient technical architectures for various load scenarios",
        "Develop product roadmaps accounting for different user adoption patterns",
        "Prepare contingency plans for various operational scenarios",
        "Stress-test decisions against different future conditions",
    ],
    complexity=TechniqueComplexity.HIGH,
    timeframe=TechniqueTimeframe.LONG_TERM,
    inputs_required=[
        "Key uncertainties and driving forces",
        "Plausible ranges for critical variables",
        "Decision context and planning horizon",
    ],
    outputs_provided=[
        "Diverse scenario narratives",
        "Scenario impact analysis",
        "Robust strategy recommendations",
        "Early warning indicators and triggers",
    ],
    applicable_domains=[],  # Universal
)


# Technique Registry
ALL_COMMON_TECHNIQUES = [
    StakeholderAnalysisTechnique,
    SWOTAnalysisTechnique,
    TradeoffAnalysisTechnique,
    RiskAssessmentTechnique,
    ConsensusBuildingTechnique,
    ScenarioPlanningTechnique,
]

# Aliases for compatibility with examples
ALL_TECHNIQUES = ALL_COMMON_TECHNIQUES
TECHNIQUE_REGISTRY = {technique.name: technique for technique in ALL_COMMON_TECHNIQUES}

# Create lookup dictionaries
COMMON_TECHNIQUE_REGISTRY: Dict[str, CommonTechnique] = {
    technique.name: technique for technique in ALL_COMMON_TECHNIQUES
}

TECHNIQUES_BY_TYPE: Dict[TechniqueType, List[CommonTechnique]] = {
    technique_type: [t for t in ALL_COMMON_TECHNIQUES if t.technique_type == technique_type]
    for technique_type in TechniqueType
}

TECHNIQUES_BY_COMPLEXITY: Dict[TechniqueComplexity, List[CommonTechnique]] = {
    complexity: [t for t in ALL_COMMON_TECHNIQUES if t.complexity == complexity] for complexity in TechniqueComplexity
}

TECHNIQUES_BY_TIMEFRAME: Dict[TechniqueTimeframe, List[CommonTechnique]] = {
    timeframe: [t for t in ALL_COMMON_TECHNIQUES if t.timeframe == timeframe] for timeframe in TechniqueTimeframe
}


def get_common_technique(name: str) -> Optional[CommonTechnique]:
    """Get a common technique by name"""
    return COMMON_TECHNIQUE_REGISTRY.get(name)


def get_common_techniques_by_type(technique_type: TechniqueType) -> List[CommonTechnique]:
    """Get common techniques filtered by type"""
    return TECHNIQUES_BY_TYPE.get(technique_type, [])


def get_common_techniques_by_complexity(complexity: TechniqueComplexity) -> List[CommonTechnique]:
    """Get common techniques filtered by complexity level"""
    return TECHNIQUES_BY_COMPLEXITY.get(complexity, [])


def get_common_techniques_by_timeframe(timeframe: TechniqueTimeframe) -> List[CommonTechnique]:
    """Get common techniques filtered by timeframe"""
    return TECHNIQUES_BY_TIMEFRAME.get(timeframe, [])


def get_recommended_common_techniques(
    technique_type: Optional[TechniqueType] = None,
    complexity: Optional[TechniqueComplexity] = None,
    timeframe: Optional[TechniqueTimeframe] = None,
    limit: Optional[int] = None,
) -> List[CommonTechnique]:
    """
    Get recommended common techniques based on filtering criteria

    Args:
        technique_type: Filter by technique type (optional)
        complexity: Filter by complexity level (optional)
        timeframe: Filter by timeframe (optional)
        limit: Maximum number of techniques to return (optional)

    Returns:
        List of matching common techniques
    """
    techniques = ALL_COMMON_TECHNIQUES.copy()

    if technique_type:
        techniques = [t for t in techniques if t.technique_type == technique_type]

    if complexity:
        techniques = [t for t in techniques if t.complexity == complexity]

    if timeframe:
        techniques = [t for t in techniques if t.timeframe == timeframe]

    if limit:
        techniques = techniques[:limit]

    return techniques


def format_technique_for_prompt(technique: CommonTechnique) -> str:
    """Format a common technique for use in LLM prompts"""
    return f"""**{technique.name}** ({technique.technique_type.value})
{technique.description}

**Use Cases:**
{chr(10).join(f"- {use_case}" for use_case in technique.use_cases)}

**Complexity:** {technique.complexity.value.title()}
**Timeframe:** {technique.timeframe.value.title()}

**Required Inputs:**
{chr(10).join(f"- {input_req}" for input_req in technique.inputs_required)}

**Outputs Provided:**
{chr(10).join(f"- {output}" for output in technique.outputs_provided)}"""


def get_techniques_prompt_text(
    technique_type: Optional[TechniqueType] = None,
    complexity: Optional[TechniqueComplexity] = None,
    timeframe: Optional[TechniqueTimeframe] = None,
    limit: int = 3,
) -> str:
    """Generate formatted text of common techniques for LLM prompts"""
    techniques = get_recommended_common_techniques(technique_type, complexity, timeframe, limit)

    if not techniques:
        return "No common techniques match the specified criteria."

    technique_texts = [format_technique_for_prompt(t) for t in techniques]
    return "\n\n".join(technique_texts)
