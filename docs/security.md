# Polyhegel A2A Security Configuration

This document describes the security features and configuration options for polyhegel A2A agents.

## Overview

Polyhegel implements comprehensive security for A2A agent communication including:

- **API Key Authentication**: Secure agent identification using API keys
- **JWT Token Authorization**: Stateless authorization with role-based permissions
- **TLS/SSL Encryption**: Encrypted communication between agents
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Agent Identity Verification**: Cryptographic agent authentication
- **Role-Based Access Control**: Granular permission management

## Authentication Methods

### API Key Authentication

Each agent is assigned a unique API key for identification:

```python
# Agent credentials are automatically generated
pk_a1b2c3d4e5f6...  # 32-character hex API key
```

API keys are passed in the `Authorization` header:
```http
Authorization: Bearer pk_a1b2c3d4e5f6...
```

### JWT Token Authentication

JWT tokens provide stateless authorization with embedded permissions:

```json
{
  "agent_id": "polyhegel-leader",
  "role": "leader",
  "permissions": ["generate_themes", "access_agent_cards"],
  "iat": 1640995200,
  "exp": 1641081600
}
```

## Agent Roles and Permissions

### Roles

- **LEADER**: Generates strategic themes and coordinates strategy development
- **FOLLOWER**: Develops detailed strategies from themes
- **SIMULATION**: Orchestrates strategic simulations and analysis
- **CLIENT**: External clients connecting to agents
- **ADMIN**: Administrative access to all agent functions

### Permissions

- **GENERATE_THEMES**: Generate strategic themes
- **DEVELOP_STRATEGIES**: Develop detailed implementation strategies
- **ACCESS_AGENT_CARDS**: Access agent capability descriptions
- **EXECUTE_SIMULATIONS**: Run strategic simulations
- **MANAGE_AGENTS**: Administrative agent management
- **VIEW_METRICS**: Access telemetry and monitoring data

## Environment Configuration

### Basic Security Settings

```bash
# Authentication
POLYHEGEL_ENABLE_AUTH=true
POLYHEGEL_JWT_SECRET=your-secret-key-here
POLYHEGEL_JWT_EXPIRATION_HOURS=24

# Rate limiting
POLYHEGEL_RATE_LIMIT=100  # requests per minute
POLYHEGEL_MAX_REQUEST_SIZE=10485760  # 10MB

# CORS
POLYHEGEL_ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com
```

### TLS/SSL Configuration

```bash
# TLS certificates
POLYHEGEL_TLS_CERT_FILE=/path/to/cert.pem
POLYHEGEL_TLS_KEY_FILE=/path/to/key.pem
POLYHEGEL_TLS_CA_FILE=/path/to/ca.pem

# TLS settings
POLYHEGEL_TLS_VERIFY_SSL=true
POLYHEGEL_TLS_REQUIRE_CLIENT_CERT=false

# Auto-generate certificates (development only)
POLYHEGEL_TLS_AUTO_GENERATE=false
POLYHEGEL_TLS_CERT_DIR=./certs
POLYHEGEL_TLS_CERT_VALIDITY_DAYS=365
```

### Agent API Keys

```bash
# Set API keys for each agent
POLYHEGEL_LEADER_API_KEY=pk_leader_key_here
POLYHEGEL_FOLLOWER_RESOURCE_API_KEY=pk_resource_key_here
POLYHEGEL_FOLLOWER_SECURITY_API_KEY=pk_security_key_here
POLYHEGEL_FOLLOWER_VALUE_API_KEY=pk_value_key_here
POLYHEGEL_FOLLOWER_GENERAL_API_KEY=pk_general_key_here

# Or use JWT tokens
POLYHEGEL_LEADER_JWT_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Usage Examples

### Starting Secure Agent Server

```python
from polyhegel.servers import create_leader_server
from polyhegel.security import TLSConfig, setup_tls_for_agent

# Setup TLS
tls_config = setup_tls_for_agent("polyhegel-leader")

# Create secure server
server = create_leader_server(
    host="0.0.0.0",
    port=8001,
    enable_auth=True
)

# Run with TLS
import uvicorn
uvicorn.run(
    server.build(),
    host="0.0.0.0", 
    port=8001,
    **tls_config.get_uvicorn_ssl_config()
)
```

### Connecting with Authentication

```python
from polyhegel.clients import PolyhegelA2AClient, A2AAgentEndpoints

# Configure endpoints with authentication
endpoints = A2AAgentEndpoints(
    leader_url="https://leader.example.com:8001",
    api_keys={
        "leader": "pk_leader_key_here"
    }
)

# Use authenticated client
async with PolyhegelA2AClient(endpoints) as client:
    strategies = await client.generate_hierarchical_strategies(
        "Strategic challenge here"
    )
```

### Custom Permission Checks

```python
from polyhegel.security import require_permission, Permission
from fastapi import Depends

@app.post("/custom-endpoint")
async def custom_endpoint(
    credentials = Depends(require_permission(Permission.GENERATE_THEMES))
):
    return {"agent_id": credentials.agent_id}
```

## Security Best Practices

### Production Deployment

1. **Use Strong Secrets**: Generate cryptographically secure JWT secrets
2. **Enable TLS**: Always use TLS/SSL in production
3. **Verify Certificates**: Enable certificate verification
4. **Rotate Keys**: Regularly rotate API keys and JWT secrets
5. **Monitor Access**: Log and monitor authentication attempts
6. **Network Security**: Use firewalls and VPNs for agent communication

### Development

1. **Disable Auth for Testing**: Set `POLYHEGEL_ENABLE_AUTH=false` for local development
2. **Auto-Generate Certs**: Use `POLYHEGEL_TLS_AUTO_GENERATE=true` for dev certificates
3. **Log Credentials**: Development servers log API keys and tokens for testing

### Key Management

```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_hex(32))"

# Generate API key
python -c "import hashlib, uuid; print(f'pk_{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]}')"
```

## Certificate Management

### Auto-Generated Certificates (Development)

```python
from polyhegel.security.tls_config import CertificateManager, TLSConfig

config = TLSConfig(auto_generate_certs=True, cert_dir="./certs")
cert_manager = CertificateManager(config)

# Generate CA and agent certificates
certificates = cert_manager.setup_agent_certificates()
```

### Custom Certificates (Production)

1. Generate or obtain TLS certificates from a trusted CA
2. Place certificates in secure location
3. Configure file paths in environment variables
4. Ensure proper file permissions (600 for private keys)

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check API key format and expiration
2. **Certificate Errors**: Verify certificate paths and permissions
3. **Rate Limited**: Reduce request frequency or increase limits
4. **CORS Blocked**: Add client origin to allowed origins list

### Debug Authentication

```python
from polyhegel.security import get_auth_manager

auth_manager = get_auth_manager()

# List all agents
for agent in auth_manager.list_agents():
    print(f"Agent: {agent.agent_id}")
    print(f"Role: {agent.role.value}")
    print(f"API Key: {agent.api_key}")
    print(f"Permissions: {[p.value for p in agent.permissions]}")
```

### Verify TLS Configuration

```python
from polyhegel.security.tls_config import TLSConfig

config = TLSConfig.from_env()
ssl_context = config.create_ssl_context(server_side=True)
print(f"TLS configured: {ssl_context is not None}")
```

## API Reference

### Security Classes

- `AgentCredentials`: Agent authentication credentials
- `SecurityConfig`: Security configuration settings
- `A2AAuthManager`: Authentication and authorization manager
- `TLSConfig`: TLS/SSL configuration
- `CertificateManager`: Certificate generation and management

### FastAPI Dependencies

- `verify_api_key_auth`: Verify API key authentication
- `require_permission()`: Require specific permission
- `require_role()`: Require specific agent role
- `rate_limit_dependency`: Apply rate limiting

See the source code for detailed API documentation.