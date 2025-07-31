"""
Polyhegel Agents Package

This package implements the hierarchical agent architecture inspired by LLM-As-Hierarchical-Policy,
adapted for strategic planning and decision-making.

The package provides:
- BaseAgent: Abstract base class for all agents
- LeaderAgent: High-level strategic theme identification
- FollowerAgent: Detailed strategy implementation
- Agent coordination and communication patterns
"""

from .base import (
    BaseAgent, AgentRole, AgentCapabilities, AgentContext, 
    AgentResponse, AgentCoordinator
)
from .leader import LeaderAgent
from .follower import FollowerAgent

__all__ = [
    "BaseAgent",
    "AgentRole", 
    "AgentCapabilities",
    "AgentContext",
    "AgentResponse",
    "AgentCoordinator",
    "LeaderAgent",
    "FollowerAgent"
]