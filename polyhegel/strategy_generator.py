"""
Strategy generation module for Polyhegel
"""

import asyncio
import logging
from typing import List, Tuple, Optional
from pydantic_ai import Agent

from .models import GenesisStrategy, StrategyChain
from .config import Config
from .web_tools import WEB_TOOLS
from .git_tools import GIT_TOOLS

logger = logging.getLogger(__name__)


class StrategyGenerator:
    """Handles strategy generation using LLMs"""
    
    def __init__(self, model, system_prompt: Optional[str] = None):
        """
        Initialize strategy generator
        
        Args:
            model: pydantic-ai model instance
            system_prompt: Optional custom system prompt
        """
        self.model = model
        self.system_prompt = system_prompt or Config.get_default_system_prompt()
        # Temporarily disable tools to focus on basic simulation
        # all_tools = WEB_TOOLS + GIT_TOOLS
        self.agent = Agent(
            self.model,
            output_type=GenesisStrategy,
            system_prompt=self.system_prompt
            # tools=all_tools
        )
    
    async def generate_strategies(self,
                                temperature_counts: List[Tuple[float, int]],
                                custom_system_prompt: Optional[str] = None,
                                user_prompt: Optional[str] = None) -> List[StrategyChain]:
        """
        Generate multiple strategies at different temperatures
        
        Args:
            target_users: Target number of users for the strategy
            temperature_counts: List of (temperature, count) tuples
            custom_system_prompt: Optional custom system prompt
            
        Returns:
            List of StrategyChain objects
        """
        chains = []
        total_samples = sum(count for _, count in temperature_counts)
        logger.info(f"Generating {total_samples} samples across {len(temperature_counts)} temperature settings")
        
        # Use custom prompt if provided
        if custom_system_prompt:
            # all_tools = WEB_TOOLS + GIT_TOOLS
            agent = Agent(
                self.model,
                output_type=GenesisStrategy,
                system_prompt=custom_system_prompt
                # tools=all_tools
            )
        else:
            agent = self.agent
        
        sample_id = 0
        
        for temp, count in temperature_counts:
            logger.info(f"Generating {count} samples at temperature {temp}")
            
            # Create tasks for concurrent generation
            tasks = []
            for i in range(count):
                prompt = user_prompt or self._create_default_prompt()
                task = self._generate_single_strategy(agent, prompt, temp, sample_id)
                tasks.append(task)
                sample_id += 1
            
            # Execute tasks with rate limiting
            batch_size = Config.DEFAULT_MAX_CONCURRENT
            for i in range(0, len(tasks), batch_size):
                batch = tasks[i:i + batch_size]
                results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, StrategyChain):
                        chains.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Failed to generate strategy: {result}")
        
        logger.info(f"Successfully generated {len(chains)} strategies")
        return chains
    
    async def _generate_single_strategy(self, 
                                      agent: Agent,
                                      prompt: str,
                                      temperature: float,
                                      sample_id: int) -> StrategyChain:
        """Generate a single strategy"""
        try:
            from pydantic_ai.settings import ModelSettings
            settings = ModelSettings(temperature=temperature)
            result = await agent.run(prompt, model_settings=settings)
            chain = StrategyChain(
                strategy=result.output,
                source_sample=sample_id,
                temperature=temperature
            )
            logger.debug(f"Generated strategy {sample_id} at temperature {temperature}")
            return chain
        except Exception as e:
            logger.error(f"Failed to generate strategy {sample_id}: {e}")
            raise
    
    def _create_default_prompt(self) -> str:
        """Create a default user prompt for strategy generation"""
        return """Generate a strategic plan.

Requirements:
1. Provide a clear, actionable title
2. Break down into 4-8 concrete steps
3. Each step should have clear prerequisites, outcomes, and risks
4. Include resource requirements and timeline
5. Ensure steps are practical and achievable"""