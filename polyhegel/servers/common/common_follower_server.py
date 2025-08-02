#!/usr/bin/env python3
"""
A2A Common Technique Follower Server

Standalone A2A server application for polyhegel common technique followers.
Supports all common cross-domain technique followers via configuration.
"""

import os
import sys
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from polyhegel.agents.common.cards import (
    create_stakeholder_analysis_follower_card,
    create_tradeoff_analysis_follower_card,
    create_risk_assessment_follower_card,
    create_consensus_builder_follower_card,
    create_scenario_planning_follower_card,
)
from polyhegel.agents.common.agents import (
    StakeholderAnalysisFollower,
    TradeoffAnalysisFollower,
    RiskAssessmentFollower,
    ConsensusBuilderFollower,
    ScenarioPlanningFollower,
)
from polyhegel.model_manager import ModelManager


# Configuration mapping for different follower types
FOLLOWER_CONFIG = {
    "stakeholder": {
        "agent_class": StakeholderAnalysisFollower,
        "card_function": create_stakeholder_analysis_follower_card,
        "default_port": 7002,
    },
    "tradeoff": {
        "agent_class": TradeoffAnalysisFollower,
        "card_function": create_tradeoff_analysis_follower_card,
        "default_port": 7003,
    },
    "risk": {
        "agent_class": RiskAssessmentFollower,
        "card_function": create_risk_assessment_follower_card,
        "default_port": 7004,
    },
    "consensus": {
        "agent_class": ConsensusBuilderFollower,
        "card_function": create_consensus_builder_follower_card,
        "default_port": 7005,
    },
    "scenario": {
        "agent_class": ScenarioPlanningFollower,
        "card_function": create_scenario_planning_follower_card,
        "default_port": 7006,
    },
}


def create_common_follower_server(
    follower_type: str,
    host: str = "0.0.0.0",
    port: int = None,
    model_name: str = "claude-3-haiku-20240307",
) -> A2AStarletteApplication:
    """
    Create A2A server application for a common technique follower

    Args:
        follower_type: Type of follower (stakeholder, tradeoff, risk, consensus, scenario)
        host: Server host address
        port: Server port (uses default for type if not specified)
        model_name: LLM model to use

    Returns:
        Configured A2AStarletteApplication
    """
    if follower_type not in FOLLOWER_CONFIG:
        raise ValueError(f"Unknown follower type: {follower_type}. Available: {list(FOLLOWER_CONFIG.keys())}")

    config = FOLLOWER_CONFIG[follower_type]

    # Use default port if not specified
    if port is None:
        port = config["default_port"]

    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_class = config["agent_class"]
    agent_executor = agent_class(model=model)

    # Create agent card
    card_function = config["card_function"]
    agent_card = card_function(base_url=f"http://{host}:{port}")

    # Set up request handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    # Create server application
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return server


def main():
    """Main entry point for common follower server"""
    # Get follower type from environment or command line
    follower_type = os.getenv("POLYHEGEL_FOLLOWER_TYPE")
    if not follower_type and len(sys.argv) > 1:
        follower_type = sys.argv[1]

    if not follower_type:
        print("Error: POLYHEGEL_FOLLOWER_TYPE environment variable or command line argument required")
        print(f"Available types: {list(FOLLOWER_CONFIG.keys())}")
        sys.exit(1)

    if follower_type not in FOLLOWER_CONFIG:
        print(f"Error: Unknown follower type '{follower_type}'")
        print(f"Available types: {list(FOLLOWER_CONFIG.keys())}")
        sys.exit(1)

    # Configuration from environment
    host = os.getenv("POLYHEGEL_FOLLOWER_HOST", "0.0.0.0")
    port = os.getenv("POLYHEGEL_FOLLOWER_PORT")
    if port:
        port = int(port)
    model_name = os.getenv("POLYHEGEL_FOLLOWER_MODEL", "claude-3-haiku-20240307")

    # Use default port if not specified
    if port is None:
        port = FOLLOWER_CONFIG[follower_type]["default_port"]

    print(f"Starting Polyhegel {follower_type.title()} Analysis Follower Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Follower type: {follower_type}")

    # Create and run server
    server = create_common_follower_server(
        follower_type=follower_type,
        host=host,
        port=port,
        model_name=model_name,
    )

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
