"""
Polyhegel Core Techniques Package

This package provides the generic technique framework for polyhegel.
Domain-specific techniques are provided through examples and can be loaded via PYTHONPATH.

The core framework provides base classes and utilities for technique implementations.
"""

# This is now a namespace package that can be extended by examples/
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__all__ = []
