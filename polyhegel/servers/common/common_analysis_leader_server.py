#!/usr/bin/env python3
"""
A2A Common Analysis Leader Server

Standalone A2A server application for polyhegel CommonAnalysisLeader.
Coordinates cross-domain analytical techniques via A2A protocol.
"""

import os
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from polyhegel.agents.common.cards import create_common_analysis_leader_card
from polyhegel.agents.common.agents import CommonAnalysisLeader
from polyhegel.model_manager import ModelManager


def create_common_leader_server(
    host: str = "0.0.0.0",
    port: int = 7001,
    model_name: str = "claude-3-haiku-20240307",
    max_techniques: int = 3,
) -> A2AStarletteApplication:
    """
    Create A2A server application for CommonAnalysisLeader

    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        max_techniques: Maximum number of techniques to coordinate

    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_executor = CommonAnalysisLeader(model=model, max_techniques=max_techniques)

    # Create agent card
    agent_card = create_common_analysis_leader_card(base_url=f"http://{host}:{port}")

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
    """Main entry point for common analysis leader server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_COMMON_LEADER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_COMMON_LEADER_PORT", "7001"))
    model_name = os.getenv("POLYHEGEL_COMMON_LEADER_MODEL", "claude-3-haiku-20240307")
    max_techniques = int(os.getenv("POLYHEGEL_MAX_TECHNIQUES", "3"))

    print("Starting Polyhegel Common Analysis Leader Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Max techniques: {max_techniques}")

    # Create and run server
    server = create_common_leader_server(
        host=host,
        port=port,
        model_name=model_name,
        max_techniques=max_techniques,
    )

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
