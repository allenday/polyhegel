# Tournament Strategy Selection Guide

## Overview

Tournament selection provides a competitive approach to strategy evaluation and refinement. This system pits strategies against each other in head-to-head comparisons to identify the most effective approaches through systematic elimination.

## Tournament Concepts

### Basic Tournament Structure
```python
from polyhegel.selection.tournament import TournamentSelector, TournamentConfig

# Configure tournament parameters
config = TournamentConfig(
    tournament_type="single_elimination",
    evaluation_criteria=["coherence", "feasibility", "innovation"],
    min_participants=4,
    max_rounds=3
)

# Create tournament selector
selector = TournamentSelector(config)

# Run tournament on strategy candidates
candidates = [strategy1, strategy2, strategy3, strategy4]
winner = await selector.run_tournament(candidates)
```

### Tournament Types

#### Single Elimination
**Best For**: Quick selection with clear winners
```python
config = TournamentConfig(
    tournament_type="single_elimination",
    bracket_seeding="performance_based"  # Seed by initial scores
)

# Each strategy gets one chance - losers are eliminated
winner = await selector.run_tournament(candidates)
```

#### Double Elimination  
**Best For**: More robust selection allowing recovery from early losses
```python
config = TournamentConfig(
    tournament_type="double_elimination",
    allow_comeback=True  # Strategies can recover from one loss
)

# Strategies get second chances in losers bracket
winner = await selector.run_tournament(candidates)
```

#### Round Robin
**Best For**: Comprehensive comparison of all strategies
```python
config = TournamentConfig(
    tournament_type="round_robin",
    head_to_head_rounds=2  # Each pair competes twice
)

# Every strategy competes against every other strategy
ranking = await selector.run_tournament(candidates)
```

#### Swiss System
**Best For**: Large numbers of strategies with time constraints
```python
config = TournamentConfig(
    tournament_type="swiss_system",
    rounds=5,  # Fixed number of rounds
    pairing_method="strength_based"  # Pair similar-strength strategies
)

# Efficient tournament for many participants
top_strategies = await selector.run_tournament(candidates)
```

## Tournament Evaluation

### Multi-Criteria Evaluation
```python
from polyhegel.evaluation.tournament_judge import TournamentJudge

class ComprehensiveTournamentJudge(TournamentJudge):
    def __init__(self):
        self.evaluation_weights = {
            "strategic_coherence": 0.25,
            "implementation_feasibility": 0.25,
            "risk_management": 0.20,
            "innovation_level": 0.15,
            "resource_efficiency": 0.15
        }
    
    async def evaluate_matchup(self, strategy_a, strategy_b, context):
        # Score each strategy on all criteria
        scores_a = await self._score_strategy(strategy_a, context)
        scores_b = await self._score_strategy(strategy_b, context)
        
        # Calculate weighted comparison
        weighted_score_a = sum(
            scores_a[criterion] * weight 
            for criterion, weight in self.evaluation_weights.items()
        )
        weighted_score_b = sum(
            scores_b[criterion] * weight 
            for criterion, weight in self.evaluation_weights.items()
        )
        
        # Determine winner with confidence score
        if weighted_score_a > weighted_score_b:
            return {
                "winner": strategy_a,
                "confidence": abs(weighted_score_a - weighted_score_b),
                "detailed_scores": {"a": scores_a, "b": scores_b}
            }
        else:
            return {
                "winner": strategy_b,
                "confidence": abs(weighted_score_b - weighted_score_a),
                "detailed_scores": {"a": scores_a, "b": scores_b}
            }
```

### Domain-Specific Tournaments
```python
from polyhegel.strategic_techniques import StrategyDomain

# Resource-focused tournament
resource_config = TournamentConfig(
    tournament_type="single_elimination",
    evaluation_criteria=["resource_efficiency", "scalability", "cost_effectiveness"],
    domain_focus=StrategyDomain.RESOURCE_ACQUISITION
)

# Security-focused tournament  
security_config = TournamentConfig(
    tournament_type="double_elimination",
    evaluation_criteria=["threat_coverage", "implementation_complexity", "compliance_alignment"],
    domain_focus=StrategyDomain.STRATEGIC_SECURITY
)

# Run domain-specific tournaments
resource_winner = await TournamentSelector(resource_config).run_tournament(resource_strategies)
security_winner = await TournamentSelector(security_config).run_tournament(security_strategies)
```

## Advanced Tournament Features

### Adaptive Tournament Brackets
```python
class AdaptiveTournamentSelector(TournamentSelector):
    async def run_adaptive_tournament(self, candidates):
        # Start with initial bracket
        current_round = candidates
        tournament_history = []
        
        while len(current_round) > 1:
            # Analyze performance patterns
            performance_analysis = self._analyze_round_performance(tournament_history)
            
            # Adapt evaluation criteria based on patterns
            adapted_criteria = self._adapt_criteria(performance_analysis)
            
            # Run next round with adapted criteria
            next_round = []
            matchups = self._generate_matchups(current_round)
            
            for strategy_a, strategy_b in matchups:
                result = await self.judge.evaluate_matchup(
                    strategy_a, strategy_b, 
                    evaluation_criteria=adapted_criteria
                )
                next_round.append(result["winner"])
                tournament_history.append(result)
            
            current_round = next_round
        
        return current_round[0], tournament_history
```

### Tournament with Audience Voting
```python
from polyhegel.evaluation.human_judge import HumanJudgeIntegration

class HybridTournamentSelector(TournamentSelector):
    def __init__(self, config, human_weight=0.3):
        super().__init__(config)
        self.human_judge = HumanJudgeIntegration()
        self.human_weight = human_weight
        self.ai_weight = 1.0 - human_weight
    
    async def evaluate_matchup_with_humans(self, strategy_a, strategy_b, context):
        # Get AI evaluation
        ai_result = await self.ai_judge.evaluate_matchup(strategy_a, strategy_b, context)
        
        # Get human evaluation
        human_result = await self.human_judge.get_human_evaluation(
            strategy_a, strategy_b, context,
            voting_window_minutes=10
        )
        
        # Combine AI and human scores
        combined_score = (
            ai_result["confidence"] * self.ai_weight +
            human_result["confidence"] * self.human_weight
        )
        
        # Determine overall winner
        if ai_result["winner"] == human_result["winner"]:
            return {
                "winner": ai_result["winner"],
                "confidence": combined_score,
                "consensus": True
            }
        else:
            # Handle disagreement - use combined score
            return {
                "winner": ai_result["winner"] if combined_score > 0.5 else human_result["winner"],
                "confidence": combined_score,
                "consensus": False,
                "disagreement_details": {
                    "ai_choice": ai_result["winner"],
                    "human_choice": human_result["winner"]
                }
            }
```

## Integration with Strategy Generation

### Tournament-Driven Refinement
```python
from polyhegel.refinement.tournament_driven import TournamentDrivenRefinement

class TournamentRefinementPipeline:
    def __init__(self):
        self.generator = StrategyGenerator()
        self.tournament_selector = TournamentSelector()
        self.refinement_engine = RecursiveRefinementEngine()
    
    async def generate_and_compete(self, challenge: str, generations: int = 3):
        current_population = []
        
        for generation in range(generations):
            # Generate new candidates
            if generation == 0:
                # Initial generation from scratch
                candidates = await self.generator.generate_strategies(
                    temperature_counts=[(0.7, 8)],
                    user_prompt=challenge
                )
            else:
                # Generate from tournament winners
                candidates = await self._generate_from_winners(
                    current_population[:4], challenge  # Top 4 winners
                )
            
            # Run tournament
            tournament_results = await self.tournament_selector.run_tournament(candidates)
            
            # Refine top performers
            refined_strategies = []
            for strategy in tournament_results[:4]:  # Top 4
                refined = await self.refinement_engine.refine_strategy(
                    strategy, user_prompt=challenge
                )
                refined_strategies.append(refined.best_strategy)
            
            current_population = refined_strategies
            
            print(f"Generation {generation + 1} complete. Top score: {tournament_results[0].strategy.alignment_score}")
        
        return current_population[0]  # Ultimate winner
    
    async def _generate_from_winners(self, winners, challenge):
        # Generate new strategies inspired by tournament winners
        candidates = []
        for winner in winners:
            # Create variations of winning strategies
            variations = await self.generator.generate_variations(
                base_strategy=winner,
                variation_count=2,
                user_prompt=challenge
            )
            candidates.extend(variations)
        return candidates
```

### Multi-Stage Tournament Pipeline
```python
class MultiStageTournamentSystem:
    def __init__(self):
        self.qualification_config = TournamentConfig(
            tournament_type="swiss_system",
            rounds=3,
            qualification_threshold=0.6
        )
        
        self.semifinal_config = TournamentConfig(
            tournament_type="double_elimination",
            evaluation_criteria=["strategic_coherence", "feasibility", "innovation"]
        )
        
        self.final_config = TournamentConfig(
            tournament_type="best_of_series",
            series_length=5,
            evaluation_criteria=["overall_strategic_value"]
        )
    
    async def run_championship_tournament(self, initial_candidates):
        # Stage 1: Qualification rounds
        qualified = await TournamentSelector(self.qualification_config).run_tournament(
            initial_candidates
        )
        print(f"Qualified: {len(qualified)} strategies")
        
        # Stage 2: Semifinals
        semifinalists = await TournamentSelector(self.semifinal_config).run_tournament(
            qualified[:16]  # Top 16 qualifiers
        )
        print(f"Semifinalists: {len(semifinalists)} strategies")
        
        # Stage 3: Finals
        champion = await TournamentSelector(self.final_config).run_tournament(
            semifinalists[:4]  # Top 4 semifinalists
        )
        
        return champion, {"qualified": qualified, "semifinalists": semifinalists}
```

## Performance Analytics

### Tournament Statistics
```python
from polyhegel.analytics.tournament_stats import TournamentAnalytics

class TournamentPerformanceAnalyzer:
    def __init__(self):
        self.analytics = TournamentAnalytics()
    
    def analyze_tournament_results(self, tournament_history):
        stats = {
            "total_matchups": len(tournament_history),
            "average_confidence": sum(r["confidence"] for r in tournament_history) / len(tournament_history),
            "upset_count": self._count_upsets(tournament_history),
            "dominant_criteria": self._identify_dominant_criteria(tournament_history),
            "strategy_archetypes": self._analyze_winning_patterns(tournament_history)
        }
        
        return stats
    
    def _count_upsets(self, history):
        # Count times lower-seeded strategy beat higher-seeded
        upsets = 0
        for result in history:
            if hasattr(result, "seed_difference") and result.seed_difference < 0:
                upsets += 1
        return upsets
    
    def _identify_dominant_criteria(self, history):
        # Analyze which evaluation criteria were most decisive
        criteria_impact = {}
        for result in history:
            if "detailed_scores" in result:
                winner_scores = result["detailed_scores"]["winner"] 
                loser_scores = result["detailed_scores"]["loser"]
                
                for criterion in winner_scores:
                    diff = winner_scores[criterion] - loser_scores[criterion]
                    criteria_impact[criterion] = criteria_impact.get(criterion, 0) + abs(diff)
        
        # Return criteria sorted by impact
        return sorted(criteria_impact.items(), key=lambda x: x[1], reverse=True)
```

## Best Practices

### Tournament Design
1. **Match Tournament Type to Goals**:
   - Single elimination: Quick, decisive selection
   - Double elimination: More robust, allows recovery
   - Round robin: Comprehensive comparison
   - Swiss system: Efficient for large populations

2. **Evaluation Criteria Selection**:
   - Choose 3-5 key criteria to avoid analysis paralysis
   - Weight criteria based on strategic priorities
   - Consider domain-specific requirements

3. **Population Size Guidelines**:
   - Minimum 4 strategies for meaningful tournament
   - Optimal 8-16 strategies for balanced competition
   - Consider computational resources for larger tournaments

### Performance Optimization
1. **Parallel Evaluation**: Run independent matchups simultaneously
2. **Early Termination**: Stop tournaments when winner is statistically certain
3. **Caching**: Store evaluation results for repeated matchups
4. **Adaptive Scheduling**: Prioritize high-impact matchups

### Quality Assurance
1. **Validation Tournaments**: Run multiple tournaments to verify consistency
2. **Cross-Domain Testing**: Test strategies across different evaluation contexts
3. **Human Oversight**: Include human evaluation for critical decisions
4. **Bias Detection**: Monitor for systematic biases in tournament outcomes