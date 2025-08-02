# Core vs Examples Architecture Guide

**Polyhegel's Modular Design for Immediate Value and Infinite Extensibility**

## Overview

Polyhegel uses a sophisticated **core + examples** architecture that provides immediate value while remaining infinitely extensible. This design separates generic analytical capabilities from domain-specific implementations, allowing users to start quickly and extend as needed.

```
┌─────────────────┐    ┌─────────────────────┐
│   Core Package  │    │     Examples        │
│   (polyhegel/)  │────│  (examples/*)       │
│                 │    │                     │
│ • Common techs  │    │ • Strategic domain  │
│ • Default agents│    │ • Technical domain  │
│ • A2A servers   │    │ • Product domain    │
│ • Cross-domain  │    │ • Custom domains    │
└─────────────────┘    └─────────────────────┘
        │                        │
        └────────────────────────┘
               Seamless Integration
             via Namespace Extension
```

## Core Philosophy

### 🎯 **Immediate Value**
- Core package provides working multi-agent analysis out-of-the-box
- Common cross-domain techniques work across any problem space
- No configuration required for basic analytical capabilities

### 🔧 **Progressive Complexity**
- Start with core techniques, add domain expertise as needed
- Examples demonstrate best practices for domain-specific extensions
- Custom domains integrate seamlessly with existing infrastructure

### 🌐 **Namespace Preservation**
- All functionality accessible via `polyhegel.*` imports
- Examples extend the namespace without breaking existing code
- Users work with unified API regardless of technique source

## Architecture Components

### Core Package (`polyhegel/`)

**Purpose:** Generic, unopinionated analytical framework

```python
# Immediate value after pip install polyhegel
from polyhegel.techniques.common import ALL_TECHNIQUES
from polyhegel.agents.common import CommonAnalysisLeader

# 6 cross-domain techniques available immediately:
# - Stakeholder Analysis, SWOT Analysis, Trade-off Analysis
# - Risk Assessment, Consensus Building, Scenario Planning
```

**Contents:**
- **`techniques/common/`** - Cross-domain analytical techniques
- **`agents/common/`** - Default agent implementations
- **`servers/common/`** - A2A server implementations
- **`domain_manager.py`** - Plugin discovery system

### Examples Package (`examples/polyhegel/`)

**Purpose:** Domain-specific implementations and reference architectures

```python
# Extended functionality via PYTHONPATH
export PYTHONPATH="/path/to/examples:$PYTHONPATH"

from polyhegel.techniques.strategic import ALL_TECHNIQUES      # Strategic planning
from polyhegel.techniques.technical_architecture import ALL_TECHNIQUES  # Architecture
from polyhegel.techniques.product import ALL_TECHNIQUES        # Product roadmap
```

**Contents:**
- **`techniques/strategic/`** - Strategic planning domain
- **`techniques/technical_architecture/`** - Technical architecture domain  
- **`techniques/product/`** - Product roadmap domain
- **`agents/*/`** - Domain-specific agent implementations
- **`servers/*/`** - Domain-specific A2A servers

## Key Design Patterns

### 1. Namespace Extension

**How it works:**
```python
# In each __init__.py
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
```

**Result:**
- Core and examples appear as unified `polyhegel.*` namespace
- No import path changes when adding domains
- Backwards compatibility maintained automatically

### 2. Domain Plugin Architecture

**Discovery:**
```python
from polyhegel import discover_domains, get_all_techniques

# Automatically discovers available domains
domains = discover_domains()
techniques = get_all_techniques()  # From core + examples + custom
```

**Extension:**
```python
# Custom domains integrate seamlessly
my_domain/polyhegel/techniques/custom/
└── techniques.py  # Follows same patterns as examples
```

### 3. A2A Communication

**Unified Protocol:**
- All agents (core, examples, custom) use same A2A protocol
- Service discovery works across domain boundaries
- Leader agents can coordinate followers from any domain

## Usage Patterns

### Pattern 1: Core Only (Immediate Value)

**Use Case:** Quick analysis, cross-domain insights, getting started

```bash
pip install polyhegel

# Immediate multi-agent analysis
./scripts/run-all-common-agents.sh

# Access 6 common techniques instantly
python -c "from polyhegel.techniques.common import ALL_TECHNIQUES; print(len(ALL_TECHNIQUES))"
```

**Benefits:**
- ✅ Zero configuration required
- ✅ Works across any problem domain
- ✅ Full A2A multi-agent capabilities
- ✅ Production-ready out-of-the-box

### Pattern 2: Core + Examples (Extended Functionality)

**Use Case:** Domain expertise, comprehensive analysis, learning best practices

```bash
pip install polyhegel
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"

# Access all domains seamlessly
python -c "from polyhegel.techniques.strategic import ALL_TECHNIQUES; print('Strategic:', len(ALL_TECHNIQUES))"
python -c "from polyhegel.techniques.technical_architecture import ALL_TECHNIQUES; print('TechArch:', len(ALL_TECHNIQUES))"
python -c "from polyhegel.techniques.product import ALL_TECHNIQUES; print('Product:', len(ALL_TECHNIQUES))"
```

**Benefits:**
- ✅ Domain-specific expertise (20+ techniques per domain)
- ✅ Specialized agent implementations
- ✅ Reference architectures for custom development
- ✅ Same unified API as core-only usage

### Pattern 3: Custom Domain Development

**Use Case:** Organization-specific techniques, proprietary methodologies, novel domains

```bash
# Create custom domain following examples patterns
my_project/polyhegel/techniques/finance/
├── __init__.py
├── techniques.py      # Define FinancialTechnique dataclasses
├── prompts/          # LLM prompt templates
└── agents.py         # Custom agent implementations

# Integrate seamlessly
export PYTHONPATH="/path/to/my_project:$PYTHONPATH"
python -c "from polyhegel.techniques.finance import ALL_TECHNIQUES"
```

**Benefits:**
- ✅ Full framework capabilities for custom domains
- ✅ Same patterns as built-in examples
- ✅ A2A integration with existing agents
- ✅ No framework modifications required

## Installation Scenarios

### Scenario 1: Evaluation & Quick Analysis

```bash
# Install and test immediately
pip install polyhegel
python -c "from polyhegel.techniques.common import ALL_TECHNIQUES; print(f'{len(ALL_TECHNIQUES)} techniques ready')"

# Start multi-agent analysis
./scripts/run-all-common-agents.sh
```

**Time to value:** < 2 minutes

### Scenario 2: Domain-Specific Work

```bash
# Clone with examples
git clone https://github.com/allenday/polyhegel.git
cd polyhegel

# Setup with examples
export PYTHONPATH="$(pwd)/examples:$PYTHONPATH"
pip install -e .

# Access domain expertise
python -c "from polyhegel.techniques.strategic import ALL_TECHNIQUES; print(f'{len(ALL_TECHNIQUES)} strategic techniques')"
```

**Time to value:** < 5 minutes

### Scenario 3: Custom Development

```bash
# Development setup
git clone https://github.com/allendy/polyhegel.git
cd polyhegel
pip install -e ".[dev]"

# Create custom domain (following examples patterns)
mkdir -p my_domains/polyhegel/techniques/custom
# ... implement following examples/polyhegel/techniques/strategic/ pattern

# Test integration
export PYTHONPATH="$(pwd)/my_domains:$(pwd)/examples:$PYTHONPATH"
python -c "from polyhegel.techniques.custom import ALL_TECHNIQUES"
```

**Time to value:** < 15 minutes with custom domain

## Advanced Concepts

### Domain Interoperability

**Cross-Domain Analysis:**
```python
# Leader from one domain can coordinate followers from others
from polyhegel.agents.strategic import StrategicLeader
from polyhegel.agents.technical_architecture import BackendFollower
from polyhegel.agents.common import StakeholderAnalysisFollower

# Multi-domain coordination works seamlessly
# Strategic leader can utilize technical and common followers
```

### Technique Composition

**Layered Analysis:**
```python
# Common techniques provide foundation
from polyhegel.techniques.common import StakeholderAnalysisTechnique

# Domain techniques build on common foundation
from polyhegel.techniques.strategic import StrategicStakeholderTechnique
# ^ Extends common stakeholder analysis with strategic context
```

### A2A Service Discovery

**Automatic Agent Discovery:**
```python
# Agents automatically discover each other across domains
from polyhegel.agents.common.cards import create_all_common_agent_cards
from polyhegel.agents.strategic.cards import create_all_strategic_agent_cards

# A2A protocol enables cross-domain coordination
# No manual configuration required
```

## Best Practices

### For Users

1. **Start with Core** - Get familiar with common techniques first
2. **Add Examples Gradually** - Introduce domain-specific functionality as needed  
3. **Follow Patterns** - Use examples as templates for custom domains
4. **Test Integration** - Verify namespace extension works before deployment

### For Developers

1. **Maintain Compatibility** - Always support core-only usage
2. **Follow Conventions** - Use same patterns as existing examples
3. **Document Extensions** - Clear documentation for custom domains
4. **Test Isolation** - Ensure examples don't break core functionality

### For Organizations

1. **Evaluate First** - Start with core package for proof-of-concept
2. **Extend Strategically** - Add domain examples that match your use cases
3. **Develop Incrementally** - Build custom domains following proven patterns
4. **Share Knowledge** - Consider contributing useful domains back to examples

## Migration Guide

### From Legacy Strategic-Only to Core+Examples

**Before:**
```python
from polyhegel.strategic_techniques import StrategyTechnique
from polyhegel.agents import LeaderAgent
```

**After:**
```python
# Core techniques available immediately
from polyhegel.techniques.common import StakeholderAnalysisTechnique
from polyhegel.agents.common import CommonAnalysisLeader

# Strategic techniques via examples
export PYTHONPATH="/path/to/examples:$PYTHONPATH"
from polyhegel.techniques.strategic import StrategicTechnique
from polyhegel.agents.strategic import StrategicLeader
```

**Benefits:**
- ✅ More techniques available (6 common + 15+ strategic)
- ✅ Cross-domain capabilities
- ✅ Better separation of concerns
- ✅ Easier custom domain development

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'polyhegel.techniques.strategic'"**
```bash
# Solution: Add examples to PYTHONPATH
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"
```

**"Techniques not appearing in discover_domains()"**
```bash
# Solution: Verify __init__.py files have pkgutil.extend_path
# Check that PYTHONPATH includes your custom domains
```

**"A2A agents not discovering each other"**
```bash
# Solution: Ensure all agent servers are running
./scripts/run-all-common-agents.sh

# Check agent cards are properly configured
python -c "from polyhegel.agents.common.cards import create_all_common_agent_cards; print(len(create_all_common_agent_cards()))"
```

### Getting Help

- **Core Issues:** Check `polyhegel/techniques/common/` and `polyhegel/agents/common/`
- **Examples Issues:** Verify PYTHONPATH and check `examples/polyhegel/`
- **Custom Domain Issues:** Follow patterns from `examples/polyhegel/techniques/strategic/`
- **A2A Issues:** Verify agent servers are running and cards are configured

## Conclusion

Polyhegel's core vs examples architecture provides:

- **🚀 Immediate Value** - Working multi-agent analysis out-of-the-box
- **🔧 Progressive Complexity** - Add domain expertise as needed
- **🌐 Unified Experience** - Consistent API regardless of technique source
- **⚡ Infinite Extensibility** - Custom domains integrate seamlessly

This design enables polyhegel to serve everyone from quick evaluators to advanced researchers building novel analytical methodologies, all while maintaining a simple and consistent user experience.

---

*For more information, see [Getting Started Guide](../getting-started.md) and [Developer Documentation](../development/).*