"""
Recursive refinement system for continuous strategy optimization

This module implements the recursive refinement mechanisms described in
CLM Section 4: Protocol of Recursive Evolution for continuous strategy
improvement based on performance feedback.
"""

from .recursive import RecursiveRefinementEngine, RefinementConfiguration
from .metrics import PerformanceTracker, RefinementMetrics
from .feedback import FeedbackLoop, StrategyImprover

__all__ = [
    'RecursiveRefinementEngine',
    'RefinementConfiguration',
    'PerformanceTracker', 
    'RefinementMetrics',
    'FeedbackLoop',
    'StrategyImprover'
]