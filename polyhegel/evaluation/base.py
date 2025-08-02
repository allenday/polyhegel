"""
Generic evaluation framework for Polyhegel

Provides base classes and interfaces for domain-specific evaluation implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
from pydantic import BaseModel


class EvaluationMetrics(BaseModel):
    """Base class for evaluation metrics"""

    # Performance metrics (generic)
    execution_time: float = 0.0
    memory_usage: float = 0.0

    # Method metadata
    method_name: str = ""
    timestamp: Optional[float] = None


class MetricsCollector(Protocol):
    """Protocol for metrics collection implementations"""

    def collect_performance_metrics(self) -> Dict[str, float]:
        """Collect performance-related metrics"""
        ...

    def collect_domain_metrics(self, results: Any) -> Dict[str, float]:
        """Collect domain-specific metrics"""
        ...


class EvaluationFramework(ABC):
    """Abstract base class for evaluation frameworks"""

    @abstractmethod
    def configure_test(self, config: Dict[str, Any]) -> None:
        """Configure the evaluation test"""
        pass

    @abstractmethod
    def run_evaluation(self) -> Dict[str, Any]:
        """Run the evaluation and return results"""
        pass

    @abstractmethod
    def compare_methods(self, method_a: str, method_b: str) -> Dict[str, Any]:
        """Compare two evaluation methods"""
        pass


class BaseTestConfiguration(BaseModel):
    """Base configuration for evaluation tests"""

    test_name: str = "evaluation_test"
    iterations: int = 3
    timeout_seconds: int = 300

    # Generic test parameters
    model_name: Optional[str] = None
    temperature: Optional[float] = None
