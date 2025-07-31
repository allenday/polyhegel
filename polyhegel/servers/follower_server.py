#!/usr/bin/env python3
"""
A2A Follower Agent Server

Standalone A2A server application for polyhegel FollowerAgent.
Handles detailed strategy development requests via A2A protocol.
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

from polyhegel.agents.a2a_cards import create_follower_agent_card
from polyhegel.agents.a2a_executors import FollowerAgentExecutor
from polyhegel.model_manager import ModelManager
from polyhegel.strategic_techniques import StrategyDomain


def create_follower_server(
    host: str = "0.0.0.0",
    port: int = 8002,
    model_name: str = "claude-3-haiku-20240307",
    specialization_domain: Optional[StrategyDomain] = None
) -> A2AStarletteApplication:
    """
    Create A2A server application for FollowerAgent
    
    Args:
        host: Server host address
        port: Server port
        model_name: LLM model to use
        specialization_domain: Strategic domain specialization
        
    Returns:
        Configured A2AStarletteApplication
    """
    # Initialize model
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)
    
    # Create agent executor
    agent_executor = FollowerAgentExecutor(
        model=model,
        specialization_domain=specialization_domain
    )
    
    # Create agent card
    agent_card = create_follower_agent_card(
        specialization_domain=specialization_domain,
        base_url=f"http://{host}:{port}"
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
    
    return server


def main():
    """Main entry point for follower server"""
    # Configuration from environment
    host = os.getenv("POLYHEGEL_FOLLOWER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_FOLLOWER_PORT", "8002"))
    model_name = os.getenv("POLYHEGEL_FOLLOWER_MODEL", "claude-3-haiku-20240307")
    
    # Parse specialization domain from environment
    specialization_domain = None
    domain_env = os.getenv("POLYHEGEL_SPECIALIZATION_DOMAIN", "")
    if domain_env:
        try:
            specialization_domain = StrategyDomain(domain_env.strip())
        except ValueError:
            print(f"Warning: Invalid specialization domain '{domain_env}', using general agent")
    
    print(f"Starting Polyhegel Follower Agent Server...")
    print(f"Host: {host}:{port}")
    print(f"Model: {model_name}")
    print(f"Specialization: {specialization_domain.value if specialization_domain else 'general'}")
    
    # Create and run server
    server = create_follower_server(
        host=host,
        port=port,
        model_name=model_name,
        specialization_domain=specialization_domain
    )
    
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()