"""
Tests for PolyhegelSimulator
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from polyhegel.simulator import PolyhegelSimulator
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep, StrategicTheme, ThemeCategory


@pytest.mark.unit
class TestPolyhegelSimulator:
    """Test PolyhegelSimulator functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.simulator = PolyhegelSimulator(model_name="test")

    def test_simulator_initialization(self):
        """Test simulator initialization"""
        assert self.simulator.model_name == "test"
        assert self.simulator.generator is not None
        assert self.simulator.embedder is not None
        assert self.simulator.clusterer is not None
        assert self.simulator.summarizer is not None
        assert self.simulator.chains == []
        assert self.simulator.trunk is None
        assert self.simulator.twigs == []

    def test_parse_temperature_counts(self):
        """Test temperature count parsing"""
        # Test valid formats
        temp_counts = self.simulator.parse_temperature_counts(["0.1:1", "0.3:2", "0.7:5"])
        expected = [(0.1, 1), (0.3, 2), (0.7, 5)]
        assert temp_counts == expected

        # Test backward compatibility (single temperature)
        temp_counts = self.simulator.parse_temperature_counts(["0.5"])
        expected = [(0.5, 1)]
        assert temp_counts == expected

        # Test mixed formats
        temp_counts = self.simulator.parse_temperature_counts(["0.1:2", "0.8"])
        expected = [(0.1, 2), (0.8, 1)]
        assert temp_counts == expected

        # Test invalid formats (should be skipped)
        temp_counts = self.simulator.parse_temperature_counts(["invalid", "0.5:abc", "0.7:3"])
        expected = [(0.7, 3)]
        assert temp_counts == expected


@pytest.mark.integration
class TestPolyhegelSimulatorIntegration:
    """Integration tests for PolyhegelSimulator"""

    def setup_method(self):
        """Set up test environment"""
        self.simulator = PolyhegelSimulator(model_name="test")

        # Mock strategies for testing
        self.mock_strategies = [
            GenesisStrategy(
                title=f"Test Strategy {i}",
                steps=[
                    StrategyStep(
                        action=f"Action {i}",
                        prerequisites=[f"Prerequisite {i}"],
                        outcome=f"Outcome {i}",
                        risks=[f"Risk {i}"],
                    )
                ],
                alignment_score={"test": 4.0},
                estimated_timeline="6 months",
                resource_requirements=[f"Resource {i}"],
            )
            for i in range(3)
        ]

        self.mock_chains = [
            StrategyChain(strategy=strategy, source_sample=i, temperature=0.7)
            for i, strategy in enumerate(self.mock_strategies)
        ]

    @pytest.mark.asyncio
    async def test_temperature_mode_simulation(self):
        """Test complete simulation pipeline in temperature mode"""
        with patch.object(self.simulator.generator, "generate_strategies", new_callable=AsyncMock) as mock_gen:
            with patch.object(self.simulator.embedder, "embed_strategies") as mock_embed:
                with patch.object(self.simulator.clusterer, "cluster_strategies") as mock_cluster:
                    with patch.object(
                        self.simulator.summarizer, "summarize_results", new_callable=AsyncMock
                    ) as mock_summary:

                        # Setup mocks
                        mock_gen.return_value = self.mock_chains
                        mock_cluster.return_value = {
                            "trunk": self.mock_chains[0],
                            "twigs": self.mock_chains[1:],
                            "cluster_count": 2,
                            "noise_count": 0,
                            "cluster_sizes": {0: 1, 1: 2},
                        }
                        mock_summary.return_value = "Test summary"

                        # Run simulation
                        results = await self.simulator.run_simulation(
                            temperature_counts=[(0.7, 3)], user_prompt="Test strategic challenge", mode="temperature"
                        )

                        # Verify results structure
                        assert "trunk" in results
                        assert "twigs" in results
                        assert "summary" in results
                        assert "metadata" in results
                        assert "statistics" in results

                        assert results["summary"] == "Test summary"
                        assert results["metadata"]["total_chains"] == 3
                        assert results["metadata"]["model"] == "test"

                        # Verify mocks were called
                        mock_gen.assert_called_once()
                        mock_embed.assert_called_once()
                        mock_cluster.assert_called_once()
                        mock_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_hierarchical_mode_simulation(self):
        """Test complete simulation pipeline in hierarchical mode"""
        with patch.object(
            self.simulator, "_generate_hierarchical_strategies", new_callable=AsyncMock
        ) as mock_hierarchical:
            with patch.object(self.simulator.embedder, "embed_strategies") as mock_embed:
                with patch.object(self.simulator.clusterer, "cluster_strategies") as mock_cluster:
                    with patch.object(
                        self.simulator.summarizer, "summarize_results", new_callable=AsyncMock
                    ) as mock_summary:

                        # Setup mocks
                        mock_hierarchical.return_value = self.mock_chains
                        mock_cluster.return_value = {
                            "trunk": self.mock_chains[0],
                            "twigs": self.mock_chains[1:],
                            "cluster_count": 2,
                            "noise_count": 0,
                            "cluster_sizes": {0: 1, 1: 2},
                        }
                        mock_summary.return_value = "Hierarchical test summary"

                        # Run simulation
                        results = await self.simulator.run_simulation(
                            user_prompt="Test strategic challenge", mode="hierarchical"
                        )

                        # Verify results structure
                        assert "trunk" in results
                        assert "twigs" in results
                        assert "summary" in results
                        assert "metadata" in results
                        assert "statistics" in results

                        assert results["summary"] == "Hierarchical test summary"
                        assert results["metadata"]["total_chains"] == 3

                        # Verify hierarchical generation was called
                        mock_hierarchical.assert_called_once()
                        mock_embed.assert_called_once()
                        mock_cluster.assert_called_once()
                        mock_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_hierarchical_strategy_generation(self):
        """Test hierarchical strategy generation method"""
        # Mock themes from leader
        mock_themes = [
            StrategicTheme(
                title="Resource Optimization",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="Optimize resource allocation and acquisition processes for improved operational efficiency and cost reduction",
                domain_alignment={"2.1": 4.5, "2.2": 2.0, "2.3": 2.5},
                key_concepts=["resources", "optimization"],
                success_criteria=["Improved efficiency"],
            ),
            StrategicTheme(
                title="Security Enhancement",
                category=ThemeCategory.STRATEGIC_SECURITY,
                description="Enhance organizational security posture through comprehensive threat detection and protection mechanisms",
                domain_alignment={"2.1": 2.0, "2.2": 4.5, "2.3": 2.0},
                key_concepts=["security", "protection"],
                success_criteria=["Enhanced security"],
            ),
        ]

        # Mock strategies from followers
        mock_strategies = [
            GenesisStrategy(
                title="Resource Optimization Strategy",
                steps=[
                    StrategyStep(
                        action="Analyze current resource usage",
                        prerequisites=["Resource audit"],
                        outcome="Usage analysis",
                        risks=["Incomplete data"],
                    )
                ],
                alignment_score={"efficiency": 4.0},
                estimated_timeline="4 months",
                resource_requirements=["Analytics team"],
            ),
            GenesisStrategy(
                title="Security Enhancement Strategy",
                steps=[
                    StrategyStep(
                        action="Implement security framework",
                        prerequisites=["Security assessment"],
                        outcome="Enhanced security",
                        risks=["Implementation complexity"],
                    )
                ],
                alignment_score={"security": 4.5},
                estimated_timeline="6 months",
                resource_requirements=["Security team"],
            ),
        ]

        with patch("polyhegel.hierarchical_agent.AgentCoordinator") as mock_coordinator_class:
            with patch("polyhegel.simulator.LeaderAgent"):
                with patch("polyhegel.simulator.FollowerAgent"):

                    # Setup coordinator mock
                    mock_coordinator = MagicMock()
                    mock_coordinator_class.return_value = mock_coordinator

                    # Setup theme generation response
                    mock_theme_response = MagicMock()
                    mock_theme_response.success = True
                    mock_theme_response.content = mock_themes

                    # Setup strategy generation responses
                    mock_strategy_responses = []
                    for strategy in mock_strategies:
                        mock_response = MagicMock()
                        mock_response.success = True
                        mock_response.content = strategy
                        mock_strategy_responses.append(mock_response)

                    # Configure coordinate_task to return appropriate responses
                    async def mock_coordinate_task(task):
                        if task["type"] == "generate_themes":
                            return [mock_theme_response]
                        elif task["type"] == "develop_strategy":
                            # Return one strategy response for each theme
                            return [mock_strategy_responses.pop(0)]
                        return []

                    mock_coordinator.coordinate_task = mock_coordinate_task

                    # Run hierarchical generation
                    chains = await self.simulator._generate_hierarchical_strategies(
                        user_prompt="Test strategic challenge"
                    )

                    # Verify results
                    assert len(chains) == 2
                    assert all(isinstance(chain, StrategyChain) for chain in chains)
                    assert chains[0].strategy.title == "Resource Optimization Strategy"
                    assert chains[1].strategy.title == "Security Enhancement Strategy"
                    assert all(chain.temperature == 0.7 for chain in chains)

    @pytest.mark.asyncio
    async def test_hierarchical_mode_requires_user_prompt(self):
        """Test that hierarchical mode requires user prompt"""
        with pytest.raises(ValueError, match="User prompt is required"):
            await self.simulator.run_simulation(mode="hierarchical")

    @pytest.mark.asyncio
    async def test_no_strategies_generated_error(self):
        """Test error handling when no strategies are generated"""
        with patch.object(self.simulator.generator, "generate_strategies", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = []

            with pytest.raises(ValueError, match="No strategies generated"):
                await self.simulator.run_simulation(
                    temperature_counts=[(0.7, 1)], user_prompt="Test prompt", mode="temperature"
                )

    def test_list_available_models(self):
        """Test listing available models"""
        with patch.object(self.simulator.model_manager, "discover_available_models") as mock_discover:
            mock_discover.return_value = {"openai": ["gpt-4", "gpt-3.5"], "anthropic": ["claude-3"]}

            models = self.simulator.list_available_models()
            assert "openai" in models
            assert "anthropic" in models
            mock_discover.assert_called_once()

    def test_list_models_with_availability(self):
        """Test listing models with availability status"""
        with patch.object(self.simulator.model_manager, "list_models_with_availability") as mock_list:
            mock_list.return_value = {"gpt-4": {"available": True, "provider": "openai"}}

            models = self.simulator.list_models_with_availability()
            assert "gpt-4" in models
            mock_list.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
