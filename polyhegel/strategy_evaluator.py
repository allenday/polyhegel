"""
Strategy evaluator module - Compatibility wrapper

This module provides backward compatibility for imports expecting StrategyEvaluator.
"""

from .evaluator import Evaluator as StrategyEvaluator

__all__ = ["StrategyEvaluator"]
