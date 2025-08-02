"""
Polyhegel: Swarm AI Genesis Simulator
"""

# Import core models and domain management (no dependencies)
from .models import StrategyStep, GenesisStrategy, StrategyChain
from .domain_manager import (
    get_domain_manager,
    get_domain,
    list_domains,
    get_all_techniques,
    get_all_agents,
    discover_domains,
)

# Optional imports that require extra dependencies
_optional_imports = {}

try:
    from .simulator import PolyhegelSimulator

    _optional_imports["PolyhegelSimulator"] = PolyhegelSimulator
except ImportError:
    # Simulator requires sentence_transformers
    pass

try:
    from .cli import main

    _optional_imports["main"] = main
except ImportError:
    # CLI might require additional dependencies
    pass

# Expose optional imports at module level
for name, obj in _optional_imports.items():
    globals()[name] = obj

__version__ = "0.1.0"
__all__ = [
    "StrategyStep",
    "GenesisStrategy",
    "StrategyChain",
    "get_domain_manager",
    "get_domain",
    "list_domains",
    "get_all_techniques",
    "get_all_agents",
    "discover_domains",
] + list(_optional_imports.keys())
