"""
Polyhegel Agents Package

This package implements A2A (Agent-to-Agent) protocol integration for distributed
strategic simulation using Google's Agent2Agent framework.

The package provides:
- A2A AgentCard definitions for polyhegel agents
- A2A AgentSkill definitions for strategic capabilities
- A2A AgentExecutor implementations for distributed execution
- A2A coordination and communication patterns
"""

from .a2a_cards import create_leader_agent_card, create_follower_agent_card, create_simulation_agent_card
from .a2a_executors import LeaderAgentExecutor, FollowerAgentExecutor
from .a2a_simulation import generate_hierarchical_strategies_a2a

__all__ = [
    "create_leader_agent_card",
    "create_follower_agent_card",
    "create_simulation_agent_card",
    "LeaderAgentExecutor",
    "FollowerAgentExecutor",
    "generate_hierarchical_strategies_a2a",
]
