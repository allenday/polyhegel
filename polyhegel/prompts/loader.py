"""
Centralized prompt loading and management system for pydantic-ai agents

Following pydantic-ai best practices for prompt management:
- Structured prompt configuration
- Type-safe prompt loading
- Dynamic prompt composition
- Version management
- Template parameter validation
"""

import yaml
from typing import Dict, Optional, Any, List
from pathlib import Path
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)


class PromptTemplate(BaseModel):
    """Pydantic model for prompt template configuration"""

    file: str = Field(..., description="Path to prompt file relative to prompts directory")
    description: str = Field(..., description="Description of the prompt's purpose")
    parameters: Optional[List[str]] = Field(default=None, description="List of template parameters")
    version: Optional[str] = Field(default="1.0", description="Prompt version")

    @field_validator("file")
    @classmethod
    def validate_file_extension(cls, v):
        """Validate file has appropriate extension"""
        if not (v.endswith(".md") or v.endswith(".txt")):
            raise ValueError("Prompt files must have .md or .txt extension")
        return v


class PromptsConfig(BaseModel):
    """Pydantic model for entire prompts configuration"""

    prompts: Dict[str, Dict[str, PromptTemplate]]
    templates: Dict[str, PromptTemplate]
    version: str = Field(default="1.0")
    schema_version: str = Field(default="1.0")


@dataclass
class LoadedPrompt:
    """Container for a loaded prompt with metadata"""

    content: str
    template: PromptTemplate
    category: Optional[str] = None
    name: Optional[str] = None


class PromptLoader:
    """
    Centralized prompt loader following pydantic-ai best practices

    Provides type-safe loading of prompts from markdown files with:
    - Configuration validation
    - Template parameter checking
    - Dynamic prompt composition
    - Caching for performance
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize prompt loader

        Args:
            prompts_dir: Directory containing prompts (defaults to package prompts dir)
        """
        self.prompts_dir = prompts_dir or Path(__file__).parent
        self.config_file = self.prompts_dir / "config.yaml"
        self._config: Optional[PromptsConfig] = None
        self._cache: Dict[str, LoadedPrompt] = {}

        if not self.config_file.exists():
            raise FileNotFoundError(f"Prompt config not found: {self.config_file}")

    @property
    def config(self) -> PromptsConfig:
        """Load and cache prompt configuration"""
        if self._config is None:
            self._load_config()
        if self._config is None:
            raise RuntimeError("Failed to load prompt configuration")
        return self._config

    def _load_config(self):
        """Load prompt configuration with validation"""
        try:
            with open(self.config_file, "r") as f:
                config_data = yaml.safe_load(f)

            # Parse and validate configuration
            self._config = PromptsConfig(**config_data)
            logger.info(f"Loaded prompt config v{self._config.version}")

        except Exception as e:
            logger.error(f"Failed to load prompt config: {e}")
            raise

    def get_system_prompt(self, category: str, name: str) -> str:
        """
        Get system prompt for pydantic-ai Agent

        Args:
            category: Prompt category (e.g., 'strategic', 'general')
            name: Prompt name (e.g., 'evaluator', 'generator')

        Returns:
            System prompt string ready for pydantic-ai Agent
        """
        key = f"{category}.{name}"

        if key in self._cache:
            return self._cache[key].content

        # Find prompt template
        if category not in self.config.prompts:
            raise ValueError(f"Unknown prompt category: {category}")

        if name not in self.config.prompts[category]:
            raise ValueError(f"Unknown prompt '{name}' in category '{category}'")

        template = self.config.prompts[category][name]
        content = self._load_prompt_file(template.file)

        # Cache loaded prompt
        loaded_prompt = LoadedPrompt(content=content, template=template, category=category, name=name)
        self._cache[key] = loaded_prompt

        return content

    def get_template(self, name: str, **kwargs) -> str:
        """
        Get template with parameter substitution

        Args:
            name: Template name
            **kwargs: Template parameters for substitution

        Returns:
            Formatted template string
        """
        if name not in self.config.templates:
            raise ValueError(f"Unknown template: {name}")

        template_config = self.config.templates[name]
        content = self._load_prompt_file(template_config.file)

        # Perform parameter substitution if kwargs provided
        if kwargs:
            try:
                content = content.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing template parameter {e} for template '{name}'")
                raise ValueError(f"Missing required parameter {e} for template '{name}'")

        return content

    def _load_prompt_file(self, relative_path: str) -> str:
        """Load prompt content from file"""
        file_path = self.prompts_dir / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                logger.warning(f"Empty prompt file: {file_path}")

            return content

        except Exception as e:
            logger.error(f"Failed to load prompt file {file_path}: {e}")
            raise

    def list_available_prompts(self) -> Dict[str, List[str]]:
        """List all available prompts by category"""
        return {category: list(prompts.keys()) for category, prompts in self.config.prompts.items()}

    def list_available_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.config.templates.keys())

    def validate_template_parameters(self, template_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate template parameters before substitution

        Args:
            template_name: Name of template
            parameters: Parameters to validate

        Returns:
            True if parameters are valid
        """
        if template_name not in self.config.templates:
            raise ValueError(f"Unknown template: {template_name}")

        template_config = self.config.templates[template_name]
        content = self._load_prompt_file(template_config.file)

        # Extract required parameters from template
        import re

        required_params = set(re.findall(r"\{(\w+)\}", content))
        provided_params = set(parameters.keys())

        missing_params = required_params - provided_params
        if missing_params:
            logger.error(f"Missing required parameters for template '{template_name}': {missing_params}")
            return False

        return True

    def get_prompt_info(self, category: str, name: str) -> PromptTemplate:
        """Get metadata about a prompt"""
        if category not in self.config.prompts:
            raise ValueError(f"Unknown prompt category: {category}")

        if name not in self.config.prompts[category]:
            raise ValueError(f"Unknown prompt '{name}' in category '{category}'")

        return self.config.prompts[category][name]

    def reload_config(self):
        """Reload configuration and clear cache"""
        self._config = None
        self._cache.clear()
        self._load_config()


# Global prompt loader instance
_prompt_loader: Optional[PromptLoader] = None


def get_prompt_loader() -> PromptLoader:
    """Get global prompt loader instance"""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader


def get_system_prompt(category: str, name: str) -> str:
    """
    Convenience function to get system prompt

    Usage with pydantic-ai:
        agent = Agent(
            model,
            system_prompt=get_system_prompt('strategic', 'evaluator')
        )
    """
    return get_prompt_loader().get_system_prompt(category, name)


def get_template(name: str, **kwargs) -> str:
    """
    Convenience function to get formatted template

    Usage:
        comparison_prompt = get_template('strategic_compare',
                                       question=context,
                                       solution1=strategy1_text,
                                       solution2=strategy2_text)
    """
    return get_prompt_loader().get_template(name, **kwargs)


def load_prompt(filename: str) -> str:
    """
    Legacy compatibility function for existing load_prompt calls

    Args:
        filename: Just the filename (e.g., 'strategic_compare.txt')

    Returns:
        Template content
    """
    # Map legacy filenames to new template names
    legacy_mapping = {
        "strategic_compare.txt": "strategic_compare",
        "strategic_techniques.txt": "strategic_techniques",
        "theme_generation.txt": "theme_generation",
        "use_techniques.txt": "use_techniques",
    }

    template_name = legacy_mapping.get(filename, filename.replace(".txt", ""))
    return get_template(template_name)
