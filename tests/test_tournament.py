"""
Tests for strategic tournament system
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from polyhegel.tournament import StrategyTournament, TournamentRunner
from polyhegel.strategy_evaluator import StrategyEvaluator
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep


class TestStrategyTournament:
    """Test strategic tournament functionality"""

    def setup_method(self):
        """Set up test environment"""
        # Create mock evaluator
        self.mock_evaluator = AsyncMock(spec=StrategyEvaluator)
        self.tournament = StrategyTournament(self.mock_evaluator)
        
        # Create test strategies
        self.strategies = self._create_test_strategies()

    def _create_test_strategies(self):
        """Create test strategies for tournaments"""
        strategies = []
        
        for i in range(3):
            strategy = GenesisStrategy(
                title=f"Test Strategy {i+1}",
                steps=[
                    StrategyStep(
                        action=f"Action {i+1}",
                        prerequisites=[f"Prerequisite {i+1}"],
                        outcome=f"Outcome {i+1}",
                        risks=[f"Risk {i+1}"],
                        confidence=0.8
                    )
                ],
                alignment_score={"test": 4.0 + i * 0.5},
                estimated_timeline=f"{i+1} months",
                resource_requirements=[f"Resource {i+1}"]
            )
            
            chain = StrategyChain(
                strategy=strategy,
                source_sample=i,
                temperature=0.7
            )
            strategies.append(chain)
        
        return strategies

    @pytest.mark.asyncio
    async def test_tournament_initialization(self):
        """Test tournament initialization"""
        assert self.tournament.evaluator == self.mock_evaluator
        assert self.tournament.results == {}

    @pytest.mark.asyncio
    async def test_basic_elimination_tournament(self):
        """Test basic elimination tournament"""
        # Mock evaluator responses
        self.mock_evaluator.compare_strategies.side_effect = [
            {"preferred_strategy": 1, "evaluation_text": "Strategy 1 is better"},
            {"preferred_strategy": 2, "evaluation_text": "Strategy 3 is better"}
        ]
        
        winner, results = await self.tournament.run_tournament(
            self.strategies,
            "Test context",
            num_comparisons=1,
            save_results=False
        )
        
        # Should return a winning strategy
        assert winner is not None
        assert isinstance(winner, StrategyChain)
        
        # Results should have proper structure
        assert "strategies" in results
        assert "comparisons" in results
        assert "winner" in results
        assert "context" in results
        
        # Should have made the right number of comparisons
        assert len(results["comparisons"]) == 2  # 3 strategies = 2 comparisons

    @pytest.mark.asyncio
    async def test_tournament_with_voting(self):
        """Test tournament with multiple comparisons for voting"""
        # Mock multiple comparison results
        self.mock_evaluator.compare_strategies.side_effect = [
            {"preferred_strategy": 1, "evaluation_text": "Round 1: Strategy 1"},
            {"preferred_strategy": 1, "evaluation_text": "Round 2: Strategy 1"},
            {"preferred_strategy": 2, "evaluation_text": "Round 1: Strategy 3"},
            {"preferred_strategy": 2, "evaluation_text": "Round 2: Strategy 3"}
        ]
        
        winner, results = await self.tournament.run_tournament(
            self.strategies,
            "Test context",
            num_comparisons=2,  # 2 comparisons per pair
            save_results=False
        )
        
        # Should have voting results
        assert "voting_results" in results
        assert len(results["comparisons"]) == 4  # 2 pairs × 2 comparisons each

    @pytest.mark.asyncio
    async def test_round_robin_tournament(self):
        """Test round-robin tournament"""
        # Mock all pairwise comparisons (3 strategies = 3 pairs)
        self.mock_evaluator.compare_strategies.side_effect = [
            {"preferred_strategy": 1, "evaluation_text": "1 vs 2: Strategy 1"},
            {"preferred_strategy": 1, "evaluation_text": "1 vs 3: Strategy 1"}, 
            {"preferred_strategy": 2, "evaluation_text": "2 vs 3: Strategy 3"}
        ]
        
        results = await self.tournament.run_round_robin_tournament(
            self.strategies,
            "Test context",
            num_comparisons=1
        )
        
        # Should have proper round-robin structure
        assert results["tournament_type"] == "round_robin"
        assert "rankings" in results
        assert "head_to_head" in results
        assert "winner" in results
        
        # Should have rankings for all strategies
        assert len(results["rankings"]) == 3
        
        # Rankings should be sorted by wins
        rankings = results["rankings"]
        for i in range(len(rankings) - 1):
            assert rankings[i]["wins"] >= rankings[i + 1]["wins"]

    @pytest.mark.asyncio
    async def test_tournament_error_handling(self):
        """Test tournament handles comparison errors gracefully"""
        # Mock evaluator to raise an exception
        self.mock_evaluator.compare_strategies.side_effect = Exception("Comparison failed")
        
        winner, results = await self.tournament.run_tournament(
            self.strategies,
            "Test context",
            num_comparisons=1,
            save_results=False
        )
        
        # Should still return a winner (defaults to first strategy)
        assert winner is not None
        
        # Comparisons should contain error information
        assert len(results["comparisons"]) > 0
        for comparison in results["comparisons"]:
            assert "error" in comparison

    @pytest.mark.asyncio
    async def test_insufficient_strategies_error(self):
        """Test error handling for insufficient strategies"""
        with pytest.raises(ValueError, match="Tournament requires at least 2 strategies"):
            await self.tournament.run_tournament(
                [self.strategies[0]],  # Only one strategy
                "Test context"
            )

    def test_vote_aggregation(self):
        """Test vote aggregation logic"""
        # Test clear winner
        comparison_results = [
            {"preferred_strategy": 1},
            {"preferred_strategy": 1},
            {"preferred_strategy": 2}
        ]
        
        voting_result = self.tournament._aggregate_votes(comparison_results)
        assert voting_result["winner"] == 1
        assert voting_result["votes_strategy1"] == 2
        assert voting_result["votes_strategy2"] == 1
        
        # Test tie (should default to strategy 1)
        tie_results = [
            {"preferred_strategy": 1},
            {"preferred_strategy": 2}
        ]
        
        tie_voting = self.tournament._aggregate_votes(tie_results)
        assert tie_voting["winner"] == 1

    def test_serialization(self):
        """Test results serialization"""
        test_obj = {
            "strategy": self.strategies[0],
            "nested": {"value": 42},
            "list": [1, 2, 3]
        }
        
        serialized = self.tournament._make_serializable(test_obj)
        
        # Should be JSON-serializable
        import json
        json_str = json.dumps(serialized)
        assert isinstance(json_str, str)


class TestTournamentRunner:
    """Test high-level tournament runner"""

    def setup_method(self):
        """Set up test environment"""
        self.mock_evaluator = AsyncMock(spec=StrategyEvaluator)
        self.runner = TournamentRunner(self.mock_evaluator)
        self.strategies = self._create_test_strategies()

    def _create_test_strategies(self):
        """Create test strategies"""
        strategies = []
        for i in range(3):
            strategy = GenesisStrategy(
                title=f"Strategy {i+1}",
                steps=[StrategyStep(
                    action=f"Action {i+1}",
                    prerequisites=[],
                    outcome=f"Outcome {i+1}",
                    risks=[],
                    confidence=0.8
                )],
                alignment_score={"test": 4.0},
                estimated_timeline="1 month",
                resource_requirements=[]
            )
            
            chain = StrategyChain(
                strategy=strategy,
                source_sample=i,
                temperature=0.7
            )
            strategies.append(chain)
        
        return strategies

    @pytest.mark.asyncio
    async def test_find_best_strategy_elimination(self):
        """Test finding best strategy with elimination tournament"""
        self.mock_evaluator.compare_strategies.return_value = {
            "preferred_strategy": 1,
            "evaluation_text": "Strategy 1 is better"
        }
        
        winner, results = await self.runner.find_best_strategy(
            self.strategies,
            "Test context",
            tournament_type="elimination"
        )
        
        assert winner is not None
        assert isinstance(winner, StrategyChain)
        assert "winner" in results

    @pytest.mark.asyncio
    async def test_find_best_strategy_round_robin(self):
        """Test finding best strategy with round-robin tournament"""
        self.mock_evaluator.compare_strategies.return_value = {
            "preferred_strategy": 1,
            "evaluation_text": "Strategy 1 is better"
        }
        
        winner, results = await self.runner.find_best_strategy(
            self.strategies,
            "Test context",
            tournament_type="round_robin"
        )
        
        assert winner is not None
        assert results["tournament_type"] == "round_robin"

    @pytest.mark.asyncio
    async def test_invalid_tournament_type(self):
        """Test error handling for invalid tournament type"""
        with pytest.raises(ValueError, match="Unknown tournament type"):
            await self.runner.find_best_strategy(
                self.strategies,
                "Test context",
                tournament_type="invalid_type"
            )

    @pytest.mark.asyncio
    async def test_compare_technique_strategies(self):
        """Test technique-specific tournament"""
        # Create strategies with technique metadata
        technique_strategies = []
        for i, mandate in enumerate(["2.1", "2.2", "2.1"]):  # Two 2.1, one 2.2
            strategy = GenesisStrategy(
                title=f"Technique Strategy {i+1}",
                steps=[StrategyStep(
                    action=f"Action {i+1}",
                    prerequisites=[],
                    outcome=f"Outcome {i+1}",
                    risks=[],
                    confidence=0.8
                )],
                alignment_score={"test": 4.0},
                estimated_timeline="1 month",
                resource_requirements=[]
            )
            
            chain = StrategyChain(
                strategy=strategy,
                source_sample=i,
                temperature=0.7,
                technique_name=f"Technique {i+1}",
                technique_mandate=mandate
            )
            technique_strategies.append(chain)
        
        # Mock evaluator
        self.mock_evaluator.compare_strategies.return_value = {
            "preferred_strategy": 1,
            "evaluation_text": "Strategy comparison"
        }
        
        results = await self.runner.compare_technique_strategies(
            technique_strategies,
            "Test context"
        )
        
        # Should group by mandate
        assert "by_mandate" in results
        assert "2.1" in results["by_mandate"]
        assert "2.2" in results["by_mandate"]
        
        # Should have overall winner
        assert "overall_winner" in results


class TestTournamentIntegration:
    """Integration tests for tournament system"""

    @pytest.mark.asyncio
    async def test_tournament_with_real_strategy_structure(self):
        """Test tournament with realistic strategy structures"""
        # Create more realistic strategies
        strategies = []
        
        strategy_data = [
            {
                "title": "Rapid Market Entry Strategy",
                "steps": [
                    ("Launch MVP", ["Secure funding", "Hire core team"], "Market validation", ["Product-market fit risk"], 0.7),
                    ("Scale Operations", ["Proven demand", "Operational systems"], "Sustainable growth", ["Scaling challenges"], 0.8)
                ],
                "timeline": "6-12 months",
                "resources": ["Capital", "Technical team", "Marketing budget"]
            },
            {
                "title": "Conservative Growth Strategy", 
                "steps": [
                    ("Market Research", ["Define scope", "Allocate research budget"], "Deep market understanding", ["Analysis paralysis"], 0.9),
                    ("Gradual Expansion", ["Validated market", "Strong foundation"], "Stable growth", ["Missed opportunities"], 0.8)
                ],
                "timeline": "12-24 months",
                "resources": ["Research team", "Conservative capital", "Patience"]
            }
        ]
        
        for i, data in enumerate(strategy_data):
            steps = []
            for action, prereqs, outcome, risks, confidence in data["steps"]:
                steps.append(StrategyStep(
                    action=action,
                    prerequisites=prereqs,
                    outcome=outcome,
                    risks=risks,
                    confidence=confidence
                ))
            
            strategy = GenesisStrategy(
                title=data["title"],
                steps=steps,
                alignment_score={"Strategic Viability": 4.0 + i * 0.5},
                estimated_timeline=data["timeline"],
                resource_requirements=data["resources"]
            )
            
            chain = StrategyChain(
                strategy=strategy,
                source_sample=i,
                temperature=0.7
            )
            strategies.append(chain)
        
        # Test with mock evaluator
        mock_evaluator = AsyncMock()
        mock_evaluator.compare_strategies.return_value = {
            "preferred_strategy": 1,
            "evaluation_text": "Detailed strategic comparison analysis..."
        }
        
        runner = TournamentRunner(mock_evaluator)
        winner, results = await runner.find_best_strategy(
            strategies,
            "Startup strategy selection",
            tournament_type="elimination"
        )
        
        # Verify realistic results
        assert winner.strategy.title in ["Rapid Market Entry Strategy", "Conservative Growth Strategy"]
        assert len(results["comparisons"]) == 1  # 2 strategies = 1 comparison
        assert results["context"] == "Startup strategy selection"


if __name__ == "__main__":
    pytest.main([__file__])