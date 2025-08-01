"""
Tests for strategic techniques module
"""

import pytest
from polyhegel.strategic_techniques import (
    StrategyDomain,
    StrategicTechnique,
    ALL_TECHNIQUES,
    TECHNIQUE_REGISTRY,
    get_techniques_for_domain,
    get_techniques_by_complexity,
    get_techniques_by_timeframe,
    get_technique_by_name,
    get_recommended_techniques,
    get_techniques_prompt_text,
    format_technique_for_prompt,
)


class TestStrategicTechniques:
    """Test strategic techniques functionality"""

    def test_all_techniques_loaded(self):
        """Test that all techniques are properly loaded"""
        assert len(ALL_TECHNIQUES) == 15  # 5 per domain * 3 domains
        assert len(TECHNIQUE_REGISTRY) == 15

        # Verify each domain has 5 techniques
        resource_techniques = get_techniques_for_domain(StrategyDomain.RESOURCE_ACQUISITION)
        security_techniques = get_techniques_for_domain(StrategyDomain.STRATEGIC_SECURITY)
        value_techniques = get_techniques_for_domain(StrategyDomain.VALUE_CATALYSIS)

        assert len(resource_techniques) == 5
        assert len(security_techniques) == 5
        assert len(value_techniques) == 5

    def test_technique_structure(self):
        """Test that techniques have proper structure"""
        technique = ALL_TECHNIQUES[0]
        assert isinstance(technique, StrategicTechnique)
        assert isinstance(technique.name, str)
        assert isinstance(technique.description, str)
        assert isinstance(technique.domain, StrategyDomain)
        assert isinstance(technique.use_cases, list)
        assert len(technique.use_cases) > 0
        assert technique.complexity in ["low", "medium", "high"]
        assert technique.timeframe in ["immediate", "short-term", "long-term"]

    def test_get_techniques_for_domain(self):
        """Test filtering techniques by domain"""
        resource_techniques = get_techniques_for_domain(StrategyDomain.RESOURCE_ACQUISITION)
        assert all(t.domain == StrategyDomain.RESOURCE_ACQUISITION for t in resource_techniques)

        security_techniques = get_techniques_for_domain(StrategyDomain.STRATEGIC_SECURITY)
        assert all(t.domain == StrategyDomain.STRATEGIC_SECURITY for t in security_techniques)

        value_techniques = get_techniques_for_domain(StrategyDomain.VALUE_CATALYSIS)
        assert all(t.domain == StrategyDomain.VALUE_CATALYSIS for t in value_techniques)

    def test_get_techniques_by_complexity(self):
        """Test filtering techniques by complexity"""
        low_complexity = get_techniques_by_complexity("low")
        medium_complexity = get_techniques_by_complexity("medium")
        high_complexity = get_techniques_by_complexity("high")

        assert all(t.complexity == "low" for t in low_complexity)
        assert all(t.complexity == "medium" for t in medium_complexity)
        assert all(t.complexity == "high" for t in high_complexity)

        # Should have techniques in each category
        assert len(low_complexity) > 0
        assert len(medium_complexity) > 0
        assert len(high_complexity) > 0

        # Total should equal all techniques
        assert len(low_complexity) + len(medium_complexity) + len(high_complexity) == len(ALL_TECHNIQUES)

    def test_get_techniques_by_timeframe(self):
        """Test filtering techniques by timeframe"""
        immediate = get_techniques_by_timeframe("immediate")
        short_term = get_techniques_by_timeframe("short-term")
        long_term = get_techniques_by_timeframe("long-term")

        assert all(t.timeframe == "immediate" for t in immediate)
        assert all(t.timeframe == "short-term" for t in short_term)
        assert all(t.timeframe == "long-term" for t in long_term)

        # Should have techniques in each timeframe
        assert len(immediate) > 0
        assert len(short_term) > 0
        assert len(long_term) > 0

        # Total should equal all techniques
        assert len(immediate) + len(short_term) + len(long_term) == len(ALL_TECHNIQUES)

    def test_get_technique_by_name(self):
        """Test getting specific technique by name"""
        technique_name = ALL_TECHNIQUES[0].name
        technique = get_technique_by_name(technique_name)

        assert technique is not None
        assert technique.name == technique_name

        # Test non-existent technique
        assert get_technique_by_name("Non-existent Technique") is None

    def test_get_recommended_techniques_filtering(self):
        """Test multi-criteria filtering"""
        # Filter by domain and complexity
        resource_medium = get_recommended_techniques(domain=StrategyDomain.RESOURCE_ACQUISITION, complexity="medium")
        assert all(
            t.domain == StrategyDomain.RESOURCE_ACQUISITION and t.complexity == "medium" for t in resource_medium
        )

        # Filter by timeframe with limit
        immediate_limited = get_recommended_techniques(timeframe="immediate", limit=2)
        assert len(immediate_limited) <= 2
        assert all(t.timeframe == "immediate" for t in immediate_limited)

    def test_format_technique_for_prompt(self):
        """Test technique formatting for prompts"""
        technique = ALL_TECHNIQUES[0]
        formatted = format_technique_for_prompt(technique)

        assert technique.name in formatted
        assert technique.description in formatted
        assert technique.domain.value in formatted
        assert technique.complexity.title() in formatted
        assert technique.timeframe.title() in formatted

        # Should include use cases
        for use_case in technique.use_cases:
            assert use_case in formatted

    def test_get_techniques_prompt_text(self):
        """Test generating prompt text for techniques"""
        # Basic prompt text
        prompt_text = get_techniques_prompt_text(limit=2)
        assert len(prompt_text) > 0

        # Should contain technique names
        techniques = get_recommended_techniques(limit=2)
        for technique in techniques:
            assert technique.name in prompt_text

        # Test with specific criteria
        resource_prompt = get_techniques_prompt_text(domain=StrategyDomain.RESOURCE_ACQUISITION, limit=1)
        assert len(resource_prompt) > 0

        # Test no matches
        no_match_prompt = get_techniques_prompt_text(
            domain=StrategyDomain.RESOURCE_ACQUISITION, complexity="nonexistent"
        )
        assert "No techniques match" in no_match_prompt

    def test_domain_coverage(self):
        """Test that all strategic domains are covered"""
        domains_covered = set(t.domain for t in ALL_TECHNIQUES)
        expected_domains = set(StrategyDomain)

        assert domains_covered == expected_domains

    def test_technique_diversity(self):
        """Test that techniques have good diversity in complexity and timeframe"""
        complexities = set(t.complexity for t in ALL_TECHNIQUES)
        timeframes = set(t.timeframe for t in ALL_TECHNIQUES)

        assert complexities == {"low", "medium", "high"}
        assert timeframes == {"immediate", "short-term", "long-term"}

    def test_technique_use_cases(self):
        """Test that all techniques have meaningful use cases"""
        for technique in ALL_TECHNIQUES:
            assert len(technique.use_cases) >= 3  # Each should have at least 3 use cases
            assert all(isinstance(use_case, str) and len(use_case) > 10 for use_case in technique.use_cases)

    def test_technique_names_unique(self):
        """Test that all technique names are unique"""
        names = [t.name for t in ALL_TECHNIQUES]
        assert len(names) == len(set(names))  # No duplicates


if __name__ == "__main__":
    pytest.main([__file__])
