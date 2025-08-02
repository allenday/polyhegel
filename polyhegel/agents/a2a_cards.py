"""
A2A Cards module - Compatibility wrapper

This module provides backward compatibility for A2A card functionality.
"""

from .common.cards import generate_agent_card, AgentCard, CardType


# Additional specific card creators for A2A integration tests
def create_leader_agent_card() -> AgentCard:
    """Create a leader agent card for A2A integration"""
    return generate_agent_card(
        name="LeaderAgent",
        card_type=CardType.LEADER,
        description="A2A leader agent for coordinating strategic operations",
        capabilities=["coordination", "task_delegation", "strategy_planning"],
        requirements={"role": "leader", "a2a_compatible": True},
    )


def create_follower_agent_card() -> AgentCard:
    """Create a follower agent card for A2A integration"""
    return generate_agent_card(
        name="FollowerAgent",
        card_type=CardType.FOLLOWER,
        description="A2A follower agent for executing strategic tasks",
        capabilities=["task_execution", "data_collection", "reporting"],
        requirements={"role": "follower", "a2a_compatible": True},
    )


def create_simulation_agent_card() -> AgentCard:
    """Create a simulation agent card for A2A integration"""
    return generate_agent_card(
        name="SimulationAgent",
        card_type=CardType.ANALYZER,
        description="A2A simulation agent for scenario modeling",
        capabilities=["simulation", "modeling", "analysis"],
        requirements={"role": "simulator", "a2a_compatible": True},
    )


def create_all_agent_cards():
    """Create all A2A agent cards"""
    return [
        create_leader_agent_card(),
        create_follower_agent_card(),
        create_simulation_agent_card(),
    ]


# Additional exports that tests might expect
__all__ = [
    "generate_agent_card",
    "AgentCard",
    "CardType",
    "create_leader_agent_card",
    "create_follower_agent_card",
    "create_simulation_agent_card",
    "create_all_agent_cards",
]
