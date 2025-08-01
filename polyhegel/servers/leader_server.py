#!/usr/bin/env python3
"""
A2A Leader Agent Server

Standalone A2A server application for polyhegel LeaderAgent.
Handles strategic theme generation requests via A2A protocol.
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
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

from polyhegel.agents.a2a_cards import create_leader_agent_card
from polyhegel.agents.a2a_executors import LeaderAgentExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.strategic_techniques import StrategyDomain
from polyhegel.security import AgentRole, Permission, SecurityConfig, get_auth_manager, require_permission, require_role
from polyhegel.telemetry import setup_telemetry_for_agent, A2AMonitoringMiddleware, TelemetryExporter


def create_leader_server(
    host: str = "0.0.0.0",
    port: int = 8001,
    model_name: str = "claude-3-haiku-20240307",
    focus_domains: list[StrategyDomain] = None,
    max_themes: int = 5,
    enable_auth: bool = True,
) -> A2AStarletteApplication:
    """
    Create A2A server application for LeaderAgent

    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        focus_domains: Strategic domains to focus on
        max_themes: Maximum number of themes to generate
        enable_auth: Enable authentication middleware

    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    # Create agent executor
    agent_executor = LeaderAgentExecutor(model=model, focus_domains=focus_domains or [], max_themes=max_themes)

    # Create agent card
    agent_card = create_leader_agent_card(base_url=f"http://{host}:{port}")

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
    telemetry_collector = setup_telemetry_for_agent("polyhegel-leader")
    telemetry_exporter = TelemetryExporter(telemetry_collector)

    # Add monitoring and security configuration if enabled
    if enable_auth:
        app = server.build()

        # Add telemetry middleware
        monitoring_middleware = A2AMonitoringMiddleware(telemetry_collector)
        app.middleware("http")(monitoring_middleware)

        # Add CORS middleware
        security_config = SecurityConfig.from_env()
        if security_config.allowed_origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=security_config.allowed_origins,
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"],
            )

        # Authentication endpoints
        @app.get("/auth/agent-info")
        async def get_agent_info(credentials=Depends(require_role(AgentRole.LEADER))):
            """Get authenticated agent information"""
            return {
                "agent_id": credentials.agent_id,
                "role": credentials.role.value,
                "permissions": [p.value for p in credentials.permissions],
            }

        @app.get("/auth/health")
        async def auth_health():
            """Health check endpoint"""
            return {"status": "healthy", "service": "polyhegel-leader-agent"}

        # Telemetry and monitoring endpoints
        @app.get("/metrics")
        async def get_metrics(credentials=Depends(require_permission(Permission.VIEW_METRICS))):
            """Get agent metrics"""
            return {
                "summary": telemetry_collector.get_summary(),
                "recent_events": [e.to_dict() for e in telemetry_collector.get_events(limit=50)],
                "recent_metrics": [m.to_dict() for m in telemetry_collector.get_metrics(limit=50)],
            }

        @app.get("/telemetry/summary")
        async def get_telemetry_summary(credentials=Depends(require_permission(Permission.VIEW_METRICS))):
            """Get telemetry summary"""
            return telemetry_collector.get_summary()

        @app.get("/telemetry/events")
        async def get_telemetry_events(
            limit: int = 100, credentials=Depends(require_permission(Permission.VIEW_METRICS))
        ):
            """Get recent telemetry events"""
            events = telemetry_collector.get_events(limit=limit)
            return {"events": [e.to_dict() for e in events]}

        @app.post("/telemetry/export")
        async def export_telemetry(
            filepath: str = "/tmp/leader-telemetry.json",
            credentials=Depends(require_permission(Permission.VIEW_METRICS)),
        ):
            """Export telemetry data to file"""
            telemetry_exporter.export_to_json_file(filepath)
            return {"status": "exported", "filepath": filepath}

        # Protected endpoints require theme generation permission
        @app.post("/generate-themes")
        async def generate_themes_endpoint(
            request: dict, credentials=Depends(require_permission(Permission.GENERATE_THEMES))
        ):
            """Protected theme generation endpoint"""
            # This would integrate with the A2A request handler
            return {"status": "authenticated", "agent_id": credentials.agent_id}

        return server

    return server


def main():
    """Main entry point for leader server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_LEADER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_LEADER_PORT", "8001"))
    model_name = os.getenv("POLYHEGEL_LEADER_MODEL", "claude-3-haiku-20240307")
    max_themes = int(os.getenv("POLYHEGEL_MAX_THEMES", "5"))
    enable_auth = os.getenv("POLYHEGEL_ENABLE_AUTH", "true").lower() == "true"

    # Parse focus domains from environment
    focus_domains = []
    focus_domains_env = os.getenv("POLYHEGEL_FOCUS_DOMAINS", "")
    if focus_domains_env:
        for domain_str in focus_domains_env.split(","):
            domain_str = domain_str.strip()
            try:
                domain = StrategyDomain(domain_str)
                focus_domains.append(domain)
            except ValueError:
                print(f"Warning: Invalid strategy domain '{domain_str}', skipping")

    print("Starting Polyhegel Leader Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Focus domains: {[d.value for d in focus_domains] if focus_domains else 'all'}")
    print(f"Max themes: {max_themes}")
    print(f"Authentication: {'enabled' if enable_auth else 'disabled'}")

    # Create and run server
    server = create_leader_server(
        host=host,
        port=port,
        model_name=model_name,
        focus_domains=focus_domains,
        max_themes=max_themes,
        enable_auth=enable_auth,
    )

    # Initialize auth manager and print credentials for development
    if enable_auth:
        auth_manager = get_auth_manager()
        leader_creds = auth_manager.get_agent_credentials("polyhegel-leader")
        if leader_creds:
            print(f"Leader Agent API Key: {leader_creds.api_key}")
            print(f"Leader Agent JWT Token: {auth_manager.create_jwt_token('polyhegel-leader')}")

    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
