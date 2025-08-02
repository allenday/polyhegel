"""
Generic Evaluation Framework for Polyhegel

Provides base classes and interfaces for domain-specific evaluation implementations.
Domain-specific evaluations are available through examples via PYTHONPATH.
"""

from .base import EvaluationMetrics, MetricsCollector, EvaluationFramework, BaseTestConfiguration

# This is now a namespace package that can be extended by examples/
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__all__ = ["EvaluationMetrics", "MetricsCollector", "EvaluationFramework", "BaseTestConfiguration"]
