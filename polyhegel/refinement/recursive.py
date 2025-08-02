"""
Recursive refinement engine for continuous strategy optimization

Implements the main orchestration system for recursive strategy refinement
using systematic optimization protocols and performance feedback loops.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path
import json
from datetime import datetime

from ..models import StrategyChain
from ..evaluation.metrics import MetricsCollector, StrategicMetrics
from ..simulator import PolyhegelSimulator
from .metrics import PerformanceTracker, RefinementMetrics
from .feedback import FeedbackLoop, StrategyImprover, FeedbackAnalysis, ImprovementCategory

logger = logging.getLogger(__name__)


class RefinementConfiguration(BaseModel):
    """Configuration for recursive refinement process"""

    # Core parameters
    max_generations: int = 10
    convergence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    improvement_threshold: float = Field(default=0.05, ge=0.0)
    quality_target: float = Field(default=8.5, description="Target overall score")

    # Resource limits
    max_refinement_time_minutes: int = Field(default=60, gt=0)
    max_concurrent_refinements: int = Field(default=3, gt=0)

    # Model configuration
    model_name: str = "claude-3-haiku-20240307"
    temperature_counts: List[Tuple[float, int]] = Field(default_factory=lambda: [(0.7, 3)])

    # Strategic compliance
    strategic_compliance_target: float = Field(default=0.8, ge=0.0, le=1.0)
    require_strategic_compliance: bool = True

    # Focus areas for improvement
    improvement_priorities: List[ImprovementCategory] = Field(default_factory=list)

    # Output configuration
    save_intermediate_results: bool = True
    output_directory: Optional[Path] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RefinementSession(BaseModel):
    """Represents a complete refinement session"""

    session_id: str
    original_strategy: StrategyChain
    configuration: RefinementConfiguration
    start_time: datetime = Field(default_factory=datetime.now)

    # Results tracking
    generations: List[StrategyChain] = Field(default_factory=list)
    performance_history: List[RefinementMetrics] = Field(default_factory=list)
    feedback_analyses: List[FeedbackAnalysis] = Field(default_factory=list)

    # Session state
    current_generation: int = Field(default=0, ge=0)
    is_complete: bool = False
    completion_reason: str = ""
    best_strategy: Optional[StrategyChain] = None
    best_score: float = Field(default=0.0, ge=0.0)

    # Resource tracking
    total_execution_time: float = Field(default=0.0, ge=0.0)
    total_llm_calls: int = Field(default=0, ge=0)
    total_cost_estimate: float = Field(default=0.0, ge=0.0)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class RecursiveRefinementEngine:
    """Main engine for recursive strategy refinement"""

    def __init__(
        self,
        configuration: Optional[RefinementConfiguration] = None,
        performance_tracker: Optional[PerformanceTracker] = None,
    ):
        """
        Initialize recursive refinement engine

        Args:
            configuration: Refinement configuration
            performance_tracker: Performance tracking system
        """
        self.config = configuration or RefinementConfiguration()
        self.performance_tracker = performance_tracker or PerformanceTracker()

        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.feedback_loop = FeedbackLoop(self.performance_tracker, self.config.model_name)
        self.strategy_improver = StrategyImprover(self.config.model_name)

        # Session tracking
        self.active_sessions: Dict[str, RefinementSession] = {}
        self.completed_sessions: List[RefinementSession] = []

        # Performance monitoring
        self._total_strategies_refined = 0
        self._total_refinement_time = 0.0

    async def refine_strategy(
        self,
        strategy: StrategyChain,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> RefinementSession:
        """
        Perform recursive refinement on a strategy

        Args:
            strategy: Strategy to refine
            system_prompt: System prompt for evaluation
            user_prompt: User prompt context
            session_id: Optional session ID for tracking

        Returns:
            Completed RefinementSession with results
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = f"refinement_{int(time.time())}_{hash(str(strategy))}"

        logger.info(f"Starting recursive refinement session {session_id}")

        # Create refinement session
        session = RefinementSession(session_id=session_id, original_strategy=strategy, configuration=self.config)

        self.active_sessions[session_id] = session

        try:
            # Run refinement loop
            await self._execute_refinement_loop(session, system_prompt, user_prompt)

            # Mark session as complete
            session.is_complete = True
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]

            # Update global statistics
            self._total_strategies_refined += 1
            self._total_refinement_time += session.total_execution_time

            logger.info(
                f"Refinement session {session_id} completed: "
                f"{session.current_generation} generations, "
                f"best_score={session.best_score:.2f}, "
                f"reason={session.completion_reason}"
            )

            return session

        except Exception as e:
            logger.error(f"Refinement session {session_id} failed: {e}")
            session.is_complete = True
            session.completion_reason = f"Error: {str(e)}"
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            raise

    async def _execute_refinement_loop(
        self, session: RefinementSession, system_prompt: Optional[str], user_prompt: Optional[str]
    ) -> None:
        """Execute the main recursive refinement loop for a strategy.

        This method orchestrates the strategy refinement process by:
        1. Evaluating the initial strategy
        2. Generating feedback and performance metrics
        3. Iteratively improving the strategy
        4. Tracking performance and implementing stopping conditions

        Args:
            session (RefinementSession): The current refinement session being processed.
            system_prompt (Optional[str]): Optional system-level context for refinement.
            user_prompt (Optional[str]): Optional user-level context for refinement.

        Returns:
            None: Modifies the session in-place with refinement results.

        Raises:
            Exception: If strategy improvement or evaluation fails during the process.
        """
        current_strategy = session.original_strategy
        session.generations.append(current_strategy)

        # Evaluate initial strategy
        initial_metrics = await self._evaluate_strategy(current_strategy, system_prompt, user_prompt)
        initial_refinement_metrics = self.performance_tracker.record_performance(
            current_strategy, initial_metrics, generation=0, refinement_id=session.session_id
        )

        session.performance_history.append(initial_refinement_metrics)
        session.best_strategy = current_strategy
        session.best_score = initial_metrics.overall_score()

        logger.info(f"Initial strategy score: {session.best_score:.2f}")

        # Main refinement loop
        while session.current_generation < self.config.max_generations:
            loop_start_time = time.time()

            # Check time limit
            if (time.time() - session.start_time.timestamp()) > (self.config.max_refinement_time_minutes * 60):
                session.completion_reason = "Time limit reached"
                break

            # Analyze current performance
            current_metrics = session.performance_history[-1]
            feedback_analysis = await self.feedback_loop.analyze_performance(
                f"{session.session_id}_gen_{session.current_generation}", current_metrics
            )
            session.feedback_analyses.append(feedback_analysis)

            # Check stopping conditions
            if not feedback_analysis.should_continue_refinement:
                session.completion_reason = "Feedback loop recommended stopping"
                break

            # Check convergence
            if current_metrics.convergence_indicator > self.config.convergence_threshold:
                session.completion_reason = f"Converged (level: {current_metrics.convergence_indicator:.3f})"
                break

            # Check quality target
            if session.best_score >= self.config.quality_target:
                session.completion_reason = f"Quality target reached ({session.best_score:.2f})"
                break

            # Check strategic compliance if required
            if (
                self.config.require_strategic_compliance
                and current_metrics.strategic_compliance_score >= self.config.strategic_compliance_target
            ):
                session.completion_reason = (
                    f"Strategic compliance achieved ({current_metrics.strategic_compliance_score:.3f})"
                )
                break

            # Generate improved strategy
            logger.info(f"Generating improved strategy for generation {session.current_generation + 1}")

            try:
                improved_strategy = await self.strategy_improver.improve_strategy(
                    current_strategy, feedback_analysis, focus_areas=self.config.improvement_priorities or None
                )

                # Evaluate improved strategy
                improved_metrics = await self._evaluate_strategy(improved_strategy, system_prompt, user_prompt)

                # Record performance
                improved_refinement_metrics = self.performance_tracker.record_performance(
                    improved_strategy,
                    improved_metrics,
                    generation=session.current_generation + 1,
                    refinement_id=session.session_id,
                )

                # Update session
                session.current_generation += 1
                session.generations.append(improved_strategy)
                session.performance_history.append(improved_refinement_metrics)

                # Check if this is the best strategy so far
                improved_score = improved_metrics.overall_score()
                if improved_score > session.best_score:
                    session.best_strategy = improved_strategy
                    session.best_score = improved_score
                    logger.info(f"New best strategy: {improved_score:.2f} (generation {session.current_generation})")
                else:
                    logger.info(
                        f"Generation {session.current_generation} score: {improved_score:.2f} "
                        f"(best remains: {session.best_score:.2f})"
                    )

                # Update current strategy for next iteration
                current_strategy = improved_strategy

                # Check improvement threshold
                improvement = improved_refinement_metrics.improvement_score
                if abs(improvement) < self.config.improvement_threshold:
                    session.completion_reason = f"Minimal improvement ({improvement:.4f})"
                    break

                # Save intermediate results if configured
                if self.config.save_intermediate_results and self.config.output_directory:
                    await self._save_intermediate_results(session)

            except Exception as e:
                logger.error(f"Failed to improve strategy in generation {session.current_generation + 1}: {e}")
                session.completion_reason = f"Improvement failed: {str(e)}"
                break

            # Track loop execution time
            loop_time = time.time() - loop_start_time
            session.total_execution_time += loop_time
            session.total_llm_calls += 2  # Evaluation + improvement

        # Set completion reason if loop completed naturally
        if not session.completion_reason:
            session.completion_reason = f"Maximum generations reached ({self.config.max_generations})"

        # Save final results
        if self.config.output_directory:
            await self._save_final_results(session)

    async def _evaluate_strategy(
        self, strategy: StrategyChain, system_prompt: Optional[str], user_prompt: Optional[str]
    ) -> StrategicMetrics:
        """Evaluate strategy performance using simulation"""

        try:
            # Create simulator
            simulator = PolyhegelSimulator(model_name=self.config.model_name)

            # Run evaluation simulation (small scale for speed)
            results = await simulator.run_simulation(
                temperature_counts=self.config.temperature_counts,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                mode="temperature",
                selection_method="tournament",  # Faster than clustering
            )

            # Collect metrics
            execution_time = 0.0  # Would need to track this in simulator
            metrics = self.metrics_collector.collect_metrics(results, execution_time)

            return metrics

        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            # Return minimal metrics
            return StrategicMetrics(
                coherence_score=5.0,
                feasibility_score=5.0,
                domain_alignment_score=5.0,
                risk_management_score=5.0,
                resource_efficiency_score=5.0,
            )

    async def _save_intermediate_results(self, session: RefinementSession):
        """Save intermediate refinement results"""

        if not self.config.output_directory:
            return

        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save current generation strategy
        gen_file = output_dir / f"{session.session_id}_generation_{session.current_generation}.json"
        current_strategy = session.generations[-1]

        strategy_data = {
            "session_id": session.session_id,
            "generation": session.current_generation,
            "strategy": {
                "title": current_strategy.strategy.title,
                "steps": [
                    {
                        "action": step.action,
                        "prerequisites": step.prerequisites,
                        "outcome": step.outcome,
                        "risks": step.risks,
                        "confidence": step.confidence,
                    }
                    for step in current_strategy.strategy.steps
                ],
                "alignment_score": current_strategy.strategy.alignment_score,
                "estimated_timeline": current_strategy.strategy.estimated_timeline,
                "resource_requirements": current_strategy.strategy.resource_requirements,
            },
            "performance_metrics": session.performance_history[-1].to_dict(),
            "timestamp": datetime.now().isoformat(),
        }

        with open(gen_file, "w") as f:
            json.dump(strategy_data, f, indent=2)

    async def _save_final_results(self, session: RefinementSession):
        """Save final refinement session results"""

        if not self.config.output_directory:
            return

        output_dir = Path(self.config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save complete session results
        session_file = output_dir / f"{session.session_id}_complete.json"

        session_data = {
            "session_id": session.session_id,
            "configuration": {
                "max_generations": self.config.max_generations,
                "convergence_threshold": self.config.convergence_threshold,
                "improvement_threshold": self.config.improvement_threshold,
                "quality_target": self.config.quality_target,
                "model_name": self.config.model_name,
            },
            "results": {
                "total_generations": session.current_generation,
                "completion_reason": session.completion_reason,
                "best_score": session.best_score,
                "initial_score": session.performance_history[0].strategic_metrics.overall_score(),
                "total_improvement": session.best_score
                - session.performance_history[0].strategic_metrics.overall_score(),
                "execution_time_seconds": session.total_execution_time,
                "llm_calls": session.total_llm_calls,
            },
            "best_strategy": (
                {
                    "title": session.best_strategy.strategy.title,
                    "steps": [
                        {
                            "action": step.action,
                            "prerequisites": step.prerequisites,
                            "outcome": step.outcome,
                            "risks": step.risks,
                            "confidence": step.confidence,
                        }
                        for step in session.best_strategy.strategy.steps
                    ],
                    "alignment_score": session.best_strategy.strategy.alignment_score,
                    "estimated_timeline": session.best_strategy.strategy.estimated_timeline,
                    "resource_requirements": session.best_strategy.strategy.resource_requirements,
                }
                if session.best_strategy is not None
                else None
            ),
            "performance_history": [metrics.model_dump(mode="json") for metrics in session.performance_history],
            "feedback_analyses": [
                {
                    "generation": i,
                    "strengths": analysis.strengths,
                    "weaknesses": analysis.weaknesses,
                    "improvement_suggestions": [s.model_dump(mode="json") for s in analysis.improvement_suggestions],
                    "should_continue": analysis.should_continue_refinement,
                    "refinement_priority": analysis.refinement_priority,
                }
                for i, analysis in enumerate(session.feedback_analyses)
            ],
            "timestamp": datetime.now().isoformat(),
        }

        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)

        # Save summary report
        await self._generate_session_report(session, output_dir)

        logger.info(f"Saved complete refinement results to {session_file}")

    async def _generate_session_report(self, session: RefinementSession, output_dir: Path):
        """Generate human-readable session report"""

        report_file = output_dir / f"{session.session_id}_report.md"

        initial_score = session.performance_history[0].strategic_metrics.overall_score()
        final_score = session.best_score
        improvement = final_score - initial_score

        report_lines = [
            "# Recursive Refinement Report",
            f"## Session: {session.session_id}",
            "",
            f"**Start Time:** {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Duration:** {session.total_execution_time:.1f} seconds",
            f"**Generations:** {session.current_generation}",
            f"**Completion Reason:** {session.completion_reason}",
            "",
            "## Performance Summary",
            "",
            f"**Initial Score:** {initial_score:.2f}/10",
            f"**Final Score:** {final_score:.2f}/10",
            f"**Total Improvement:** {improvement:+.2f}",
            f"**Improvement Rate:** {(improvement/initial_score*100):+.1f}%" if initial_score > 0 else "N/A",
            "",
            "## Best Strategy",
            "",
            f"**Title:** {session.best_strategy.strategy.title if session.best_strategy else 'No strategy found'}",
            f"**Timeline:** {session.best_strategy.strategy.estimated_timeline if session.best_strategy else 'N/A'}",
            f"**Resources:** {len(session.best_strategy.strategy.resource_requirements) if session.best_strategy else 0} required",
            f"**Steps:** {len(session.best_strategy.strategy.steps) if session.best_strategy else 0}",
            "",
            "### Strategy Steps",
            "",
        ]

        if session.best_strategy:
            for i, step in enumerate(session.best_strategy.strategy.steps, 1):
                report_lines.extend(
                    [
                        f"**{i}. {step.action}** (Confidence: {step.confidence:.1f})",
                        f"   - Prerequisites: {', '.join(step.prerequisites)}",
                        f"   - Outcome: {step.outcome}",
                        f"   - Risks: {', '.join(step.risks)}",
                        "",
                    ]
                )

        # Performance evolution
        report_lines.extend(
            [
                "## Performance Evolution",
                "",
                "| Generation | Score | Improvement | Convergence | Strategic Compliance |",
                "|------------|-------|-------------|-------------|----------------|",
            ]
        )

        for i, metrics in enumerate(session.performance_history):
            score = metrics.strategic_metrics.overall_score()
            improvement = metrics.improvement_score
            convergence = metrics.convergence_indicator
            strategic_compliance = metrics.strategic_compliance_score

            report_lines.append(
                f"| {i} | {score:.2f} | {improvement:+.3f} | {convergence:.3f} | {strategic_compliance:.3f} |"
            )

        # Key insights
        if session.feedback_analyses:
            report_lines.extend(["", "## Key Insights", ""])

            # Most common weaknesses
            all_weaknesses: List[str] = []
            for analysis in session.feedback_analyses:
                all_weaknesses.extend(analysis.weaknesses)

            if all_weaknesses:
                weakness_counts: Dict[str, int] = {}
                for weakness in all_weaknesses:
                    weakness_counts[weakness] = weakness_counts.get(weakness, 0) + 1

                common_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)

                report_lines.append("**Most Common Issues:**")
                for weakness, count in common_weaknesses[:3]:
                    report_lines.append(f"- {weakness} (mentioned {count} times)")
                report_lines.append("")

            # Final recommendations
            final_analysis = session.feedback_analyses[-1]
            if final_analysis.next_steps:
                report_lines.extend(["**Final Recommendations:**"])
                for step_text in final_analysis.next_steps[:5]:
                    report_lines.append(f"- {step_text}")

        # Write report
        with open(report_file, "w") as f:
            f.write("\n".join(report_lines))

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active or completed refinement session"""

        # Check active sessions
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session_id,
                "status": "active",
                "current_generation": session.current_generation,
                "best_score": session.best_score,
                "elapsed_time": (datetime.now() - session.start_time).total_seconds(),
            }

        # Check completed sessions
        for session in self.completed_sessions:
            if session.session_id == session_id:
                return {
                    "session_id": session_id,
                    "status": "completed",
                    "total_generations": session.current_generation,
                    "completion_reason": session.completion_reason,
                    "best_score": session.best_score,
                    "total_time": session.total_execution_time,
                }

        return None

    def get_global_statistics(self) -> Dict[str, Any]:
        """Get global refinement statistics"""

        return {
            "total_strategies_refined": self._total_strategies_refined,
            "total_refinement_time": self._total_refinement_time,
            "active_sessions": len(self.active_sessions),
            "completed_sessions": len(self.completed_sessions),
            "average_refinement_time": (
                self._total_refinement_time / self._total_strategies_refined
                if self._total_strategies_refined > 0
                else 0
            ),
        }
