# Configuration Guide

## Overview

Polyhegel provides flexible configuration options for customizing behavior across different environments and use cases. Configuration can be managed through environment variables, configuration files, or programmatic setup.

## Environment Variables

### Core Configuration
```bash
# AI Model Configuration
export POLYHEGEL_MODEL_NAME="claude-3-sonnet-20240229"
export POLYHEGEL_DEFAULT_TEMPERATURE="0.7"
export POLYHEGEL_MAX_TOKENS="4000"

# API Keys
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"

# Performance Settings
export POLYHEGEL_TIMEOUT_SECONDS="120"
export POLYHEGEL_MAX_CONCURRENT_REQUESTS="5"
export POLYHEGEL_RETRY_ATTEMPTS="3"

# Logging and Telemetry
export POLYHEGEL_LOG_LEVEL="INFO"
export POLYHEGEL_TELEMETRY_ENABLED="true"
export POLYHEGEL_TELEMETRY_ENDPOINT="http://localhost:4317"
```

### A2A Agent Configuration
```bash
# Agent Endpoints
export POLYHEGEL_LEADER_URL="https://leader.polyhegel.com"
export POLYHEGEL_FOLLOWER_RESOURCE_URL="https://resource.polyhegel.com"
export POLYHEGEL_FOLLOWER_SECURITY_URL="https://security.polyhegel.com"
export POLYHEGEL_FOLLOWER_VALUE_URL="https://value.polyhegel.com"
export POLYHEGEL_FOLLOWER_GENERAL_URL="https://general.polyhegel.com"

# Authentication
export POLYHEGEL_LEADER_API_KEY="leader-api-key"
export POLYHEGEL_FOLLOWER_RESOURCE_JWT_TOKEN="resource-jwt-token"
export POLYHEGEL_FOLLOWER_SECURITY_API_KEY="security-api-key"
export POLYHEGEL_FOLLOWER_VALUE_JWT_TOKEN="value-jwt-token"
export POLYHEGEL_FOLLOWER_GENERAL_API_KEY="general-api-key"
```

### Development and Debugging
```bash
# Development Mode
export POLYHEGEL_DEBUG_MODE="true"
export POLYHEGEL_SAVE_DEBUG_ARTIFACTS="true"
export POLYHEGEL_DEBUG_OUTPUT_DIR="./debug_output"

# Testing Configuration
export POLYHEGEL_TEST_MODE="true"
export POLYHEGEL_MOCK_EXTERNAL_APIS="true"
export POLYHEGEL_TEST_DATA_DIR="./test_data"
```

## Configuration Files

### Main Configuration File
Create a `polyhegel.toml` file in your project root:

```toml
[model]
name = "claude-3-sonnet-20240229"
default_temperature = 0.7
max_tokens = 4000
timeout_seconds = 120

[generation]
max_concurrent_requests = 5
retry_attempts = 3
enable_caching = true
cache_ttl_seconds = 3600

[refinement]
max_generations = 10
convergence_threshold = 0.8
improvement_threshold = 0.05
quality_target = 8.5
max_refinement_time_minutes = 60

[evaluation]
default_criteria = ["coherence", "feasibility", "innovation"]
scoring_model = "claude-3-haiku-20240307"
enable_human_feedback = false

[telemetry]
enabled = true
endpoint = "http://localhost:4317"
batch_size = 100
export_interval_seconds = 30
include_sensitive_data = false

[a2a]
leader_url = "http://localhost:8001"
follower_resource_url = "http://localhost:8002"
follower_security_url = "http://localhost:8003"
follower_value_url = "http://localhost:8004"
follower_general_url = "http://localhost:8005"
connection_timeout = 30.0
request_timeout = 120.0

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file = "polyhegel.log"
max_file_size_mb = 100
backup_count = 5

[security]
enable_input_validation = true
max_input_length = 10000
sanitize_outputs = true
mask_sensitive_data = true
```

### Environment-Specific Configuration
Create separate configuration files for different environments:

#### `config/development.toml`
```toml
[model]
name = "claude-3-haiku-20240307"  # Faster, cheaper model for dev

[generation]
max_concurrent_requests = 2  # Lower limits for development

[telemetry]
enabled = false  # Disable telemetry in development

[logging]
level = "DEBUG"

[a2a]
# Local development endpoints
leader_url = "http://localhost:8001"
follower_resource_url = "http://localhost:8002"
follower_security_url = "http://localhost:8003"
follower_value_url = "http://localhost:8004"
follower_general_url = "http://localhost:8005"
```

#### `config/production.toml`
```toml
[model]
name = "claude-3-sonnet-20240229"  # Production-grade model

[generation]
max_concurrent_requests = 10  # Higher limits for production

[telemetry]
enabled = true
endpoint = "${TELEMETRY_ENDPOINT}"  # Use environment variable

[logging]
level = "WARNING"  # Reduced logging for production

[security]
enable_input_validation = true
sanitize_outputs = true
mask_sensitive_data = true

[a2a]
# Production endpoints from environment
leader_url = "${POLYHEGEL_LEADER_URL}"
follower_resource_url = "${POLYHEGEL_FOLLOWER_RESOURCE_URL}"
follower_security_url = "${POLYHEGEL_FOLLOWER_SECURITY_URL}"
follower_value_url = "${POLYHEGEL_FOLLOWER_VALUE_URL}"
follower_general_url = "${POLYHEGEL_FOLLOWER_GENERAL_URL}"
```

## Programmatic Configuration

### Using Configuration Classes
```python
from polyhegel.config import PolyhegelConfig, ModelConfig, A2AConfig

# Create configuration programmatically
config = PolyhegelConfig(
    model=ModelConfig(
        name="claude-3-sonnet-20240229",
        default_temperature=0.7,
        max_tokens=4000,
        timeout_seconds=120
    ),
    a2a=A2AConfig(
        leader_url="https://leader.polyhegel.com",
        follower_urls={
            "resource": "https://resource.polyhegel.com",
            "security": "https://security.polyhegel.com",
            "value": "https://value.polyhegel.com",
            "general": "https://general.polyhegel.com"
        },
        connection_timeout=30.0
    ),
    telemetry_enabled=True,
    debug_mode=False
)

# Use configuration with components
from polyhegel.strategy_generator import StrategyGenerator

generator = StrategyGenerator(config=config)
```

### Configuration Loading
```python
from polyhegel.config import load_config

# Load from file
config = load_config("polyhegel.toml")

# Load environment-specific config
config = load_config("config/production.toml")

# Load with environment variable overrides
config = load_config("polyhegel.toml", override_from_env=True)

# Load from multiple sources (merged in order)
config = load_config([
    "polyhegel.toml",           # Base configuration
    "config/production.toml",   # Environment-specific
    "config/local.toml"         # Local overrides
])
```

## Strategic Technique Configuration

### Custom Technique Registration
```python
from polyhegel.strategic_techniques import register_technique, StrategyDomain

@register_technique(domain=StrategyDomain.RESOURCE_ACQUISITION)
class CustomResourceTechnique:
    name = "lean_startup"
    description = "Lean startup methodology for resource optimization"
    
    def __init__(self, config=None):
        self.config = config or {
            "mvp_focus": True,
            "rapid_iteration": True,
            "validated_learning": True
        }

# Configure technique in settings
config.techniques = {
    "lean_startup": {
        "enabled": True,
        "mvp_focus": True,
        "rapid_iteration": True,
        "validated_learning": True
    }
}
```

### Technique-Specific Settings
```toml
[techniques.resource_optimization]
enabled = true
focus_areas = ["cost_efficiency", "scalability", "automation"]
optimization_target = "roi"

[techniques.risk_management]  
enabled = true
risk_tolerance = "moderate"
compliance_frameworks = ["iso27001", "soc2"]
threat_modeling = true

[techniques.value_creation]
enabled = true
innovation_level = "high"
market_focus = ["b2b", "enterprise"]
value_metrics = ["customer_satisfaction", "retention", "expansion"]
```

## Performance Tuning

### Memory Management
```toml
[performance]
max_memory_usage_mb = 2048
gc_threshold = 10000
strategy_cache_size = 1000
result_cache_ttl_seconds = 3600

[concurrency]
max_concurrent_generations = 5
max_concurrent_refinements = 2
thread_pool_size = 10
async_timeout_seconds = 300
```

### Model Optimization
```python
# Configure model-specific optimizations
config.model.optimization = {
    "enable_streaming": True,
    "batch_requests": True,
    "connection_pooling": True,
    "request_compression": True,
    "response_caching": True,
}

# Configure retry behavior
config.model.retry = {
    "max_attempts": 3,
    "backoff_factor": 2.0,
    "max_backoff_seconds": 60,
    "retry_on_timeout": True,
    "retry_on_rate_limit": True
}
```

## Security Configuration

### Input Validation
```toml
[security.input_validation]
enabled = true
max_input_length = 10000
allowed_characters = "alphanumeric_punctuation_whitespace"
block_code_injection = true
block_prompt_injection = true

[security.output_sanitization]
enabled = true
remove_sensitive_patterns = true
mask_api_keys = true
mask_personal_info = true
```

### API Security
```python
from polyhegel.security import SecurityConfig

security_config = SecurityConfig(
    api_key_validation=True,
    rate_limiting={
        "requests_per_minute": 60,
        "burst_size": 10
    },
    request_signing=True,
    tls_verification=True,
    allowed_origins=["https://trusted-domain.com"]
)

config.security = security_config
```

## Monitoring and Observability

### Telemetry Configuration
```toml
[telemetry]
enabled = true
endpoint = "http://otel-collector:4317"
protocol = "grpc"
batch_size = 100
export_interval_seconds = 30

[telemetry.metrics]
enabled = true
include_histograms = true
include_counters = true
include_gauges = true

[telemetry.traces]
enabled = true
sample_rate = 0.1  # Sample 10% of traces
include_sensitive_data = false

[telemetry.logs]
enabled = true
structured_logging = true
include_context = true
```

### Health Checks
```python
from polyhegel.monitoring import HealthCheckConfig

health_config = HealthCheckConfig(
    endpoint="/health",
    detailed_endpoint="/health/detailed",
    checks=[
        "model_connectivity",
        "a2a_agent_availability", 
        "memory_usage",
        "disk_space",
        "database_connection"
    ],
    timeout_seconds=10
)
```

## Configuration Validation

### Validation Rules
```python
from polyhegel.config import ConfigValidator

validator = ConfigValidator()

# Validate configuration
try:
    validator.validate(config)
    print("Configuration is valid")
except ValidationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration errors
```

### Custom Validation
```python
from polyhegel.config import ValidationRule

class CustomValidationRule(ValidationRule):
    def validate(self, config):
        if config.model.name.startswith("gpt") and not config.api_keys.openai:
            raise ValidationError("OpenAI API key required for GPT models")
        
        if config.a2a.enabled and not all(config.a2a.follower_urls.values()):
            raise ValidationError("All A2A follower URLs must be configured")

# Register custom validation
validator.add_rule(CustomValidationRule())
```

## Configuration Best Practices

### Environment Management
1. **Use Environment Variables**: For sensitive data and deployment-specific settings
2. **Configuration Files**: For complex, structured configuration
3. **Layered Configuration**: Base config + environment-specific overrides
4. **Validation**: Always validate configuration before use

### Security Considerations
1. **Never Commit Secrets**: Use environment variables or secret management
2. **Least Privilege**: Configure minimal required permissions
3. **Input Validation**: Enable all security validation features
4. **Audit Logging**: Log configuration changes and access

### Performance Optimization
1. **Resource Limits**: Set appropriate memory and concurrency limits
2. **Caching**: Enable caching for better performance
3. **Connection Pooling**: Reuse connections where possible
4. **Monitoring**: Track performance metrics and adjust accordingly

### Development Workflow
1. **Local Development**: Use lighter models and reduced limits
2. **Testing**: Mock external services and use test data
3. **Staging**: Mirror production configuration for testing
4. **Production**: Optimize for performance and reliability