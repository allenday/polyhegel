"""
Strategy generation module for Polyhegel
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from pydantic_ai import Agent

from .models import GenesisStrategy, StrategyChain
from .config import Config
from .web_tools import WEB_TOOLS
from .git_tools import GIT_TOOLS
from .strategic_techniques import (
    StrategicTechnique, 
    get_technique_by_name,
    get_recommended_techniques
)
from .prompts import get_system_prompt

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
        self.system_prompt = system_prompt or get_system_prompt('strategic', 'generator')
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
                                      sample_id: int,
                                      max_retries: int = 3) -> StrategyChain:
        """Generate a single strategy with retry logic"""
        from pydantic_ai.settings import ModelSettings
        settings = ModelSettings(temperature=temperature)
        
        for attempt in range(max_retries):
            try:
                result = await agent.run(prompt, model_settings=settings)
                chain = StrategyChain(
                    strategy=result.output,
                    source_sample=sample_id,
                    temperature=temperature
                )
                logger.debug(f"Generated strategy {sample_id} at temperature {temperature} (attempt {attempt + 1})")
                return chain
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"Failed to generate strategy {sample_id} after {max_retries} attempts: {e}")
                    raise
                else:
                    logger.warning(f"Attempt {attempt + 1} failed for strategy {sample_id}: {e}. Retrying...")
                    await asyncio.sleep(1)  # Brief delay before retry
    
    async def generate_with_technique(self,
                                     strategic_challenge: str,
                                     technique_name: str,
                                     temperature: float = 0.7,
                                     count: int = 1) -> List[StrategyChain]:
        """
        Generate strategies using a specific strategic technique
        
        Args:
            strategic_challenge: The strategic challenge to address
            technique_name: Name of the strategic technique to use
            temperature: Temperature for generation
            count: Number of strategies to generate
            
        Returns:
            List of StrategyChain objects guided by the technique
        """
        # Get the technique
        technique = get_technique_by_name(technique_name)
        if not technique:
            raise ValueError(f"Unknown technique: {technique_name}")
        
        # Load the strategic techniques template
        template_path = Path(__file__).parent / "prompts" / "strategic_techniques.txt"
        if not template_path.exists():
            raise FileNotFoundError(f"Strategic techniques template not found: {template_path}")
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Format use cases as bullet points
        use_cases_text = "\n".join([f"- {use_case}" for use_case in technique.use_cases])
        
        # Format the prompt with technique details
        technique_prompt = template.format(
            strategic_challenge=strategic_challenge,
            key_technique=technique.name,
            clm_mandate=technique.mandate.value,
            technique_description=technique.description,
            technique_use_cases=use_cases_text
        )
        
        logger.info(f"Generating {count} strategies using technique: {technique_name}")
        
        # Create a specialized agent for technique-guided generation
        technique_agent = Agent(
            self.model,
            output_type=GenesisStrategy,
            system_prompt=f"You are a strategic planning expert specializing in {technique.mandate.value} techniques."
        )
        
        # Generate strategies using the technique-guided prompt
        chains = []
        sample_id = 0
        
        for i in range(count):
            try:
                chain = await self._generate_single_strategy(
                    technique_agent,
                    technique_prompt,
                    temperature,
                    sample_id,
                    max_retries=3
                )
                # Mark this chain as technique-guided
                chain.technique_name = technique_name
                chain.technique_mandate = technique.mandate.value
                chains.append(chain)
                sample_id += 1
                
            except Exception as e:
                logger.warning(f"Failed to generate technique-guided strategy {i}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(chains)} technique-guided strategies")
        return chains
    
    async def generate_with_multiple_techniques(self,
                                               strategic_challenge: str,
                                               technique_names: List[str],
                                               temperature: float = 0.7,
                                               count_per_technique: int = 1) -> List[StrategyChain]:
        """
        Generate strategies using multiple strategic techniques
        
        Args:
            strategic_challenge: The strategic challenge to address
            technique_names: List of technique names to use
            temperature: Temperature for generation
            count_per_technique: Number of strategies per technique
            
        Returns:
            List of StrategyChain objects from all techniques
        """
        all_chains = []
        
        for technique_name in technique_names:
            try:
                chains = await self.generate_with_technique(
                    strategic_challenge,
                    technique_name,
                    temperature,
                    count_per_technique
                )
                all_chains.extend(chains)
            except Exception as e:
                logger.error(f"Failed to generate strategies with technique {technique_name}: {e}")
                continue
        
        logger.info(f"Generated {len(all_chains)} total strategies across {len(technique_names)} techniques")
        return all_chains

    def _create_default_prompt(self) -> str:
        """Create a default user prompt for strategy generation"""
        return """Generate a strategic plan.

Requirements:
1. Provide a clear, actionable title
2. Break down into 4-8 concrete steps
3. Each step should have clear prerequisites, outcomes, and risks
4. Include resource requirements and timeline
5. Ensure steps are practical and achievable"""