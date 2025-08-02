"""
A2A Executors module - Compatibility wrapper

This module provides backward compatibility for A2A executor functionality.
"""

from .common.agents import (
    CommonAnalysisLeader,
    StakeholderAnalysisFollower,
    TradeoffAnalysisFollower,
    RiskAssessmentFollower,
    ConsensusBuilderFollower,
    ScenarioPlanningFollower,
)

# Create compatibility aliases
LeaderAgentExecutor = CommonAnalysisLeader
FollowerAgentExecutor = StakeholderAnalysisFollower

__all__ = [
    "CommonAnalysisLeader",
    "StakeholderAnalysisFollower",
    "TradeoffAnalysisFollower",
    "RiskAssessmentFollower",
    "ConsensusBuilderFollower",
    "ScenarioPlanningFollower",
    "LeaderAgentExecutor",
    "FollowerAgentExecutor",
]
