"""
Tests for StrategyEvaluator functionality
"""

import pytest
from polyhegel.strategy_evaluator import StrategyEvaluator
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep
from polyhegel.model_manager import ModelManager


class TestStrategyEvaluator:
    """Test strategy evaluation functionality"""

    def test_evaluator_initialization(self):
        """Test that StrategyEvaluator initializes properly"""
        model_manager = ModelManager()
        model = model_manager.get_model("claude-3-haiku-20240307")

        evaluator = StrategyEvaluator(model)

        assert evaluator.model is not None
        assert evaluator.agent is not None
        assert evaluator.comparison_template is not None
        assert "Strategic Situation:" in evaluator.comparison_template

    def test_evaluator_with_custom_prompt(self):
        """Test StrategyEvaluator with custom system prompt"""
        model_manager = ModelManager()
        model = model_manager.get_model("claude-3-haiku-20240307")
        custom_prompt = "You are a test evaluator."

        evaluator = StrategyEvaluator(model, system_prompt=custom_prompt)

        assert custom_prompt in evaluator.system_prompt

    def test_format_strategy_for_comparison(self):
        """Test strategy formatting for comparison"""
        model_manager = ModelManager()
        model = model_manager.get_model("claude-3-haiku-20240307")
        evaluator = StrategyEvaluator(model)

        # Create test strategy
        steps = [
            StrategyStep(
                action="Test Action",
                prerequisites=["Prerequisite 1", "Prerequisite 2"],
                outcome="Expected outcome",
                risks=["Risk 1", "Risk 2"],
            )
        ]

        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=steps,
            alignment_score={"domain1": 8.5, "domain2": 7.0},
            estimated_timeline="2 weeks",
            resource_requirements=["Resource 1", "Resource 2"],
        )

        chain = StrategyChain(strategy=strategy, source_sample=1, temperature=0.8)

        formatted = evaluator._format_strategy_for_comparison(chain)

        assert "Test Strategy" in formatted
        assert "Test Action" in formatted
        assert "Expected outcome" in formatted
        assert "2 weeks" in formatted
        assert "Resource 1" in formatted

    def test_parse_preference_explicit(self):
        """Test parsing explicit preference statements"""
        model_manager = ModelManager()
        model = model_manager.get_model("claude-3-haiku-20240307")
        evaluator = StrategyEvaluator(model)

        # Test explicit preference
        text1 = "After analysis... Preferred Strategy Index: 1"
        assert evaluator._parse_preference(text1) == 1

        text2 = "Based on evaluation... Preferred Strategy Index: 2"
        assert evaluator._parse_preference(text2) == 2

    def test_parse_preference_fallback(self):
        """Test parsing preference with fallback logic"""
        model_manager = ModelManager()
        model = model_manager.get_model("claude-3-haiku-20240307")
        evaluator = StrategyEvaluator(model)

        # Test fallback logic
        text = "Strategy 1 is better. Strategy 1 has advantages. Strategy 2 is okay."
        assert evaluator._parse_preference(text) == 1

        text2 = "Strategy 2 is superior. Strategy 2 works well."
        assert evaluator._parse_preference(text2) == 2

    @pytest.mark.asyncio
    async def test_compare_strategies_mock(self):
        """Test strategy comparison with mocked LLM response"""
        # Skip if no API key available
        try:
            model_manager = ModelManager()
            model = model_manager.get_model("claude-3-haiku-20240307")
            evaluator = StrategyEvaluator(model)

            # Create two test strategies
            strategy1 = self._create_test_strategy("Strategy 1", "Action 1")
            strategy2 = self._create_test_strategy("Strategy 2", "Action 2")

            # This will only work if API key is available
            result = await evaluator.compare_strategies(strategy1, strategy2, "Test context")

            assert "preferred_strategy" in result
            assert "preferred_chain" in result
            assert "evaluation_text" in result
            assert result["preferred_strategy"] in [1, 2]

        except Exception as e:
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip(f"Skipping API test due to: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_evaluate_strategy_mock(self):
        """Test single strategy evaluation with mocked response"""
        try:
            model_manager = ModelManager()
            model = model_manager.get_model("claude-3-haiku-20240307")
            evaluator = StrategyEvaluator(model)

            strategy = self._create_test_strategy("Test Strategy", "Test Action")

            result = await evaluator.evaluate_strategy(strategy, "Test context")

            assert "strategy" in result
            assert "evaluation_text" in result
            assert "strategy_formatted" in result
            assert result["strategy"] == strategy

        except Exception as e:
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip(f"Skipping API test due to: {e}")
            else:
                raise

    def _create_test_strategy(self, title: str, action: str) -> StrategyChain:
        """Helper to create test strategy"""
        steps = [
            StrategyStep(
                action=action, prerequisites=["Test prerequisite"], outcome="Test outcome", risks=["Test risk"]
            )
        ]

        strategy = GenesisStrategy(
            title=title,
            steps=steps,
            alignment_score={"test_domain": 8.0},
            estimated_timeline="1 week",
            resource_requirements=["Test resource"],
        )

        return StrategyChain(strategy=strategy, source_sample=1, temperature=0.8)


if __name__ == "__main__":
    pytest.main([__file__])
