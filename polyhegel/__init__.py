"""
Polyhegel: Swarm AI Genesis Simulator
"""

from .simulator import PolyhegelSimulator
from .models import StrategyStep, GenesisStrategy, StrategyChain
from .cli import main

__version__ = "0.1.0"
__all__ = ["PolyhegelSimulator", "StrategyStep", "GenesisStrategy", "StrategyChain", "main"]
