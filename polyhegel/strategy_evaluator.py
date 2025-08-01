"""
Strategic evaluation module for comparing and ranking strategies
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pydantic_ai import Agent
from pydantic import ValidationError

from .models import StrategyChain, StrategyEvaluationResponse, StrategyAnalysisResponse
from .prompts import get_system_prompt, get_template

logger = logging.getLogger(__name__)


class StrategyEvaluator:
    """Evaluates and compares strategic plans using LLM-based analysis"""

    def __init__(self, model, system_prompt: Optional[str] = None):
        """
        Initialize strategy evaluator

        Args:
            model: pydantic-ai model instance for evaluation
            system_prompt: Optional custom system prompt for evaluation
        """
        self.model = model
        self.system_prompt = system_prompt or get_system_prompt("strategic", "evaluator")

        # Agent for structured strategy comparison
        self.comparison_agent = Agent(
            self.model, output_type=StrategyEvaluationResponse, system_prompt=self.system_prompt
        )

        # Agent for structured strategy analysis
        self.analysis_agent = Agent(self.model, output_type=StrategyAnalysisResponse, system_prompt=self.system_prompt)

        # Load comparison template using new centralized system
        # Template will be loaded dynamically when needed

    async def compare_strategies(
        self, strategy1: StrategyChain, strategy2: StrategyChain, context: str = ""
    ) -> Dict[str, Any]:
        """
        Compare two strategies and determine which is more effective

        Args:
            strategy1: First strategy to compare
            strategy2: Second strategy to compare
            context: Optional context/situation for the comparison

        Returns:
            Dictionary with comparison results including preferred strategy
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Format strategies for comparison
                strategy1_text = self._format_strategy_for_comparison(strategy1)
                strategy2_text = self._format_strategy_for_comparison(strategy2)

                # Create comparison prompt using centralized template
                comparison_prompt = get_template(
                    "strategic_compare",
                    question=context or "Strategic planning situation requiring optimal approach selection",
                    solution1=strategy1_text,
                    solution2=strategy2_text,
                )

                # Get structured LLM evaluation with retry logic
                result = await self.comparison_agent.run(comparison_prompt)
                evaluation = result.output

                # If we get here, validation succeeded
                break

            except ValidationError as e:
                logger.warning(f"Structured output validation failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    # Last attempt failed, fall back to basic response
                    logger.error("All structured output attempts failed, using fallback response")
                    evaluation = StrategyEvaluationResponse(
                        preferred_strategy_index=1,  # Default fallback
                        confidence_score=0.5,
                        reasoning="Structured output validation failed, defaulting to strategy 1",
                    )
                    break
                # Wait briefly before retry
                await asyncio.sleep(0.5)

        return {
            "preferred_strategy": evaluation.preferred_strategy_index,
            "preferred_chain": strategy1 if evaluation.preferred_strategy_index == 1 else strategy2,
            "confidence_score": evaluation.confidence_score,
            "reasoning": evaluation.reasoning,
            "coherence_scores": evaluation.coherence_comparison,
            "feasibility_scores": evaluation.feasibility_comparison,
            "risk_scores": evaluation.risk_management_comparison,
            "evaluation_text": evaluation.reasoning,  # For backward compatibility
            "strategy1_formatted": strategy1_text,
            "strategy2_formatted": strategy2_text,
            "comparison_prompt": comparison_prompt,
        }

    async def evaluate_strategy(self, strategy: StrategyChain, context: str = "") -> Dict[str, Any]:
        """
        Evaluate a single strategy for quality and viability

        Args:
            strategy: Strategy to evaluate
            context: Optional context for evaluation

        Returns:
            Dictionary with evaluation metrics and analysis
        """
        max_retries = 3
        strategy_text = self._format_strategy_for_comparison(strategy)

        evaluation_prompt = get_template(
            "strategic_evaluate_single",
            context=context or "General strategic planning situation",
            strategy_text=strategy_text,
        )

        for attempt in range(max_retries):
            try:
                # Get structured evaluation with retry logic
                result = await self.analysis_agent.run(evaluation_prompt)
                analysis = result.output
                break

            except ValidationError as e:
                logger.warning(f"Analysis validation failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    # Last attempt failed, create fallback response
                    logger.error("All analysis attempts failed, using fallback response")
                    analysis = StrategyAnalysisResponse(
                        overall_score=5.0,
                        coherence_score=5.0,
                        feasibility_score=5.0,
                        risk_management_score=5.0,
                        strategic_alignment_score=5.0,
                        strengths=["Structured output validation failed"],
                        weaknesses=["Unable to perform detailed analysis"],
                        recommendations=["Retry evaluation with different model settings"],
                    )
                    break
                await asyncio.sleep(0.5)

        return {
            "strategy": strategy,
            "overall_score": analysis.overall_score,
            "coherence_score": analysis.coherence_score,
            "feasibility_score": analysis.feasibility_score,
            "risk_management_score": analysis.risk_management_score,
            "strategic_alignment_score": analysis.strategic_alignment_score,
            "strengths": analysis.strengths,
            "weaknesses": analysis.weaknesses,
            "recommendations": analysis.recommendations,
            "evaluation_text": f"Score: {analysis.overall_score}/10. Strengths: {', '.join(analysis.strengths)}",  # For backward compatibility
            "strategy_formatted": strategy_text,
            "context": context,
        }

    def _format_strategy_for_comparison(self, strategy: StrategyChain) -> str:
        """Format a strategy for comparison prompt"""
        lines = [f"**Title:** {strategy.strategy.title}", "", "**Execution Steps:**"]

        for i, step in enumerate(strategy.strategy.steps, 1):
            lines.append(f"{i}. **{step.action}**")
            if step.prerequisites:
                lines.append(f"   Prerequisites: {', '.join(step.prerequisites[:2])}")
            lines.append(f"   Expected Outcome: {step.outcome}")
            if step.risks:
                lines.append(f"   Key Risk: {step.risks[0]}")
            lines.append("")

        lines.extend(
            [
                f"**Timeline:** {strategy.strategy.estimated_timeline}",
                "",
                "**Resource Requirements:**",
                *[f"- {req}" for req in strategy.strategy.resource_requirements[:3]],
                "",
                "**Strategic Alignment Scores:**",
            ]
        )

        for domain, score in list(strategy.strategy.alignment_score.items())[:3]:
            lines.append(f"- {domain}: {score:.1f}/10")

        return "\n".join(lines)

    def format_strategy_for_comparison(self, strategy: StrategyChain) -> str:
        """
        Public method to format a strategy for comparison
        
        Args:
            strategy: Strategy chain to format
            
        Returns:
            Formatted strategy text
        """
        return self._format_strategy_for_comparison(strategy)
