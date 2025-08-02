"""
Strategy generator module - Compatibility wrapper

This module provides backward compatibility for imports expecting StrategyGenerator.
"""

from .generator import Generator as StrategyGenerator

__all__ = ["StrategyGenerator"]
