"""
A2A Authentication and Security Configuration

Provides authentication, authorization, and security middleware for
polyhegel A2A agent communication.
"""

import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import os
import logging

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent role definitions for authorization"""

    LEADER = "leader"
    FOLLOWER = "follower"
    SIMULATION = "simulation"
    CLIENT = "client"
    ADMIN = "admin"


class Permission(Enum):
    """Permission definitions for agent operations"""

    GENERATE_THEMES = "generate_themes"
    DEVELOP_STRATEGIES = "develop_strategies"
    ACCESS_AGENT_CARDS = "access_agent_cards"
    EXECUTE_SIMULATIONS = "execute_simulations"
    MANAGE_AGENTS = "manage_agents"
    VIEW_METRICS = "view_metrics"


@dataclass
class AgentCredentials:
    """Agent authentication credentials"""

    agent_id: str
    api_key: str
    role: AgentRole
    permissions: Set[Permission]
    created_at: float
    expires_at: Optional[float] = None
    metadata: Optional[Dict] = None


@dataclass
class SecurityConfig:
    """Security configuration for A2A agents"""

    jwt_secret: str
    api_key_header: str = "X-Polyhegel-API-Key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    require_tls: bool = True
    rate_limit_per_minute: int = 100
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    allowed_origins: Optional[List[str]] = None

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create security config from environment variables"""
        return cls(
            jwt_secret=os.getenv("POLYHEGEL_JWT_SECRET", cls._generate_secret()),
            api_key_header=os.getenv("POLYHEGEL_API_KEY_HEADER", "X-Polyhegel-API-Key"),
            jwt_algorithm=os.getenv("POLYHEGEL_JWT_ALGORITHM", "HS256"),
            jwt_expiration_hours=int(os.getenv("POLYHEGEL_JWT_EXPIRATION_HOURS", "24")),
            require_tls=os.getenv("POLYHEGEL_REQUIRE_TLS", "true").lower() == "true",
            rate_limit_per_minute=int(os.getenv("POLYHEGEL_RATE_LIMIT", "100")),
            max_request_size=int(os.getenv("POLYHEGEL_MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
            allowed_origins=(
                [origin.strip() for origin in os.getenv("POLYHEGEL_ALLOWED_ORIGINS", "").split(",")]
                if os.getenv("POLYHEGEL_ALLOWED_ORIGINS")
                else None
            ),
        )

    @staticmethod
    def _generate_secret() -> str:
        """Generate a secure random secret"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()


class A2AAuthManager:
    """Manages A2A agent authentication and authorization"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self._agent_credentials: Dict[str, AgentCredentials] = {}
        self._api_key_to_agent: Dict[str, str] = {}
        self._setup_default_agents()

        # Security headers
        self.security = HTTPBearer(auto_error=False)

    def _setup_default_agents(self):
        """Setup default agent credentials"""
        default_agents: List[Dict[str, Any]] = [
            {
                "agent_id": "polyhegel-leader",
                "role": AgentRole.LEADER,
                "permissions": {Permission.GENERATE_THEMES, Permission.ACCESS_AGENT_CARDS},
            },
            {
                "agent_id": "polyhegel-follower-resource",
                "role": AgentRole.FOLLOWER,
                "permissions": {Permission.DEVELOP_STRATEGIES, Permission.ACCESS_AGENT_CARDS},
            },
            {
                "agent_id": "polyhegel-follower-security",
                "role": AgentRole.FOLLOWER,
                "permissions": {Permission.DEVELOP_STRATEGIES, Permission.ACCESS_AGENT_CARDS},
            },
            {
                "agent_id": "polyhegel-follower-value",
                "role": AgentRole.FOLLOWER,
                "permissions": {Permission.DEVELOP_STRATEGIES, Permission.ACCESS_AGENT_CARDS},
            },
            {
                "agent_id": "polyhegel-follower-general",
                "role": AgentRole.FOLLOWER,
                "permissions": {Permission.DEVELOP_STRATEGIES, Permission.ACCESS_AGENT_CARDS},
            },
            {
                "agent_id": "polyhegel-simulation",
                "role": AgentRole.SIMULATION,
                "permissions": {Permission.EXECUTE_SIMULATIONS, Permission.ACCESS_AGENT_CARDS, Permission.VIEW_METRICS},
            },
        ]

        for agent_config in default_agents:
            self.create_agent_credentials(
                agent_id=agent_config["agent_id"], role=agent_config["role"], permissions=agent_config["permissions"]
            )

    def create_agent_credentials(
        self, agent_id: str, role: AgentRole, permissions: Set[Permission], expires_hours: Optional[int] = None
    ) -> AgentCredentials:
        """Create new agent credentials"""

        # Generate secure API key
        api_key = self._generate_api_key(agent_id)

        # Calculate expiration
        expires_at = None
        if expires_hours:
            expires_at = time.time() + (expires_hours * 3600)

        credentials = AgentCredentials(
            agent_id=agent_id,
            api_key=api_key,
            role=role,
            permissions=permissions,
            created_at=time.time(),
            expires_at=expires_at,
            metadata={"created_by": "system"},
        )

        # Store credentials
        self._agent_credentials[agent_id] = credentials
        self._api_key_to_agent[api_key] = agent_id

        logger.info(f"Created credentials for agent {agent_id} with role {role.value}")
        return credentials

    def _generate_api_key(self, agent_id: str) -> str:
        """Generate secure API key for agent"""
        # Create deterministic yet secure API key
        seed = f"{agent_id}:{self.config.jwt_secret}:{time.time()}"
        return f"pk_{hashlib.sha256(seed.encode()).hexdigest()[:32]}"

    def verify_api_key(self, api_key: str) -> Optional[AgentCredentials]:
        """Verify API key and return agent credentials"""
        agent_id = self._api_key_to_agent.get(api_key)
        if not agent_id:
            return None

        credentials = self._agent_credentials.get(agent_id)
        if not credentials:
            return None

        # Check expiration
        if credentials.expires_at and time.time() > credentials.expires_at:
            logger.warning(f"Expired credentials for agent {agent_id}")
            return None

        return credentials

    def create_jwt_token(self, agent_id: str, additional_claims: Dict = None) -> str:
        """Create JWT token for agent"""
        credentials = self._agent_credentials.get(agent_id)
        if not credentials:
            raise ValueError(f"Agent {agent_id} not found")

        now = time.time()
        payload = {
            "agent_id": agent_id,
            "role": credentials.role.value,
            "permissions": [p.value for p in credentials.permissions],
            "iat": now,
            "exp": now + (self.config.jwt_expiration_hours * 3600),
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
        return str(token)

    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm])
            return dict(payload)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def check_permission(self, credentials: AgentCredentials, required_permission: Permission) -> bool:
        """Check if agent has required permission"""
        return required_permission in credentials.permissions

    def get_agent_credentials(self, agent_id: str) -> Optional[AgentCredentials]:
        """Get agent credentials by ID"""
        return self._agent_credentials.get(agent_id)

    def list_agents(self) -> List[AgentCredentials]:
        """List all registered agents"""
        return list(self._agent_credentials.values())

    def revoke_agent(self, agent_id: str) -> bool:
        """Revoke agent credentials"""
        credentials = self._agent_credentials.pop(agent_id, None)
        if credentials:
            self._api_key_to_agent.pop(credentials.api_key, None)
            logger.info(f"Revoked credentials for agent {agent_id}")
            return True
        return False


# Dependency injection for FastAPI
_auth_manager_instance: Optional[A2AAuthManager] = None


def get_auth_manager() -> A2AAuthManager:
    """Get auth manager instance"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        config = SecurityConfig.from_env()
        _auth_manager_instance = A2AAuthManager(config)
    return _auth_manager_instance


async def verify_api_key_auth(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    auth_manager: A2AAuthManager = Depends(get_auth_manager),
) -> AgentCredentials:
    """FastAPI dependency for API key authentication"""

    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")

    # Extract API key from Bearer token
    api_key = credentials.credentials

    agent_credentials = auth_manager.verify_api_key(api_key)
    if not agent_credentials:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return agent_credentials


def require_permission(permission: Permission):
    """Decorator factory for permission-based authorization"""

    def permission_dependency(
        credentials: AgentCredentials = Depends(verify_api_key_auth),
        auth_manager: A2AAuthManager = Depends(get_auth_manager),
    ) -> AgentCredentials:
        if not auth_manager.check_permission(credentials, permission):
            raise HTTPException(status_code=403, detail=f"Permission {permission.value} required")
        return credentials

    return permission_dependency


def require_role(required_role: AgentRole):
    """Decorator factory for role-based authorization"""

    def role_dependency(credentials: AgentCredentials = Depends(verify_api_key_auth)) -> AgentCredentials:
        if credentials.role != required_role:
            raise HTTPException(status_code=403, detail=f"Role {required_role.value} required")
        return credentials

    return role_dependency


# Rate limiting (simple in-memory implementation)
class RateLimiter:
    """Simple rate limiter for API requests"""

    def __init__(self, max_requests: int = 100, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self._requests: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        window_start = now - self.window_seconds

        # Get or create request history
        if key not in self._requests:
            self._requests[key] = []

        requests = self._requests[key]

        # Remove old requests outside window
        requests[:] = [req_time for req_time in requests if req_time > window_start]

        # Check limit
        if len(requests) >= self.max_requests:
            return False

        # Add current request
        requests.append(now)
        return True


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        config = SecurityConfig.from_env()
        _rate_limiter = RateLimiter(max_requests=config.rate_limit_per_minute)
    return _rate_limiter


async def rate_limit_dependency(
    credentials: AgentCredentials = Depends(verify_api_key_auth), rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    """FastAPI dependency for rate limiting"""
    if not rate_limiter.is_allowed(credentials.agent_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return credentials
