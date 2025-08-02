"""
Polyhegel Core Servers Package

This package provides the generic server framework for polyhegel.
Domain-specific servers are provided through examples and can be loaded via PYTHONPATH.
"""

# This is now a namespace package that can be extended by examples/
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

__all__ = []
