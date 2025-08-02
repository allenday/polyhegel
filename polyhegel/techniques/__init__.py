"""
Polyhegel Core Techniques Package

This package provides the generic technique framework for polyhegel, including
common cross-domain techniques that work across multiple domains.

Core Features:
- Common cross-domain techniques (stakeholder analysis, SWOT, trade-offs, etc.)
- Base classes and utilities for technique implementations
- Extensible namespace for domain-specific techniques via PYTHONPATH

Domain-specific techniques are provided through examples and can be loaded via PYTHONPATH.
"""

# This is now a namespace package that can be extended by examples/
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Import common techniques for immediate availability
from .common import (
    ALL_COMMON_TECHNIQUES,
    COMMON_TECHNIQUE_REGISTRY,
    get_common_technique,
    get_common_techniques_by_type,
    CommonTechnique,
    TechniqueType,
    TechniqueComplexity,
    TechniqueTimeframe,
)

__all__ = [
    "ALL_COMMON_TECHNIQUES",
    "COMMON_TECHNIQUE_REGISTRY",
    "get_common_technique",
    "get_common_techniques_by_type",
    "CommonTechnique",
    "TechniqueType",
    "TechniqueComplexity",
    "TechniqueTimeframe",
]
