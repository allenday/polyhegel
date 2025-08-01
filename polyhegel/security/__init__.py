"""
Polyhegel Security Module

Authentication, authorization, and security utilities for A2A agents.
"""

from .a2a_auth import (
    AgentRole,
    Permission,
    AgentCredentials,
    SecurityConfig,
    A2AAuthManager,
    get_auth_manager,
    verify_api_key_auth,
    require_permission,
    require_role,
    RateLimiter,
    get_rate_limiter,
    rate_limit_dependency,
)

__all__ = [
    "AgentRole",
    "Permission",
    "AgentCredentials",
    "SecurityConfig",
    "A2AAuthManager",
    "get_auth_manager",
    "verify_api_key_auth",
    "require_permission",
    "require_role",
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit_dependency",
]
