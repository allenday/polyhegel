"""
Model management for Polyhegel - handles pydantic-ai model discovery and initialization
"""

import logging
import os
from typing import Dict, List, Optional
from pydantic_ai import models
from pydantic_ai.models import Model

from .config import Config

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages AI model discovery and initialization"""

    def __init__(self):
        self._cached_models: Optional[Dict[str, List[str]]] = None
        self._initialized_models: Dict[str, Model] = {}

    def discover_available_models(self) -> Dict[str, List[str]]:
        """Discover available models from pydantic-ai"""
        if self._cached_models is not None:
            return self._cached_models

        try:
            # Try to discover models by attempting to create them with dummy API keys
            available_models = {}

            # Test each provider by trying to initialize a model
            test_models = {
                "openai": "gpt-4o-mini",
                "anthropic": "claude-3-haiku-20240307",
                "google": "gemini-1.5-flash",
                "mistral": "mistral-small-latest",
                "groq": "llama-3.3-70b-versatile",
                "grok": "grok-2-1212",
            }

            for provider, test_model in test_models.items():
                try:
                    # Temporarily set a dummy API key
                    key_name = f"{provider.upper()}_API_KEY"
                    original_key = os.environ.get(key_name)
                    os.environ[key_name] = "dummy_key_for_discovery"

                    # Try to create the model to see if pydantic-ai recognizes it
                    from pydantic_ai import models

                    models.infer_model(test_model)

                    # If we get here, the provider is supported
                    available_models[provider] = f"Models available (use any valid {provider} model name)"

                    # Restore original key
                    if original_key is not None:
                        os.environ[key_name] = original_key
                    else:
                        del os.environ[key_name]

                except Exception:
                    # Provider not supported or model name invalid
                    if original_key is not None:
                        os.environ[key_name] = original_key
                    elif key_name in os.environ:
                        del os.environ[key_name]
                    continue

            if not available_models:
                raise RuntimeError("No supported model providers found in pydantic-ai")

            self._cached_models = available_models
            return available_models

        except Exception as e:
            logger.error(f"Failed to discover models from pydantic-ai: {e}")
            raise

    def list_models_with_availability(self) -> Dict[str, Dict[str, any]]:
        """List models with their availability status based on API keys"""
        models_dict = self.discover_available_models()
        availability = {}

        for provider, description in models_dict.items():
            provider_available = self._check_provider_availability(provider)
            availability[provider] = {"available": provider_available, "description": description}

        return availability

    def _check_provider_availability(self, provider: str) -> bool:
        """Check if API key is available for a provider"""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "grok": "XAI_API_KEY",
            "ollama": None,  # Ollama doesn't need API key
            "test": None,  # Test model doesn't need API key
        }

        env_key = key_mapping.get(provider)
        if env_key is None:
            return True  # Providers that don't need API keys

        return bool(os.environ.get(env_key))

    def get_model(self, model_name: str, api_key: Optional[str] = None) -> Model:
        """Get or initialize a model instance"""
        if model_name in self._initialized_models:
            return self._initialized_models[model_name]

        try:
            # Set API key if provided
            if api_key:
                provider = Config.get_provider_from_model(model_name)
                Config.set_api_key_for_provider(provider, api_key)

            # Use pydantic-ai's infer_model
            model = models.infer_model(model_name)
            self._initialized_models[model_name] = model
            logger.info(f"Successfully initialized model: {model_name}")
            return model

        except Exception as e:
            logger.error(f"Failed to initialize model {model_name}: {e}")
            raise

    def validate_model_name(self, model_name: str) -> bool:
        """Validate if a model name can be initialized by pydantic-ai"""
        try:
            from pydantic_ai import models

            model = models.infer_model(model_name)
            return model is not None
        except Exception:
            return False
