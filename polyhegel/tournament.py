"""
Strategic Tournament System for Polyhegel

Adapted from LLM-As-Hierarchical-Policy tournament logic for strategic comparison.
Instead of mathematical problem solving, this implements pairwise strategy comparison
to identify the best strategic approaches through elimination tournaments.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict
from pathlib import Path

from .models import StrategyChain
from .evaluator import Evaluator as StrategyEvaluator

logger = logging.getLogger(__name__)


class StrategyTournament:
    """Strategic tournament system for comparing and ranking strategies"""

    def __init__(self, evaluator: StrategyEvaluator):
        """
        Initialize tournament with strategy evaluator

        Args:
            evaluator: StrategyEvaluator instance for pairwise comparisons
        """
        self.evaluator = evaluator
        self.results: Dict[str, Any] = {}

    async def run_tournament(
        self,
        strategies: List[StrategyChain],
        context: str,
        num_comparisons: int = 1,
        save_results: bool = True,
        results_file: Optional[str] = None,
    ) -> Tuple[Optional[StrategyChain], Dict[Any, Any]]:
        """
        Run a tournament to find the best strategy

        Args:
            strategies: List of strategies to compare
            context: Context for strategic comparison
            num_comparisons: Number of comparisons per pair (for voting)
            save_results: Whether to save detailed results
            results_file: Optional file to save results to

        Returns:
            Tuple of (winning_strategy, detailed_results)
        """
        if len(strategies) < 2:
            raise ValueError("Tournament requires at least 2 strategies")

        logger.info(f"Starting tournament with {len(strategies)} strategies")

        # Initialize results tracking
        tournament_results: Dict[str, Any] = {
            "strategies": {i: strategy for i, strategy in enumerate(strategies)},
            "comparisons": [],
            "voting_results": {},
            "winner": None,
            "context": context,
        }

        # Convert strategies to tournament format
        candidates = {i: strategy for i, strategy in enumerate(strategies)}

        # Find the best strategy through pairwise elimination
        best_strategy_idx = await self._elimination_tournament(candidates, context, num_comparisons, tournament_results)

        winning_strategy = strategies[best_strategy_idx]
        tournament_results["winner"] = best_strategy_idx

        logger.info(f"Tournament winner: {winning_strategy.strategy.title}")

        if save_results and results_file:
            self._save_results(tournament_results, results_file)

        return winning_strategy, tournament_results

    async def _elimination_tournament(
        self, candidates: Dict[int, StrategyChain], context: str, num_comparisons: int, results: Dict
    ) -> int:
        """
        Run elimination tournament to find best strategy

        Args:
            candidates: Dictionary mapping candidate IDs to strategies
            context: Context for comparison
            num_comparisons: Number of comparisons per pair
            results: Results dictionary to update

        Returns:
            ID of winning strategy
        """
        candidate_ids = sorted(candidates.keys())
        current_best = candidate_ids[0]

        # Challenge current best with each subsequent candidate
        for i in range(1, len(candidate_ids)):
            challenger_id = candidate_ids[i]

            logger.info(f"Comparing strategy {current_best} vs {challenger_id}")

            # Run multiple comparisons for voting
            comparison_results = []
            for comp_round in range(num_comparisons):
                comparison_result = await self._compare_strategies(
                    candidates[current_best], candidates[challenger_id], context, round_num=comp_round
                )
                comparison_results.append(comparison_result)

            # Aggregate voting results
            voting_result = self._aggregate_votes(comparison_results)
            comparison_key = f"{current_best}_vs_{challenger_id}"
            results["voting_results"][comparison_key] = voting_result
            results["comparisons"].extend(comparison_results)

            # Determine winner of this round
            if voting_result["winner"] == 2:  # Challenger wins
                current_best = challenger_id
                logger.info(f"Strategy {challenger_id} defeats {current_best}")
            else:
                logger.info(f"Strategy {current_best} remains champion")

        return current_best

    async def _compare_strategies(
        self, strategy1: StrategyChain, strategy2: StrategyChain, context: str, round_num: int = 0
    ) -> Dict:
        """
        Compare two strategies using the evaluator

        Args:
            strategy1: First strategy to compare
            strategy2: Second strategy to compare
            context: Context for comparison
            round_num: Round number for tracking

        Returns:
            Comparison result with voting information
        """
        try:
            # Run strategy comparison
            result = await self.evaluator.compare_strategies(strategy1, strategy2, context)

            # Extract preference (1 for strategy1, 2 for strategy2)
            preferred = result.get("preferred_strategy", 1)

            comparison_result = {
                "round": round_num,
                "strategy1_title": strategy1.strategy.title,
                "strategy2_title": strategy2.strategy.title,
                "evaluation_text": result.get("evaluation_text", ""),
                "preferred_strategy": preferred,
                "context": context,
            }

            return comparison_result

        except Exception as e:
            logger.error(f"Strategy comparison failed: {e}")
            # Default to strategy1 in case of error
            return {
                "round": round_num,
                "strategy1_title": strategy1.strategy.title,
                "strategy2_title": strategy2.strategy.title,
                "evaluation_text": f"Comparison failed: {e}",
                "preferred_strategy": 1,
                "context": context,
                "error": str(e),
            }

    def _aggregate_votes(self, comparison_results: List[Dict]) -> Dict:
        """
        Aggregate multiple comparison results into voting outcome

        Args:
            comparison_results: List of comparison results

        Returns:
            Aggregated voting result
        """
        voting: Dict[int, int] = defaultdict(int)

        for result in comparison_results:
            preferred = result.get("preferred_strategy", 1)
            voting[preferred] += 1

        # Determine overall winner
        if voting[2] > voting[1]:
            winner = 2
        elif voting[1] > voting[2]:
            winner = 1
        else:
            # Tie-breaker: default to strategy 1
            winner = 1

        return {
            "votes_strategy1": voting[1],
            "votes_strategy2": voting[2],
            "winner": winner,
            "total_rounds": len(comparison_results),
        }

    async def run_round_robin_tournament(
        self, strategies: List[StrategyChain], context: str, num_comparisons: int = 1
    ) -> Dict:
        """
        Run round-robin tournament where every strategy competes with every other

        Args:
            strategies: List of strategies to compare
            context: Context for strategic comparison
            num_comparisons: Number of comparisons per pair

        Returns:
            Detailed tournament results with rankings
        """
        if len(strategies) < 2:
            raise ValueError("Round-robin tournament requires at least 2 strategies")

        logger.info(f"Starting round-robin tournament with {len(strategies)} strategies")

        # Track wins and losses for each strategy
        wins: Dict[int, int] = defaultdict(int)
        losses: Dict[int, int] = defaultdict(int)
        head_to_head = {}
        all_comparisons = []

        # Compare every pair of strategies
        for i in range(len(strategies)):
            for j in range(i + 1, len(strategies)):
                strategy1 = strategies[i]
                strategy2 = strategies[j]

                logger.info(f"Round-robin: Strategy {i} vs {j}")

                # Run multiple comparisons for this pair
                comparison_results = []
                for comp_round in range(num_comparisons):
                    result = await self._compare_strategies(strategy1, strategy2, context, comp_round)
                    comparison_results.append(result)

                # Aggregate votes for this pairing
                voting_result = self._aggregate_votes(comparison_results)

                # Update win/loss records
                if voting_result["winner"] == 1:
                    wins[i] += 1
                    losses[j] += 1
                else:
                    wins[j] += 1
                    losses[i] += 1

                # Store head-to-head result
                head_to_head[f"{i}_vs_{j}"] = voting_result
                all_comparisons.extend(comparison_results)

        # Calculate final rankings
        rankings = []
        for i, strategy in enumerate(strategies):
            win_rate = wins[i] / (wins[i] + losses[i]) if (wins[i] + losses[i]) > 0 else 0
            rankings.append(
                {
                    "strategy_id": i,
                    "strategy_title": strategy.strategy.title,
                    "wins": wins[i],
                    "losses": losses[i],
                    "win_rate": win_rate,
                }
            )

        # Sort by wins (then by win rate for ties)
        rankings.sort(key=lambda x: (x["wins"], x["win_rate"]), reverse=True)

        return {
            "tournament_type": "round_robin",
            "strategies": {i: strategy for i, strategy in enumerate(strategies)},
            "rankings": rankings,
            "head_to_head": head_to_head,
            "all_comparisons": all_comparisons,
            "context": context,
            "winner": rankings[0]["strategy_id"] if rankings else None,
        }

    def _save_results(self, results: Dict, filename: str):
        """Save tournament results to file"""
        try:
            import json

            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert non-serializable objects for JSON
            serializable_results = self._make_serializable(results)

            with open(output_path, "w") as f:
                json.dump(serializable_results, f, indent=2)

            logger.info(f"Tournament results saved to {filename}")

        except Exception as e:
            logger.error(f"Failed to save tournament results: {e}")

    def _make_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, "model_dump"):  # Pydantic model
            return obj.model_dump()
        elif hasattr(obj, "__dict__"):  # Dataclass or custom object
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items()}
        else:
            try:
                import json

                json.dumps(obj)  # Test if serializable
                return obj
            except (TypeError, ValueError):
                return str(obj)


class TournamentRunner:
    """High-level interface for running strategic tournaments"""

    def __init__(self, evaluator: StrategyEvaluator):
        """Initialize with strategy evaluator"""
        self.tournament = StrategyTournament(evaluator)

    async def find_best_strategy(
        self,
        strategies: List[StrategyChain],
        context: str,
        tournament_type: str = "elimination",
        num_comparisons: int = 1,
        save_results: bool = False,
        results_file: Optional[str] = None,
    ) -> Tuple[Optional[StrategyChain], Dict[Any, Any]]:
        """
        Find the best strategy using tournament selection

        Args:
            strategies: List of strategies to evaluate
            context: Context for strategic comparison
            tournament_type: "elimination" or "round_robin"
            num_comparisons: Number of comparisons per pair
            save_results: Whether to save results
            results_file: File to save results to

        Returns:
            Tuple of (best_strategy, tournament_results)
        """
        if tournament_type == "elimination":
            return await self.tournament.run_tournament(
                strategies, context, num_comparisons, save_results, results_file
            )
        elif tournament_type == "round_robin":
            results = await self.tournament.run_round_robin_tournament(strategies, context, num_comparisons)
            if save_results and results_file:
                self.tournament._save_results(results, results_file)

            # Return winner and results
            winner_id = results["winner"]
            winner_strategy = strategies[winner_id] if winner_id is not None else None
            return winner_strategy, results
        else:
            raise ValueError(f"Unknown tournament type: {tournament_type}")

    async def compare_technique_strategies(self, strategies: List[StrategyChain], context: str) -> Dict:
        """
        Special tournament for comparing technique-guided strategies

        Args:
            strategies: List of technique-guided strategies
            context: Strategic context

        Returns:
            Results organized by technique domain
        """
        # Group strategies by technique domain
        domain_groups = defaultdict(list)
        for strategy in strategies:
            domain = getattr(strategy, "technique_domain", "unknown")
            domain_groups[domain].append(strategy)

        results: Dict[str, Any] = {"by_domain": {}, "overall_winner": None}

        # Run tournament within each domain group
        for domain, group_strategies in domain_groups.items():
            if len(group_strategies) > 1:
                winner, tournament_results = await self.find_best_strategy(
                    group_strategies, f"{context} (Strategic Domain {domain})", tournament_type="round_robin"
                )
                results["by_domain"][domain] = {"winner": winner, "results": tournament_results}
            elif len(group_strategies) == 1:
                results["by_domain"][domain] = {"winner": group_strategies[0], "results": {"single_strategy": True}}

        # If we have winners from multiple domains, run final tournament
        domain_winners = [
            result["winner"] for result in results["by_domain"].values() if result.get("winner") is not None
        ]

        if len(domain_winners) > 1:
            overall_winner, final_results = await self.find_best_strategy(
                domain_winners, f"{context} (Cross-Domain Final)", tournament_type="elimination"
            )
            results["overall_winner"] = overall_winner
            results["final_tournament"] = final_results
        elif len(domain_winners) == 1:
            results["overall_winner"] = domain_winners[0]

        return results
