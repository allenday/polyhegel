"""
Pytest configuration and shared fixtures for polyhegel tests
"""

import pytest


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: marks tests as unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: marks tests as integration tests (may use multiple components)")
    config.addinivalue_line("markers", "slow: marks tests as slow (>5 seconds)")
    config.addinivalue_line("markers", "llm: marks tests that make real LLM API calls")
    config.addinivalue_line("markers", "web: marks tests that make web requests")
    config.addinivalue_line("markers", "git: marks tests that interact with git repositories")


def pytest_collection_modifyitems(config, items):
    """Automatically add markers based on test names/paths"""
    for item in items:
        # Auto-mark integration tests
        if "test_integration" in item.nodeid or "test_full_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # Auto-mark web tests
        if "test_web_tools" in item.nodeid:
            item.add_marker(pytest.mark.web)

        # Auto-mark git tests
        if "test_git_tools" in item.nodeid:
            item.add_marker(pytest.mark.git)

        # Auto-mark slow tests
        if any(name in item.nodeid for name in ["test_full_integration", "test_tournament"]):
            item.add_marker(pytest.mark.slow)

        # Auto-mark unit tests (if not already marked)
        if not any(mark.name in ["integration", "slow", "llm", "web", "git"] for mark in item.iter_markers()):
            if "test_models" in item.nodeid or "test_base_agent" in item.nodeid or "test_leader_agent" in item.nodeid:
                item.add_marker(pytest.mark.unit)
