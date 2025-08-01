"""
Strategic evaluation module for comparing and ranking strategies
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pydantic_ai import Agent

from .models import StrategyChain
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
        self.system_prompt = system_prompt or get_system_prompt('strategic', 'evaluator')
        self.agent = Agent(
            self.model,
            output_type=str,
            system_prompt=self.system_prompt
        )
        
        # Load comparison template using new centralized system
        # Template will be loaded dynamically when needed
    
    async def compare_strategies(self, 
                               strategy1: StrategyChain, 
                               strategy2: StrategyChain,
                               context: str = "") -> Dict[str, Any]:
        """
        Compare two strategies and determine which is more effective
        
        Args:
            strategy1: First strategy to compare
            strategy2: Second strategy to compare  
            context: Optional context/situation for the comparison
            
        Returns:
            Dictionary with comparison results including preferred strategy
        """
        try:
            # Format strategies for comparison
            strategy1_text = self._format_strategy_for_comparison(strategy1)
            strategy2_text = self._format_strategy_for_comparison(strategy2)
            
            # Create comparison prompt using centralized template
            comparison_prompt = get_template(
                'strategic_compare',
                question=context or "Strategic planning situation requiring optimal approach selection",
                solution1=strategy1_text,
                solution2=strategy2_text
            )
            
            # Get LLM evaluation
            result = await self.agent.run(comparison_prompt)
            
            # Parse the result to extract preference
            preferred_index = self._parse_preference(result.output)
            
            return {
                'preferred_strategy': 1 if preferred_index == 1 else 2,
                'preferred_chain': strategy1 if preferred_index == 1 else strategy2,
                'evaluation_text': result.output,
                'strategy1_formatted': strategy1_text,
                'strategy2_formatted': strategy2_text,
                'comparison_prompt': comparison_prompt
            }
            
        except Exception as e:
            logger.error(f"Strategy comparison failed: {e}")
            raise
    
    async def evaluate_strategy(self, strategy: StrategyChain, context: str = "") -> Dict[str, Any]:
        """
        Evaluate a single strategy for quality and viability
        
        Args:
            strategy: Strategy to evaluate
            context: Optional context for evaluation
            
        Returns:
            Dictionary with evaluation metrics and analysis
        """
        try:
            strategy_text = self._format_strategy_for_comparison(strategy)
            
            evaluation_prompt = f"""
Evaluate this strategic approach:

Context: {context or "General strategic planning situation"}

Strategy:
{strategy_text}

Provide analysis on:
1. Strategic Viability (0-10 score)
2. Coherence (0-10 score) 
3. Risk Management (0-10 score)
4. Resource Efficiency (0-10 score)
5. Overall Assessment

Format your response with clear scores and reasoning.
"""
            
            result = await self.agent.run(evaluation_prompt)
            
            return {
                'strategy': strategy,
                'evaluation_text': result.output,
                'strategy_formatted': strategy_text,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            raise
    
    def _format_strategy_for_comparison(self, strategy: StrategyChain) -> str:
        """Format a strategy for comparison prompt"""
        lines = [
            f"**Title:** {strategy.strategy.title}",
            "",
            "**Execution Steps:**"
        ]
        
        for i, step in enumerate(strategy.strategy.steps, 1):
            lines.append(f"{i}. **{step.action}**")
            if step.prerequisites:
                lines.append(f"   Prerequisites: {', '.join(step.prerequisites[:2])}")
            lines.append(f"   Expected Outcome: {step.outcome}")
            if step.risks:
                lines.append(f"   Key Risk: {step.risks[0]}")
            lines.append("")
        
        lines.extend([
            f"**Timeline:** {strategy.strategy.estimated_timeline}",
            "",
            "**Resource Requirements:**",
            *[f"- {req}" for req in strategy.strategy.resource_requirements[:3]],
            "",
            "**Strategic Alignment Scores:**"
        ])
        
        for mandate, score in list(strategy.strategy.alignment_score.items())[:3]:
            lines.append(f"- {mandate}: {score:.1f}/10")
        
        return "\n".join(lines)
    
    def _parse_preference(self, evaluation_text: str) -> int:
        """Parse the preferred strategy index from evaluation text"""
        try:
            # Look for "Preferred Strategy Index: N" pattern
            if "Preferred Strategy Index: 1" in evaluation_text:
                return 1
            elif "Preferred Strategy Index: 2" in evaluation_text:
                return 2
            else:
                # Fallback: count mentions of "Strategy 1" vs "Strategy 2" in positive context
                strategy1_mentions = evaluation_text.lower().count("strategy 1")
                strategy2_mentions = evaluation_text.lower().count("strategy 2")
                return 1 if strategy1_mentions >= strategy2_mentions else 2
                
        except Exception as e:
            logger.warning(f"Failed to parse preference, defaulting to strategy 1: {e}")
            return 1
    
