"""
Domain Manager for Polyhegel

This module provides domain discovery, loading, and management capabilities
for the polyhegel framework. It allows dynamic loading of domain plugins
from the domains/ directory.
"""

import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add domains to Python path for imports
_project_root = Path(__file__).parent.parent
_domains_path = _project_root / "domains"
if str(_domains_path) not in sys.path:
    sys.path.insert(0, str(_domains_path))


class DomainManager:
    """Manages discovery and loading of polyhegel domains"""

    def __init__(self):
        self._domains: Dict[str, Any] = {}
        self._loaded = False

    def discover_domains(self) -> None:
        """Discover and load all available domains"""
        if self._loaded:
            return

        try:
            # Import the domains package which will auto-register domains
            import domains

            domains.discover_domains()

            # Store discovered domains
            self._domains = {name: domains.get_domain(name) for name in domains.list_domains()}
            self._loaded = True

        except ImportError as e:
            print(f"Warning: Could not import domains package: {e}")
        except Exception as e:
            print(f"Warning: Error discovering domains: {e}")

    def get_domain(self, name: str) -> Optional[Any]:
        """Get a domain by name"""
        if not self._loaded:
            self.discover_domains()
        return self._domains.get(name)

    def list_domains(self) -> List[str]:
        """List all available domain names"""
        if not self._loaded:
            self.discover_domains()
        return list(self._domains.keys())

    def get_all_techniques(self) -> Dict[str, List[Any]]:
        """Get techniques from all domains"""
        if not self._loaded:
            self.discover_domains()

        all_techniques = {}
        for domain_name, domain in self._domains.items():
            try:
                all_techniques[domain_name] = domain.get_techniques()
            except Exception as e:
                print(f"Warning: Could not get techniques from domain '{domain_name}': {e}")
                all_techniques[domain_name] = []

        return all_techniques

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get agents from all domains"""
        if not self._loaded:
            self.discover_domains()

        all_agents = {}
        for domain_name, domain in self._domains.items():
            try:
                all_agents[domain_name] = domain.get_agents()
            except Exception as e:
                print(f"Warning: Could not get agents from domain '{domain_name}': {e}")
                all_agents[domain_name] = {}

        return all_agents

    def get_domain_techniques(self, domain_name: str) -> List[Any]:
        """Get techniques from a specific domain"""
        domain = self.get_domain(domain_name)
        if domain:
            try:
                return domain.get_techniques()
            except Exception as e:
                print(f"Warning: Could not get techniques from domain '{domain_name}': {e}")
        return []

    def get_domain_agents(self, domain_name: str) -> Dict[str, Any]:
        """Get agents from a specific domain"""
        domain = self.get_domain(domain_name)
        if domain:
            try:
                return domain.get_agents()
            except Exception as e:
                print(f"Warning: Could not get agents from domain '{domain_name}': {e}")
        return {}

    def get_domain_prompts_path(self, domain_name: str) -> Optional[str]:
        """Get prompts path for a specific domain"""
        domain = self.get_domain(domain_name)
        if domain:
            try:
                return domain.get_prompts_path()
            except Exception as e:
                print(f"Warning: Could not get prompts path from domain '{domain_name}': {e}")
        return None

    def reload_domains(self) -> None:
        """Reload all domains (useful for development)"""
        self._loaded = False
        self._domains.clear()

        # Clear module cache for domains
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name.startswith("domains."):
                modules_to_remove.append(module_name)

        for module_name in modules_to_remove:
            del sys.modules[module_name]

        # Rediscover
        self.discover_domains()


# Global domain manager instance
_domain_manager = DomainManager()


def get_domain_manager() -> DomainManager:
    """Get the global domain manager instance"""
    return _domain_manager


def get_domain(name: str) -> Optional[Any]:
    """Get a domain by name (convenience function)"""
    return _domain_manager.get_domain(name)


def list_domains() -> List[str]:
    """List all available domain names (convenience function)"""
    return _domain_manager.list_domains()


def get_all_techniques() -> Dict[str, List[Any]]:
    """Get techniques from all domains (convenience function)"""
    return _domain_manager.get_all_techniques()


def get_all_agents() -> Dict[str, Dict[str, Any]]:
    """Get agents from all domains (convenience function)"""
    return _domain_manager.get_all_agents()


def discover_domains() -> None:
    """Discover all available domains (convenience function)"""
    _domain_manager.discover_domains()


# Auto-discover domains on import
discover_domains()
