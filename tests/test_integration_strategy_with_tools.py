"""
Integration tests for strategy generation using web and git tools

Tests verify that StrategyGenerator and other agents can successfully use
both web and git tools during strategy generation workflows.
"""

import pytest
from unittest.mock import patch
from pydantic_ai.models.test import TestModel

from polyhegel.strategy_generator import StrategyGenerator
from polyhegel.strategy_evaluator import StrategyEvaluator
from polyhegel.web_tools import WEB_SEARCH_TOOL, WEB_FETCH_TOOL
from polyhegel.git_tools import GIT_REPO_TOOL, LOCAL_REPO_TOOL
from polyhegel.models import GenesisStrategy


class TestStrategyGenerationWithTools:
    """Integration tests for strategy generation using web and git tools"""

    @pytest.fixture
    def mock_model(self):
        """Create a test model for strategy generation"""
        # Configure with mock strategy response using custom_output_args for structured output
        from polyhegel.models import StrategyStep

        mock_strategy = GenesisStrategy(
            title="Cloud Migration Strategy",
            steps=[
                StrategyStep(
                    action="Research cloud migration best practices",
                    prerequisites=["Current infrastructure assessment"],
                    outcome="Comprehensive migration plan",
                    risks=["Downtime during migration"],
                    confidence=0.8,
                )
            ],
            alignment_score={"resource_acquisition": 4.0},
            estimated_timeline="6 months",
            resource_requirements=["Cloud architecture team", "Migration tools"],
        )
        return TestModel(custom_output_args=mock_strategy)

    @pytest.fixture
    def enhanced_strategy_generator(self, mock_model):
        """Create strategy generator with tools enabled"""
        generator = StrategyGenerator(mock_model)
        # Re-enable tools for integration testing
        from pydantic_ai import Agent

        generator.agent = Agent(
            model=mock_model,
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL, GIT_REPO_TOOL, LOCAL_REPO_TOOL],
            output_type=GenesisStrategy,
        )
        return generator

    @pytest.fixture
    def enhanced_strategy_evaluator(self, mock_model):
        """Create strategy evaluator with tools enabled"""
        from polyhegel.models import StrategyAnalysisResponse

        # Create a mock analysis response for the analysis agent
        mock_analysis = StrategyAnalysisResponse(
            overall_score=8.5,
            coherence_score=8.0,
            feasibility_score=7.5,
            risk_management_score=8.2,
            strategic_alignment_score=9.0,
            strengths=["Well-structured approach", "Clear objectives"],
            weaknesses=["Resource intensive"],
            recommendations=["Consider phased implementation"],
        )

        analysis_model = TestModel(custom_output_args=mock_analysis)
        evaluator = StrategyEvaluator(analysis_model)

        # Re-enable tools for integration testing
        from pydantic_ai import Agent

        from polyhegel.models import StrategyEvaluationResponse

        # Create mock evaluation response for comparison agent
        mock_evaluation = StrategyEvaluationResponse(
            preferred_strategy_index=1,
            confidence_score=0.85,
            reasoning="Strategy 1 demonstrates superior risk management and resource allocation",
            coherence_comparison={"strategy1": 8.5, "strategy2": 7.2},
            feasibility_comparison={"strategy1": 8.0, "strategy2": 6.8},
            risk_management_comparison={"strategy1": 9.0, "strategy2": 7.5},
        )

        comparison_model = TestModel(custom_output_args=mock_evaluation)

        evaluator.comparison_agent = Agent(
            model=comparison_model,
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL, GIT_REPO_TOOL, LOCAL_REPO_TOOL],
            output_type=StrategyEvaluationResponse,
        )

        evaluator.analysis_agent = Agent(
            model=analysis_model,
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL, GIT_REPO_TOOL, LOCAL_REPO_TOOL],
            output_type=StrategyAnalysisResponse,
        )
        return evaluator

    @pytest.mark.asyncio
    async def test_strategy_generation_with_web_research(self, enhanced_strategy_generator):
        """Test strategy generation with web research tools"""
        search_results = "Cloud migration best practices: 6R framework, AWS Well-Architected Framework, phased approach"
        detailed_guide = (
            "AWS Cloud Migration Framework - comprehensive guide with assessment, mobilization, and migration phases"
        )

        with (
            patch.object(WEB_SEARCH_TOOL.function, "__call__", return_value=search_results),
            patch.object(WEB_FETCH_TOOL.function, "__call__", return_value=detailed_guide),
        ):
            # Generate strategy with tools (TestModel will return our mock JSON)
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Generate a cloud migration strategy. Research current best practices first.",
            )

            assert len(chains) == 1
            strategy = chains[0].strategy
            assert "cloud migration" in strategy.title.lower()
            assert len(strategy.steps) >= 1
            assert any("research" in step.action.lower() for step in strategy.steps)

    @pytest.mark.asyncio
    async def test_strategy_generation_with_codebase_analysis(self, enhanced_strategy_generator):
        """Test strategy generation with git/codebase analysis"""
        repo_analysis = """
# Codebase Analysis Report
## Technology Stack
- Python 3.11
- FastAPI framework
- PostgreSQL database
- Redis cache

## Architecture
- Microservices pattern
- REST APIs
- Event-driven components
"""

        with patch.object(GIT_REPO_TOOL.function, "__call__", return_value=repo_analysis):
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)], user_prompt="Analyze codebase and generate modernization strategy"
            )

            assert len(chains) == 1
            strategy = chains[0].strategy
            assert strategy.title
            assert len(strategy.steps) >= 1

    @pytest.mark.asyncio
    async def test_strategy_evaluation_with_research(self, enhanced_strategy_evaluator):
        """Test strategy evaluation enhanced with research tools"""
        from polyhegel.models import StrategyChain

        mock_strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[],
            alignment_score={"test": 4.0},
            estimated_timeline="1 month",
            resource_requirements=["Test resources"],
        )

        mock_chain = StrategyChain(
            strategy=mock_strategy,
            source_sample=1,
            temperature=0.7,
            technique_name="Test Technique",
            technique_domain="test_domain",
        )

        comparison_details = "Industry benchmarks show similar strategies achieve 85% success rate"

        with patch.object(WEB_FETCH_TOOL.function, "__call__", return_value=comparison_details):
            evaluation = await enhanced_strategy_evaluator.evaluate_strategy(
                mock_chain, context="Test evaluation with research tools"
            )

            assert evaluation
            assert len(evaluation) > 0

    @pytest.mark.asyncio
    async def test_end_to_end_strategy_workflow_with_tools(
        self, enhanced_strategy_generator, enhanced_strategy_evaluator
    ):
        """Test complete strategy workflow with tools"""
        search_results = (
            "AI implementation best practices focus on data quality, model governance, and ethical considerations"
        )

        with patch.object(WEB_SEARCH_TOOL.function, "__call__", return_value=search_results):
            # Step 1: Generate strategy with research
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)], user_prompt="Create AI implementation strategy with research"
            )

            assert len(chains) == 1
            strategy = chains[0].strategy
            assert strategy.title
            assert len(strategy.steps) >= 1

    @pytest.mark.asyncio
    async def test_technique_guidance_with_web_tools(self, enhanced_strategy_generator):
        """Test technique-guided generation with web research"""
        technique_research = "Stakeholder Alignment Matrix involves mapping stakeholder interests to resource needs"

        with patch.object(WEB_SEARCH_TOOL.function, "__call__", return_value=technique_research):
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Use stakeholder alignment techniques for partnership strategy",
            )

            assert len(chains) == 1
            strategy = chains[0].strategy
            assert strategy.title
            assert len(strategy.steps) >= 1

    @pytest.mark.asyncio
    async def test_tools_error_resilience_in_workflows(self, enhanced_strategy_generator):
        """Test that strategy generation continues even when tools fail"""

        # Simulate tool failure
        with patch.object(WEB_SEARCH_TOOL.function, "__call__", side_effect=Exception("Network error")):
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)], user_prompt="Generate strategy despite tool failure"
            )

            # Should still generate strategy using model alone
            assert len(chains) == 1
            strategy = chains[0].strategy
            assert strategy.title
            assert len(strategy.steps) >= 1
