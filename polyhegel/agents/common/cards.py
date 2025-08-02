"""
A2A Agent Cards for Common Cross-Domain Agents

This module defines A2A protocol AgentCard and AgentSkill objects for the common
cross-domain agents, enabling service discovery and agent-to-agent communication.
"""

from typing import List
from a2a.types import AgentCard, AgentSkill, AgentCapabilities


def create_common_analysis_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for CommonAnalysisLeader capabilities"""

    coordinate_analysis_skill = AgentSkill(
        id="coordinate_cross_domain_analysis",
        name="Coordinate Cross-Domain Analysis",
        description=(
            "Coordinates comprehensive analysis across multiple domains by selecting "
            "and orchestrating appropriate common techniques (stakeholder analysis, "
            "SWOT, trade-offs, risk assessment, consensus building, scenario planning). "
            "Provides structured analysis plans and technique recommendations."
        ),
        tags=["analysis", "coordination", "cross-domain", "leadership", "techniques"],
        examples=[
            "Coordinate comprehensive analysis for digital transformation initiative",
            "Design multi-technique analysis approach for strategic decision",
            "Plan cross-domain evaluation of technology architecture options",
            "Orchestrate stakeholder and risk analysis for organizational change",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [coordinate_analysis_skill]


def create_stakeholder_analysis_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for StakeholderAnalysisFollower capabilities"""

    stakeholder_skill = AgentSkill(
        id="stakeholder_identification_analysis",
        name="Stakeholder Identification and Analysis",
        description=(
            "Systematically identifies, analyzes, and prioritizes stakeholders across "
            "any domain or project context. Creates stakeholder maps, influence matrices, "
            "and engagement strategies for effective stakeholder management."
        ),
        tags=["stakeholder", "analysis", "mapping", "engagement", "strategy"],
        examples=[
            "Identify key stakeholders for technical architecture decision",
            "Map stakeholder interests and influence for product launch",
            "Develop engagement strategy for organizational change initiative",
            "Analyze stakeholder alignment for strategic planning process",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [stakeholder_skill]


def create_tradeoff_analysis_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for TradeoffAnalysisFollower capabilities"""

    tradeoff_skill = AgentSkill(
        id="systematic_tradeoff_analysis",
        name="Systematic Trade-off Analysis",
        description=(
            "Conducts comprehensive trade-off analysis by evaluating competing options "
            "across multiple criteria. Provides multi-criteria decision matrices, "
            "sensitivity analysis, and evidence-based recommendations for complex decisions."
        ),
        tags=["tradeoff", "decision", "analysis", "evaluation", "multi-criteria"],
        examples=[
            "Evaluate architecture patterns with different performance characteristics",
            "Compare strategic alternatives with different resource requirements",
            "Assess product features with competing user value propositions",
            "Analyze implementation approaches with different risk profiles",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [tradeoff_skill]


def create_risk_assessment_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for RiskAssessmentFollower capabilities"""

    risk_skill = AgentSkill(
        id="comprehensive_risk_assessment",
        name="Comprehensive Risk Assessment",
        description=(
            "Identifies, analyzes, and prioritizes risks across any domain with "
            "detailed mitigation strategies. Provides risk matrices, probability/impact "
            "assessments, early warning systems, and comprehensive risk management plans."
        ),
        tags=["risk", "assessment", "mitigation", "planning", "management"],
        examples=[
            "Assess technical risks in system architecture implementation",
            "Identify strategic risks for business planning and market entry",
            "Evaluate operational risks for process changes and improvements",
            "Analyze project risks with mitigation and contingency planning",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [risk_skill]


def create_consensus_building_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for ConsensusBuilderFollower capabilities"""

    consensus_skill = AgentSkill(
        id="multi_party_consensus_building",
        name="Multi-Party Consensus Building",
        description=(
            "Facilitates multi-party agreement and alignment through structured "
            "negotiation and collaboration. Designs consensus processes, manages "
            "stakeholder conflicts, and develops sustainable agreements across groups."
        ),
        tags=["consensus", "facilitation", "negotiation", "alignment", "collaboration"],
        examples=[
            "Build alignment on technical standards across development teams",
            "Facilitate consensus on strategic direction across leadership",
            "Resolve conflicts in cross-functional project decisions",
            "Design collaborative agreement process for organizational changes",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [consensus_skill]


def create_scenario_planning_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for ScenarioPlanningFollower capabilities"""

    scenario_skill = AgentSkill(
        id="future_scenario_planning",
        name="Future Scenario Planning",
        description=(
            "Explores multiple future scenarios and outcomes to improve decision-making "
            "under uncertainty. Develops scenario narratives, identifies driving forces, "
            "creates robust strategies, and establishes early warning indicator systems."
        ),
        tags=["scenario", "planning", "futures", "uncertainty", "strategy"],
        examples=[
            "Develop scenarios for technology adoption and market evolution",
            "Plan strategic responses to different competitive conditions",
            "Design resilient architectures for various operational scenarios",
            "Create contingency plans for different business environments",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [scenario_skill]


def create_common_analysis_leader_card(base_url: str = "http://localhost:7001") -> AgentCard:
    """Create A2A AgentCard for CommonAnalysisLeader"""

    return AgentCard(
        name="Polyhegel Common Analysis Leader",
        description=(
            "Cross-domain analysis coordinator that orchestrates multiple common "
            "techniques (stakeholder analysis, SWOT, trade-offs, risk assessment, "
            "consensus building, scenario planning) to provide comprehensive analysis "
            "across strategic, technical, and product domains."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_common_analysis_skills(),
        supports_authenticated_extended_card=False,
    )


def create_stakeholder_analysis_follower_card(base_url: str = "http://localhost:7002") -> AgentCard:
    """Create A2A AgentCard for StakeholderAnalysisFollower"""

    return AgentCard(
        name="Polyhegel Stakeholder Analysis Specialist",
        description=(
            "Specialized agent for stakeholder identification, analysis, and engagement "
            "strategy development across any domain context. Provides comprehensive "
            "stakeholder mapping, influence analysis, and strategic engagement planning."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_stakeholder_analysis_skills(),
        supports_authenticated_extended_card=False,
    )


def create_tradeoff_analysis_follower_card(base_url: str = "http://localhost:7003") -> AgentCard:
    """Create A2A AgentCard for TradeoffAnalysisFollower"""

    return AgentCard(
        name="Polyhegel Trade-off Analysis Specialist",
        description=(
            "Expert in systematic trade-off analysis and multi-criteria decision making. "
            "Evaluates competing options across complex criteria sets, provides "
            "sensitivity analysis, and delivers evidence-based recommendations."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_tradeoff_analysis_skills(),
        supports_authenticated_extended_card=False,
    )


def create_risk_assessment_follower_card(base_url: str = "http://localhost:7004") -> AgentCard:
    """Create A2A AgentCard for RiskAssessmentFollower"""

    return AgentCard(
        name="Polyhegel Risk Assessment Specialist",
        description=(
            "Comprehensive risk assessment and management specialist across all domains. "
            "Identifies, analyzes, and prioritizes risks while developing detailed "
            "mitigation strategies and monitoring systems for proactive risk management."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_risk_assessment_skills(),
        supports_authenticated_extended_card=False,
    )


def create_consensus_builder_follower_card(base_url: str = "http://localhost:7005") -> AgentCard:
    """Create A2A AgentCard for ConsensusBuilderFollower"""

    return AgentCard(
        name="Polyhegel Consensus Building Facilitator",
        description=(
            "Expert facilitator for multi-party agreement and collaborative decision-making. "
            "Designs consensus processes, manages stakeholder conflicts, and builds "
            "sustainable agreements through structured negotiation and alignment techniques."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_consensus_building_skills(),
        supports_authenticated_extended_card=False,
    )


def create_scenario_planning_follower_card(base_url: str = "http://localhost:7006") -> AgentCard:
    """Create A2A AgentCard for ScenarioPlanningFollower"""

    return AgentCard(
        name="Polyhegel Scenario Planning Specialist",
        description=(
            "Future-focused strategic planning specialist that develops multiple scenarios "
            "and robust strategies for decision-making under uncertainty. Creates scenario "
            "narratives, identifies early indicators, and designs adaptive strategies."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_scenario_planning_skills(),
        supports_authenticated_extended_card=False,
    )


def create_all_common_agent_cards(
    leader_url: str = "http://localhost:7001",
    follower_base_url: str = "http://localhost:7002",
) -> dict[str, AgentCard]:
    """Create all common cross-domain agent cards"""

    return {
        "common_leader": create_common_analysis_leader_card(leader_url),
        "stakeholder_follower": create_stakeholder_analysis_follower_card(f"{follower_base_url}"),
        "tradeoff_follower": create_tradeoff_analysis_follower_card(f"{follower_base_url[:-1]}3"),
        "risk_follower": create_risk_assessment_follower_card(f"{follower_base_url[:-1]}4"),
        "consensus_follower": create_consensus_builder_follower_card(f"{follower_base_url[:-1]}5"),
        "scenario_follower": create_scenario_planning_follower_card(f"{follower_base_url[:-1]}6"),
    }
