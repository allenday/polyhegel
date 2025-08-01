"""
Tests for comparative evaluation framework
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from polyhegel.evaluation import ComparativeTestFramework, MetricsCollector, StrategicMetrics
from polyhegel.evaluation.comparative_test import TestConfiguration, ComparisonResult
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep


class TestMetricsCollector:
    """Test strategic metrics collection"""

    def setup_method(self):
        """Set up test environment"""
        self.collector = MetricsCollector()
        self.sample_strategy = self._create_sample_strategy()

    def _create_sample_strategy(self) -> StrategyChain:
        """Create a sample strategy for testing"""
        strategy = GenesisStrategy(
            title="Test Strategic Initiative",
            steps=[
                StrategyStep(
                    action="Initial Analysis",
                    prerequisites=["Market research completed"],
                    outcome="Comprehensive understanding of strategic landscape",
                    risks=["Incomplete data", "Analysis paralysis"],
                    confidence=0.8
                ),
                StrategyStep(
                    action="Stakeholder Alignment",
                    prerequisites=["Initial analysis completed"],
                    outcome="Aligned stakeholder expectations and commitments",
                    risks=["Conflicting interests"],
                    confidence=0.75
                ),
                StrategyStep(
                    action="Implementation Planning",
                    prerequisites=["Stakeholder alignment achieved"],
                    outcome="Detailed implementation roadmap",
                    risks=["Resource constraints", "Timeline pressure"],
                    confidence=0.85
                )
            ],
            alignment_score={
                "Strategic Coherence": 4.2,
                "Implementation Feasibility": 3.8,
                "Risk Management": 4.0
            },
            estimated_timeline="6 months",
            resource_requirements=[
                "Cross-functional team",
                "Strategic consulting budget",
                "Executive sponsorship",
                "Technology infrastructure"
            ]
        )
        
        return StrategyChain(
            strategy=strategy,
            source_sample=1,
            temperature=0.8
        )

    def test_metrics_collector_initialization(self):
        """Test metrics collector initialization"""
        collector = MetricsCollector()
        assert isinstance(collector.collected_metrics, list)
        assert len(collector.collected_metrics) == 0

    def test_collect_metrics_basic(self):
        """Test basic metrics collection"""
        # Create mock simulation results
        simulation_results = {
            'trunk': self.sample_strategy,
            'twigs': [],
            'metadata': {'selection_method': 'clustering'}
        }
        
        metrics = self.collector.collect_metrics(
            simulation_results,
            execution_time=45.0,
            memory_usage=128.5
        )
        
        assert isinstance(metrics, StrategicMetrics)
        assert metrics.execution_time == 45.0
        assert metrics.memory_usage == 128.5
        assert metrics.selection_method == 'clustering'
        assert metrics.trunk_strategy_title == "Test Strategic Initiative"
        assert metrics.total_strategies == 1

    def test_coherence_score_calculation(self):
        """Test strategic coherence score calculation"""
        metrics = self.collector._calculate_coherence_score(self.sample_strategy)
        
        # Should be a reasonable score (3-10 range for good strategy)
        assert 0 <= metrics <= 10
        assert metrics > 5  # Our sample strategy should score well

    def test_feasibility_score_calculation(self):
        """Test feasibility score calculation"""
        metrics = self.collector._calculate_feasibility_score(self.sample_strategy)
        
        assert 0 <= metrics <= 10
        # 6-month timeline with 4 resources and identified risks should be feasible
        assert metrics > 6

    def test_domain_alignment_score_calculation(self):
        """Test domain alignment score calculation"""
        metrics = self.collector._calculate_domain_alignment_score(self.sample_strategy)
        
        assert 0 <= metrics <= 10
        # Our strategy has alignment scores, should be > 5
        assert metrics > 5

    def test_risk_management_score_calculation(self):
        """Test risk management score calculation"""
        metrics = self.collector._calculate_risk_management_score(self.sample_strategy)
        
        assert 0 <= metrics <= 10
        # Strategy has good risk identification
        assert metrics > 5

    def test_resource_efficiency_score_calculation(self):
        """Test resource efficiency score calculation"""
        metrics = self.collector._calculate_resource_efficiency_score(self.sample_strategy)
        
        assert 0 <= metrics <= 10

    def test_strategy_diversity_calculation(self):
        """Test strategy diversity calculation"""
        # Create multiple strategies
        strategies = [self.sample_strategy]
        
        # Add another different strategy
        different_strategy = GenesisStrategy(
            title="Alternative Innovation Approach",
            steps=[
                StrategyStep(
                    action="Rapid Prototyping",
                    prerequisites=["Team assembled"],
                    outcome="Working prototype",
                    risks=["Technical challenges"],
                    confidence=0.7
                )
            ],
            alignment_score={"Innovation": 4.5},
            estimated_timeline="3 months",
            resource_requirements=["Development team", "Prototype budget"]
        )
        
        different_chain = StrategyChain(
            strategy=different_strategy,
            source_sample=2,
            temperature=0.9
        )
        strategies.append(different_chain)
        
        diversity = self.collector._calculate_strategy_diversity(strategies)
        assert 0 <= diversity <= 10
        # Two different strategies should have reasonable diversity
        assert diversity > 0

    def test_metrics_comparison(self):
        """Test comparing multiple metrics"""
        # Create sample metrics
        metrics1 = StrategicMetrics(
            coherence_score=8.0,
            feasibility_score=7.5,
            domain_alignment_score=8.2,
            selection_method="clustering",
            execution_time=30.0
        )
        
        metrics2 = StrategicMetrics(
            coherence_score=7.8,
            feasibility_score=8.0,
            domain_alignment_score=7.9,
            selection_method="tournament",
            execution_time=45.0
        )
        
        comparison = self.collector.compare_metrics([metrics1, metrics2])
        
        assert 'by_method' in comparison
        assert 'clustering' in comparison['by_method']
        assert 'tournament' in comparison['by_method']
        assert 'recommendations' in comparison


class TestComparativeTestFramework:
    """Test comparative testing framework"""

    def setup_method(self):
        """Set up test environment"""
        self.test_config = TestConfiguration(
            test_name="test_comparison",
            iterations=2,
            timeout_seconds=60
        )
        self.framework = ComparativeTestFramework(self.test_config)

    def test_framework_initialization(self):
        """Test framework initialization"""
        assert self.framework.config.test_name == "test_comparison"
        assert self.framework.config.iterations == 2
        assert isinstance(self.framework.metrics_collector, MetricsCollector)
        assert len(self.framework.results_history) == 0

    def test_configuration_defaults(self):
        """Test default configuration values"""
        config = TestConfiguration()
        
        assert config.test_name == "comparative_test"
        assert config.iterations == 3
        assert config.timeout_seconds == 300
        assert config.mode == "temperature"

    @pytest.mark.asyncio
    async def test_single_test_mock(self):
        """Test single test run with mocked simulator"""
        
        # Mock the simulator and its results
        mock_simulator = MagicMock()
        mock_simulator.run_simulation = AsyncMock(return_value={
            'trunk': self._create_mock_strategy(),
            'twigs': [],
            'metadata': {'selection_method': 'clustering'},
            'summary': "Test summary"
        })
        
        with patch('polyhegel.evaluation.comparative_test.PolyhegelSimulator', return_value=mock_simulator):
            metrics = await self.framework._run_single_test(
                selection_method="clustering",
                system_prompt="Test system prompt",
                user_prompt="Test user prompt",
                iteration=0
            )
        
        assert isinstance(metrics, StrategicMetrics)
        assert metrics.selection_method == "clustering"
        mock_simulator.run_simulation.assert_called_once()

    def _create_mock_strategy(self):
        """Create mock strategy for testing"""
        strategy = GenesisStrategy(
            title="Mock Strategy",
            steps=[
                StrategyStep(
                    action="Mock action",
                    prerequisites=["Mock prerequisite"],
                    outcome="Mock outcome",
                    risks=["Mock risk"],
                    confidence=0.8
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="3 months",
            resource_requirements=["Mock resource"]
        )
        
        return StrategyChain(
            strategy=strategy,
            source_sample=0,
            temperature=0.8
        )

    @pytest.mark.asyncio
    async def test_comparative_test_mock(self):
        """Test full comparative test with mocked components"""
        
        mock_strategy = self._create_mock_strategy()
        
        # Mock the simulator
        mock_simulator = MagicMock()
        mock_simulator.run_simulation = AsyncMock(return_value={
            'trunk': mock_strategy,
            'twigs': [],
            'metadata': {'selection_method': 'clustering'},
            'summary': "Test summary"
        })
        
        with patch('polyhegel.evaluation.comparative_test.PolyhegelSimulator', return_value=mock_simulator):
            result = await self.framework.run_comparative_test(
                system_prompt="Test system",
                user_prompt="Test user"
            )
        
        assert isinstance(result, ComparisonResult)
        assert len(result.clustering_metrics) <= self.test_config.iterations
        assert len(result.tournament_metrics) <= self.test_config.iterations
        assert 'comparative_analysis' in result.to_dict()

    def test_statistical_analysis(self):
        """Test statistical analysis functionality"""
        
        # Create sample metrics for comparison
        clustering_metrics = [
            StrategicMetrics(
                coherence_score=8.0,
                feasibility_score=7.5,
                execution_time=30.0,
                selection_method="clustering"
            ),
            StrategicMetrics(
                coherence_score=7.8,
                feasibility_score=7.8,
                execution_time=32.0,
                selection_method="clustering"
            )
        ]
        
        tournament_metrics = [
            StrategicMetrics(
                coherence_score=8.2,
                feasibility_score=8.0,
                execution_time=45.0,
                selection_method="tournament"
            ),
            StrategicMetrics(
                coherence_score=8.1,
                feasibility_score=7.9,
                execution_time=43.0,
                selection_method="tournament"
            )
        ]
        
        analysis = self.framework._perform_statistical_analysis(
            clustering_metrics, tournament_metrics
        )
        
        assert 'effect_sizes' in analysis
        assert 'performance_comparison' in analysis
        assert 'reliability_analysis' in analysis
        
        # Check that analysis contains expected metrics
        assert 'overall' in analysis['effect_sizes']
        assert 'coherence' in analysis['effect_sizes']
        assert 'execution_time' in analysis['effect_sizes']

    @pytest.mark.asyncio
    async def test_save_results(self):
        """Test results saving functionality"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            # Create mock comparison result
            result = ComparisonResult(
                clustering_metrics=[
                    StrategicMetrics(
                        coherence_score=8.0,
                        selection_method="clustering"
                    )
                ],
                tournament_metrics=[
                    StrategicMetrics(
                        coherence_score=8.2,
                        selection_method="tournament"
                    )
                ],
                comparative_analysis={"test": "analysis"},
                test_configuration=self.test_config,
                execution_summary={"test": "summary"}
            )
            
            await self.framework._save_results(result, output_dir)
            
            # Check that files were created
            results_file = output_dir / f"{self.test_config.test_name}_results.json"
            summary_file = output_dir / f"{self.test_config.test_name}_summary.md"
            
            assert results_file.exists()
            assert summary_file.exists()
            
            # Verify JSON content
            with open(results_file) as f:
                saved_data = json.load(f)
            
            assert 'clustering_metrics' in saved_data
            assert 'tournament_metrics' in saved_data
            assert 'comparative_analysis' in saved_data

    def test_automated_test_suite_config(self):
        """Test automated test suite configuration"""
        
        test_scenarios = [
            {
                'name': 'scenario_1',
                'iterations': 2,
                'system_prompt': 'Test system 1',
                'user_prompt': 'Test user 1'
            },
            {
                'name': 'scenario_2', 
                'iterations': 1,
                'system_prompt': 'Test system 2',
                'user_prompt': 'Test user 2'
            }
        ]
        
        # Test that scenarios are properly configured
        assert len(test_scenarios) == 2
        assert test_scenarios[0]['name'] == 'scenario_1'
        assert test_scenarios[1]['iterations'] == 1


class TestStrategicMetrics:
    """Test StrategicMetrics dataclass"""

    def test_metrics_initialization(self):
        """Test metrics initialization with defaults"""
        metrics = StrategicMetrics()
        
        assert metrics.coherence_score == 0.0
        assert metrics.feasibility_score == 0.0
        assert metrics.execution_time == 0.0
        assert metrics.selection_method == ""

    def test_overall_score_calculation(self):
        """Test overall score calculation with weights"""
        metrics = StrategicMetrics(
            coherence_score=8.0,
            feasibility_score=7.0,
            domain_alignment_score=9.0,
            risk_management_score=6.0,
            resource_efficiency_score=8.0
        )
        
        # Calculate expected weighted score
        expected = (8.0 * 0.25 + 7.0 * 0.25 + 9.0 * 0.20 + 6.0 * 0.15 + 8.0 * 0.15)
        
        assert abs(metrics.overall_score() - expected) < 0.01

    def test_metrics_to_dict(self):
        """Test metrics conversion to dictionary"""
        metrics = StrategicMetrics(
            coherence_score=8.0,
            feasibility_score=7.5,
            selection_method="tournament",
            execution_time=45.0
        )
        
        data = metrics.to_dict()
        
        assert 'strategic_scores' in data
        assert 'performance_metrics' in data
        assert 'metadata' in data
        
        assert data['strategic_scores']['coherence'] == 8.0
        assert data['strategic_scores']['feasibility'] == 7.5
        assert data['performance_metrics']['execution_time'] == 45.0
        assert data['metadata']['selection_method'] == "tournament"
        assert 'overall' in data['strategic_scores']


class TestIntegration:
    """Integration tests for the evaluation framework"""

    @pytest.mark.asyncio
    async def test_end_to_end_mock_workflow(self):
        """Test complete end-to-end workflow with mocks"""
        
        # Create test configuration
        config = TestConfiguration(
            test_name="integration_test",
            iterations=1,
            timeout_seconds=30
        )
        
        framework = ComparativeTestFramework(config)
        
        # Mock strategy for consistent results
        mock_strategy = GenesisStrategy(
            title="Integration Test Strategy",
            steps=[
                StrategyStep(
                    action="Test action",
                    prerequisites=["Test prerequisite"],
                    outcome="Test outcome",
                    risks=["Test risk"],
                    confidence=0.8
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="2 months",
            resource_requirements=["Test resource"]
        )
        
        mock_chain = StrategyChain(
            strategy=mock_strategy,
            source_sample=0,
            temperature=0.8
        )
        
        # Mock simulator
        mock_simulator = MagicMock()
        mock_simulator.run_simulation = AsyncMock(return_value={
            'trunk': mock_chain,
            'twigs': [],
            'metadata': {'selection_method': 'clustering'},
            'summary': "Integration test summary"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            with patch('polyhegel.evaluation.comparative_test.PolyhegelSimulator', return_value=mock_simulator):
                result = await framework.run_comparative_test(
                    system_prompt="Integration test system prompt",
                    user_prompt="Integration test user prompt",
                    output_dir=output_dir
                )
            
            # Verify result structure
            assert isinstance(result, ComparisonResult)
            assert result.test_configuration.test_name == "integration_test"
            
            # Verify files were created
            results_file = output_dir / "integration_test_results.json"
            summary_file = output_dir / "integration_test_summary.md"
            
            assert results_file.exists()
            assert summary_file.exists()
            
            # Verify summary file content
            with open(summary_file) as f:
                summary_content = f.read()
            
            assert "Integration Test Strategy" in summary_content or "Comparative Test Results" in summary_content


if __name__ == "__main__":
    pytest.main([__file__])