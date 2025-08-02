"""
Leader server implementation for Polyhegel framework.
"""

import os
import uvicorn
from polyhegel.model_manager import ModelManager
from typing import List, Optional


def create_leader_server(
    host: str = "localhost",
    port: int = 8000,
    model_name: str = "claude-3-haiku-20240307",
    max_themes: int = 5,
    focus_domains: Optional[List[str]] = None,
    enable_auth: bool = True,
):
    """
    Create a leader server with specified configuration.

    Args:
        host (str): Server host address
        port (int): Server port
        model_name (str): Name of the model to use
        max_themes (int): Maximum number of strategic themes
        focus_domains (Optional[List[str]]): List of strategic focus domains
        enable_auth (bool): Whether to enable authentication

    Returns:
        A configured leader server instance
    """
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)

    class LeaderServer:
        def __init__(self, model, config):
            self.model = model
            self.config = config

        def build(self):
            # Minimal viable implementation
            return self

    return LeaderServer(
        model,
        {
            "host": host,
            "port": port,
            "model_name": model_name,
            "max_themes": max_themes,
            "focus_domains": focus_domains or [],
            "enable_auth": enable_auth,
        },
    )


def main():
    """Entry point for leader server"""
    host = os.getenv("POLYHEGEL_LEADER_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_LEADER_PORT", "8000"))
    model_name = os.getenv("POLYHEGEL_LEADER_MODEL", "claude-3-haiku-20240307")
    max_themes = int(os.getenv("POLYHEGEL_MAX_THEMES", "5"))
    focus_domains = os.getenv("POLYHEGEL_FOCUS_DOMAINS", "").split(",") if os.getenv("POLYHEGEL_FOCUS_DOMAINS") else []

    server = create_leader_server(
        host=host,
        port=port,
        model_name=model_name,
        max_themes=max_themes,
        focus_domains=focus_domains,
        enable_auth=True,  # Explicitly added
    )

    app = server.build()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
