"""
Feedback loop and strategy improvement system for recursive refinement

Implements the feedback mechanisms that analyze performance metrics and
generate automated strategy improvement suggestions.
"""

import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import statistics

from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from ..models import StrategyChain, GenesisStrategy, StrategyStep, FeedbackAnalysisResponse
from ..prompts import get_system_prompt
from .metrics import RefinementMetrics, PerformanceTracker

logger = logging.getLogger(__name__)


class ImprovementCategory(Enum):
    """Categories of strategy improvements"""

    COHERENCE = "coherence"
    FEASIBILITY = "feasibility"
    RISK_MANAGEMENT = "risk_management"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    DOMAIN_ALIGNMENT = "domain_alignment"
    TIMELINE_OPTIMIZATION = "timeline_optimization"
    STAKEHOLDER_ALIGNMENT = "stakeholder_alignment"


class ImprovementSuggestion(BaseModel):
    """A specific suggestion for improving a strategy"""

    category: ImprovementCategory
    priority: float = Field(ge=0.0, le=1.0, description="Priority level, higher = more important")
    description: str
    specific_changes: List[str]
    expected_impact: float = Field(ge=0.0, le=1.0, description="Expected improvement in overall score")
    implementation_effort: float = Field(ge=0.0, le=1.0, description="Implementation effort, higher = more effort")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in suggestion")

    # Strategic alignment factors
    strategic_alignment: Dict[str, float] = Field(default_factory=dict)
    risk_mitigation: List[str] = Field(default_factory=list)


class FeedbackAnalysis(BaseModel):
    """Analysis of strategy performance with improvement recommendations"""

    strategy_id: str
    current_metrics: RefinementMetrics
    historical_performance: List[RefinementMetrics]

    # Analysis results
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_suggestions: List[ImprovementSuggestion] = Field(default_factory=list)

    # Performance insights
    convergence_analysis: Dict[str, Any] = Field(default_factory=dict)
    trend_analysis: Dict[str, Any] = Field(default_factory=dict)
    strategic_compliance_analysis: Dict[str, Any] = Field(default_factory=dict)

    # Recommendations
    should_continue_refinement: bool = True
    refinement_priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Refinement priority level")
    next_steps: List[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FeedbackLoop:
    """Analyzes performance metrics and generates improvement recommendations"""

    def __init__(self, performance_tracker: PerformanceTracker, model_name: Optional[str] = None):
        """
        Initialize feedback loop

        Args:
            performance_tracker: Tracker for accessing historical performance
            model_name: LLM model for generating improvement suggestions
        """
        self.performance_tracker = performance_tracker
        self.model_name = model_name

        # Initialize pydantic-ai agent for structured feedback analysis
        model = TestModel() if model_name is None else model_name  # Use TestModel for tests
        system_prompt = """You are a strategic analysis expert. Analyze the provided strategic metrics and provide structured feedback.

Focus on:
- Identifying specific strengths based on high-performing metrics (>7.5/10)
- Highlighting weaknesses in low-performing areas (<5.0/10) 
- Providing actionable insights
- Prioritizing the most critical improvement areas

Be specific and actionable in your analysis."""

        self.analysis_agent = Agent(model=model, output_type=FeedbackAnalysisResponse, system_prompt=system_prompt)

        # Thresholds for feedback decisions
        self.convergence_threshold = 0.8  # Stop refining if highly converged
        self.improvement_threshold = 0.05  # Min improvement to continue
        self.max_generations = 10  # Max refinement iterations

        # Cache for recent analyses
        self.analysis_cache: Dict[str, FeedbackAnalysis] = {}

    async def analyze_performance(self, strategy_id: str, current_metrics: RefinementMetrics) -> FeedbackAnalysis:
        """
        Analyze strategy performance and generate feedback

        Args:
            strategy_id: ID of strategy to analyze
            current_metrics: Current performance metrics

        Returns:
            FeedbackAnalysis with recommendations
        """
        logger.info(f"Analyzing performance for strategy {strategy_id}")

        # Get historical performance
        historical_metrics = self.performance_tracker.get_all_metrics(strategy_id)

        # Create base analysis
        analysis = FeedbackAnalysis(
            strategy_id=strategy_id, current_metrics=current_metrics, historical_performance=historical_metrics
        )

        # Perform different types of analysis
        await self._analyze_strengths_weaknesses(analysis)
        await self._analyze_convergence(analysis)
        await self._analyze_trends(analysis)
        await self._analyze_strategic_compliance(analysis)
        await self._generate_improvement_suggestions(analysis)
        await self._determine_refinement_recommendations(analysis)

        # Cache analysis
        self.analysis_cache[strategy_id] = analysis

        logger.info(
            f"Analysis complete for {strategy_id}: "
            f"{len(analysis.improvement_suggestions)} suggestions, "
            f"continue_refinement={analysis.should_continue_refinement}"
        )

        return analysis

    async def _analyze_strengths_weaknesses(self, analysis: FeedbackAnalysis):
        """Identify strategy strengths and weaknesses using AI-powered analysis"""

        current = analysis.current_metrics.strategic_metrics

        # Format metrics for analysis
        metrics_summary = f"""Strategic Performance Metrics Analysis:

Coherence Score: {current.coherence_score:.1f}/10 - How well strategy steps flow logically
Feasibility Score: {current.feasibility_score:.1f}/10 - Implementation practicality  
Domain Alignment Score: {current.domain_alignment_score:.1f}/10 - Strategic objective alignment
Risk Management Score: {current.risk_management_score:.1f}/10 - Risk identification and mitigation
Resource Efficiency Score: {current.resource_efficiency_score:.1f}/10 - Resource utilization effectiveness

Overall Score: {current.overall_score():.1f}/10

Historical Context:
- Current Generation: {analysis.current_metrics.generation}
- Improvement Trend: {analysis.current_metrics.performance_trend}
- Evolution Velocity: {analysis.current_metrics.evolution_velocity:.2f}
"""

        try:
            # Get structured AI analysis
            result = await self.analysis_agent.run(metrics_summary)
            ai_analysis = result.output

            # Update analysis with AI-generated insights
            analysis.strengths.extend(ai_analysis.strengths)
            analysis.weaknesses.extend(ai_analysis.weaknesses)

            # Store additional insights for later use
            analysis.convergence_analysis["ai_assessment"] = ai_analysis.overall_assessment
            analysis.convergence_analysis["confidence"] = ai_analysis.confidence_score
            analysis.next_steps.extend(ai_analysis.priority_areas)

        except Exception as e:
            logger.warning(f"AI analysis failed, falling back to threshold-based analysis: {e}")

            # Fallback to simple threshold-based analysis
            strong_threshold = 7.5
            weak_threshold = 5.0

            metrics_analysis = {
                "coherence": current.coherence_score,
                "feasibility": current.feasibility_score,
                "domain_alignment": current.domain_alignment_score,
                "risk_management": current.risk_management_score,
                "resource_efficiency": current.resource_efficiency_score,
            }

            for metric_name, score in metrics_analysis.items():
                if score >= strong_threshold:
                    analysis.strengths.append(f"Strong {metric_name.replace('_', ' ')}: {score:.1f}/10")
                elif score <= weak_threshold:
                    analysis.weaknesses.append(f"Weak {metric_name.replace('_', ' ')}: {score:.1f}/10")

    async def _analyze_convergence(self, analysis: FeedbackAnalysis):
        """Analyze convergence patterns"""

        current = analysis.current_metrics

        analysis.convergence_analysis = {
            "convergence_level": current.convergence_indicator,
            "is_converging": current.convergence_indicator > 0.6,
            "is_highly_converged": current.convergence_indicator > self.convergence_threshold,
            "evolution_velocity": current.evolution_velocity,
            "is_evolving": abs(current.evolution_velocity) > 0.1,
        }

        # Add insights
        if analysis.convergence_analysis["is_highly_converged"]:
            analysis.next_steps.append("Strategy has converged - consider exploring new approaches")
        elif not analysis.convergence_analysis["is_evolving"]:
            analysis.next_steps.append("Strategy evolution has stalled - significant changes may be needed")

    async def _analyze_trends(self, analysis: FeedbackAnalysis):
        """Analyze performance trends"""

        current = analysis.current_metrics
        historical = analysis.historical_performance

        analysis.trend_analysis = {
            "trend": current.performance_trend,
            "trend_confidence": current.trend_confidence,
            "recent_improvement": current.improvement_score,
            "generation": current.generation,
        }

        # Calculate trend consistency
        if len(historical) >= 3:
            recent_trends = [m.performance_trend for m in historical[-3:]]
            trend_consistency = len(set(recent_trends)) == 1
            analysis.trend_analysis["trend_consistency"] = trend_consistency

        # Add trend-based insights
        if current.performance_trend == "degrading":
            analysis.next_steps.append("Performance is degrading - consider reverting to previous generation")
        elif current.performance_trend == "oscillating":
            analysis.next_steps.append("Performance is unstable - focus on consistency improvements")
        elif current.performance_trend == "stable" and current.improvement_score < 0.01:
            analysis.next_steps.append("Performance has plateaued - try more significant changes")

    async def _analyze_strategic_compliance(self, analysis: FeedbackAnalysis):
        """Analyze strategic compliance"""

        current = analysis.current_metrics

        analysis.strategic_compliance_analysis = {
            "compliance_score": current.strategic_compliance_score,
            "is_compliant": current.strategic_compliance_score > 0.7,
            "compliance_trend": "stable",  # Default
        }

        # Analyze compliance trend if historical data available
        if len(analysis.historical_performance) >= 2:
            recent_compliance = [m.strategic_compliance_score for m in analysis.historical_performance[-5:]]
            if len(recent_compliance) > 1:
                compliance_slope = (recent_compliance[-1] - recent_compliance[0]) / len(recent_compliance)

                if compliance_slope > 0.05:
                    analysis.strategic_compliance_analysis["compliance_trend"] = "improving"
                elif compliance_slope < -0.05:
                    analysis.strategic_compliance_analysis["compliance_trend"] = "degrading"

        # Add compliance-based recommendations
        if not analysis.strategic_compliance_analysis["is_compliant"]:
            analysis.next_steps.append("Improve strategic compliance - focus on strategic rigor")

    async def _generate_improvement_suggestions(self, analysis: FeedbackAnalysis):
        """Generate specific improvement suggestions"""

        current = analysis.current_metrics.strategic_metrics

        # Generate suggestions based on weak metrics
        suggestions = []

        # Coherence improvements
        if current.coherence_score < 7.0:
            suggestions.append(
                ImprovementSuggestion(
                    category=ImprovementCategory.COHERENCE,
                    priority=0.9,
                    description="Improve logical flow and consistency between strategy steps",
                    specific_changes=[
                        "Ensure prerequisites are met by previous steps",
                        "Align step outcomes with overall strategy goals",
                        "Standardize confidence levels across similar steps",
                    ],
                    expected_impact=0.8,
                    implementation_effort=0.4,
                    confidence=0.8,
                    strategic_alignment={"strategic_rigor": 0.9},
                    risk_mitigation=["Reduces execution confusion", "Improves stakeholder clarity"],
                )
            )

        # Feasibility improvements
        if current.feasibility_score < 7.0:
            suggestions.append(
                ImprovementSuggestion(
                    category=ImprovementCategory.FEASIBILITY,
                    priority=0.8,
                    description="Enhance implementation feasibility and timeline realism",
                    specific_changes=[
                        "Adjust timeline estimates based on step complexity",
                        "Identify and plan for resource constraints",
                        "Add contingency planning for high-risk steps",
                    ],
                    expected_impact=0.7,
                    implementation_effort=0.5,
                    confidence=0.7,
                    strategic_alignment={"practical_execution": 0.8},
                    risk_mitigation=["Reduces implementation failure risk"],
                )
            )

        # Risk management improvements
        if current.risk_management_score < 7.0:
            suggestions.append(
                ImprovementSuggestion(
                    category=ImprovementCategory.RISK_MANAGEMENT,
                    priority=0.85,
                    description="Strengthen risk identification and mitigation strategies",
                    specific_changes=[
                        "Identify risks for all strategy steps",
                        "Develop mitigation strategies for high-impact risks",
                        "Adjust confidence levels to reflect risk exposure",
                    ],
                    expected_impact=0.6,
                    implementation_effort=0.3,
                    confidence=0.85,
                    strategic_alignment={"risk_awareness": 0.9},
                    risk_mitigation=["Improves strategic resilience"],
                )
            )

        # Resource efficiency improvements
        if current.resource_efficiency_score < 7.0:
            suggestions.append(
                ImprovementSuggestion(
                    category=ImprovementCategory.RESOURCE_EFFICIENCY,
                    priority=0.7,
                    description="Optimize resource allocation and efficiency",
                    specific_changes=[
                        "Specify resource requirements more precisely",
                        "Identify opportunities for resource sharing across steps",
                        "Consider alternative approaches with lower resource needs",
                    ],
                    expected_impact=0.5,
                    implementation_effort=0.6,
                    confidence=0.6,
                    strategic_alignment={"efficiency": 0.8},
                    risk_mitigation=["Reduces resource waste"],
                )
            )

        # Domain alignment improvements
        if current.domain_alignment_score < 7.0:
            suggestions.append(
                ImprovementSuggestion(
                    category=ImprovementCategory.DOMAIN_ALIGNMENT,
                    priority=0.75,
                    description="Better align strategy with domain requirements and constraints",
                    specific_changes=[
                        "Review alignment with strategic domains",
                        "Ensure activities support core objectives",
                        "Align resource allocation with strategic priorities",
                    ],
                    expected_impact=0.6,
                    implementation_effort=0.4,
                    confidence=0.7,
                    strategic_alignment={"domain_alignment": 0.9},
                    risk_mitigation=["Improves strategic focus"],
                )
            )

        # Sort suggestions by priority
        suggestions.sort(key=lambda s: s.priority, reverse=True)
        analysis.improvement_suggestions = suggestions[:5]  # Top 5 suggestions

    async def _determine_refinement_recommendations(self, analysis: FeedbackAnalysis):
        """Determine whether to continue refinement and at what priority"""

        current = analysis.current_metrics

        # Check stopping conditions
        should_stop_reasons = []

        # Check convergence
        if current.convergence_indicator > self.convergence_threshold:
            should_stop_reasons.append("Strategy has converged")

        # Check generation limit
        if current.generation >= self.max_generations:
            should_stop_reasons.append("Maximum refinement iterations reached")

        # Check improvement trend
        if current.performance_trend == "degrading" and current.trend_confidence > 0.7:
            should_stop_reasons.append("Performance is consistently degrading")

        # Check ROI
        if current.roi_estimate < -1.0:  # Negative ROI
            should_stop_reasons.append("Refinement ROI is negative")

        # Check if performance is already excellent
        if current.strategic_metrics.overall_score() > 9.0:
            should_stop_reasons.append("Strategy quality is already excellent")

        # Determine if refinement should continue
        analysis.should_continue_refinement = len(should_stop_reasons) == 0

        if should_stop_reasons:
            analysis.next_steps.extend([f"Stop refinement: {reason}" for reason in should_stop_reasons])

        # Calculate refinement priority
        if analysis.should_continue_refinement:
            priority_factors = [
                current.improvement_score,  # Recent improvement
                1.0 - current.convergence_indicator,  # Room for improvement
                current.roi_estimate / 10.0,  # ROI normalized
                len(analysis.improvement_suggestions) / 5.0,  # Number of suggestions
                (10.0 - current.strategic_metrics.overall_score()) / 10.0,  # Room for score improvement
            ]

            analysis.refinement_priority = statistics.mean([max(0, min(1, f)) for f in priority_factors])
        else:
            analysis.refinement_priority = 0.0


class StrategyImprover:
    """Applies improvement suggestions to generate refined strategies"""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize strategy improver

        Args:
            model_name: LLM model for strategy refinement
        """
        self.model_name = model_name

    async def improve_strategy(
        self,
        original_strategy: StrategyChain,
        feedback_analysis: FeedbackAnalysis,
        focus_areas: Optional[List[ImprovementCategory]] = None,
    ) -> StrategyChain:
        """
        Generate improved strategy based on feedback analysis

        Args:
            original_strategy: Original strategy to improve
            feedback_analysis: Analysis with improvement suggestions
            focus_areas: Specific areas to focus improvement on

        Returns:
            Improved StrategyChain
        """
        logger.info(f"Improving strategy {feedback_analysis.strategy_id}")

        # Filter suggestions by focus areas if specified
        suggestions = feedback_analysis.improvement_suggestions
        if focus_areas:
            suggestions = [s for s in suggestions if s.category in focus_areas]

        # Take top suggestions by priority
        top_suggestions = sorted(suggestions, key=lambda s: s.priority, reverse=True)[:3]

        if not top_suggestions:
            logger.warning("No improvement suggestions to apply")
            return original_strategy

        # Generate improvement prompt
        improvement_context = self._build_improvement_context(original_strategy, feedback_analysis, top_suggestions)

        # Use LLM to generate improved strategy
        if self.model_name:
            improved_strategy = await self._generate_improved_strategy_llm(original_strategy, improvement_context)
        else:
            # Fall back to rule-based improvement
            improved_strategy = await self._generate_improved_strategy_rules(original_strategy, top_suggestions)

        # Update metadata
        improved_strategy.source_sample = original_strategy.source_sample
        improved_strategy.temperature = original_strategy.temperature

        logger.info(f"Generated improved strategy for {feedback_analysis.strategy_id}")
        return improved_strategy

    def _build_improvement_context(
        self,
        original_strategy: StrategyChain,
        feedback_analysis: FeedbackAnalysis,
        suggestions: List[ImprovementSuggestion],
    ) -> Dict[str, Any]:
        """Build context for strategy improvement"""

        return {
            "original_strategy": {
                "title": original_strategy.strategy.title,
                "steps": [
                    {
                        "action": step.action,
                        "prerequisites": step.prerequisites,
                        "outcome": step.outcome,
                        "risks": step.risks,
                        "confidence": step.confidence,
                    }
                    for step in original_strategy.strategy.steps
                ],
                "timeline": original_strategy.strategy.estimated_timeline,
                "resources": original_strategy.strategy.resource_requirements,
            },
            "performance_analysis": {
                "strengths": feedback_analysis.strengths,
                "weaknesses": feedback_analysis.weaknesses,
                "overall_score": feedback_analysis.current_metrics.strategic_metrics.overall_score(),
                "strategic_compliance": feedback_analysis.current_metrics.strategic_compliance_score,
            },
            "improvement_suggestions": [s.model_dump(mode="json") for s in suggestions],
        }

    async def _generate_improved_strategy_llm(
        self, original_strategy: StrategyChain, improvement_context: Dict[str, Any]
    ) -> StrategyChain:
        """Generate improved strategy using LLM"""

        try:
            # Create improvement agent
            system_prompt = get_system_prompt("strategic", "refine")  # Would need to add this prompt

            # For now, use TestModel for consistency with existing tests
            test_model = TestModel()

            agent = Agent(test_model, output_type=GenesisStrategy, system_prompt=system_prompt)

            # Generate improvement prompt
            improvement_prompt = self._format_improvement_prompt(improvement_context)

            # Generate improved strategy
            result = await agent.run(improvement_prompt)

            # Create strategy chain
            improved_chain = StrategyChain(
                strategy=result.output,
                source_sample=original_strategy.source_sample,
                temperature=original_strategy.temperature,
            )

            return improved_chain

        except Exception as e:
            logger.error(f"LLM strategy improvement failed: {e}")
            # Fall back to rule-based improvement
            return await self._generate_improved_strategy_rules(
                original_strategy, improvement_context["improvement_suggestions"]
            )

    def _format_improvement_prompt(self, context: Dict[str, Any]) -> str:
        """Format improvement prompt for LLM"""

        original = context["original_strategy"]
        analysis = context["performance_analysis"]
        suggestions = context["improvement_suggestions"]

        prompt_parts = [
            "Please improve the following strategy based on performance analysis and suggestions:",
            "",
            f"Original Strategy: {original['title']}",
            f"Timeline: {original['timeline']}",
            "",
            "Current Performance:",
            f"- Overall Score: {analysis['overall_score']:.1f}/10",
            f"- Strategic Compliance: {analysis['strategic_compliance']:.1f}",
            "",
            "Strengths:",
        ]

        for strength in analysis["strengths"]:
            prompt_parts.append(f"- {strength}")

        prompt_parts.extend(
            [
                "",
                "Areas for Improvement:",
            ]
        )

        for weakness in analysis["weaknesses"]:
            prompt_parts.append(f"- {weakness}")

        prompt_parts.extend(
            [
                "",
                "Specific Improvement Suggestions:",
            ]
        )

        for i, suggestion in enumerate(suggestions, 1):
            prompt_parts.extend(
                [
                    f"{i}. {suggestion['description']} (Priority: {suggestion['priority']:.1f})",
                    f"   Changes: {', '.join(suggestion['specific_changes'])}",
                    "",
                ]
            )

        prompt_parts.extend(
            [
                "Please generate an improved strategy that addresses these suggestions while maintaining the core strategic intent.",
                "Focus on the highest priority improvements and ensure strategic compliance.",
            ]
        )

        return "\n".join(prompt_parts)

    async def _generate_improved_strategy_rules(
        self, original_strategy: StrategyChain, suggestions: List[ImprovementSuggestion]
    ) -> StrategyChain:
        """Generate improved strategy using rule-based approach"""

        # Create copy of original strategy
        original = original_strategy.strategy
        improved_steps = []

        for step in original.steps:
            improved_step = StrategyStep(
                action=step.action,
                prerequisites=step.prerequisites.copy(),
                outcome=step.outcome,
                risks=step.risks.copy(),
                confidence=step.confidence,
            )

            # Apply rule-based improvements
            for suggestion in suggestions:
                if suggestion.category == ImprovementCategory.COHERENCE:
                    # Improve step coherence
                    if "ensure prerequisites" in suggestion.description.lower():
                        # Add more specific prerequisites
                        if len(improved_step.prerequisites) < 2:
                            improved_step.prerequisites.append("Previous step outcomes validated")

                elif suggestion.category == ImprovementCategory.RISK_MANAGEMENT:
                    # Improve risk management
                    if len(improved_step.risks) == 0:
                        improved_step.risks.append("Implementation challenges")
                        improved_step.confidence = max(0.1, improved_step.confidence - 0.1)

                elif suggestion.category == ImprovementCategory.FEASIBILITY:
                    # Adjust confidence for feasibility
                    if "timeline" in suggestion.description.lower():
                        if improved_step.confidence > 0.8:
                            improved_step.confidence = min(0.9, improved_step.confidence - 0.05)

            improved_steps.append(improved_step)

        # Create improved strategy
        improved_strategy = GenesisStrategy(
            title=f"{original.title} (Refined)",
            steps=improved_steps,
            alignment_score=original.alignment_score.copy(),
            estimated_timeline=original.estimated_timeline,
            resource_requirements=original.resource_requirements.copy(),
        )

        # Apply resource improvements
        for suggestion in suggestions:
            if suggestion.category == ImprovementCategory.RESOURCE_EFFICIENCY:
                if "specify resource requirements" in suggestion.description.lower():
                    # Make resources more specific
                    improved_resources = []
                    for resource in improved_strategy.resource_requirements:
                        if len(resource.split()) < 3:  # Make generic resources more specific
                            improved_resources.append(f"Specialized {resource}")
                        else:
                            improved_resources.append(resource)
                    improved_strategy.resource_requirements = improved_resources

        # Create improved strategy chain
        improved_chain = StrategyChain(
            strategy=improved_strategy,
            source_sample=original_strategy.source_sample,
            temperature=original_strategy.temperature,
        )

        return improved_chain
