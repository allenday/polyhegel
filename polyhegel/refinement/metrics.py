"""
Performance tracking and metrics collection for recursive refinement

Tracks strategy performance over time using structured logging and
in-memory session data for the refinement feedback loop.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import statistics

from ..models import StrategyChain
from ..evaluation.metrics import StrategicMetrics

logger = logging.getLogger(__name__)


class RefinementMetrics(BaseModel):
    """Metrics for tracking refinement performance over time"""

    # Refinement metadata
    refinement_id: str
    strategy_id: str
    generation: int = Field(ge=0, description="Refinement generation (0 = original, 1+ = refinement iterations)")
    timestamp: datetime = Field(default_factory=datetime.now)

    # Performance metrics
    strategic_metrics: StrategicMetrics = Field(default_factory=StrategicMetrics)
    improvement_score: float = Field(
        default=0.0, ge=-1.0, le=1.0, description="Improvement score, negative = degradation"
    )
    convergence_indicator: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Convergence level, higher = more converged"
    )

    # Strategic compliance metrics
    strategic_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Strategic compliance score")
    recursive_depth: int = Field(default=0, ge=0, description="How many refinement levels deep")
    evolution_velocity: float = Field(default=0.0, ge=-1.0, le=1.0, description="Rate of improvement per iteration")

    # Trend analysis
    performance_trend: str = Field(
        default="stable", description="Performance trend: improving, degrading, stable, oscillating"
    )
    trend_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in trend analysis")

    # Resource efficiency
    refinement_cost: float = Field(default=0.0, ge=0.0, description="Time/compute cost for this refinement")
    roi_estimate: float = Field(default=0.0, description="Return on investment for refinement effort")

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        data["timestamp"] = self.timestamp.isoformat()
        data["strategic_metrics"] = self.strategic_metrics.model_dump(mode="json")
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RefinementMetrics":
        """Create from dictionary"""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["strategic_metrics"] = (
            StrategicMetrics.model_validate(data["strategic_metrics"])
            if hasattr(StrategicMetrics, "model_validate")
            else StrategicMetrics.parse_obj(data["strategic_metrics"])
        )
        return cls(**data)


class PerformanceTracker:
    """Tracks strategy performance over time using structured logging and in-memory session data"""

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize performance tracker

        Args:
            session_id: Optional session identifier for this refinement session
        """
        self.session_id = session_id or f"session_{int(time.time())}"

        # In-memory storage for current session metrics
        self.session_metrics: Dict[str, List[RefinementMetrics]] = {}
        self.max_metrics_per_strategy = 100  # Limit memory usage

    def _log_metrics(self, metrics: RefinementMetrics):
        """Log metrics as structured JSON for telemetry aggregation"""
        logger.info(
            "refinement_metrics",
            extra={
                "event_type": "refinement_metrics",
                "session_id": self.session_id,
                "refinement_id": metrics.refinement_id,
                "strategy_id": metrics.strategy_id,
                "generation": metrics.generation,
                "timestamp": metrics.timestamp.isoformat(),
                "improvement_score": metrics.improvement_score,
                "convergence_indicator": metrics.convergence_indicator,
                "strategic_compliance_score": metrics.strategic_compliance_score,
                "performance_trend": metrics.performance_trend,
                "trend_confidence": metrics.trend_confidence,
                "evolution_velocity": metrics.evolution_velocity,
                "roi_estimate": metrics.roi_estimate,
                "strategic_metrics": metrics.strategic_metrics.model_dump(mode="json"),
            },
        )

    def record_performance(
        self,
        strategy: StrategyChain,
        strategic_metrics: StrategicMetrics,
        generation: int = 0,
        refinement_id: Optional[str] = None,
    ) -> RefinementMetrics:
        """
        Record performance metrics for a strategy

        Args:
            strategy: Strategy to track
            strategic_metrics: Evaluated strategic metrics
            generation: Refinement generation (0 = original)
            refinement_id: Unique refinement session ID

        Returns:
            RefinementMetrics object with calculated metrics
        """

        # Generate IDs if not provided
        strategy_id = getattr(strategy, "id", None) or f"strategy_{hash(str(strategy))}"
        refinement_id = refinement_id or f"refinement_{int(time.time())}"

        # Calculate improvement score vs previous generation
        improvement_score = self._calculate_improvement_score(strategy_id, strategic_metrics, generation)

        # Calculate convergence indicator
        convergence_indicator = self._calculate_convergence_indicator(strategy_id, strategic_metrics)

        # Calculate strategic compliance score
        strategic_compliance_score = self._calculate_strategic_compliance(strategy, strategic_metrics)

        # Calculate evolution velocity
        evolution_velocity = self._calculate_evolution_velocity(strategy_id, improvement_score, generation)

        # Analyze performance trend
        trend_info = self._analyze_performance_trend(strategy_id, strategic_metrics)

        # Calculate refinement ROI
        roi_estimate = self._calculate_refinement_roi(improvement_score, strategic_metrics.execution_time)

        # Create refinement metrics
        metrics = RefinementMetrics(
            refinement_id=refinement_id,
            strategy_id=strategy_id,
            generation=generation,
            strategic_metrics=strategic_metrics,
            improvement_score=improvement_score,
            convergence_indicator=convergence_indicator,
            strategic_compliance_score=strategic_compliance_score,
            recursive_depth=generation,
            evolution_velocity=evolution_velocity,
            performance_trend=trend_info["trend"],
            trend_confidence=trend_info["confidence"],
            refinement_cost=strategic_metrics.execution_time,
            roi_estimate=roi_estimate,
        )

        # Log metrics for telemetry aggregation
        self._log_metrics(metrics)

        # Store in session memory
        if strategy_id not in self.session_metrics:
            self.session_metrics[strategy_id] = []

        self.session_metrics[strategy_id].append(metrics)

        # Trim memory if too large
        if len(self.session_metrics[strategy_id]) > self.max_metrics_per_strategy:
            self.session_metrics[strategy_id] = self.session_metrics[strategy_id][-self.max_metrics_per_strategy :]

        logger.info(
            f"Recorded performance for {strategy_id} generation {generation}: "
            f"improvement={improvement_score:.3f}, convergence={convergence_indicator:.3f}"
        )

        return metrics

    def _calculate_improvement_score(
        self, strategy_id: str, current_metrics: StrategicMetrics, generation: int
    ) -> float:
        """Calculate improvement score vs previous generation"""

        if generation == 0:
            return 0.0  # Baseline, no improvement to measure

        # Get previous generation metrics
        previous_metrics = self.get_metrics_by_generation(strategy_id, generation - 1)
        if not previous_metrics:
            return 0.0

        previous = previous_metrics[-1].strategic_metrics  # Most recent of previous gen
        current = current_metrics

        # Compare overall scores
        prev_score = previous.overall_score()
        curr_score = current.overall_score()

        if prev_score == 0:
            return 1.0 if curr_score > 0 else 0.0

        # Calculate relative improvement (-1 to 1)
        improvement = (curr_score - prev_score) / prev_score
        return max(-1.0, min(1.0, improvement))

    def _calculate_convergence_indicator(self, strategy_id: str, current_metrics: StrategicMetrics) -> float:
        """Calculate how much the strategy is converging"""

        recent_metrics = self.get_recent_metrics(strategy_id, limit=5)
        if len(recent_metrics) < 3:
            return 0.0

        # Look at variance in recent scores - lower variance = more convergence
        recent_scores = [m.strategic_metrics.overall_score() for m in recent_metrics]
        if all(score == recent_scores[0] for score in recent_scores):
            return 1.0  # Perfect convergence

        variance = statistics.variance(recent_scores)
        max_possible_variance = 25.0  # Assume max score range of 10

        # Convert variance to convergence (0 = high variance, 1 = low variance)
        convergence = max(0.0, 1.0 - (variance / max_possible_variance))
        return convergence

    def _calculate_strategic_compliance(self, strategy: StrategyChain, strategic_metrics: StrategicMetrics) -> float:
        """Calculate strategic compliance score"""

        compliance_factors = []

        # Factor 1: Strategic coherence (requirement for logical flow)
        coherence_score = strategic_metrics.coherence_score / 10.0
        compliance_factors.append(coherence_score)

        # Factor 2: Risk management (requirement for risk awareness)
        risk_score = strategic_metrics.risk_management_score / 10.0
        compliance_factors.append(risk_score)

        # Factor 3: Domain alignment (strategic domain alignment)
        domain_score = strategic_metrics.domain_alignment_score / 10.0
        compliance_factors.append(domain_score)

        # Factor 4: Resource efficiency (requirement for efficiency)
        resource_score = strategic_metrics.resource_efficiency_score / 10.0
        compliance_factors.append(resource_score)

        # Factor 5: Implementation feasibility (requirement for practicality)
        feasibility_score = strategic_metrics.feasibility_score / 10.0
        compliance_factors.append(feasibility_score)

        # Weighted average with emphasis on coherence and risk management
        weights = [0.25, 0.25, 0.2, 0.15, 0.15]
        compliance_score = sum(factor * weight for factor, weight in zip(compliance_factors, weights))

        return compliance_score

    def _calculate_evolution_velocity(self, strategy_id: str, improvement_score: float, generation: int) -> float:
        """Calculate rate of evolution/improvement over time"""

        if generation == 0:
            return 0.0

        # Get historical improvement scores
        all_metrics = self.get_all_metrics(strategy_id)
        if len(all_metrics) < 2:
            return improvement_score  # Only current improvement to go on

        # Calculate moving average of improvement scores
        recent_improvements = [m.improvement_score for m in all_metrics[-5:]]  # Last 5
        avg_improvement = statistics.mean(recent_improvements)

        # Factor in time - faster improvements have higher velocity
        time_factor = 1.0 / max(1, generation)  # Velocity decreases with more generations

        velocity = avg_improvement * (1.0 + time_factor)
        return max(-1.0, min(1.0, velocity))

    def _analyze_performance_trend(self, strategy_id: str, current_metrics: StrategicMetrics) -> Dict[str, Any]:
        """Analyze performance trend over recent history"""

        recent_metrics = self.get_recent_metrics(strategy_id, limit=10)
        if len(recent_metrics) < 3:
            return {"trend": "stable", "confidence": 0.0}

        # Extract overall scores
        scores = [m.strategic_metrics.overall_score() for m in recent_metrics]

        # Calculate trend using linear regression
        x = list(range(len(scores)))
        if len(scores) > 1:
            slope = (
                statistics.correlation(x, scores)
                if statistics.variance(x) > 0 and statistics.variance(scores) > 0
                else 0
            )
        else:
            slope = 0

        # Classify trend
        if abs(slope) < 0.05:
            trend = "stable"
        elif slope > 0.15:
            trend = "improving"
        elif slope < -0.15:
            trend = "degrading"
        else:
            # Check for oscillation
            ups = sum(1 for i in range(1, len(scores)) if scores[i] > scores[i - 1])
            downs = sum(1 for i in range(1, len(scores)) if scores[i] < scores[i - 1])

            if abs(ups - downs) <= 1:  # Equal ups and downs
                trend = "oscillating"
            elif slope > 0:
                trend = "improving"
            else:
                trend = "degrading"

        # Calculate confidence based on consistency
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0
        confidence = max(0.0, min(1.0, 1.0 - (score_variance / 10.0)))

        return {"trend": trend, "confidence": confidence, "slope": slope, "variance": score_variance}

    def _calculate_refinement_roi(self, improvement_score: float, refinement_cost: float) -> float:
        """Calculate return on investment for refinement effort"""

        if refinement_cost <= 0:
            return improvement_score * 10  # High ROI if no cost

        # ROI = (improvement * impact_factor) / cost
        impact_factor = 100  # Assume 100 "value units" for full improvement
        roi = (improvement_score * impact_factor) / refinement_cost

        return max(-10.0, min(10.0, roi))  # Cap ROI between -10 and 10

    def get_metrics_by_generation(self, strategy_id: str, generation: int) -> List[RefinementMetrics]:
        """Get all metrics for a specific generation of a strategy from current session"""

        if strategy_id not in self.session_metrics:
            return []

        return [metrics for metrics in self.session_metrics[strategy_id] if metrics.generation == generation]

    def get_recent_metrics(self, strategy_id: str, limit: int = 10) -> List[RefinementMetrics]:
        """Get recent metrics for a strategy from current session"""

        if strategy_id not in self.session_metrics:
            return []

        return self.session_metrics[strategy_id][-limit:]

    def get_all_metrics(self, strategy_id: str) -> List[RefinementMetrics]:
        """Get all metrics for a strategy from current session"""

        return self.session_metrics.get(strategy_id, [])

    def get_performance_summary(self, strategy_id: str) -> Dict[str, Any]:
        """Get performance summary for a strategy"""

        all_metrics = self.get_all_metrics(strategy_id)
        if not all_metrics:
            return {}

        latest = all_metrics[-1]

        # Calculate summary statistics
        overall_scores = [m.strategic_metrics.overall_score() for m in all_metrics]
        improvement_scores = [m.improvement_score for m in all_metrics]

        summary = {
            "strategy_id": strategy_id,
            "total_generations": len(set(m.generation for m in all_metrics)),
            "total_refinements": len(all_metrics),
            "latest_generation": latest.generation,
            "latest_score": latest.strategic_metrics.overall_score(),
            "best_score": max(overall_scores),
            "average_score": statistics.mean(overall_scores),
            "score_trend": latest.performance_trend,
            "trend_confidence": latest.trend_confidence,
            "convergence_level": latest.convergence_indicator,
            "strategic_compliance": latest.strategic_compliance_score,
            "evolution_velocity": latest.evolution_velocity,
            "average_improvement": statistics.mean(improvement_scores) if improvement_scores else 0.0,
            "refinement_efficiency": latest.roi_estimate,
            "time_span_hours": (all_metrics[-1].timestamp - all_metrics[0].timestamp).total_seconds() / 3600,
        }

        return summary

    def clear_session_metrics(self, strategy_id: Optional[str] = None):
        """Clear metrics from current session"""

        if strategy_id:
            if strategy_id in self.session_metrics:
                del self.session_metrics[strategy_id]
                logger.info(f"Cleared session metrics for strategy {strategy_id}")
        else:
            cleared_count = len(self.session_metrics)
            self.session_metrics.clear()
            logger.info(f"Cleared all session metrics ({cleared_count} strategies)")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session metrics"""

        total_strategies = len(self.session_metrics)
        total_metrics = sum(len(metrics) for metrics in self.session_metrics.values())

        return {
            "session_id": self.session_id,
            "strategies_tracked": total_strategies,
            "total_metrics_recorded": total_metrics,
            "strategies": list(self.session_metrics.keys()),
        }
