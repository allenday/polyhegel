"""
Strategy generation module for Polyhegel
"""

import asyncio
import logging
from typing import List, Tuple, Optional
from pydantic_ai import Agent

from .models import GenesisStrategy, StrategyChain
from .config import Config
from .domain_manager import get_domain
from .prompts import get_system_prompt, get_template

logger = logging.getLogger(__name__)


class Generator:
    """Handles strategy generation using LLMs.

    This class orchestrates the generation of strategic content using various
    AI models and techniques. It supports multiple generation modes including
    temperature-based sampling, technique-guided generation, and batch processing.

    Attributes:
        model: The pydantic-ai model instance used for generation.
        system_prompt: The system prompt used for strategy generation.
        agent: The pydantic-ai Agent configured for strategy generation.
    """

    def __init__(self, model, system_prompt: Optional[str] = None):
        """Initialize strategy generator.

        Sets up the AI agent with the specified model and system prompt.
        Tools are currently disabled to focus on basic simulation.

        Args:
            model: pydantic-ai model instance for generating strategies.
            system_prompt: Optional custom system prompt. If None, uses the
                default strategic generator prompt.
        """
        self.model = model
        self.system_prompt = system_prompt or get_system_prompt("strategic", "generator")
        # Temporarily disable tools to focus on basic simulation
        # all_tools = WEB_TOOLS + GIT_TOOLS
        self.agent = Agent(
            self.model,
            output_type=GenesisStrategy,
            system_prompt=self.system_prompt,
            # tools=all_tools
        )

    async def generate_strategies(
        self,
        temperature_counts: List[Tuple[float, int]],
        custom_system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> List[StrategyChain]:
        """Generate multiple strategies at different temperatures.

        Generates strategies using various temperature settings to explore
        different levels of creativity and consistency. Uses concurrent
        generation with rate limiting for efficiency.

        Args:
            temperature_counts: List of (temperature, count) tuples specifying
                how many strategies to generate at each temperature level.
            custom_system_prompt: Optional custom system prompt to override
                the default prompt for this generation session.
            user_prompt: Optional custom user prompt. If None, uses default.

        Returns:
            List of StrategyChain objects containing generated strategies.
            Failed generations are logged but don't stop the process.
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
                system_prompt=custom_system_prompt,
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
                batch = tasks[i : i + batch_size]
                results = await asyncio.gather(*batch, return_exceptions=True)

                for result in results:
                    if isinstance(result, StrategyChain):
                        chains.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Failed to generate strategy: {result}")

        logger.info(f"Successfully generated {len(chains)} strategies")
        return chains

    async def _generate_single_strategy(
        self, agent: Agent[None, GenesisStrategy], prompt: str, temperature: float, sample_id: int, max_retries: int = 3
    ) -> StrategyChain:
        """Generate a single strategy with retry logic.

        Attempts to generate a single strategy with automatic retry on failure.
        Includes exponential backoff and comprehensive error handling.

        Args:
            agent: The pydantic-ai Agent to use for generation.
            prompt: The user prompt for strategy generation.
            temperature: Temperature setting for the generation.
            sample_id: Unique identifier for this strategy sample.
            max_retries: Maximum number of retry attempts. Defaults to 3.

        Returns:
            StrategyChain object containing the generated strategy.

        Raises:
            RuntimeError: If all retry attempts fail.
        """
        from pydantic_ai.settings import ModelSettings

        settings = ModelSettings(temperature=temperature)

        for attempt in range(max_retries):
            try:
                result = await agent.run(prompt, model_settings=settings)
                chain = StrategyChain(strategy=result.output, source_sample=sample_id, temperature=temperature)
                logger.debug(f"Generated strategy {sample_id} at temperature {temperature} (attempt {attempt + 1})")
                return chain
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    logger.error(f"Failed to generate strategy {sample_id} after {max_retries} attempts: {e}")
                    raise
                else:
                    logger.warning(f"Attempt {attempt + 1} failed for strategy {sample_id}: {e}. Retrying...")
                    await asyncio.sleep(1)  # Brief delay before retry

        # Should never reach here due to raise above, but needed for mypy
        raise RuntimeError(f"Failed to generate strategy {sample_id} after all attempts")

    async def generate_with_technique(
        self, strategic_challenge: str, technique_name: str, temperature: float = 0.7, count: int = 1
    ) -> List[StrategyChain]:
        """Generate strategies using a specific strategic technique.

        Applies domain-specific strategic techniques to guide the generation
        process. Each technique provides specialized frameworks and approaches
        for addressing strategic challenges.

        Args:
            strategic_challenge: The strategic challenge to address.
            technique_name: Name of the strategic technique to use. Must be
                a valid technique registered in the strategic_techniques module.
            temperature: Temperature for generation. Defaults to 0.7.
            count: Number of strategies to generate. Defaults to 1.

        Returns:
            List of StrategyChain objects guided by the specified technique.
            Each chain includes technique metadata.

        Raises:
            ValueError: If the specified technique name is not found.
        """
        # Get the technique from strategic domain
        strategic_domain = get_domain("strategic")
        if not strategic_domain:
            raise ValueError("Strategic domain not available")

        technique = strategic_domain.get_technique_registry().get(technique_name)
        if not technique:
            raise ValueError(f"Unknown technique: {technique_name}")

        # Format use cases as bullet points
        use_cases_text = "\n".join([f"- {use_case}" for use_case in technique.use_cases])

        # Get technique prompt from centralized template system
        technique_prompt = get_template(
            "strategic_techniques",
            strategic_challenge=strategic_challenge,
            key_technique=technique.name,
            domain=technique.domain.value,
            technique_description=technique.description,
            technique_use_cases=use_cases_text,
        )

        logger.info(f"Generating {count} strategies using technique: {technique_name}")

        # Create a specialized agent for technique-guided generation
        technique_agent = Agent(
            self.model, output_type=GenesisStrategy, system_prompt=get_system_prompt("strategic", "generator")
        )

        # Generate strategies using the technique-guided prompt
        chains = []
        sample_id = 0

        for i in range(count):
            try:
                chain = await self._generate_single_strategy(
                    technique_agent, technique_prompt, temperature, sample_id, max_retries=3
                )
                # Mark this chain as technique-guided
                chain.technique_name = technique_name
                chain.technique_domain = technique.domain.value
                chains.append(chain)
                sample_id += 1

            except Exception as e:
                logger.warning(f"Failed to generate technique-guided strategy {i}: {e}")
                continue

        logger.info(f"Successfully generated {len(chains)} technique-guided strategies")
        return chains

    async def generate_with_multiple_techniques(
        self,
        strategic_challenge: str,
        technique_names: List[str],
        temperature: float = 0.7,
        count_per_technique: int = 1,
    ) -> List[StrategyChain]:
        """Generate strategies using multiple strategic techniques.

        Applies multiple strategic techniques to the same challenge,
        providing diverse perspectives and approaches. Failed techniques
        are logged but don't stop the overall generation process.

        Args:
            strategic_challenge: The strategic challenge to address.
            technique_names: List of technique names to apply. Invalid
                technique names are skipped with error logging.
            temperature: Temperature for generation. Defaults to 0.7.
            count_per_technique: Number of strategies to generate per
                technique. Defaults to 1.

        Returns:
            List of StrategyChain objects from all successful techniques.
            Results from different techniques are combined in the order
            they complete.
        """
        all_chains = []

        for technique_name in technique_names:
            try:
                chains = await self.generate_with_technique(
                    strategic_challenge, technique_name, temperature, count_per_technique
                )
                all_chains.extend(chains)
            except Exception as e:
                logger.error(f"Failed to generate strategies with technique {technique_name}: {e}")
                continue

        logger.info(f"Generated {len(all_chains)} total strategies across {len(technique_names)} techniques")
        return all_chains

    def _create_default_prompt(self) -> str:
        """Create a default user prompt for strategy generation.

        Returns:
            Default user prompt template for basic strategy generation.
        """
        return get_template("default_user")
