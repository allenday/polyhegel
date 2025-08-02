# Getting Started with Polyhegel

**Multi-Agent Analysis Framework - From Zero to Analysis in Minutes**

## Quick Start (30 seconds)

```bash
# Install and try immediately
pip install polyhegel
polyhegel demo

# Start multi-agent analysis
polyhegel simulate "analyze our digital transformation strategy"
```

**That's it!** You now have access to 6 cross-domain analytical techniques with multi-agent coordination.

## Understanding the Architecture

Polyhegel uses a **core + examples** design:

- **Core Package** (`polyhegel/`) - Generic techniques that work across any domain
- **Examples** (`examples/`) - Domain-specific expertise (strategic, technical, product)

```python
# Core techniques (always available)
from polyhegel.techniques.common import ALL_TECHNIQUES
print(f"{len(ALL_TECHNIQUES)} cross-domain techniques ready")

# Examples techniques (when enabled)
from polyhegel.techniques.strategic import ALL_TECHNIQUES  # Requires PYTHONPATH
```

## Three Usage Patterns

### 1. 🚀 Quick Analysis (Core Only)

**Best for:** Cross-domain insights, getting started, quick evaluations

```bash
pip install polyhegel

# Available immediately:
# • Stakeholder Analysis  • SWOT Analysis      • Trade-off Analysis
# • Risk Assessment       • Consensus Building  • Scenario Planning
```

**Example:**
```python
from polyhegel.techniques.common import StakeholderAnalysisTechnique, SWOTAnalysisTechnique

# Works for any domain - strategic, technical, product, etc.
polyhegel simulate "evaluate stakeholders for our API redesign project"
```

### 2. 🎯 Domain Expertise (Core + Examples)

**Best for:** Specialized analysis, learning best practices, comprehensive insights

```bash
# Enable examples with domain-specific techniques
git clone https://github.com/allenday/polyhegel.git
cd polyhegel
export PYTHONPATH="$(pwd)/examples:$PYTHONPATH"
pip install -e .

# Now access 50+ specialized techniques:
polyhegel discover --domain all
```

**Available Domains:**
- **Strategic** (15+ techniques) - Vision, execution, competitive analysis
- **Technical Architecture** (20+ techniques) - Backend, frontend, infrastructure, security  
- **Product** (15+ techniques) - Planning, validation, prioritization, analytics

**Example:**
```python
# Strategic domain techniques
from polyhegel.techniques.strategic import VisioningTechnique, CompetitiveAnalysisTechnique

# Technical architecture techniques  
from polyhegel.techniques.technical_architecture import MicroservicesTechnique, APIGatewayTechnique

# Product techniques
from polyhegel.techniques.product import UserStoryMappingTechnique, RICEScoringTechnique
```

### 3. 🔧 Custom Development (Core + Examples + Your Domains)

**Best for:** Organization-specific methodologies, proprietary techniques, novel domains

```bash
# Create custom domain following examples patterns
mkdir -p my_domains/polyhegel/techniques/finance
# ... implement following examples/polyhegel/techniques/strategic/ pattern

export PYTHONPATH="$(pwd)/my_domains:$(pwd)/examples:$PYTHONPATH"
```

## Installation Guide

### Option A: Core Only (Fastest)

```bash
pip install polyhegel
```

**Capabilities:**
- ✅ 6 cross-domain analytical techniques
- ✅ Multi-agent A2A coordination  
- ✅ Production-ready servers
- ✅ Works across any problem domain

**Time to value:** 30 seconds

### Option B: With Examples (Recommended)

```bash
# Clone repository
git clone https://github.com/allenday/polyhegel.git
cd polyhegel

# Enable examples
export PYTHONPATH="$(pwd)/examples:$PYTHONPATH"
pip install -e .

# Verify setup
polyhegel discover
```

**Capabilities:**
- ✅ All core capabilities
- ✅ 50+ domain-specific techniques
- ✅ Reference architectures
- ✅ Specialized agents

**Time to value:** 2 minutes

### Option C: Development Setup

```bash
git clone https://github.com/allendy/polyhegel.git
cd polyhegel

# Development environment
pip install -e ".[dev]"
export PYTHONPATH="$(pwd)/examples:$PYTHONPATH"

# Verify development setup
make test
polyhegel discover --format json
```

**Capabilities:**
- ✅ All previous capabilities
- ✅ Development tools
- ✅ Testing framework
- ✅ Custom domain scaffolding

**Time to value:** 5 minutes

## Core Concepts

### Cross-Domain Techniques

**What they are:** Analytical methods that work across any problem space

**Available techniques:**
1. **Stakeholder Analysis** - Identify and prioritize key stakeholders
2. **SWOT Analysis** - Strengths, weaknesses, opportunities, threats
3. **Trade-off Analysis** - Systematic evaluation of competing options
4. **Risk Assessment** - Identify and mitigate potential risks
5. **Consensus Building** - Multi-party agreement facilitation
6. **Scenario Planning** - Explore multiple future outcomes

**Example usage:**
```python
# Same techniques work for any domain
polyhegel simulate "stakeholder analysis for cloud migration"      # Technical
polyhegel simulate "SWOT analysis for product launch"              # Product  
polyhegel simulate "risk assessment for market expansion"          # Strategic
```

### Multi-Agent Coordination

**How it works:** Leader agents coordinate specialized followers via A2A protocol

```bash
# Start complete agent ecosystem
./scripts/run-all-common-agents.sh

# Agents automatically discover each other:
# • CommonAnalysisLeader (port 7001) - Coordinates analysis
# • StakeholderFollower (port 7002) - Stakeholder expertise
# • TradeoffFollower (port 7003) - Decision analysis
# • RiskFollower (port 7004) - Risk management
# • ConsensusFollower (port 7005) - Agreement facilitation
# • ScenarioFollower (port 7006) - Future planning
```

### Namespace Extension

**Key insight:** All techniques accessible via `polyhegel.*` imports regardless of source

```python
# Core techniques
from polyhegel.techniques.common import ALL_TECHNIQUES

# Examples techniques (same namespace!)
from polyhegel.techniques.strategic import ALL_TECHNIQUES
from polyhegel.techniques.product import ALL_TECHNIQUES

# Custom techniques (same namespace!)
from polyhegel.techniques.your_domain import ALL_TECHNIQUES
```

**Technical detail:** Uses `pkgutil.extend_path()` for seamless namespace extension

## Common Workflows

### Workflow 1: Quick Problem Analysis

```bash
# One-command analysis
polyhegel simulate "evaluate our microservices migration strategy"

# Multi-step analysis
polyhegel simulate "stakeholder analysis for API redesign" 
polyhegel simulate "risk assessment for API redesign"
polyhegel simulate "consensus building for API redesign"
```

### Workflow 2: Comprehensive Domain Analysis

```bash
# Enable strategic domain
export PYTHONPATH="/path/to/examples:$PYTHONPATH"

# Strategic analysis with domain expertise
polyhegel simulate "develop 3-year strategic plan for SaaS expansion"
polyhegel simulate "competitive analysis of fintech market entry"
```

### Workflow 3: Multi-Agent Coordination

```bash
# Start agent ecosystem
./scripts/run-all-common-agents.sh

# Leader coordinates multiple followers automatically
polyhegel simulate "comprehensive analysis of digital transformation"
# ^ Uses stakeholder analysis + risk assessment + scenario planning
```

### Workflow 4: Custom Domain Development

```bash
# Create custom domain
mkdir -p my_domains/polyhegel/techniques/healthcare
# ... implement following examples patterns

# Test integration  
export PYTHONPATH="$(pwd)/my_domains:$PYTHONPATH"
polyhegel discover --domain all
```

## Examples

### Example 1: Strategic Planning

```bash
# Core techniques (immediate)
polyhegel simulate "SWOT analysis for entering European market"

# Strategic domain techniques (with examples)
polyhegel simulate "develop go-to-market strategy for B2B SaaS"
```

### Example 2: Technical Decisions  

```bash
# Core techniques (immediate)
polyhegel simulate "trade-off analysis of database architectures"

# Technical domain techniques (with examples)  
polyhegel simulate "design microservices architecture for e-commerce platform"
```

### Example 3: Product Development

```bash
# Core techniques (immediate)
polyhegel simulate "stakeholder analysis for mobile app redesign"

# Product domain techniques (with examples)
polyhegel simulate "prioritize features using RICE scoring framework"
```

## Advanced Usage

### Discovery and Introspection

```bash
# Discover available capabilities
polyhegel discover
polyhegel discover --domain strategic
polyhegel discover --format json

# Verify setup
polyhegel status --with-availability
```

### Custom Configuration

```bash
# Environment customization
export POLYHEGEL_MODEL="claude-3-opus-20240229"  # Upgrade model
export POLYHEGEL_HOST="0.0.0.0"                 # Server binding
export PYTHONPATH="/custom/domains:/examples:$PYTHONPATH"  # Multiple domains
```

### Development and Testing

```bash
# Run tests
make test

# Development server
make dev-server

# Create custom domain
# Follow patterns in examples/polyhegel/techniques/strategic/
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'polyhegel.techniques.strategic'"

**Problem:** Examples not enabled
**Solution:** 
```bash
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"
```

### "No techniques found"

**Problem:** Import or setup issue
**Solution:**
```bash
# Verify core installation
python -c "from polyhegel.techniques.common import ALL_TECHNIQUES; print(len(ALL_TECHNIQUES))"

# Check examples setup
polyhegel discover
```

### "Agents not discovering each other"

**Problem:** A2A servers not running
**Solution:**
```bash
# Start agent ecosystem
./scripts/run-all-common-agents.sh

# Verify agents
curl http://localhost:7001/health  # Leader
curl http://localhost:7002/health  # Stakeholder follower
```

## Next Steps

1. **Try the Demo:** `polyhegel demo` - See capabilities immediately
2. **Read Architecture Guide:** [Core vs Examples Architecture](architecture/core-vs-examples.md)
3. **Explore Examples:** Check `examples/polyhegel/techniques/` for domain implementations
4. **Join Community:** Contributing guide and discussions on GitHub

## Resources

- **Architecture Guide:** [Core vs Examples](architecture/core-vs-examples.md)
- **API Reference:** [API Documentation](reference/index.md)
- **Examples:** [Domain Implementations](../examples/)
- **Contributing:** [Development Guide](contributing/development.md)

---

**Need help?** Open an issue on [GitHub](https://github.com/allenday/polyhegel/issues) or check existing [discussions](https://github.com/allenday/polyhegel/discussions).