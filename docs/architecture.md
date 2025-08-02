# Polyhegel Architecture: Core and Examples Design

## Overview

Polyhegel employs a flexible, extensible architecture that separates core functionality from domain-specific implementations. This design enables users to quickly get started with generic techniques while providing seamless extensibility for custom domains.

## Architecture Principles

### Core Package Design
The `polyhegel/` directory contains the core package, which is:
- Generic and unopinionated
- Provides cross-domain techniques and common infrastructure
- Serves as a foundational framework for strategic reasoning

### Examples Package Design
The `examples/polyhegel/` directory houses:
- Domain-specific technique implementations
- Specialized agent configurations
- Concrete examples of applying Polyhegel across different contexts

## Namespace and Import Mechanisms

### Namespace Extension
Polyhegel uses `pkgutil.extend_path()` to enable:
- Seamless `polyhegel.*` imports across core and example packages
- Dynamic package discovery
- Flexible domain extension without modifying core package

### PYTHONPATH Integration
Users can extend Polyhegel by:
1. Adding custom domains to PYTHONPATH
2. Maintaining the `polyhegel.*` import structure
3. Preserving core package integrity

## Directory Structure

```
polyhegel/                    # Core Package
├── techniques/common/        # Cross-domain techniques
│   ├── stakeholder/          # Generic stakeholder analysis
│   ├── swot/                 # Universal SWOT framework
│   └── trade_offs/           # Decision trade-off techniques
├── agents/common/            # Default agent implementations
├── servers/common/           # A2A server implementations
└── domain_manager.py         # Plugin discovery system

examples/polyhegel/           # Domain-Specific Examples
├── techniques/strategic/     # Strategic planning techniques
├── techniques/technical_architecture/ # Architecture techniques
├── techniques/product/       # Product roadmap techniques
└── agents/*/                 # Domain-specific agents
```

## Installation Patterns

### Minimal Installation
```bash
pip install polyhegel  # Core package only
```

### Full Installation with Examples
```bash
pip install polyhegel
export PYTHONPATH=$PYTHONPATH:/path/to/examples
```

## Development Workflow

### Extending Core Techniques
1. Create a new technique in `techniques/`
2. Follow existing technique interface
3. Register with `domain_manager.py`

### Creating Custom Domains
1. Create a new directory under `examples/polyhegel/`
2. Implement domain-specific techniques
3. Ensure compatibility with core package interfaces

## Integration Points

### Technique Registration
- Use `domain_manager.py` to dynamically discover and register techniques
- Techniques must conform to core interface contracts

### Agent Extensibility
- Core agents provide base implementations
- Domain-specific agents can inherit and specialize

## Best Practices

1. Keep core package generic and unopinionated
2. Use domain-specific examples for concrete implementations
3. Maintain consistent import and extension mechanisms
4. Document new techniques and agents thoroughly

## Advanced Usage: Custom Domain Integration

```python
from polyhegel.domain_manager import register_technique
from polyhegel.techniques.base import BaseTechnique

class MyCustomTechnique(BaseTechnique):
    # Implement your custom technique
    pass

# Dynamically register the technique
register_technique(MyCustomTechnique)
```

## Troubleshooting

### Common Issues
- Import errors: Verify PYTHONPATH configuration
- Technique discovery: Check domain manager registration
- Compatibility: Ensure techniques conform to base interfaces

## Performance Considerations
- Namespace extension has minimal runtime overhead
- PYTHONPATH-based loading ensures efficient technique discovery

## Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on extending Polyhegel's core and example packages.