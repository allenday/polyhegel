#!/usr/bin/env python3
"""
A2A Product Roadmap Follower Agent Server

Standalone A2A server application for polyhegel Product Roadmap Follower Agents.
Handles specialized product strategy development requests via A2A protocol.
"""

import os
import sys
import uvicorn
from pathlib import Path
from typing import Optional

# Add polyhegel to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from polyhegel.agents.product_roadmap_cards import create_product_roadmap_follower_card
from polyhegel.agents.product_roadmap_executors import ProductRoadmapFollowerExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.product_roadmap import ProductRoadmapDomain
from polyhegel.security import get_auth_manager

# from polyhegel.telemetry import setup_telemetry_for_agent  # TODO: Use when auth routes are added


def create_product_roadmap_follower_server(
    specialization_domain: ProductRoadmapDomain,
    host: str = "0.0.0.0",
    port: int = 9007,
    model_name: str = "claude-3-haiku-20240307",
    enable_auth: bool = True,
) -> A2AStarletteApplication:
    """
    Create A2A server application for Product Roadmap Follower Agent

    Args:
        specialization_domain: Product roadmap domain specialization
        host: Server host address
        port: Server port
        model_name: LLM model to use
        enable_auth: Enable authentication middleware

    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_executor = ProductRoadmapFollowerExecutor(
        model=model,
        specialization_domain=specialization_domain,
    )

    # Create agent card
    agent_card = create_product_roadmap_follower_card(
        specialization_domain=specialization_domain,
        base_url=f"http://{host}:{port}",
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
    # telemetry_collector = setup_telemetry_for_agent(f"polyhegel-product-follower-{specialization_domain.value}")
    # telemetry_exporter = TelemetryExporter(telemetry_collector)  # TODO: Use when auth routes are added

    # TODO: Add monitoring and security configuration using proper Starlette routing
    # For now, returning basic server without additional routes

    return server


def get_specialization_from_env() -> Optional[ProductRoadmapDomain]:
    """Get specialization domain from environment variable"""
    specialization_str = os.getenv("POLYHEGEL_PRODUCT_FOLLOWER_SPECIALIZATION", "")
    if not specialization_str:
        return None

    try:
        return ProductRoadmapDomain(specialization_str)
    except ValueError:
        print(f"Warning: Invalid product roadmap domain '{specialization_str}'")
        return None


def main():
    """Main entry point for product roadmap follower server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_PRODUCT_FOLLOWER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_PRODUCT_FOLLOWER_PORT", "9007"))
    model_name = os.getenv("POLYHEGEL_PRODUCT_FOLLOWER_MODEL", "claude-3-haiku-20240307")
    enable_auth = os.getenv("POLYHEGEL_ENABLE_AUTH", "true").lower() == "true"

    # Get specialization domain
    specialization_domain = get_specialization_from_env()
    if not specialization_domain:
        print("Error: POLYHEGEL_PRODUCT_FOLLOWER_SPECIALIZATION environment variable must be set")
        print("Valid values: feature_prioritization, market_analysis, strategic_planning, resource_management")
        sys.exit(1)

    print("Starting Polyhegel Product Roadmap Follower Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Specialization: {specialization_domain.display_name}")
    print(f"Authentication: {'enabled' if enable_auth else 'disabled'}")

    # Create and run server
    server = create_product_roadmap_follower_server(
        specialization_domain=specialization_domain,
        host=host,
        port=port,
        model_name=model_name,
        enable_auth=enable_auth,
    )

    # Initialize auth manager and print credentials for development
    if enable_auth:
        auth_manager = get_auth_manager()
        agent_id = f"polyhegel-product-follower-{specialization_domain.value}"
        follower_creds = auth_manager.get_agent_credentials(agent_id)
        if follower_creds:
            print(f"Product Roadmap Follower Agent API Key: {follower_creds.api_key}")
            print(f"Product Roadmap Follower Agent JWT Token: {auth_manager.create_jwt_token(agent_id)}")

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
