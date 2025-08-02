"""
Follower server implementation for Polyhegel framework.
"""

import os
import uvicorn
from polyhegel.model_manager import ModelManager
from polyhegel.strategic_techniques import StrategyDomain
from typing import Optional


def create_follower_server(
    host: str = "localhost",
    port: int = 8001,
    model_name: str = "claude-3-haiku-20240307",
    specialization_domain: Optional[StrategyDomain] = None,
    enable_auth: bool = True,
):
    """
    Create a follower server with specified configuration.

    Args:
        host (str): Server host address
        port (int): Server port
        model_name (str): Name of the model to use
        specialization_domain (Optional[StrategyDomain]): Specialized strategic domain
        enable_auth (bool): Whether to enable authentication

    Returns:
        A configured follower server instance
    """
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    class FollowerServer:
        def __init__(self, model, config):
            self.model = model
            self.config = config

        def build(self):
            # Minimal viable implementation
            return self

    return FollowerServer(
        model,
        {
            "host": host,
            "port": port,
            "model_name": model_name,
            "specialization_domain": specialization_domain,
            "enable_auth": enable_auth,
        },
    )


def main():
    """Entry point for follower server"""
    host = os.getenv("POLYHEGEL_FOLLOWER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_FOLLOWER_PORT", "8001"))
    model_name = os.getenv("POLYHEGEL_FOLLOWER_MODEL", "claude-3-haiku-20240307")
    specialization_str = os.getenv("POLYHEGEL_SPECIALIZATION_DOMAIN")

    # Map string to StrategyDomain if provided
    specialization_domain = StrategyDomain[specialization_str.upper()] if specialization_str else None

    server = create_follower_server(
        host=host, port=port, model_name=model_name, specialization_domain=specialization_domain
    )

    app = server.build()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
