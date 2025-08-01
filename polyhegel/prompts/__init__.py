"""
Centralized prompt loading utilities for Polyhegel

This module provides a pydantic-ai compatible prompt management system with:
- Type-safe prompt loading
- Configuration-driven prompt organization
- Template parameter validation
- Version management
"""

from pathlib import Path
from .loader import (
    PromptLoader,
    get_prompt_loader,
    get_system_prompt,
    get_template,
    load_prompt  # Legacy compatibility
)

# Constants for backwards compatibility
PROMPTS_DIR = Path(__file__).parent

__all__ = [
    'PromptLoader',
    'get_prompt_loader', 
    'get_system_prompt',
    'get_template',
    'load_prompt',
    'PROMPTS_DIR'
]