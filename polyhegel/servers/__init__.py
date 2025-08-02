"""
Compatibility and convenience wrappers for server modules.

This module provides compatibility imports and factory functions for creating
leader and follower servers in the Polyhegel framework.
"""

from .leader_server import create_leader_server
from .follower_server import create_follower_server

__all__ = ["create_leader_server", "create_follower_server"]
