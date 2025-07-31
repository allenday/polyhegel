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

from polyhegel.agents.a2a_cards import create_leader_agent_card, create_leader_agent_skills
from polyhegel.agents.a2a_executors import LeaderAgentExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.strategic_techniques import StrategyDomain


def create_leader_server(
    host: str = "0.0.0.0",
    port: int = 8001,
    model_name: str = "claude-3-haiku-20240307",
    focus_domains: list[StrategyDomain] = None,
    max_themes: int = 5
) -> A2AStarletteApplication:
    """
    Create A2A server application for LeaderAgent
    
    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        focus_domains: Strategic domains to focus on
        max_themes: Maximum number of themes to generate
        
    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)
    
    # Create agent executor
    agent_executor = LeaderAgentExecutor(
        model=model,
        focus_domains=focus_domains or [],
        max_themes=max_themes
    )
    
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
    
    return server


def main():
    """Main entry point for leader server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_LEADER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_LEADER_PORT", "8001"))
    model_name = os.getenv("POLYHEGEL_LEADER_MODEL", "claude-3-haiku-20240307")
    max_themes = int(os.getenv("POLYHEGEL_MAX_THEMES", "5"))
    
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
    
    print(f"Starting Polyhegel Leader Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Focus domains: {[d.value for d in focus_domains] if focus_domains else 'all'}")
    print(f"Max themes: {max_themes}")
    
    # Create and run server
    server = create_leader_server(
        host=host,
        port=port,
        model_name=model_name,
        focus_domains=focus_domains,
        max_themes=max_themes
    )
    
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()