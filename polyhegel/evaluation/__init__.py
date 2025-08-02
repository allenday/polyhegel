"""
Evaluation framework for strategic performance and metrics collection.
"""

from .comparative_test import ComparativeTestFramework, TestConfiguration, ComparisonResult
from .metrics import MetricsCollector, StrategicMetrics

__all__ = ["ComparativeTestFramework", "TestConfiguration", "ComparisonResult", "MetricsCollector", "StrategicMetrics"]
