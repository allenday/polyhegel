# Domain Loading Guide

## Overview

Polyhegel follows a clean separation between the core framework and domain-specific implementations:

- **`polyhegel/`** - Generic framework (core)
- **`examples/polyhegel/`** - Domain-specific implementations that extend the core

## Loading Domain Capabilities

Domain-specific agents and techniques can be loaded via the PYTHONPATH mechanism:

```bash
# Add examples directory to PYTHONPATH
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"

# Or for one-time usage:
PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH" python your_script.py
```

## Available Domain Imports

Once PYTHONPATH is configured, you can import domain capabilities using the namespace structure:

### Strategic Domain
```python
# Import strategic techniques
from polyhegel.techniques.strategic.techniques import ALL_TECHNIQUES
from polyhegel.techniques.strategic.techniques import (
    generate_strategic_themes,
    hierarchical_strategic_breakdown,
    competitive_advantage_analysis
)

# Import strategic agents
from polyhegel.agents.strategic.a2a_cards import create_leader_agent_card
from polyhegel.agents.strategic.a2a_executors import LeaderAgentExecutor
```

### Technical Architecture Domain
```python
# Import technical architecture techniques
from polyhegel.techniques.technical_architecture.techniques import ALL_TECHNIQUES

# Import technical architecture agents
from polyhegel.agents.technical_architecture.technical_architecture_cards import create_technical_leader_card
from polyhegel.agents.technical_architecture.technical_architecture_executors import TechnicalLeaderExecutor
```

### Product Domain
```python
# Import product techniques
from polyhegel.techniques.product.techniques import ALL_TECHNIQUES
from polyhegel.techniques.product.evaluation import ProductEvaluator

# Import product agents
from polyhegel.agents.product.product_roadmap_cards import create_product_leader_card
from polyhegel.agents.product.product_roadmap_executors import ProductLeaderExecutor
```

## Directory Structure

The domain implementations follow this structure:

```
polyhegel/
├── polyhegel/              # Core framework (generic)
│   ├── agents/            # Generic agent framework
│   ├── techniques/        # Generic technique framework  
│   └── ...               # Other core components
├── examples/              # Domain examples
│   └── polyhegel/        # Namespace extension
│       ├── agents/       # Domain-specific agents
│       │   ├── strategic/
│       │   ├── technical_architecture/
│       │   └── product/
│       └── techniques/   # Domain-specific techniques
│           ├── strategic/
│           ├── technical_architecture/
│           └── product/
```

## Development Setup

For development, add the examples directory to your PYTHONPATH:

1. **Using environment variable:**
   ```bash
   export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"
   ```

2. **Using .bashrc/.zshrc:**
   ```bash
   echo 'export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"' >> ~/.bashrc
   ```

3. **Using IDE settings:**
   - **PyCharm:** Settings → Project → Python Interpreter → Show All → Show paths → Add `/path/to/polyhegel/examples`
   - **VSCode:** Add to `python.defaultInterpreterPath` or workspace settings

## Testing Imports

Verify that domain imports work correctly:

```python
#!/usr/bin/env python3
"""Test domain imports"""

import os
import sys

# Ensure examples is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'examples'))

def test_strategic_domain():
    """Test strategic domain imports"""
    try:
        from polyhegel.techniques.strategic.techniques import ALL_TECHNIQUES
        print(f"✓ Strategic techniques: {len(ALL_TECHNIQUES)} found")
        return True
    except ImportError as e:
        print(f"✗ Strategic domain import failed: {e}")
        return False

def test_product_domain():
    """Test product domain imports"""
    try:
        from polyhegel.techniques.product.techniques import ALL_TECHNIQUES
        print(f"✓ Product techniques: {len(ALL_TECHNIQUES)} found")
        return True
    except ImportError as e:
        print(f"✗ Product domain import failed: {e}")
        return False

def test_technical_architecture_domain():
    """Test technical architecture domain imports"""
    try:
        from polyhegel.techniques.technical_architecture.techniques import ALL_TECHNIQUES
        print(f"✓ Technical architecture techniques: {len(ALL_TECHNIQUES)} found")
        return True
    except ImportError as e:
        print(f"✗ Technical architecture domain import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing domain imports...")
    success = all([
        test_strategic_domain(),
        test_product_domain(), 
        test_technical_architecture_domain()
    ])
    
    if success:
        print("✓ All domain imports working correctly!")
    else:
        print("✗ Some domain imports failed.")
        sys.exit(1)
```

## Troubleshooting

### ImportError: No module named 'polyhegel.techniques.strategic'

**Solution:** Ensure PYTHONPATH includes the examples directory:
```bash
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"
```

### Module not found when importing specific functions

**Solution:** Verify the file structure and ensure __init__.py files exist in all directories.

### Namespace conflicts

**Solution:** The core polyhegel package and examples use namespace packaging to avoid conflicts. Ensure both have proper __init__.py files with `__path__` extensions.