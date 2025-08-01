"""
Tests for recursive refinement system
"""

import pytest
import tempfile
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from polyhegel.refinement import (
    RecursiveRefinementEngine,
    PerformanceTracker,
    FeedbackLoop,
    StrategyImprover,
    RefinementMetrics,
    RefinementConfiguration
)
from polyhegel.refinement.feedback import (
    ImprovementSuggestion,
    ImprovementCategory,
    FeedbackAnalysis
)
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep
from polyhegel.evaluation.metrics import StrategicMetrics


class TestPerformanceTracker:
    """Test performance tracking functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_refinement.db"
        self.tracker = PerformanceTracker(self.db_path)
        self.sample_strategy = self._create_sample_strategy()
    
    def _create_sample_strategy(self) -> StrategyChain:
        """Create sample strategy for testing"""
        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[
                StrategyStep(
                    action="Test Action",
                    prerequisites=["Test Prerequisite"],
                    outcome="Test Outcome",
                    risks=["Test Risk"],
                    confidence=0.8
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="3 months",
            resource_requirements=["Test Resource"]
        )
        
        return StrategyChain(
            strategy=strategy,
            source_sample=1,
            temperature=0.8
        )
    
    def test_tracker_initialization(self):
        """Test performance tracker initialization"""
        assert self.tracker.db_path == self.db_path
        assert self.db_path.exists()
        assert isinstance(self.tracker.recent_metrics, dict)
    
    def test_record_performance_initial(self):
        """Test recording initial performance"""
        strategic_metrics = StrategicMetrics(
            coherence_score=8.0,
            feasibility_score=7.5,
            domain_alignment_score=8.2,
            risk_management_score=7.8,
            resource_efficiency_score=7.2
        )
        
        metrics = self.tracker.record_performance(
            self.sample_strategy,
            strategic_metrics,
            generation=0,
            refinement_id="test_refinement"
        )
        
        assert isinstance(metrics, RefinementMetrics)
        assert metrics.refinement_id == "test_refinement"
        assert metrics.generation == 0
        assert metrics.improvement_score == 0.0  # No improvement for generation 0
        assert metrics.strategic_metrics == strategic_metrics
    
    def test_record_performance_improvement(self):
        """Test recording performance with improvement calculation"""
        # Record initial performance
        initial_metrics = StrategicMetrics(coherence_score=6.0, feasibility_score=6.0)
        self.tracker.record_performance(
            self.sample_strategy,
            initial_metrics,
            generation=0,
            refinement_id="test_refinement"
        )
        
        # Record improved performance
        improved_metrics = StrategicMetrics(coherence_score=8.0, feasibility_score=8.0)
        metrics = self.tracker.record_performance(
            self.sample_strategy,
            improved_metrics,
            generation=1,
            refinement_id="test_refinement"
        )
        
        assert metrics.generation == 1
        assert metrics.improvement_score > 0  # Should show improvement
    
    def test_get_metrics_by_generation(self):
        """Test retrieving metrics by generation"""
        strategic_metrics = StrategicMetrics(coherence_score=8.0)
        
        # Record multiple generations
        for gen in range(3):
            self.tracker.record_performance(
                self.sample_strategy,
                strategic_metrics,
                generation=gen,
                refinement_id="test_refinement"
            )
        
        # Get specific generation
        gen1_metrics = self.tracker.get_metrics_by_generation("strategy_test", 1)
        assert len(gen1_metrics) >= 1
        assert all(m.generation == 1 for m in gen1_metrics)
    
    def test_get_performance_summary(self):
        """Test performance summary generation"""
        strategic_metrics = StrategicMetrics(coherence_score=8.0)
        
        # Record some performance data
        for gen in range(3):
            self.tracker.record_performance(
                self.sample_strategy,
                strategic_metrics,
                generation=gen,
                refinement_id="test_refinement"
            )
        
        summary = self.tracker.get_performance_summary("strategy_test")
        
        assert 'total_generations' in summary
        assert 'best_score' in summary
        assert 'average_score' in summary
        assert summary['total_generations'] >= 1


class TestFeedbackLoop:
    """Test feedback loop functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_refinement.db"
        self.tracker = PerformanceTracker(self.db_path)
        self.feedback_loop = FeedbackLoop(self.tracker)
        
        # Create sample metrics
        self.sample_metrics = RefinementMetrics(
            refinement_id="test_refinement",
            strategy_id="test_strategy",
            generation=1,
            strategic_metrics=StrategicMetrics(
                coherence_score=6.0,
                feasibility_score=7.0,
                domain_alignment_score=8.0,
                risk_management_score=5.5,
                resource_efficiency_score=6.5
            ),
            improvement_score=0.1,
            convergence_indicator=0.3,
            clm_compliance_score=0.7
        )
    
    @pytest.mark.asyncio
    async def test_analyze_performance_basic(self):
        """Test basic performance analysis"""
        # Mock historical data
        with patch.object(self.tracker, 'get_all_metrics', return_value=[self.sample_metrics]):
            analysis = await self.feedback_loop.analyze_performance(
                "test_strategy",
                self.sample_metrics
            )
        
        assert isinstance(analysis, FeedbackAnalysis)
        assert analysis.strategy_id == "test_strategy"
        assert analysis.current_metrics == self.sample_metrics
        assert len(analysis.strengths) > 0 or len(analysis.weaknesses) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_strengths_weaknesses(self):
        """Test strength and weakness identification"""
        analysis = FeedbackAnalysis(
            strategy_id="test_strategy",
            current_metrics=self.sample_metrics,
            historical_performance=[self.sample_metrics]
        )
        
        await self.feedback_loop._analyze_strengths_weaknesses(analysis)
        
        # Should identify domain alignment as strength (8.0)
        domain_strength = any("domain alignment" in s.lower() for s in analysis.strengths)
        assert domain_strength
        
        # Should identify risk management as weakness (5.5)
        risk_weakness = any("risk management" in w.lower() for w in analysis.weaknesses)
        assert risk_weakness
    
    @pytest.mark.asyncio
    async def test_generate_improvement_suggestions(self):
        """Test improvement suggestion generation"""
        analysis = FeedbackAnalysis(
            strategy_id="test_strategy",
            current_metrics=self.sample_metrics,
            historical_performance=[self.sample_metrics]
        )
        
        await self.feedback_loop._generate_improvement_suggestions(analysis)
        
        assert len(analysis.improvement_suggestions) > 0
        
        # Check suggestion structure
        suggestion = analysis.improvement_suggestions[0]
        assert isinstance(suggestion, ImprovementSuggestion)
        assert isinstance(suggestion.category, ImprovementCategory)
        assert 0.0 <= suggestion.priority <= 1.0
        assert 0.0 <= suggestion.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_refinement_recommendations(self):
        """Test refinement continuation recommendations"""
        # Test high convergence - should stop
        high_convergence_metrics = RefinementMetrics(
            refinement_id="test",
            strategy_id="test",
            generation=5,
            convergence_indicator=0.9,  # High convergence
            strategic_metrics=StrategicMetrics(coherence_score=9.0)
        )
        
        analysis = FeedbackAnalysis(
            strategy_id="test_strategy",
            current_metrics=high_convergence_metrics,
            historical_performance=[high_convergence_metrics]
        )
        
        await self.feedback_loop._determine_refinement_recommendations(analysis)
        
        assert not analysis.should_continue_refinement
        assert analysis.refinement_priority < 0.5


class TestStrategyImprover:
    """Test strategy improvement functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.improver = StrategyImprover()
        self.sample_strategy = self._create_sample_strategy()
        self.sample_analysis = self._create_sample_analysis()
    
    def _create_sample_strategy(self) -> StrategyChain:
        """Create sample strategy"""
        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[
                StrategyStep(
                    action="Test Action",
                    prerequisites=["Test Prerequisite"],
                    outcome="Test Outcome",
                    risks=["Test Risk"],
                    confidence=0.8
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="3 months",
            resource_requirements=["Test Resource"]
        )
        
        return StrategyChain(
            strategy=strategy,
            source_sample=1,
            temperature=0.8
        )
    
    def _create_sample_analysis(self) -> FeedbackAnalysis:
        """Create sample feedback analysis"""
        suggestion = ImprovementSuggestion(
            category=ImprovementCategory.COHERENCE,
            priority=0.8,
            description="Improve step coherence",
            specific_changes=["Add more prerequisites", "Clarify outcomes"],
            expected_impact=0.6,
            implementation_effort=0.4,
            confidence=0.7
        )
        
        metrics = RefinementMetrics(
            refinement_id="test",
            strategy_id="test",
            generation=1,
            strategic_metrics=StrategicMetrics(coherence_score=6.0)
        )
        
        return FeedbackAnalysis(
            strategy_id="test_strategy",
            current_metrics=metrics,
            historical_performance=[metrics],
            improvement_suggestions=[suggestion]
        )
    
    @pytest.mark.asyncio
    async def test_improve_strategy_rules(self):
        """Test rule-based strategy improvement"""
        improved_strategy = await self.improver._generate_improved_strategy_rules(
            self.sample_strategy,
            self.sample_analysis.improvement_suggestions
        )
        
        assert isinstance(improved_strategy, StrategyChain)
        assert "Refined" in improved_strategy.strategy.title
        assert len(improved_strategy.strategy.steps) > 0
    
    def test_build_improvement_context(self):
        """Test improvement context building"""
        context = self.improver._build_improvement_context(
            self.sample_strategy,
            self.sample_analysis,
            self.sample_analysis.improvement_suggestions
        )
        
        assert 'original_strategy' in context
        assert 'performance_analysis' in context
        assert 'improvement_suggestions' in context
        
        assert context['original_strategy']['title'] == "Test Strategy"
        assert len(context['improvement_suggestions']) > 0


class TestRecursiveRefinementEngine:
    """Test recursive refinement engine"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create configuration
        self.config = RefinementConfiguration(
            max_generations=3,
            convergence_threshold=0.9,
            improvement_threshold=0.01,
            quality_target=9.0,
            max_refinement_time_minutes=10,
            output_directory=Path(self.temp_dir)
        )
        
        # Create engine
        self.engine = RecursiveRefinementEngine(self.config)
        self.sample_strategy = self._create_sample_strategy()
    
    def _create_sample_strategy(self) -> StrategyChain:
        """Create sample strategy"""
        strategy = GenesisStrategy(
            title="Test Strategy for Refinement",
            steps=[
                StrategyStep(
                    action="Initial Analysis",
                    prerequisites=["Data available"],
                    outcome="Analysis complete",
                    risks=["Data quality issues"],
                    confidence=0.7
                ),
                StrategyStep(
                    action="Implementation Planning",
                    prerequisites=["Analysis complete"],
                    outcome="Plan ready",
                    risks=["Resource constraints"],
                    confidence=0.8
                )
            ],
            alignment_score={"strategic": 4.0, "operational": 3.5},
            estimated_timeline="4 months",
            resource_requirements=["Analysis team", "Planning resources"]
        )
        
        return StrategyChain(
            strategy=strategy,
            source_sample=1,
            temperature=0.8
        )
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.config == self.config
        assert isinstance(self.engine.performance_tracker, PerformanceTracker)
        assert isinstance(self.engine.feedback_loop, FeedbackLoop)
        assert isinstance(self.engine.strategy_improver, StrategyImprover)
        assert len(self.engine.active_sessions) == 0
    
    @pytest.mark.asyncio
    async def test_evaluate_strategy_mock(self):
        """Test strategy evaluation with mocks"""
        # Mock the simulator
        mock_simulator = MagicMock()
        mock_simulator.run_simulation = AsyncMock(return_value={
            'trunk': self.sample_strategy,
            'twigs': [],
            'metadata': {'selection_method': 'tournament'},
            'summary': 'Test evaluation'
        })
        
        with patch('polyhegel.refinement.recursive.PolyhegelSimulator', return_value=mock_simulator):
            metrics = await self.engine._evaluate_strategy(
                self.sample_strategy,
                "Test system prompt",
                "Test user prompt"
            )
        
        assert isinstance(metrics, StrategicMetrics)
    
    @pytest.mark.asyncio
    async def test_refine_strategy_mock(self):
        """Test complete strategy refinement with mocks"""
        # Mock all external dependencies
        mock_simulator = MagicMock()
        mock_simulator.run_simulation = AsyncMock(return_value={
            'trunk': self.sample_strategy,
            'twigs': [],
            'metadata': {'selection_method': 'tournament'},
            'summary': 'Test evaluation'
        })
        
        # Mock strategy improvement to return improved strategy
        improved_strategy = StrategyChain(
            strategy=GenesisStrategy(
                title="Improved Test Strategy",
                steps=self.sample_strategy.strategy.steps,
                alignment_score=self.sample_strategy.strategy.alignment_score,
                estimated_timeline=self.sample_strategy.strategy.estimated_timeline,
                resource_requirements=self.sample_strategy.strategy.resource_requirements
            ),
            source_sample=1,
            temperature=0.8
        )
        
        with patch('polyhegel.refinement.recursive.PolyhegelSimulator', return_value=mock_simulator):
            with patch.object(self.engine.strategy_improver, 'improve_strategy', return_value=improved_strategy):
                session = await self.engine.refine_strategy(
                    self.sample_strategy,
                    "Test system prompt",
                    "Test user prompt"
                )
        
        assert session.is_complete
        assert len(session.generations) > 0
        assert len(session.performance_history) > 0
        assert session.best_strategy is not None
    
    def test_get_session_status(self):
        """Test session status retrieval"""
        # Test non-existent session
        status = self.engine.get_session_status("non_existent")
        assert status is None
        
        # Test would need active session to test properly
        # This is covered in integration tests
    
    def test_get_global_statistics(self):
        """Test global statistics"""
        stats = self.engine.get_global_statistics()
        
        assert 'total_strategies_refined' in stats
        assert 'total_refinement_time' in stats
        assert 'active_sessions' in stats
        assert 'completed_sessions' in stats
        assert stats['total_strategies_refined'] == 0  # Initially


class TestRefinementConfiguration:
    """Test refinement configuration"""
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = RefinementConfiguration()
        
        assert config.max_generations == 10
        assert config.convergence_threshold == 0.8
        assert config.improvement_threshold == 0.05
        assert config.quality_target == 8.5
        assert config.strategic_compliance_target == 0.8
        assert config.require_strategic_compliance == True
    
    def test_custom_configuration(self):
        """Test custom configuration"""
        config = RefinementConfiguration(
            max_generations=5,
            quality_target=9.0,
            model_name="test-model"
        )
        
        assert config.max_generations == 5
        assert config.quality_target == 9.0
        assert config.model_name == "test-model"


class TestRefinementMetrics:
    """Test refinement metrics"""
    
    def test_metrics_creation(self):
        """Test metrics creation and serialization"""
        strategic_metrics = StrategicMetrics(coherence_score=8.0)
        
        metrics = RefinementMetrics(
            refinement_id="test_refinement",
            strategy_id="test_strategy",
            generation=1,
            strategic_metrics=strategic_metrics,
            improvement_score=0.2
        )
        
        assert metrics.refinement_id == "test_refinement"
        assert metrics.strategy_id == "test_strategy"
        assert metrics.generation == 1
        assert metrics.improvement_score == 0.2
    
    def test_metrics_serialization(self):
        """Test metrics to/from dict conversion"""
        strategic_metrics = StrategicMetrics(coherence_score=8.0)
        
        metrics = RefinementMetrics(
            refinement_id="test_refinement",
            strategy_id="test_strategy",
            generation=1,
            strategic_metrics=strategic_metrics
        )
        
        # Test to_dict
        data = metrics.to_dict()
        assert 'refinement_id' in data
        assert 'timestamp' in data
        assert 'strategic_metrics' in data
        
        # Test from_dict
        restored_metrics = RefinementMetrics.from_dict(data)
        assert restored_metrics.refinement_id == metrics.refinement_id
        assert restored_metrics.strategy_id == metrics.strategy_id


@pytest.mark.asyncio
async def test_integration_refinement_workflow():
    """Integration test for complete refinement workflow"""
    temp_dir = tempfile.mkdtemp()
    
    # Create configuration
    config = RefinementConfiguration(
        max_generations=2,  # Keep small for testing
        output_directory=Path(temp_dir)
    )
    
    # Create engine
    engine = RecursiveRefinementEngine(config)
    
    # Create test strategy
    strategy = GenesisStrategy(
        title="Integration Test Strategy",
        steps=[
            StrategyStep(
                action="Test Step",
                prerequisites=["Test Prerequisite"],
                outcome="Test Outcome",
                risks=["Test Risk"],
                confidence=0.8
            )
        ],
        alignment_score={"test": 4.0},
        estimated_timeline="2 months",
        resource_requirements=["Test Resource"]
    )
    
    strategy_chain = StrategyChain(
        strategy=strategy,
        source_sample=1,
        temperature=0.8
    )
    
    # Mock external dependencies
    mock_simulator = MagicMock()
    mock_simulator.run_simulation = AsyncMock(return_value={
        'trunk': strategy_chain,
        'twigs': [],
        'metadata': {'selection_method': 'tournament'},
        'summary': 'Integration test evaluation'
    })
    
    with patch('polyhegel.refinement.recursive.PolyhegelSimulator', return_value=mock_simulator):
        # Run refinement
        session = await engine.refine_strategy(
            strategy_chain,
            "Integration test system prompt",
            "Integration test user prompt"
        )
    
    # Verify results
    assert session.is_complete
    assert session.session_id is not None
    assert len(session.generations) >= 1
    assert session.best_strategy is not None
    
    # Verify files were created
    output_dir = Path(temp_dir)
    session_files = list(output_dir.glob(f"{session.session_id}_*.json"))
    assert len(session_files) > 0
    
    # Verify session report
    report_file = output_dir / f"{session.session_id}_report.md"
    assert report_file.exists()
    
    with open(report_file) as f:
        report_content = f.read()
    
    assert "Recursive Refinement Report" in report_content
    assert session.session_id in report_content


if __name__ == "__main__":
    pytest.main([__file__])