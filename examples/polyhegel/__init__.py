"""
Polyhegel Examples Package

This package extends the core polyhegel package with domain-specific implementations.
Import these as: polyhegel.agents.strategic.*, polyhegel.techniques.strategic.*, etc.

Available domains:
- strategic: Strategic planning and business strategy techniques
- technical_architecture: Software architecture and system design techniques
- product: Product roadmap and product management techniques
"""

# Extend the core polyhegel namespace
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
