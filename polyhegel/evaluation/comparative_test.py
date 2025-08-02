"""
Comparative testing framework for evaluating clustering vs tournament selection methods
"""

import asyncio
import json
import logging
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

from ..simulator import PolyhegelSimulator
from ..config import Config
from .metrics import MetricsCollector, StrategicMetrics

logger = logging.getLogger(__name__)


@dataclass
class TestConfiguration:
    """Configuration for comparative testing"""

    # Test parameters
    test_name: str = "comparative_test"
    iterations: int = 3
    timeout_seconds: int = 300

    # Simulation parameters
    model_name: str = Config.DEFAULT_MODEL
    temperature_counts: Optional[List[Tuple[float, int]]] = None
    mode: str = "temperature"

    # Test scenarios
    test_scenarios: Optional[List[Dict[str, Any]]] = None

    def __post_init__(self):
        if self.temperature_counts is None:
            self.temperature_counts = Config.DEFAULT_TEMPERATURE_COUNTS
        if self.test_scenarios is None:
            self.test_scenarios = []


@dataclass
class ComparisonResult:
    """Results from comparing two selection methods"""

    clustering_metrics: List[StrategicMetrics]
    tournament_metrics: List[StrategicMetrics]
    comparative_analysis: Dict[str, Any]
    test_configuration: TestConfiguration
    execution_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "clustering_metrics": [m.model_dump(mode="json") for m in self.clustering_metrics],
            "tournament_metrics": [m.model_dump(mode="json") for m in self.tournament_metrics],
            "comparative_analysis": self.comparative_analysis,
            "test_configuration": asdict(self.test_configuration),
            "execution_summary": self.execution_summary,
        }


class ComparativeTestFramework:
    """Framework for comparing clustering vs tournament selection methods"""

    def __init__(self, config: Optional[TestConfiguration] = None):
        """
        Initialize comparative testing framework

        Args:
            config: Test configuration, uses defaults if None
        """
        self.config = config or TestConfiguration()
        self.metrics_collector = MetricsCollector()
        self.results_history: List[ComparisonResult] = []

    async def run_comparative_test(
        self, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None, output_dir: Optional[Path] = None
    ) -> ComparisonResult:
        """
        Run comparative test between clustering and tournament methods

        Args:
            system_prompt: System prompt for simulation
            user_prompt: User prompt for simulation
            output_dir: Directory to save detailed results

        Returns:
            ComparisonResult with comprehensive comparison data
        """
        logger.info(f"Starting comparative test: {self.config.test_name}")
        test_start_time = time.time()

        # Initialize results storage
        clustering_metrics = []
        tournament_metrics = []
        execution_summary: Dict[str, Any] = {
            "test_start_time": test_start_time,
            "clustering_runs": [],
            "tournament_runs": [],
            "errors": [],
        }

        try:
            # Run clustering method tests
            logger.info(f"Running {self.config.iterations} iterations with clustering method...")
            for i in range(self.config.iterations):
                try:
                    metrics = await self._run_single_test(
                        selection_method="clustering", system_prompt=system_prompt, user_prompt=user_prompt, iteration=i
                    )
                    clustering_metrics.append(metrics)
                    execution_summary["clustering_runs"].append(
                        {
                            "iteration": i,
                            "success": True,
                            "execution_time": metrics.execution_time,
                            "overall_score": metrics.overall_score(),
                        }
                    )

                except Exception as e:
                    logger.error(f"Clustering iteration {i} failed: {e}")
                    execution_summary["errors"].append({"method": "clustering", "iteration": i, "error": str(e)})

            # Run tournament method tests
            logger.info(f"Running {self.config.iterations} iterations with tournament method...")
            for i in range(self.config.iterations):
                try:
                    metrics = await self._run_single_test(
                        selection_method="tournament", system_prompt=system_prompt, user_prompt=user_prompt, iteration=i
                    )
                    tournament_metrics.append(metrics)
                    execution_summary["tournament_runs"].append(
                        {
                            "iteration": i,
                            "success": True,
                            "execution_time": metrics.execution_time,
                            "overall_score": metrics.overall_score(),
                        }
                    )

                except Exception as e:
                    logger.error(f"Tournament iteration {i} failed: {e}")
                    execution_summary["errors"].append({"method": "tournament", "iteration": i, "error": str(e)})

            # Perform comparative analysis
            all_metrics = clustering_metrics + tournament_metrics
            comparative_analysis = self.metrics_collector.compare_metrics(all_metrics)

            # Add detailed statistical analysis
            comparative_analysis.update(self._perform_statistical_analysis(clustering_metrics, tournament_metrics))

            # Create comparison result
            test_end_time = time.time()
            execution_summary.update(
                {
                    "test_end_time": test_end_time,
                    "total_duration": test_end_time - test_start_time,
                    "clustering_success_rate": len(clustering_metrics) / self.config.iterations,
                    "tournament_success_rate": len(tournament_metrics) / self.config.iterations,
                }
            )

            result = ComparisonResult(
                clustering_metrics=clustering_metrics,
                tournament_metrics=tournament_metrics,
                comparative_analysis=comparative_analysis,
                test_configuration=self.config,
                execution_summary=execution_summary,
            )

            # Save results if output directory specified
            if output_dir:
                await self._save_results(result, output_dir)

            self.results_history.append(result)

            logger.info(f"Comparative test completed in {execution_summary['total_duration']:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Comparative test failed: {e}")
            raise

    async def _run_single_test(
        self, selection_method: str, system_prompt: Optional[str], user_prompt: Optional[str], iteration: int
    ) -> StrategicMetrics:
        """Run a single test iteration with specified selection method"""

        logger.info(f"Running {selection_method} iteration {iteration}")

        # Start performance monitoring
        tracemalloc.start()
        start_time = time.time()
        start_memory = tracemalloc.get_traced_memory()[0]

        try:
            # Initialize simulator
            simulator = PolyhegelSimulator(model_name=self.config.model_name)

            # Run simulation with timeout
            simulation_task = asyncio.create_task(
                simulator.run_simulation(
                    temperature_counts=self.config.temperature_counts,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    mode=self.config.mode,
                    selection_method=selection_method,
                )
            )

            try:
                results = await asyncio.wait_for(simulation_task, timeout=self.config.timeout_seconds)
            except asyncio.TimeoutError:
                simulation_task.cancel()
                raise TimeoutError(f"Simulation timed out after {self.config.timeout_seconds}s")

            # Calculate performance metrics
            end_time = time.time()
            end_memory = tracemalloc.get_traced_memory()[0]
            execution_time = end_time - start_time
            memory_usage = (end_memory - start_memory) / 1024 / 1024  # MB

            # Collect strategic metrics
            metrics = self.metrics_collector.collect_metrics(results, execution_time, memory_usage)

            logger.info(
                f"{selection_method} iteration {iteration} completed: "
                f"score={metrics.overall_score():.2f}, time={execution_time:.2f}s"
            )

            return metrics

        finally:
            tracemalloc.stop()

    def _perform_statistical_analysis(
        self, clustering_metrics: List[StrategicMetrics], tournament_metrics: List[StrategicMetrics]
    ) -> Dict[str, Any]:
        """Perform statistical analysis comparing the two methods"""

        analysis: Dict[str, Any] = {
            "statistical_significance": {},
            "effect_sizes": {},
            "performance_comparison": {},
            "reliability_analysis": {},
        }

        if not clustering_metrics or not tournament_metrics:
            return analysis

        # Extract score arrays for comparison
        clustering_scores = {
            "overall": [m.overall_score() for m in clustering_metrics],
            "coherence": [m.coherence_score for m in clustering_metrics],
            "feasibility": [m.feasibility_score for m in clustering_metrics],
            "domain_alignment": [m.domain_alignment_score for m in clustering_metrics],
            "execution_time": [m.execution_time for m in clustering_metrics],
        }

        tournament_scores = {
            "overall": [m.overall_score() for m in tournament_metrics],
            "coherence": [m.coherence_score for m in tournament_metrics],
            "feasibility": [m.feasibility_score for m in tournament_metrics],
            "domain_alignment": [m.domain_alignment_score for m in tournament_metrics],
            "execution_time": [m.execution_time for m in tournament_metrics],
        }

        # Statistical comparison for each metric
        for metric_name in clustering_scores.keys():
            c_scores = clustering_scores[metric_name]
            t_scores = tournament_scores[metric_name]

            c_mean = statistics.mean(c_scores)
            t_mean = statistics.mean(t_scores)
            c_stdev = statistics.stdev(c_scores) if len(c_scores) > 1 else 0
            t_stdev = statistics.stdev(t_scores) if len(t_scores) > 1 else 0

            # Effect size (Cohen's d approximation)
            pooled_std = ((c_stdev**2 + t_stdev**2) / 2) ** 0.5
            effect_size = (t_mean - c_mean) / pooled_std if pooled_std > 0 else 0

            # Practical significance (difference > 5% of scale)
            practical_threshold = 0.5 if metric_name != "execution_time" else 5.0  # 5 seconds
            practical_difference = abs(t_mean - c_mean) > practical_threshold

            analysis["effect_sizes"][metric_name] = {
                "clustering_mean": c_mean,
                "tournament_mean": t_mean,
                "difference": t_mean - c_mean,
                "effect_size": effect_size,
                "practical_significance": practical_difference,
                "winner": (
                    "tournament"
                    if t_mean > c_mean
                    else (
                        "clustering"
                        if metric_name != "execution_time"
                        else ("clustering" if t_mean > c_mean else "tournament")
                    )
                ),
            }

        # Reliability analysis (consistency across runs)
        clustering_cv: float = 0.0
        tournament_cv: float = 0.0

        if len(clustering_scores["overall"]) > 1 and statistics.mean(clustering_scores["overall"]) > 0:
            clustering_cv = statistics.stdev(clustering_scores["overall"]) / statistics.mean(
                clustering_scores["overall"]
            )

        if len(tournament_scores["overall"]) > 1 and statistics.mean(tournament_scores["overall"]) > 0:
            tournament_cv = statistics.stdev(tournament_scores["overall"]) / statistics.mean(
                tournament_scores["overall"]
            )

        analysis["reliability_analysis"] = {
            "clustering_consistency": 1 - clustering_cv,  # Lower CV = higher consistency
            "tournament_consistency": 1 - tournament_cv,
            "more_consistent": "clustering" if clustering_cv < tournament_cv else "tournament",
        }

        # Overall performance comparison
        clustering_wins = sum(
            1
            for metric in ["overall", "coherence", "feasibility", "domain_alignment"]
            if analysis["effect_sizes"][metric]["winner"] == "clustering"
        )
        tournament_wins = sum(
            1
            for metric in ["overall", "coherence", "feasibility", "domain_alignment"]
            if analysis["effect_sizes"][metric]["winner"] == "tournament"
        )

        analysis["performance_comparison"] = {
            "clustering_wins": clustering_wins,
            "tournament_wins": tournament_wins,
            "overall_winner": (
                "clustering"
                if clustering_wins > tournament_wins
                else "tournament" if tournament_wins > clustering_wins else "tie"
            ),
            "execution_time_winner": analysis["effect_sizes"]["execution_time"]["winner"],
        }

        return analysis

    async def _save_results(self, result: ComparisonResult, output_dir: Path):
        """Save detailed results to output directory"""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save main results
        results_file = output_dir / f"{self.config.test_name}_results.json"
        with open(results_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

        # Save summary report
        await self._generate_summary_report(result, output_dir)

        logger.info(f"Results saved to {output_dir}")

    async def _generate_summary_report(self, result: ComparisonResult, output_dir: Path):
        """Generate human-readable summary report"""

        report_file = output_dir / f"{self.config.test_name}_summary.md"

        clustering_metrics = result.clustering_metrics
        tournament_metrics = result.tournament_metrics
        analysis = result.comparative_analysis

        report_lines = [
            f"# Comparative Test Results: {self.config.test_name}",
            "",
            f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Iterations:** {self.config.iterations} per method",
            f"**Model:** {self.config.model_name}",
            f"**Mode:** {self.config.mode}",
            "",
            "## Summary",
            "",
        ]

        if "performance_comparison" in analysis:
            perf = analysis["performance_comparison"]
            report_lines.extend(
                [
                    f"**Overall Winner:** {perf['overall_winner'].title()}",
                    f"**Execution Speed Winner:** {perf['execution_time_winner'].title()}",
                    f"**Clustering Metric Wins:** {perf['clustering_wins']}/4",
                    f"**Tournament Metric Wins:** {perf['tournament_wins']}/4",
                    "",
                ]
            )

        # Method comparison table
        if clustering_metrics and tournament_metrics:
            c_overall = statistics.mean([m.overall_score() for m in clustering_metrics])
            t_overall = statistics.mean([m.overall_score() for m in tournament_metrics])
            c_time = statistics.mean([m.execution_time for m in clustering_metrics])
            t_time = statistics.mean([m.execution_time for m in tournament_metrics])

            report_lines.extend(
                [
                    "## Method Comparison",
                    "",
                    "| Metric | Clustering | Tournament | Winner |",
                    "|--------|------------|------------|--------|",
                    f"| Overall Score | {c_overall:.2f} | {t_overall:.2f} | {'Tournament' if t_overall > c_overall else 'Clustering'} |",
                    f"| Execution Time | {c_time:.2f}s | {t_time:.2f}s | {'Clustering' if c_time < t_time else 'Tournament'} |",
                    "",
                ]
            )

        # Detailed metrics
        if "effect_sizes" in analysis:
            report_lines.extend(["## Detailed Analysis", ""])

            for metric_name, data in analysis["effect_sizes"].items():
                if metric_name == "execution_time":
                    continue
                report_lines.extend(
                    [
                        f"### {metric_name.replace('_', ' ').title()}",
                        f"- **Clustering:** {data['clustering_mean']:.2f}",
                        f"- **Tournament:** {data['tournament_mean']:.2f}",
                        f"- **Difference:** {data['difference']:.2f}",
                        f"- **Winner:** {data['winner'].title()}",
                        "",
                    ]
                )

        # Recommendations
        report_lines.extend(["## Recommendations", ""])

        if "recommendations" in analysis:
            for rec in analysis["recommendations"]:
                report_lines.append(f"- {rec}")

        # Add custom recommendations based on analysis
        if "performance_comparison" in analysis:
            perf = analysis["performance_comparison"]
            if perf["overall_winner"] != "tie":
                report_lines.append(f"- Use **{perf['overall_winner']}** method for optimal strategic quality")

            if perf["execution_time_winner"]:
                report_lines.append(f"- Use **{perf['execution_time_winner']}** method for faster execution")

        # Write report
        with open(report_file, "w") as f:
            f.write("\n".join(report_lines))

    def run_automated_test_suite(
        self, test_scenarios: List[Dict[str, Any]], output_dir: Optional[Path] = None
    ) -> List[ComparisonResult]:
        """
        Run automated test suite with multiple scenarios

        Args:
            test_scenarios: List of test scenario configurations
            output_dir: Base directory for saving results

        Returns:
            List of ComparisonResult objects
        """
        logger.info(f"Running automated test suite with {len(test_scenarios)} scenarios")

        results = []

        for i, scenario in enumerate(test_scenarios):
            scenario_name = scenario.get("name", f"scenario_{i}")
            logger.info(f"Running scenario: {scenario_name}")

            # Update configuration for this scenario
            scenario_config = TestConfiguration(
                test_name=scenario_name,
                **{k: v for k, v in scenario.items() if k != "name" and k in TestConfiguration.__annotations__},
            )

            # Create test framework for this scenario
            framework = ComparativeTestFramework(scenario_config)

            # Determine output directory for this scenario
            scenario_output = None
            if output_dir:
                scenario_output = Path(output_dir) / scenario_name

            try:
                result = asyncio.run(
                    framework.run_comparative_test(
                        system_prompt=scenario.get("system_prompt"),
                        user_prompt=scenario.get("user_prompt"),
                        output_dir=scenario_output,
                    )
                )
                results.append(result)

                logger.info(f"Scenario {scenario_name} completed successfully")

            except Exception as e:
                logger.error(f"Scenario {scenario_name} failed: {e}")
                # Continue with next scenario

        logger.info(f"Automated test suite completed: {len(results)}/{len(test_scenarios)} scenarios successful")
        return results
