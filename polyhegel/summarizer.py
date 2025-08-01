"""
Summary generation module for Polyhegel
"""

import logging
from typing import List, Optional
from pydantic_ai import Agent

from .models import StrategyChain
from .prompts import get_system_prompt, get_template

logger = logging.getLogger(__name__)


class StrategySummarizer:
    """Handles generation of summaries for simulation results"""
    
    def __init__(self, model):
        """
        Initialize summarizer with a model
        
        Args:
            model: pydantic-ai model instance
        """
        self.model = model
        self.agent = Agent(
            self.model,
            output_type=str,
            system_prompt=get_system_prompt('strategic', 'summarizer')
        )
    
    async def summarize_results(self,
                              trunk: Optional[StrategyChain],
                              twigs: List[StrategyChain],
                              cluster_metrics: Optional[dict] = None) -> str:
        """
        Generate a summary of the simulation results
        
        Args:
            trunk: The primary strategy (trunk)
            twigs: Alternative strategies (twigs)
            cluster_metrics: Optional clustering metrics
            
        Returns:
            Summary text
        """
        if not trunk:
            return "No trunk strategy identified. Insufficient data for meaningful analysis."
        
        # Build detailed prompt
        prompt = self._build_summary_prompt(trunk, twigs, cluster_metrics)
        
        try:
            result = await self.agent.run(prompt)
            return result.output
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return self._generate_fallback_summary(trunk, twigs)
    
    def _build_summary_prompt(self,
                            trunk: StrategyChain,
                            twigs: List[StrategyChain],
                            cluster_metrics: Optional[dict]) -> str:
        """Build a detailed prompt for summary generation"""
        
        trunk_details = self._format_strategy_details(trunk)
        twig_summaries = [self._format_strategy_brief(t) for t in twigs[:5]]  # Top 5 twigs
        
        prompt = get_template(
            'strategic_summarize_results',
            trunk_details=trunk_details,
            twig_summaries=chr(10).join(twig_summaries),
            total_chains=cluster_metrics.get('total_chains', 'N/A') if cluster_metrics else 'N/A',
            cluster_count=cluster_metrics.get('cluster_count', 'N/A') if cluster_metrics else 'N/A',
            noise_count=cluster_metrics.get('noise_count', 'N/A') if cluster_metrics else 'N/A'
        )
        
        return prompt
    
    def _format_strategy_details(self, strategy: StrategyChain) -> str:
        """Format detailed strategy information"""
        lines = [
            f"Title: {strategy.strategy.title}",
            f"Timeline: {strategy.strategy.estimated_timeline}",
            f"Temperature: {strategy.temperature}",
            "",
            "Key Steps:"
        ]
        
        for i, step in enumerate(strategy.strategy.steps[:5], 1):  # First 5 steps
            lines.append(f"{i}. {step.action}")
            if step.risks:
                lines.append(f"   Risk: {step.risks[0]}")  # First risk
        
        lines.extend([
            "",
            "Resource Requirements:",
            *[f"- {req}" for req in strategy.strategy.resource_requirements[:3]],
            "",
            "Strategic Alignment:"
        ])
        
        for mandate, score in list(strategy.strategy.alignment_score.items())[:3]:
            lines.append(f"- {mandate}: {score:.1f}")
        
        return "\n".join(lines)
    
    def _format_strategy_brief(self, strategy: StrategyChain) -> str:
        """Format brief strategy information"""
        risk_summary = "High risk" if any("high" in r.lower() for step in strategy.strategy.steps for r in step.risks) else "Moderate risk"
        return f"- {strategy.strategy.title} ({strategy.strategy.estimated_timeline}, {risk_summary})"
    
    def _generate_fallback_summary(self, trunk: StrategyChain, twigs: List[StrategyChain]) -> str:
        """Generate a basic summary without LLM"""
        return f"""Simulation identified primary strategy: {trunk.strategy.title}

This approach focuses on {trunk.strategy.estimated_timeline} implementation with {len(trunk.strategy.steps)} key steps.

{len(twigs)} alternative strategies were identified, representing different risk/reward trade-offs.

The primary strategy should be implemented with careful attention to resource requirements and risk mitigation."""
    
    async def generate_strategy_comparison(self,
                                         strategies: List[StrategyChain],
                                         focus_areas: List[str] = None) -> str:
        """
        Generate a detailed comparison of multiple strategies
        
        Args:
            strategies: List of strategies to compare
            focus_areas: Specific areas to focus on (e.g., ["timeline", "resources", "risks"])
            
        Returns:
            Comparison text
        """
        if not strategies:
            return "No strategies to compare."
        
        focus_areas = focus_areas or ["timeline", "resources", "risks", "alignment"]
        
        prompt = get_template(
            'strategic_compare_strategies',
            strategy_count=len(strategies),
            strategy_list=chr(10).join([f"{i+1}. {s.strategy.title}" for i, s in enumerate(strategies)]),
            focus_areas=', '.join(focus_areas)
        )
        
        try:
            result = await self.agent.run(prompt)
            return result.output
        except Exception as e:
            logger.error(f"Failed to generate comparison: {e}")
            return "Strategy comparison unavailable."