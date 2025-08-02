#!/usr/bin/env python3
"""
A2A Product Roadmap Leader Agent Server

Standalone A2A server application for polyhegel Product Roadmap Leader Agent.
Handles product strategy analysis requests via A2A protocol.
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

from polyhegel.agents.product_roadmap_cards import create_product_roadmap_leader_card
from polyhegel.agents.product_roadmap_executors import ProductRoadmapLeaderExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.product_roadmap import ProductRoadmapDomain
from polyhegel.security import get_auth_manager

# from polyhegel.telemetry import setup_telemetry_for_agent  # TODO: Use when auth routes are added


def create_product_roadmap_leader_server(
    host: str = "0.0.0.0",
    port: int = 9006,
    model_name: str = "claude-3-haiku-20240307",
    focus_domains: list[ProductRoadmapDomain] = None,
    complexity_tolerance: str = "medium",
    enable_auth: bool = True,
) -> A2AStarletteApplication:
    """
    Create A2A server application for Product Roadmap Leader Agent

    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        focus_domains: Product roadmap domains to focus on
        complexity_tolerance: Acceptable complexity level for recommendations
        enable_auth: Enable authentication middleware

    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_executor = ProductRoadmapLeaderExecutor(
        model=model,
        focus_domains=focus_domains or list(ProductRoadmapDomain),
        complexity_tolerance=complexity_tolerance,
    )

    # Create agent card
    agent_card = create_product_roadmap_leader_card(base_url=f"http://{host}:{port}")

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
    # telemetry_collector = setup_telemetry_for_agent("polyhegel-product-leader")
    # telemetry_exporter = TelemetryExporter(telemetry_collector)  # TODO: Use when auth routes are added

    # TODO: Add monitoring and security configuration using proper Starlette routing
    # For now, returning basic server without additional routes

    return server


def main():
    """Main entry point for product roadmap leader server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_PRODUCT_LEADER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_PRODUCT_LEADER_PORT", "9006"))
    model_name = os.getenv("POLYHEGEL_PRODUCT_LEADER_MODEL", "claude-3-haiku-20240307")
    complexity_tolerance = os.getenv("POLYHEGEL_PRODUCT_COMPLEXITY_TOLERANCE", "medium")
    enable_auth = os.getenv("POLYHEGEL_ENABLE_AUTH", "true").lower() == "true"

    # Parse focus domains from environment
    focus_domains = []
    focus_domains_env = os.getenv("POLYHEGEL_PRODUCT_FOCUS_DOMAINS", "")
    if focus_domains_env:
        for domain_str in focus_domains_env.split(","):
            domain_str = domain_str.strip()
            try:
                domain = ProductRoadmapDomain(domain_str)
                focus_domains.append(domain)
            except ValueError:
                print(f"Warning: Invalid product roadmap domain '{domain_str}', skipping")

    print("Starting Polyhegel Product Roadmap Leader Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Focus domains: {[d.value for d in focus_domains] if focus_domains else 'all'}")
    print(f"Complexity tolerance: {complexity_tolerance}")
    print(f"Authentication: {'enabled' if enable_auth else 'disabled'}")

    # Create and run server
    server = create_product_roadmap_leader_server(
        host=host,
        port=port,
        model_name=model_name,
        focus_domains=focus_domains,
        complexity_tolerance=complexity_tolerance,
        enable_auth=enable_auth,
    )

    # Initialize auth manager and print credentials for development
    if enable_auth:
        auth_manager = get_auth_manager()
        leader_creds = auth_manager.get_agent_credentials("polyhegel-product-leader")
        if leader_creds:
            print(f"Product Roadmap Leader Agent API Key: {leader_creds.api_key}")
            print(
                f"Product Roadmap Leader Agent JWT Token: {auth_manager.create_jwt_token('polyhegel-product-leader')}"
            )

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
