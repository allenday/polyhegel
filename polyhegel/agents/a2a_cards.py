"""
A2A AgentCard and AgentSkill definitions for polyhegel agents

This module defines the A2A protocol AgentCard and AgentSkill objects
that describe polyhegel's strategic simulation capabilities following
the Agent2Agent protocol specification.
"""

from typing import List, Optional
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from ..strategic_techniques import StrategyDomain


def create_leader_agent_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for LeaderAgent capabilities"""

    generate_themes_skill = AgentSkill(
        id="generate_strategic_themes",
        name="Generate Strategic Themes",
        description=(
            "Analyzes strategic challenges and generates high-level thematic frameworks "
            "that guide detailed strategy development. Applies strategic domain filtering "
            "and strategic technique analysis to identify key strategic priorities."
        ),
        tags=["strategy", "themes", "leadership", "planning"],
        examples=[
            "Generate strategic themes for resolving the hotdog-sandwich classification conflict",
            "Create thematic framework for organizational digital transformation",
            "Develop strategic themes for market expansion into emerging economies",
            "Generate themes for crisis management and organizational resilience",
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    return [generate_themes_skill]


def create_follower_agent_skills(specialization_domain: Optional[StrategyDomain] = None) -> List[AgentSkill]:
    """Create AgentSkill definitions for FollowerAgent capabilities"""

    # Base strategy development skill
    develop_strategy_skill = AgentSkill(
        id="develop_detailed_strategy",
        name="Develop Detailed Strategy",
        description=(
            "Takes strategic themes and develops comprehensive implementation strategies "
            "with specific steps, timelines, and resource requirements. Applies strategic "
            "techniques and maintains alignment with organizational domains."
        ),
        tags=["strategy", "implementation", "planning", "execution"],
        examples=[
            "Develop implementation strategy for consensus-building theme",
            "Create detailed execution plan for resource acquisition strategy",
            "Build comprehensive strategy from security-focused theme",
            "Generate step-by-step implementation for value creation theme",
        ],
        input_modes=["application/json", "text/plain"],
        output_modes=["application/json", "text/plain"],
    )

    skills = [develop_strategy_skill]

    # Add specialization-specific skills
    if specialization_domain == StrategyDomain.RESOURCE_ACQUISITION:
        resource_skill = AgentSkill(
            id="resource_acquisition_strategy",
            name="Resource Acquisition Strategy",
            description=(
                "Specializes in developing strategies for acquiring and optimizing "
                "organizational resources including funding, talent, technology, and partnerships."
            ),
            tags=["resources", "acquisition", "funding", "talent"],
            examples=[
                "Develop funding strategy for startup growth",
                "Create talent acquisition plan for technical roles",
                "Design partnership strategy for market expansion",
            ],
            input_modes=["application/json", "text/plain"],
            output_modes=["application/json", "text/plain"],
        )
        skills.append(resource_skill)

    elif specialization_domain == StrategyDomain.STRATEGIC_SECURITY:
        security_skill = AgentSkill(
            id="strategic_security_strategy",
            name="Strategic Security Strategy",
            description=(
                "Specializes in developing strategies for organizational security, "
                "risk management, resilience, and threat mitigation across all domains."
            ),
            tags=["security", "risk", "resilience", "threats"],
            examples=[
                "Develop cybersecurity strategy for digital transformation",
                "Create crisis response and business continuity plan",
                "Design risk mitigation strategy for market volatility",
            ],
            input_modes=["application/json", "text/plain"],
            output_modes=["application/json", "text/plain"],
        )
        skills.append(security_skill)

    elif specialization_domain == StrategyDomain.VALUE_CATALYSIS:
        value_skill = AgentSkill(
            id="value_catalysis_strategy",
            name="Value Catalysis Strategy",
            description=(
                "Specializes in developing strategies for value creation, innovation, "
                "stakeholder engagement, and sustainable competitive advantage."
            ),
            tags=["value", "innovation", "stakeholders", "advantage", "value-catalysis"],
            examples=[
                "Develop customer value proposition strategy",
                "Create innovation pipeline and R&D strategy",
                "Design stakeholder engagement and communication plan",
            ],
            input_modes=["application/json", "text/plain"],
            output_modes=["application/json", "text/plain"],
        )
        skills.append(value_skill)

    return skills


def create_simulation_agent_skills() -> List[AgentSkill]:
    """Create AgentSkill definitions for general strategic simulation"""

    simulate_strategies_skill = AgentSkill(
        id="simulate_strategic_scenarios",
        name="Strategic Scenario Simulation",
        description=(
            "Runs comprehensive strategic simulations using temperature sampling or "
            "hierarchical agent coordination to generate diverse strategy portfolios "
            "and identify trunk/twig patterns."
        ),
        tags=["simulation", "scenarios", "trunk-twig", "clustering"],
        examples=[
            "Simulate strategic options for market entry decision",
            "Run scenario analysis for organizational restructuring",
            "Generate strategy portfolio for competitive response",
            "Simulate consensus-building approaches for policy decisions",
        ],
        input_modes=["text/plain", "application/json"],
        output_modes=["application/json", "text/markdown"],
    )

    cluster_strategies_skill = AgentSkill(
        id="cluster_strategy_analysis",
        name="Strategy Clustering and Analysis",
        description=(
            "Analyzes collections of strategies using embedding similarity and "
            "HDBSCAN clustering to identify dominant trunk strategies and "
            "alternative twig approaches with coherence metrics."
        ),
        tags=["clustering", "analysis", "embeddings", "trunk-twig"],
        examples=[
            "Cluster and analyze 30 strategic responses to identify patterns",
            "Find dominant strategy clusters in competitive analysis",
            "Identify alternative approaches in strategic option portfolio",
        ],
        input_modes=["application/json"],
        output_modes=["application/json", "text/markdown"],
    )

    return [simulate_strategies_skill, cluster_strategies_skill]


def create_leader_agent_card(base_url: str = "http://localhost:8001") -> AgentCard:
    """Create A2A AgentCard for polyhegel LeaderAgent"""

    return AgentCard(
        name="Polyhegel Strategic Leader Agent",
        description=(
            "AI agent specializing in strategic theme generation and high-level "
            "planning using the polyhegel strategic simulation framework. "
            "Applies strategic domain analysis and strategic techniques to generate "
            "coherent thematic frameworks for complex challenges."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_leader_agent_skills(),
        supports_authenticated_extended_card=False,
    )


def create_follower_agent_card(
    specialization_domain: Optional[StrategyDomain] = None, base_url: str = "http://localhost:8002"
) -> AgentCard:
    """Create A2A AgentCard for polyhegel FollowerAgent"""

    # Determine specialization name for card
    if specialization_domain == StrategyDomain.RESOURCE_ACQUISITION:
        specialization_name = "Resource Acquisition"
        description_suffix = "specializing in resource acquisition and optimization strategies"
    elif specialization_domain == StrategyDomain.STRATEGIC_SECURITY:
        specialization_name = "Strategic Security"
        description_suffix = "specializing in security, risk management, and resilience strategies"
    elif specialization_domain == StrategyDomain.VALUE_CATALYSIS:
        specialization_name = "Value Catalysis"
        description_suffix = "specializing in value creation and stakeholder engagement strategies"
    else:
        specialization_name = "General Strategy"
        description_suffix = "providing general strategic implementation capabilities"

    card_name = f"Polyhegel Strategic Follower Agent - {specialization_name}"

    return AgentCard(
        name=card_name,
        description=(
            f"AI agent for detailed strategy development and implementation planning "
            f"using the polyhegel strategic simulation framework, {description_suffix}. "
            f"Converts high-level themes into actionable strategic plans with specific "
            f"steps, timelines, and resource requirements."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["application/json", "text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=create_follower_agent_skills(specialization_domain),
        supports_authenticated_extended_card=False,
    )


def create_simulation_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Create A2A AgentCard for general polyhegel strategic simulation"""

    return AgentCard(
        name="Polyhegel Strategic Simulation Agent",
        description=(
            "Comprehensive strategic simulation agent using the polyhegel framework "
            "for trunk/twig strategic analysis. Capable of temperature sampling, "
            "hierarchical agent coordination, strategy clustering, and coherence analysis "
            "to identify effective strategic approaches for complex challenges."
        ),
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["application/json", "text/markdown"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True, push_notifications=True),
        skills=create_simulation_agent_skills(),
        supports_authenticated_extended_card=False,
    )


# Convenience functions for creating all agent cards
def create_all_agent_cards(
    leader_url: str = "http://localhost:8001",
    follower_base_url: str = "http://localhost:8002",
    simulation_url: str = "http://localhost:8000",
) -> dict[str, AgentCard]:
    """Create all polyhegel A2A agent cards"""

    return {
        "simulation": create_simulation_agent_card(simulation_url),
        "leader": create_leader_agent_card(leader_url),
        "follower_resource": create_follower_agent_card(
            StrategyDomain.RESOURCE_ACQUISITION, f"{follower_base_url}/resource"
        ),
        "follower_security": create_follower_agent_card(
            StrategyDomain.STRATEGIC_SECURITY, f"{follower_base_url}/security"
        ),
        "follower_value": create_follower_agent_card(StrategyDomain.VALUE_CATALYSIS, f"{follower_base_url}/value"),
        "follower_general": create_follower_agent_card(None, f"{follower_base_url}/general"),
    }
