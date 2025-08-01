"""
Configuration management for Polyhegel
"""

from typing import Dict, List, Tuple, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for Polyhegel"""
    
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_TARGET_USERS = 10000
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
            'num_samples': Config.DEFAULT_NUM_SAMPLES,
            'temperature_range': Config.DEFAULT_TEMPERATURE_RANGE,
            'embedding_model': Config.DEFAULT_EMBEDDING_MODEL,
            'min_cluster_size': Config.DEFAULT_MIN_CLUSTER_SIZE,
            'twig_threshold': Config.DEFAULT_TWIG_THRESHOLD,
            'max_concurrent': Config.DEFAULT_MAX_CONCURRENT,
        }
    
    @staticmethod
    def get_provider_from_model(model_name: str) -> str:
        """Get the provider from model name."""
        if model_name.startswith('gpt-'):
            return 'openai'
        elif model_name.startswith('claude-'):
            return 'anthropic'
        elif model_name.startswith('gemini-'):
            return 'google'
        elif model_name.startswith('mistral-'):
            return 'mistral'
        else:
            return 'openai'  # Default
    
    @staticmethod
    def set_api_key_for_provider(provider: str, api_key: str):
        """Set API key for the specified provider."""
        if provider == 'openai':
            os.environ['OPENAI_API_KEY'] = api_key
        elif provider == 'anthropic':
            os.environ['ANTHROPIC_API_KEY'] = api_key
        elif provider == 'google':
            os.environ['GOOGLE_API_KEY'] = api_key
        elif provider == 'mistral':
            os.environ['MISTRAL_API_KEY'] = api_key
    
