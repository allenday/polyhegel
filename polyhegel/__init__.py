"""
Polyhegel: Swarm AI Genesis Simulator
"""

from .simulator import PolyhegelSimulator
from .models import StrategyStep, GenesisStrategy, StrategyChain
from .cli import main
from .domain_manager import (
    get_domain_manager,
    get_domain,
    list_domains,
    get_all_techniques,
    get_all_agents,
    discover_domains,
)

__version__ = "0.1.0"
__all__ = [
    "PolyhegelSimulator",
    "StrategyStep",
    "GenesisStrategy",
    "StrategyChain",
    "main",
    "get_domain_manager",
    "get_domain",
    "list_domains",
    "get_all_techniques",
    "get_all_agents",
    "discover_domains",
]
