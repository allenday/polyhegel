"""
Agent card creation and management utilities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CardType(Enum):
    """Types of agent cards"""

    LEADER = "leader"
    FOLLOWER = "follower"
    ANALYZER = "analyzer"
    COORDINATOR = "coordinator"


@dataclass
class AgentCard:
    """Agent card for A2A integration"""

    name: str
    card_type: CardType
    description: str
    capabilities: List[str]
    requirements: Dict[str, Any]

    def __post_init__(self):
        if not self.capabilities:
            self.capabilities = []
        if not self.requirements:
            self.requirements = {}


def generate_agent_card(
    name: str,
    card_type: CardType,
    description: str = "",
    capabilities: List[str] = None,
    requirements: Dict[str, Any] = None,
) -> AgentCard:
    """Generate an agent card for A2A integration"""
    return AgentCard(
        name=name,
        card_type=card_type,
        description=description or f"Agent card for {name}",
        capabilities=capabilities or [],
        requirements=requirements or {},
    )


# Specific agent card creators for compatibility
def create_common_analysis_leader_card() -> AgentCard:
    """Create a card for the common analysis leader agent"""
    return generate_agent_card(
        name="CommonAnalysisLeader",
        card_type=CardType.LEADER,
        description="Coordinates cross-domain analytical techniques",
        capabilities=["analysis_coordination", "technique_selection", "team_management"],
        requirements={"domain": "general", "complexity": "medium"},
    )


def create_stakeholder_analysis_follower_card() -> AgentCard:
    """Create a card for stakeholder analysis follower agent"""
    return generate_agent_card(
        name="StakeholderAnalysisFollower",
        card_type=CardType.FOLLOWER,
        description="Specialized in stakeholder identification and analysis",
        capabilities=["stakeholder_mapping", "influence_analysis", "communication_planning"],
        requirements={"domain": "stakeholder_management", "complexity": "medium"},
    )


def create_tradeoff_analysis_follower_card() -> AgentCard:
    """Create a card for tradeoff analysis follower agent"""
    return generate_agent_card(
        name="TradeoffAnalysisFollower",
        card_type=CardType.FOLLOWER,
        description="Focused on systematic option evaluation",
        capabilities=["option_evaluation", "criteria_weighting", "decision_matrix"],
        requirements={"domain": "decision_making", "complexity": "medium"},
    )


def create_risk_assessment_follower_card() -> AgentCard:
    """Create a card for risk assessment follower agent"""
    return generate_agent_card(
        name="RiskAssessmentFollower",
        card_type=CardType.FOLLOWER,
        description="Specialized in risk identification and mitigation",
        capabilities=["risk_identification", "probability_assessment", "mitigation_planning"],
        requirements={"domain": "risk_management", "complexity": "medium"},
    )


def create_consensus_builder_follower_card() -> AgentCard:
    """Create a card for consensus builder follower agent"""
    return generate_agent_card(
        name="ConsensusBuilderFollower",
        card_type=CardType.FOLLOWER,
        description="Facilitates multi-party agreement processes",
        capabilities=["facilitation", "conflict_resolution", "agreement_structuring"],
        requirements={"domain": "negotiation", "complexity": "medium"},
    )


def create_scenario_planning_follower_card() -> AgentCard:
    """Create a card for scenario planning follower agent"""
    return generate_agent_card(
        name="ScenarioPlanningFollower",
        card_type=CardType.FOLLOWER,
        description="Specialized in scenario development and planning",
        capabilities=["scenario_generation", "future_modeling", "contingency_planning"],
        requirements={"domain": "strategic_planning", "complexity": "high"},
    )


def create_all_common_agent_cards() -> List[AgentCard]:
    """Create all common agent cards"""
    return [
        create_common_analysis_leader_card(),
        create_stakeholder_analysis_follower_card(),
        create_tradeoff_analysis_follower_card(),
        create_risk_assessment_follower_card(),
        create_consensus_builder_follower_card(),
        create_scenario_planning_follower_card(),
    ]


def get_agent_card_by_name(name: str) -> Optional[AgentCard]:
    """
    Retrieve a specific agent card by name.

    Args:
        name: Name of the agent card to retrieve

    Returns:
        Agent card configuration or None if not found
    """
    agent_cards = create_all_common_agent_cards()
    matching_cards = [card for card in agent_cards if card.name == name]

    return matching_cards[0] if matching_cards else None
