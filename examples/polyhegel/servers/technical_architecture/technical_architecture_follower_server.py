#!/usr/bin/env python3
"""
A2A Technical Architecture Follower Agent Server

Standalone A2A server application for polyhegel Technical Architecture Follower Agent.
Handles specialized technical architecture development requests via A2A protocol.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add polyhegel to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from polyhegel.agents.technical_architecture_cards import create_technical_architecture_follower_card
from polyhegel.agents.technical_architecture_executors import TechnicalArchitectureFollowerExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.technical_architecture import TechnicalArchitectureDomain
from polyhegel.security import get_auth_manager

# from polyhegel.telemetry import setup_telemetry_for_agent  # TODO: Use when auth routes are added


def create_technical_architecture_follower_server(
    host: str = "0.0.0.0",
    port: int = 9002,
    model_name: str = "claude-3-haiku-20240307",
    specialization_domain: TechnicalArchitectureDomain = TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
    enable_auth: bool = True,
) -> A2AStarletteApplication:
    """
    Create A2A server application for Technical Architecture Follower Agent

    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        specialization_domain: Technical architecture domain specialization
        enable_auth: Enable authentication middleware

    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_executor = TechnicalArchitectureFollowerExecutor(
        model=model,
        specialization_domain=specialization_domain,
    )

    # Create agent card
    agent_card = create_technical_architecture_follower_card(
        specialization_domain=specialization_domain, base_url=f"http://{host}:{port}"
    )

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

    # Setup telemetry
    # telemetry_collector = setup_telemetry_for_agent(f"polyhegel-techarch-follower-{specialization_domain.value}")
    # telemetry_exporter = TelemetryExporter(telemetry_collector)  # TODO: Use when auth routes are added

    # TODO: Add monitoring and security configuration using proper Starlette routing
    # For now, returning basic server without additional routes

    return server


def main():
    """Main entry point for technical architecture follower server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_TECHARCH_FOLLOWER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_TECHARCH_FOLLOWER_PORT", "9002"))
    model_name = os.getenv("POLYHEGEL_TECHARCH_FOLLOWER_MODEL", "claude-3-haiku-20240307")
    enable_auth = os.getenv("POLYHEGEL_ENABLE_AUTH", "true").lower() == "true"

    # Parse specialization domain from environment
    specialization_domain_str = os.getenv("POLYHEGEL_TECHARCH_SPECIALIZATION_DOMAIN", "backend_architecture")
    try:
        specialization_domain = TechnicalArchitectureDomain(specialization_domain_str)
    except ValueError:
        print(f"Warning: Invalid specialization domain '{specialization_domain_str}', using backend_architecture")
        specialization_domain = TechnicalArchitectureDomain.BACKEND_ARCHITECTURE

    print("Starting Polyhegel Technical Architecture Follower Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Specialization: {specialization_domain.display_name}")
    print(f"Authentication: {'enabled' if enable_auth else 'disabled'}")

    # Create and run server
    server = create_technical_architecture_follower_server(
        host=host,
        port=port,
        model_name=model_name,
        specialization_domain=specialization_domain,
        enable_auth=enable_auth,
    )

    # Initialize auth manager and print credentials for development
    if enable_auth:
        auth_manager = get_auth_manager()
        agent_id = f"polyhegel-techarch-follower-{specialization_domain.value}"
        follower_creds = auth_manager.get_agent_credentials(agent_id)
        if follower_creds:
            print(f"Technical Architecture Follower Agent API Key: {follower_creds.api_key}")
            print(f"Technical Architecture Follower Agent JWT Token: {auth_manager.create_jwt_token(agent_id)}")

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
