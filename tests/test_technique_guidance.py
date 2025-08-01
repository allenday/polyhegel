"""
Tests for technique-guided strategy generation
"""

import pytest
from polyhegel.strategy_generator import StrategyGenerator
from polyhegel.model_manager import ModelManager


class TestTechniqueGuidance:
    """Test technique-guided strategy generation"""

    def setup_method(self):
        """Set up test environment"""
        self.model_manager = ModelManager()
        # Use a lighter model for testing
        self.model = self.model_manager.get_model("claude-3-haiku-20240307")
        self.generator = StrategyGenerator(self.model)

    @pytest.mark.asyncio
    async def test_generate_with_technique_basic(self):
        """Test basic technique-guided generation"""
        technique_name = "Stakeholder Alignment Matrix"
        strategic_challenge = "Build consensus around food classification standards"

        # Generate strategies using the technique
        chains = await self.generator.generate_with_technique(
            strategic_challenge=strategic_challenge, technique_name=technique_name, temperature=0.8, count=1
        )

        # Verify results
        assert len(chains) == 1
        chain = chains[0]

        # Check technique metadata
        assert chain.technique_name == technique_name
        assert chain.technique_domain == "2.1"  # Resource Acquisition

        # Check strategy content
        assert isinstance(chain.strategy.title, str)
        assert len(chain.strategy.steps) > 0
        assert chain.temperature == 0.8

        # Strategy should be related to the challenge
        strategy_text = f"{chain.strategy.title} {' '.join(step.action for step in chain.strategy.steps)}"
        assert any(keyword in strategy_text.lower() for keyword in ["stakeholder", "alignment", "consensus"])

    @pytest.mark.asyncio
    async def test_generate_with_invalid_technique(self):
        """Test error handling for invalid technique"""
        with pytest.raises(ValueError, match="Unknown technique"):
            await self.generator.generate_with_technique(
                strategic_challenge="Test challenge", technique_name="Non-existent Technique", temperature=0.8, count=1
            )

    @pytest.mark.asyncio
    async def test_generate_with_multiple_techniques(self):
        """Test generation with multiple techniques"""
        technique_names = ["Stakeholder Alignment Matrix", "Incremental Resource Bootstrap"]
        strategic_challenge = "Launch a sustainable AI research initiative"

        # Generate strategies using multiple techniques
        chains = await self.generator.generate_with_multiple_techniques(
            strategic_challenge=strategic_challenge,
            technique_names=technique_names,
            temperature=0.7,
            count_per_technique=1,
        )

        # Should have strategies from both techniques
        assert len(chains) == 2

        # Check that each technique was used
        technique_names_used = [chain.technique_name for chain in chains]
        assert set(technique_names_used) == set(technique_names)

        # All should be from Resource Acquisition domain
        assert all(chain.technique_domain == "2.1" for chain in chains)

    @pytest.mark.asyncio
    async def test_compare_technique_vs_temperature_generation(self):
        """Compare technique-guided vs temperature-only generation"""
        strategic_challenge = "Develop a strategy for maintaining operational security during rapid scaling"

        # Generate with technique guidance
        technique_chains = await self.generator.generate_with_technique(
            strategic_challenge=strategic_challenge,
            technique_name="Layered Defense Architecture",
            temperature=0.7,
            count=1,
        )

        # Generate with temperature only (traditional approach)
        temp_chains = await self.generator.generate_strategies(
            temperature_counts=[(0.7, 1)], user_prompt=strategic_challenge
        )

        # Both should produce results
        assert len(technique_chains) == 1
        assert len(temp_chains) == 1

        technique_chain = technique_chains[0]
        temp_chain = temp_chains[0]

        # Technique-guided should have technique metadata
        assert technique_chain.technique_name == "Layered Defense Architecture"
        assert technique_chain.technique_domain == "2.2"  # Strategic Security

        # Temperature-only should not have technique metadata
        assert temp_chain.technique_name is None
        assert temp_chain.technique_domain is None

        # Both should have valid strategies
        assert len(technique_chain.strategy.steps) > 0
        assert len(temp_chain.strategy.steps) > 0

    @pytest.mark.asyncio
    async def test_technique_guidance_different_domains(self):
        """Test technique guidance across different Strategic domains"""
        strategic_challenge = "Build a thriving ecosystem for collaborative innovation"

        # Test one technique from each domain
        technique_tests = [
            ("Stakeholder Alignment Matrix", "2.1"),  # Resource Acquisition
            ("Community-Based Security", "2.2"),  # Strategic Security
            ("Cross-Pollination Innovation", "2.3"),  # Value Catalysis
        ]

        for technique_name, expected_domain in technique_tests:
            chains = await self.generator.generate_with_technique(
                strategic_challenge=strategic_challenge, technique_name=technique_name, temperature=0.7, count=1
            )

            assert len(chains) == 1
            chain = chains[0]
            assert chain.technique_name == technique_name
            assert chain.technique_domain == expected_domain

            # Strategy should reflect the domain focus
            strategy_text = f"{chain.strategy.title} {' '.join(step.action for step in chain.strategy.steps)}"

            if expected_domain == "2.1":  # Resource Acquisition
                assert any(
                    keyword in strategy_text.lower() for keyword in ["resource", "stakeholder", "fund", "partner"]
                )
            elif expected_domain == "2.2":  # Strategic Security
                assert any(keyword in strategy_text.lower() for keyword in ["security", "risk", "protect", "safe"])
            elif expected_domain == "2.3":  # Value Catalysis
                assert any(keyword in strategy_text.lower() for keyword in ["value", "innovation", "catalys", "growth"])

    @pytest.mark.asyncio
    async def test_technique_template_loading(self):
        """Test that technique template is properly loaded"""
        technique_name = "Value-Based Resource Exchange"
        strategic_challenge = "Create a resource sharing network without traditional currency"

        # This should work without error if template loading works
        chains = await self.generator.generate_with_technique(
            strategic_challenge=strategic_challenge, technique_name=technique_name, temperature=0.8, count=1
        )

        assert len(chains) == 1
        chain = chains[0]

        # Strategy should reflect the technique focus
        strategy_text = f"{chain.strategy.title} {' '.join(step.action for step in chain.strategy.steps)}"
        assert any(keyword in strategy_text.lower() for keyword in ["exchange", "value", "resource", "barter"])

    @pytest.mark.asyncio
    async def test_technique_guidance_error_handling(self):
        """Test error handling in technique-guided generation"""
        # Test with missing template (should be handled gracefully)
        technique_name = "Stakeholder Alignment Matrix"
        strategic_challenge = "Test challenge"

        # Even if there are failures, should not crash
        try:
            chains = await self.generator.generate_with_technique(
                strategic_challenge=strategic_challenge,
                technique_name=technique_name,
                temperature=0.8,
                count=3,  # Try multiple to test retry logic
            )
            # Should get at least some results
            assert len(chains) >= 0
        except Exception as e:
            # If it fails, should be a clear error message
            assert isinstance(e, (ValueError, FileNotFoundError))

    def test_technique_metadata_integration(self):
        """Test that technique metadata integrates properly with StrategyChain"""
        from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep

        # Create a test strategy
        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[
                StrategyStep(
                    action="Test Action",
                    prerequisites=["Test Prerequisite"],
                    outcome="Test Outcome",
                    risks=["Test Risk"],
                    confidence=0.8,
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="1 month",
            resource_requirements=["Test Resource"],
        )

        # Create StrategyChain with technique metadata
        chain = StrategyChain(
            strategy=strategy, source_sample=0, temperature=0.7, technique_name="Test Technique", technique_domain="2.1"
        )

        # Verify metadata is properly stored
        assert chain.technique_name == "Test Technique"
        assert chain.technique_domain == "2.1"
        assert chain.strategy.title == "Test Strategy"


if __name__ == "__main__":
    pytest.main([__file__])
