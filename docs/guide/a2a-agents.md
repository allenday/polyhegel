# A2A Agent Guide

## Introduction

The Agent-to-Agent (A2A) system enables distributed strategic planning through specialized AI agents. This guide covers how to set up, configure, and use A2A agents for hierarchical strategy development.

## Agent Roles and Specializations

### Leader Agent
**Purpose**: Generates strategic themes and coordinates planning

**When to Use**:
- High-level strategic challenges
- Theme generation for complex problems
- Coordination of multiple strategic domains

**Example Usage**:
```python
from polyhegel.clients.a2a_client import PolyhegelA2AClient, A2AAgentEndpoints

# Configure endpoints
endpoints = A2AAgentEndpoints.from_env()

# Create client
async with PolyhegelA2AClient(endpoints) as client:
    themes = await client.generate_themes(
        strategic_challenge="Enter the enterprise AI market",
        max_themes=5
    )
    
    for theme in themes:
        print(f"Theme: {theme['title']}")
        print(f"Domain: {theme['domain']}")
```

### Follower Agents

#### Resource Acquisition Agent
**Specialization**: Resource optimization, capacity planning, supply chain

**Best For**:
- Funding strategies
- Technology acquisition
- Human resource planning
- Infrastructure scaling

```python
# Develop resource-focused strategy
resource_strategy = await client.develop_strategy(
    theme={"title": "Build Development Team", "domain": "resource_acquisition"},
    domain="resource"
)
```

#### Strategic Security Agent  
**Specialization**: Risk management, threat mitigation, compliance

**Best For**:
- Risk assessment strategies
- Security implementation plans
- Compliance frameworks
- Crisis response planning

```python
# Develop security-focused strategy
security_strategy = await client.develop_strategy(
    theme={"title": "Data Protection Framework", "domain": "strategic_security"},
    domain="security"
)
```

#### Value Catalysis Agent
**Specialization**: Value creation, innovation, market positioning

**Best For**:
- Business model innovation
- Market entry strategies
- Value proposition development
- Partnership strategies

```python
# Develop value-focused strategy
value_strategy = await client.develop_strategy(
    theme={"title": "Customer Value Creation", "domain": "value_catalysis"},
    domain="value"
)
```

#### General Purpose Agent
**Specialization**: Broad strategic planning, integration

**Best For**:
- Cross-domain strategies
- General planning needs
- Integration of specialized approaches

## Configuration and Setup

### Environment Configuration
Set up your A2A environment using environment variables:

```bash
# Agent URLs
export POLYHEGEL_LEADER_URL="https://leader.polyhegel.com"
export POLYHEGEL_FOLLOWER_RESOURCE_URL="https://resource.polyhegel.com"
export POLYHEGEL_FOLLOWER_SECURITY_URL="https://security.polyhegel.com"
export POLYHEGEL_FOLLOWER_VALUE_URL="https://value.polyhegel.com"
export POLYHEGEL_FOLLOWER_GENERAL_URL="https://general.polyhegel.com"

# Authentication
export POLYHEGEL_LEADER_API_KEY="your-leader-api-key"
export POLYHEGEL_FOLLOWER_RESOURCE_JWT_TOKEN="your-resource-jwt-token"
# ... other agent credentials
```

### Manual Configuration
```python
from polyhegel.clients.a2a_client import A2AAgentEndpoints

# Manual endpoint configuration
endpoints = A2AAgentEndpoints(
    leader_url="http://localhost:8001",
    follower_resource_url="http://localhost:8002",
    follower_security_url="http://localhost:8003",
    follower_value_url="http://localhost:8004",
    follower_general_url="http://localhost:8005",
    api_keys={
        "leader": "api-key-leader",
        "follower_resource": "api-key-resource"
    }
)
```

## Hierarchical Strategy Generation

### Full Workflow Example
```python
async def generate_comprehensive_strategy():
    endpoints = A2AAgentEndpoints.from_env()
    
    async with PolyhegelA2AClient(endpoints, timeout=60.0) as client:
        # Step 1: Verify agent availability
        availability = await client.verify_agent_availability()
        print(f"Available agents: {[k for k, v in availability.items() if v]}")
        
        # Step 2: Generate hierarchical strategies
        strategies = await client.generate_hierarchical_strategies(
            strategic_challenge="Launch AI-powered customer service platform",
            max_themes=4,
            context={"market": "enterprise", "timeline": "12 months"}
        )
        
        # Step 3: Process results
        for i, strategy_chain in enumerate(strategies):
            print(f"\n--- Strategy {i+1} ---")
            print(f"Title: {strategy_chain.strategy.title}")
            print(f"Timeline: {strategy_chain.strategy.estimated_timeline}")
            print(f"Steps: {len(strategy_chain.strategy.steps)}")
            
            for j, step in enumerate(strategy_chain.strategy.steps):
                print(f"  {j+1}. {step.action}")
                print(f"     Outcome: {step.outcome}")

# Run the workflow
await generate_comprehensive_strategy()
```

### Domain-Specific Strategy Development
```python
async def develop_domain_strategies():
    endpoints = A2AAgentEndpoints.from_env()
    
    async with PolyhegelA2AClient(endpoints) as client:
        # Define domain-specific themes
        themes = [
            {"title": "Secure Customer Data Platform", "domain": "strategic_security"},
            {"title": "Scale Engineering Team", "domain": "resource_acquisition"},
            {"title": "Create Competitive Differentiation", "domain": "value_catalysis"}
        ]
        
        # Generate strategies for each domain
        domain_strategies = {}
        for theme in themes:
            strategy = await client.develop_strategy(theme, theme["domain"])
            domain_strategies[theme["domain"]] = strategy
            
        return domain_strategies
```

## Error Handling and Resilience

### Agent Availability Checking
```python
async def robust_strategy_generation():
    endpoints = A2AAgentEndpoints.from_env()
    
    async with PolyhegelA2AClient(endpoints) as client:
        # Check which agents are available
        availability = await client.verify_agent_availability()
        
        if not availability.get("leader"):
            print("Warning: Leader agent unavailable, using fallback")
            # Handle fallback logic
            
        # Proceed with available agents only
        available_domains = [
            domain for domain, available in {
                "resource": availability.get("follower_resource"),
                "security": availability.get("follower_security"),
                "value": availability.get("follower_value"),
                "general": availability.get("follower_general")
            }.items() if available
        ]
        
        print(f"Using domains: {available_domains}")
```

### Timeout and Retry Configuration
```python
import httpx
from polyhegel.clients.a2a_client import PolyhegelA2AClient

# Configure client with custom timeout
async with PolyhegelA2AClient(endpoints, timeout=120.0) as client:
    try:
        strategies = await client.generate_hierarchical_strategies(
            strategic_challenge="Complex multi-domain challenge",
            max_themes=3
        )
    except httpx.TimeoutException:
        print("Request timed out, trying with reduced scope")
        # Retry with simpler request
        strategies = await client.generate_hierarchical_strategies(
            strategic_challenge="Simplified challenge",
            max_themes=1
        )
```

## Performance Optimization

### Concurrent Agent Utilization
```python
import asyncio

async def parallel_strategy_development():
    endpoints = A2AAgentEndpoints.from_env()
    
    async with PolyhegelA2AClient(endpoints) as client:
        # Generate themes first
        themes = await client.generate_themes("Market expansion strategy", 6)
        
        # Develop strategies in parallel
        tasks = [
            client.develop_strategy(theme, theme.get("domain"))
            for theme in themes
        ]
        
        strategies = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_strategies = [
            s for s in strategies if not isinstance(s, Exception)
        ]
        
        return successful_strategies
```

### Caching and Memoization
```python
from functools import lru_cache
import hashlib

class CachedA2AClient:
    def __init__(self, client):
        self.client = client
        self._cache = {}
    
    async def cached_generate_themes(self, challenge, max_themes=5):
        cache_key = hashlib.md5(f"{challenge}:{max_themes}".encode()).hexdigest()
        
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        result = await self.client.generate_themes(challenge, max_themes)
        self._cache[cache_key] = result
        return result
```

## Monitoring and Observability

### Telemetry Integration
The A2A client automatically collects telemetry data:
```python
from polyhegel.telemetry import get_telemetry_collector

# Access telemetry data after operations
telemetry = get_telemetry_collector("polyhegel-a2a-client")
metrics = telemetry.get_metrics()

print(f"Themes generated: {metrics.get('themes_generated_total', 0)}")
print(f"Strategies developed: {metrics.get('strategies_developed_total', 0)}")
print(f"Success rate: {metrics.get('hierarchical_success_rate', 0)}")
```

### Custom Monitoring
```python
import time

class MonitoredA2AClient:
    def __init__(self, client):
        self.client = client
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "avg_response_time": 0
        }
    
    async def generate_themes_with_monitoring(self, challenge, max_themes=5):
        start_time = time.time()
        self.metrics["requests"] += 1
        
        try:
            result = await self.client.generate_themes(challenge, max_themes)
            response_time = time.time() - start_time
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (self.metrics["requests"] - 1) + response_time) 
                / self.metrics["requests"]
            )
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            raise
```

## Best Practices

### Agent Selection
- **Use Leader Agent**: For high-level theme generation and coordination
- **Choose Specialized Followers**: Match domain expertise to problem type
- **Fallback to General**: When domain is unclear or agents unavailable

### Request Optimization
- **Batch Related Requests**: Minimize round-trip time
- **Set Appropriate Timeouts**: Balance responsiveness with completion
- **Handle Failures Gracefully**: Implement fallback strategies

### Security Considerations
- **Secure Credentials**: Use environment variables or secure vaults
- **Validate Inputs**: Sanitize all user inputs before sending to agents
- **Monitor Usage**: Track API usage and detect anomalies