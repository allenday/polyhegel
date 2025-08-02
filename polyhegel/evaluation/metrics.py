"""
Metrics collection and strategic performance measurement tools.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class StrategicMetrics:
    """Comprehensive metrics for strategic performance evaluation."""

    efficiency_score: float = 0.0
    risk_mitigation_score: float = 0.0
    adaptability_score: float = 0.0
    innovation_index: float = 0.0
    resource_utilization: float = 0.0
    additional_metrics: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """
    A collector and processor of strategic performance metrics.
    """

    def __init__(self):
        self.metrics_history: List[StrategicMetrics] = []

    def add_metrics(self, metrics: StrategicMetrics):
        """
        Add a set of metrics to the collection.

        Args:
            metrics: Strategic metrics to be collected
        """
        self.metrics_history.append(metrics)

    def get_latest_metrics(self) -> Optional[StrategicMetrics]:
        """
        Retrieve the most recently added metrics.

        Returns:
            Most recent StrategicMetrics or None if no metrics exist
        """
        return self.metrics_history[-1] if self.metrics_history else None

    def calculate_average_metrics(self) -> StrategicMetrics:
        """
        Calculate average metrics across all collected metrics.

        Returns:
            Averaged StrategicMetrics
        """
        if not self.metrics_history:
            return StrategicMetrics()

        avg_metrics = StrategicMetrics(
            efficiency_score=sum(m.efficiency_score for m in self.metrics_history) / len(self.metrics_history),
            risk_mitigation_score=sum(m.risk_mitigation_score for m in self.metrics_history)
            / len(self.metrics_history),
            adaptability_score=sum(m.adaptability_score for m in self.metrics_history) / len(self.metrics_history),
            innovation_index=sum(m.innovation_index for m in self.metrics_history) / len(self.metrics_history),
            resource_utilization=sum(m.resource_utilization for m in self.metrics_history) / len(self.metrics_history),
        )

        return avg_metrics
