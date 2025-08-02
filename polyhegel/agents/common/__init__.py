"""
Common Cross-Domain Agents for Polyhegel

This module provides default agent implementations that work with common cross-domain
techniques, providing immediate value out-of-the-box while serving as reference
implementations for custom agent development.

Available agents:
- CommonAnalysisLeader: Coordinates cross-domain analytical techniques
- StakeholderAnalysisFollower: Specialized in stakeholder identification and analysis
- TradeoffAnalysisFollower: Focused on systematic option evaluation
- RiskAssessmentFollower: Specialized in risk identification and mitigation
- ConsensusBuilderFollower: Facilitates multi-party agreement processes
"""

from .agents import (
    CommonAnalysisLeader,
    StakeholderAnalysisFollower,
    TradeoffAnalysisFollower,
    RiskAssessmentFollower,
    ConsensusBuilderFollower,
    ScenarioPlanningFollower,
)

from .cards import (
    create_common_analysis_leader_card,
    create_stakeholder_analysis_follower_card,
    create_tradeoff_analysis_follower_card,
    create_risk_assessment_follower_card,
    create_consensus_builder_follower_card,
    create_scenario_planning_follower_card,
    create_all_common_agent_cards,
)

__all__ = [
    # Agent classes
    "CommonAnalysisLeader",
    "StakeholderAnalysisFollower",
    "TradeoffAnalysisFollower",
    "RiskAssessmentFollower",
    "ConsensusBuilderFollower",
    "ScenarioPlanningFollower",
    # Agent card creators
    "create_common_analysis_leader_card",
    "create_stakeholder_analysis_follower_card",
    "create_tradeoff_analysis_follower_card",
    "create_risk_assessment_follower_card",
    "create_consensus_builder_follower_card",
    "create_scenario_planning_follower_card",
    "create_all_common_agent_cards",
]
