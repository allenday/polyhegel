"""
Strategic evaluation metrics for comparing different selection methods
"""

import time
import logging
from typing import Dict, List, Any
from statistics import mean, stdev
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class StrategicMetrics(BaseModel):
    """Container for strategic evaluation metrics"""

    # Core strategic metrics
    coherence_score: float = 0.0
    feasibility_score: float = 0.0
    domain_alignment_score: float = 0.0
    risk_management_score: float = 0.0
    resource_efficiency_score: float = 0.0

    # Performance metrics
    execution_time: float = 0.0
    memory_usage: float = 0.0

    # Selection method metadata
    selection_method: str = ""
    trunk_strategy_title: str = ""
    total_strategies: int = 0

    # Additional analysis
    strategy_diversity: float = 0.0
    confidence_variance: float = 0.0
    timeline_realism: float = 0.0

    def overall_score(self) -> float:
        """Calculate weighted overall strategic score"""
        weights = {
            "coherence": 0.25,
            "feasibility": 0.25,
            "domain_alignment": 0.20,
            "risk_management": 0.15,
            "resource_efficiency": 0.15,
        }

        return (
            self.coherence_score * weights["coherence"]
            + self.feasibility_score * weights["feasibility"]
            + self.domain_alignment_score * weights["domain_alignment"]
            + self.risk_management_score * weights["risk_management"]
            + self.resource_efficiency_score * weights["resource_efficiency"]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization"""
        return self.model_dump() if hasattr(self, "model_dump") else self.dict()


class MetricsCollector:
    """Collects and analyzes strategic metrics from simulation results"""

    def __init__(self, model=None):
        """
        Initialize metrics collector

        Args:
            model: Optional LLM model for advanced metric evaluation
        """
        self.model = model
        self.collected_metrics: List[StrategicMetrics] = []

    def collect_metrics(
        self, simulation_results: Dict, execution_time: float, memory_usage: float = 0.0
    ) -> StrategicMetrics:
        """
        Collect comprehensive metrics from simulation results

        Args:
            simulation_results: Results from simulator.run_simulation()
            execution_time: Time taken for simulation
            memory_usage: Memory usage during simulation

        Returns:
            StrategicMetrics object with collected metrics
        """
        start_time = time.time()

        trunk = simulation_results.get("trunk")
        twigs = simulation_results.get("twigs", [])
        metadata = simulation_results.get("metadata", {})

        if not trunk:
            logger.warning("No trunk strategy found in results")
            return StrategicMetrics()

        # Extract selection method
        selection_method = metadata.get("selection_method", "unknown")
        if "cluster_results" in simulation_results:
            cluster_results = simulation_results["cluster_results"]
            if isinstance(cluster_results, dict):
                selection_method = cluster_results.get("selection_method", selection_method)

        # Calculate core strategic metrics
        coherence_score = self._calculate_coherence_score(trunk)
        feasibility_score = self._calculate_feasibility_score(trunk)
        domain_alignment_score = self._calculate_domain_alignment_score(trunk)
        risk_management_score = self._calculate_risk_management_score(trunk)
        resource_efficiency_score = self._calculate_resource_efficiency_score(trunk)

        # Calculate additional metrics
        all_strategies = [trunk] + twigs
        strategy_diversity = self._calculate_strategy_diversity(all_strategies)
        confidence_variance = self._calculate_confidence_variance(all_strategies)
        timeline_realism = self._calculate_timeline_realism(trunk)

        metrics = StrategicMetrics(
            coherence_score=coherence_score,
            feasibility_score=feasibility_score,
            domain_alignment_score=domain_alignment_score,
            risk_management_score=risk_management_score,
            resource_efficiency_score=resource_efficiency_score,
            execution_time=execution_time,
            memory_usage=memory_usage,
            selection_method=selection_method,
            trunk_strategy_title=trunk.strategy.title if hasattr(trunk, "strategy") else str(trunk),
            total_strategies=len(all_strategies),
            strategy_diversity=strategy_diversity,
            confidence_variance=confidence_variance,
            timeline_realism=timeline_realism,
        )

        self.collected_metrics.append(metrics)

        collection_time = time.time() - start_time
        logger.info(f"Metrics collection completed in {collection_time:.2f}s")

        return metrics

    def _calculate_coherence_score(self, trunk_strategy) -> float:
        """Calculate strategic coherence score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy
                steps = strategy.steps

                if not steps:
                    return 0.0

                # Check logical flow between steps
                coherence_factors = []

                # Prerequisites fulfillment
                all_outcomes = set()
                unfulfilled_prereqs = 0

                for step in steps:
                    # Add this step's outcomes to available outcomes
                    all_outcomes.add(step.outcome.lower())

                    # Check if prerequisites are met by previous outcomes
                    for prereq in step.prerequisites:
                        if not any(prereq.lower() in outcome for outcome in all_outcomes):
                            unfulfilled_prereqs += 1

                prereq_score = max(0, 10 - (unfulfilled_prereqs * 2))
                coherence_factors.append(prereq_score)

                # Confidence consistency
                confidences = [step.confidence for step in steps]
                confidence_consistency = 10 - (stdev(confidences) * 10 if len(confidences) > 1 else 0)
                coherence_factors.append(max(0, confidence_consistency))

                # Step count reasonableness (3-7 steps is optimal)
                step_count = len(steps)
                if 3 <= step_count <= 7:
                    step_score = 10
                elif step_count < 3:
                    step_score = step_count * 3
                else:  # > 7
                    step_score = max(0, 10 - (step_count - 7))
                coherence_factors.append(step_score)

                return min(10, mean(coherence_factors))

        except Exception as e:
            logger.warning(f"Error calculating coherence score: {e}")

        return 5.0  # Default neutral score

    def _calculate_feasibility_score(self, trunk_strategy) -> float:
        """Calculate implementation feasibility score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy

                feasibility_factors = []

                # Timeline realism
                timeline = strategy.estimated_timeline.lower()
                if any(word in timeline for word in ["immediate", "days", "1 week"]):
                    timeline_score = 8  # Aggressive but possible
                elif any(word in timeline for word in ["weeks", "1-3 months", "quarter"]):
                    timeline_score = 10  # Realistic
                elif any(word in timeline for word in ["6 months", "year", "12 months"]):
                    timeline_score = 9  # Conservative but feasible
                else:
                    timeline_score = 6  # Unclear or very long term
                feasibility_factors.append(timeline_score)

                # Resource requirements reasonableness
                resources = strategy.resource_requirements
                resource_count = len(resources)
                if 2 <= resource_count <= 6:
                    resource_score = 10
                elif resource_count < 2:
                    resource_score = 5  # Too few resources identified
                else:
                    resource_score = max(0, 10 - (resource_count - 6))
                feasibility_factors.append(resource_score)

                # Risk awareness
                total_risks = sum(len(step.risks) for step in strategy.steps)
                if total_risks == 0:
                    risk_awareness_score = 3  # No risks identified is unrealistic
                elif 1 <= total_risks <= len(strategy.steps) * 2:
                    risk_awareness_score = 10  # Good risk identification
                else:
                    risk_awareness_score = 7  # Too many risks might indicate over-analysis
                feasibility_factors.append(risk_awareness_score)

                return min(10, mean(feasibility_factors))

        except Exception as e:
            logger.warning(f"Error calculating feasibility score: {e}")

        return 5.0

    def _calculate_domain_alignment_score(self, trunk_strategy) -> float:
        """Calculate strategic domain alignment score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy
                alignment_scores = strategy.alignment_score

                if not alignment_scores:
                    return 5.0  # No alignment specified

                # Convert alignment scores to 0-10 scale if needed
                normalized_scores = []
                for score in alignment_scores.values():
                    if isinstance(score, (int, float)):
                        if score <= 5:  # Assume 1-5 scale
                            normalized_scores.append(score * 2)
                        else:  # Assume already 0-10 scale
                            normalized_scores.append(min(10, score))

                if normalized_scores:
                    return mean(normalized_scores)

        except Exception as e:
            logger.warning(f"Error calculating domain alignment score: {e}")

        return 5.0

    def _calculate_risk_management_score(self, trunk_strategy) -> float:
        """Calculate risk management effectiveness score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy
                steps = strategy.steps

                risk_factors = []

                # Risk identification completeness
                steps_with_risks = sum(1 for step in steps if step.risks)
                risk_coverage = (steps_with_risks / len(steps)) * 10 if steps else 0
                risk_factors.append(risk_coverage)

                # Risk severity distribution
                total_risks = sum(len(step.risks) for step in steps)
                if total_risks > 0:
                    avg_risks_per_step = total_risks / len(steps)
                    if 0.5 <= avg_risks_per_step <= 2.0:
                        risk_distribution_score = 10
                    else:
                        risk_distribution_score = 7
                    risk_factors.append(risk_distribution_score)

                # Confidence vs risk correlation
                high_risk_steps = [step for step in steps if len(step.risks) >= 2]
                if high_risk_steps:
                    high_risk_confidences = [step.confidence for step in high_risk_steps]
                    avg_high_risk_confidence = mean(high_risk_confidences)
                    # Lower confidence for high-risk steps is more realistic
                    confidence_realism = (1 - avg_high_risk_confidence) * 10
                    risk_factors.append(max(0, confidence_realism))

                return min(10, mean(risk_factors)) if risk_factors else 5.0

        except Exception as e:
            logger.warning(f"Error calculating risk management score: {e}")

        return 5.0

    def _calculate_resource_efficiency_score(self, trunk_strategy) -> float:
        """Calculate resource efficiency score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy

                # Resource specificity
                resources = strategy.resource_requirements
                specific_resources = sum(1 for r in resources if len(r.split()) > 2)
                specificity_score = min(10, (specific_resources / len(resources)) * 10) if resources else 0

                # Resource type diversity
                resource_types = set()
                for resource in resources:
                    resource_lower = resource.lower()
                    if any(word in resource_lower for word in ["team", "people", "talent", "staff"]):
                        resource_types.add("human")
                    if any(word in resource_lower for word in ["budget", "funding", "capital", "money"]):
                        resource_types.add("financial")
                    if any(word in resource_lower for word in ["technology", "infrastructure", "system", "platform"]):
                        resource_types.add("technical")
                    if any(word in resource_lower for word in ["time", "timeline", "schedule"]):
                        resource_types.add("temporal")

                diversity_score = min(10, len(resource_types) * 2.5)

                return mean([specificity_score, diversity_score])

        except Exception as e:
            logger.warning(f"Error calculating resource efficiency score: {e}")

        return 5.0

    def _calculate_strategy_diversity(self, all_strategies: List) -> float:
        """Calculate diversity across all strategies (0-10)"""
        try:
            if len(all_strategies) < 2:
                return 0.0

            # Compare strategy titles for uniqueness
            titles = [getattr(s, "strategy", s).title if hasattr(s, "strategy") else str(s) for s in all_strategies]
            unique_words = set()
            for title in titles:
                unique_words.update(title.lower().split())

            # More unique words indicates higher diversity
            # Scale to 0-10 range: ratio of unique words to total words
            total_words = sum(len(title.split()) for title in titles)
            diversity_ratio = len(unique_words) / total_words if total_words > 0 else 0
            return min(10, diversity_ratio * 10)

        except Exception as e:
            logger.warning(f"Error calculating strategy diversity: {e}")

        return 5.0

    def _calculate_confidence_variance(self, all_strategies: List) -> float:
        """Calculate variance in confidence scores across strategies"""
        try:
            confidences = []
            for strategy in all_strategies:
                if hasattr(strategy, "strategy"):
                    strategy_obj = strategy.strategy
                    if hasattr(strategy_obj, "steps"):
                        for step in strategy_obj.steps:
                            confidences.append(step.confidence)

            if len(confidences) > 1:
                return stdev(confidences)
            return 0.0

        except Exception as e:
            logger.warning(f"Error calculating confidence variance: {e}")

        return 0.0

    def _calculate_timeline_realism(self, trunk_strategy) -> float:
        """Calculate timeline realism score (0-10)"""
        try:
            if hasattr(trunk_strategy, "strategy"):
                strategy = trunk_strategy.strategy
                timeline = strategy.estimated_timeline.lower()
                step_count = len(strategy.steps)

                # Extract time estimate
                months = 0
                if "day" in timeline:
                    months = 0.1
                elif "week" in timeline:
                    if "1-2" in timeline or "2" in timeline:
                        months = 0.5
                    else:
                        months = 0.25
                elif "month" in timeline:
                    if "1-3" in timeline:
                        months = 2
                    elif "6" in timeline:
                        months = 6
                    elif "12" in timeline:
                        months = 12
                    else:
                        months = 1
                elif "year" in timeline:
                    months = 12

                # Reasonable time per step (assuming 2-4 weeks per major step)
                expected_months = step_count * 0.75  # 3 weeks per step average

                if months == 0:
                    return 5.0  # Unclear timeline

                ratio = months / expected_months if expected_months > 0 else 1

                if 0.5 <= ratio <= 2.0:
                    return 10  # Realistic
                elif 0.25 <= ratio < 0.5:
                    return 7  # Aggressive but possible
                elif 2.0 < ratio <= 4.0:
                    return 8  # Conservative
                else:
                    return 4  # Unrealistic (too fast or too slow)

        except Exception as e:
            logger.warning(f"Error calculating timeline realism: {e}")

        return 5.0

    def compare_metrics(self, metrics_list: List[StrategicMetrics]) -> Dict[str, Any]:
        """
        Compare multiple metrics and generate analysis

        Args:
            metrics_list: List of StrategicMetrics to compare

        Returns:
            Dictionary with comparative analysis
        """
        if not metrics_list:
            return {}

        comparison = {"summary": {}, "by_method": {}, "recommendations": []}

        # Group by selection method
        method_groups = {}
        for metrics in metrics_list:
            method = metrics.selection_method
            if method not in method_groups:
                method_groups[method] = []
            method_groups[method].append(metrics)

        # Calculate averages by method
        for method, method_metrics in method_groups.items():
            avg_metrics = {
                "count": len(method_metrics),
                "avg_coherence": mean([m.coherence_score for m in method_metrics]),
                "avg_feasibility": mean([m.feasibility_score for m in method_metrics]),
                "avg_domain_alignment": mean([m.domain_alignment_score for m in method_metrics]),
                "avg_risk_management": mean([m.risk_management_score for m in method_metrics]),
                "avg_resource_efficiency": mean([m.resource_efficiency_score for m in method_metrics]),
                "avg_overall": mean([m.overall_score() for m in method_metrics]),
                "avg_execution_time": mean([m.execution_time for m in method_metrics]),
                "avg_strategy_diversity": mean([m.strategy_diversity for m in method_metrics]),
            }
            comparison["by_method"][method] = avg_metrics

        # Generate recommendations
        if len(method_groups) >= 2:
            methods = list(method_groups.keys())
            method1, method2 = methods[0], methods[1]

            m1_overall = comparison["by_method"][method1]["avg_overall"]
            m2_overall = comparison["by_method"][method2]["avg_overall"]

            if abs(m1_overall - m2_overall) < 0.5:
                comparison["recommendations"].append("Both methods show similar overall performance")
            elif m1_overall > m2_overall:
                comparison["recommendations"].append(f"{method1} shows superior overall strategic quality")
            else:
                comparison["recommendations"].append(f"{method2} shows superior overall strategic quality")

            # Performance comparison
            m1_time = comparison["by_method"][method1]["avg_execution_time"]
            m2_time = comparison["by_method"][method2]["avg_execution_time"]

            if m1_time < m2_time * 0.8:
                comparison["recommendations"].append(f"{method1} is significantly faster")
            elif m2_time < m1_time * 0.8:
                comparison["recommendations"].append(f"{method2} is significantly faster")

        return comparison
