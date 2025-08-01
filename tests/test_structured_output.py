"""
Tests for structured output validation with pydantic-ai
"""

import pytest
from unittest.mock import Mock, AsyncMock

from polyhegel.models import (
    StrategyEvaluationResponse,
    StrategyAnalysisResponse,
    GenesisStrategy,
    StrategyStep,
    StrategyChain,
)
from polyhegel.strategy_evaluator import StrategyEvaluator


class TestStructuredOutput:
    """Test structured output models and integration"""

    def test_strategy_evaluation_response_validation(self):
        """Test StrategyEvaluationResponse model validation"""

        # Valid response
        response = StrategyEvaluationResponse(
            preferred_strategy_index=1,
            confidence_score=0.8,
            reasoning="Strategy 1 has better coherence and risk management",
            coherence_comparison={"strategy1": 8.5, "strategy2": 6.2},
            feasibility_comparison={"strategy1": 7.8, "strategy2": 7.0},
            risk_management_comparison={"strategy1": 9.0, "strategy2": 5.5},
        )

        assert response.preferred_strategy_index == 1
        assert response.confidence_score == 0.8
        assert "coherence" in response.reasoning.lower()
        assert response.coherence_comparison["strategy1"] > response.coherence_comparison["strategy2"]

    def test_strategy_evaluation_response_validation_errors(self):
        """Test validation errors for invalid data"""

        # Invalid strategy index
        with pytest.raises(ValueError):
            StrategyEvaluationResponse(
                preferred_strategy_index=3, confidence_score=0.8, reasoning="Test reasoning"  # Should be 1 or 2
            )

        # Invalid confidence score
        with pytest.raises(ValueError):
            StrategyEvaluationResponse(
                preferred_strategy_index=1, confidence_score=1.5, reasoning="Test reasoning"  # Should be 0.0-1.0
            )

        # Reasoning too short
        with pytest.raises(ValueError):
            StrategyEvaluationResponse(
                preferred_strategy_index=1, confidence_score=0.8, reasoning="Too short"  # Less than 10 chars
            )

    def test_strategy_analysis_response_validation(self):
        """Test StrategyAnalysisResponse model validation"""

        # Valid response
        response = StrategyAnalysisResponse(
            overall_score=8.5,
            coherence_score=8.0,
            feasibility_score=7.5,
            risk_management_score=9.0,
            strategic_alignment_score=8.2,
            strengths=["Clear step progression", "Comprehensive risk analysis"],
            weaknesses=["Resource requirements unclear"],
            recommendations=["Define resource allocation timeline"],
        )

        assert 1.0 <= response.overall_score <= 10.0
        assert len(response.strengths) >= 1
        assert len(response.strengths) <= 5
        assert len(response.recommendations) <= 3

    def test_strategy_analysis_response_validation_errors(self):
        """Test validation errors for analysis response"""

        # Invalid score range
        with pytest.raises(ValueError):
            StrategyAnalysisResponse(
                overall_score=11.0,  # Should be 1-10
                coherence_score=8.0,
                feasibility_score=7.5,
                risk_management_score=9.0,
                strategic_alignment_score=8.2,
                strengths=["Test strength"],
            )

        # No strengths provided
        with pytest.raises(ValueError):
            StrategyAnalysisResponse(
                overall_score=8.0,
                coherence_score=8.0,
                feasibility_score=7.5,
                risk_management_score=9.0,
                strategic_alignment_score=8.2,
                strengths=[],  # Should have at least 1
            )

    @pytest.mark.asyncio
    async def test_strategy_evaluator_structured_output_integration(self):
        """Test that StrategyEvaluator correctly uses structured output"""

        # Create test model
        mock_model = "test"

        # Create test strategies
        strategy1 = StrategyChain(
            strategy=GenesisStrategy(
                title="Test Strategy 1",
                steps=[
                    StrategyStep(
                        action="Test action", prerequisites=["Test prereq"], outcome="Test outcome", risks=["Test risk"]
                    )
                ],
                alignment_score={"strategic": 8.0},
                estimated_timeline="2 months",
                resource_requirements=["Test resource"],
            ),
            source_sample=1,
            temperature=0.7,
        )

        strategy2 = StrategyChain(
            strategy=GenesisStrategy(
                title="Test Strategy 2",
                steps=[
                    StrategyStep(
                        action="Test action 2",
                        prerequisites=["Test prereq 2"],
                        outcome="Test outcome 2",
                        risks=["Test risk 2"],
                    )
                ],
                alignment_score={"strategic": 7.0},
                estimated_timeline="3 months",
                resource_requirements=["Test resource 2"],
            ),
            source_sample=2,
            temperature=0.7,
        )

        # Create evaluator
        evaluator = StrategyEvaluator(mock_model)

        # Mock the agent response for testing
        mock_evaluation = StrategyEvaluationResponse(
            preferred_strategy_index=1,
            confidence_score=0.85,
            reasoning="Strategy 1 has better coherence and clearer timeline",
            coherence_comparison={"strategy1": 8.5, "strategy2": 6.8},
            feasibility_comparison={"strategy1": 8.0, "strategy2": 7.2},
            risk_management_comparison={"strategy1": 7.5, "strategy2": 6.9},
        )

        mock_result = Mock()
        mock_result.output = mock_evaluation
        evaluator.comparison_agent.run = AsyncMock(return_value=mock_result)

        # Test comparison
        result = await evaluator.compare_strategies(strategy1, strategy2, "Test context")

        # Verify structured output is properly extracted
        assert result["preferred_strategy"] == 1
        assert result["confidence_score"] == 0.85
        assert result["reasoning"] == "Strategy 1 has better coherence and clearer timeline"
        assert result["coherence_scores"]["strategy1"] == 8.5
        assert result["feasibility_scores"]["strategy1"] == 8.0
        assert result["risk_scores"]["strategy1"] == 7.5

        # Verify backward compatibility
        assert "evaluation_text" in result
        assert result["preferred_chain"] == strategy1


if __name__ == "__main__":
    pytest.main([__file__])
