"""
Configuration management for Polyhegel
"""

from typing import Dict
import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelProvider(str, Enum):
    """Supported model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    UNKNOWN = "unknown"


class ModelPatterns:
    """Model name patterns for provider detection"""

    OPENAI_PREFIXES = ("gpt-", "o1-", "text-davinci", "text-curie", "text-babbage", "text-ada")
    ANTHROPIC_PREFIXES = ("claude-", "claude_")
    GOOGLE_PREFIXES = ("gemini-", "models/gemini-", "palm-", "bison-")
    LOCAL_PREFIXES = ("llama-", "mistral-", "mixtral-")

    OPENAI_KEYWORDS = ("gpt", "openai", "davinci", "curie")
    ANTHROPIC_KEYWORDS = ("claude", "anthropic")
    GOOGLE_KEYWORDS = ("gemini", "google", "palm", "bison")


class Config:
    """Configuration settings for Polyhegel"""

    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_OUTPUT_DIR = "results"

    # Sampling defaults (based on LLM-As-Hierarchical-Policy research)
    DEFAULT_NUM_SAMPLES = 30  # Balanced sample count for strategic exploration
    DEFAULT_TEMPERATURE_RANGE = (0.7, 0.7)  # Primary temperature from research
    DEFAULT_TEMPERATURE_COUNTS = [(0.7, 30)]  # Single temperature with strategic sample count

    # Alternative configurations for different scenarios
    ZERO_SHOT_TEMPERATURE_COUNTS = [(0.7, 64)]  # For complex zero-shot problems
    TOURNAMENT_TEMPERATURE_COUNTS = [(0.3, 5)]  # For focused comparisons
    TEST_TEMPERATURE_COUNTS = [(0.8, 3)]  # Minimal for testing to avoid costs

    # Clustering defaults
    DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DEFAULT_MIN_CLUSTER_SIZE = 5
    DEFAULT_TWIG_THRESHOLD = 0.2

    # API defaults
    DEFAULT_MAX_CONCURRENT = 5

    @staticmethod
    def get_default_config() -> Dict:
        """Returns default configuration dictionary"""
        return {
            "num_samples": Config.DEFAULT_NUM_SAMPLES,
            "temperature_range": Config.DEFAULT_TEMPERATURE_RANGE,
            "embedding_model": Config.DEFAULT_EMBEDDING_MODEL,
            "min_cluster_size": Config.DEFAULT_MIN_CLUSTER_SIZE,
            "twig_threshold": Config.DEFAULT_TWIG_THRESHOLD,
            "max_concurrent": Config.DEFAULT_MAX_CONCURRENT,
        }

    @staticmethod
    def get_provider_from_model(model_name: str) -> str:
        """Get the provider from model name using pattern matching."""
        try:
            # Check exact prefixes first
            if model_name.startswith(ModelPatterns.OPENAI_PREFIXES):
                return ModelProvider.OPENAI.value
            elif model_name.startswith(ModelPatterns.ANTHROPIC_PREFIXES):
                return ModelProvider.ANTHROPIC.value
            elif model_name.startswith(ModelPatterns.GOOGLE_PREFIXES):
                return ModelProvider.GOOGLE.value
            elif model_name.startswith(ModelPatterns.LOCAL_PREFIXES):
                return ModelProvider.LOCAL.value
            else:
                # Fallback pattern matching with keywords
                model_lower = model_name.lower()
                if any(keyword in model_lower for keyword in ModelPatterns.OPENAI_KEYWORDS):
                    return ModelProvider.OPENAI.value
                elif any(keyword in model_lower for keyword in ModelPatterns.ANTHROPIC_KEYWORDS):
                    return ModelProvider.ANTHROPIC.value
                elif any(keyword in model_lower for keyword in ModelPatterns.GOOGLE_KEYWORDS):
                    return ModelProvider.GOOGLE.value
                else:
                    return ModelProvider.UNKNOWN.value

        except Exception:
            # Ultimate fallback
            return ModelProvider.UNKNOWN.value

    @staticmethod
    def set_api_key_for_provider(provider: str, api_key: str):
        """Set API key for the specified provider."""
        if provider == ModelProvider.OPENAI.value:
            os.environ["OPENAI_API_KEY"] = api_key
        elif provider == ModelProvider.ANTHROPIC.value:
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif provider == ModelProvider.GOOGLE.value:
            os.environ["GOOGLE_API_KEY"] = api_key
        elif provider == ModelProvider.LOCAL.value:
            # Local models might use different env vars
            os.environ["LOCAL_MODEL_API_KEY"] = api_key
