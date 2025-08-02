"""
Integration tests for strategic comparison using cached results
"""

import pytest
import json
from pathlib import Path
from polyhegel.strategy_evaluator import StrategyEvaluator
from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep
from polyhegel.model_manager import ModelManager


class TestStrategicComparison:
    """Test strategic comparison with cached simulation results"""

    def setup_method(self):
        """Set up test environment"""
        # Use fixtures by default, fall back to cache for backwards compatibility
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.cache_dir = Path(__file__).parent / "out"
        self.primary_fixture = self.fixtures_dir / "hotdog_reconciliation_simulation.json"
        self.cache_file = self.cache_dir / "strategic_simulation_cache.json"

        # Initialize model manager and evaluator
        self.model_manager = ModelManager()
        self.model = self.model_manager.get_model("claude-3-haiku-20240307")
        self.evaluator = StrategyEvaluator(self.model)

    def load_cached_strategies(self):
        """Load strategies from fixtures or cache file"""
        # Try fixtures first
        if self.primary_fixture.exists():
            with open(self.primary_fixture, "r") as f:
                data = json.load(f)
                # If trunk is null, try minimal test fixture
                if data.get("trunk") is None:
                    minimal_fixture = self.fixtures_dir / "minimal_hotdog_test.json"
                    if minimal_fixture.exists():
                        with open(minimal_fixture, "r") as f:
                            return json.load(f)
                return data

        # Fall back to cache for backwards compatibility
        if self.cache_file.exists():
            with open(self.cache_file, "r") as f:
                return json.load(f)

        pytest.skip(f"No cached strategies found at {self.primary_fixture} or {self.cache_file}")

    def create_strategy_chain_from_dict(
        self, strategy_dict: dict, source_sample: int = 0, temperature: float = 0.8
    ) -> StrategyChain:
        """Convert dictionary representation back to StrategyChain"""
        # Convert steps back to StrategyStep objects
        steps = [
            StrategyStep(
                action=step["action"],
                prerequisites=step["prerequisites"],
                outcome=step["outcome"],
                risks=step["risks"],
                confidence=step["confidence"],
            )
            for step in strategy_dict["steps"]
        ]

        # Create GenesisStrategy
        strategy = GenesisStrategy(
            title=strategy_dict["title"],
            steps=steps,
            alignment_score=strategy_dict["alignment_score"],
            estimated_timeline=strategy_dict["estimated_timeline"],
            resource_requirements=strategy_dict["resource_requirements"],
        )

        # Create StrategyChain
        chain = StrategyChain(strategy=strategy, source_sample=source_sample, temperature=temperature)

        # Set metadata from cached data if available
        if "metadata" in strategy_dict:
            meta = strategy_dict["metadata"]
            chain.source_sample = meta.get("source_sample", source_sample)
            chain.temperature = meta.get("temperature", temperature)
            chain.cluster_label = meta.get("cluster_label", -1)
            chain.is_trunk = meta.get("is_trunk", False)
            chain.is_twig = meta.get("is_twig", False)

        return chain

    def create_alternative_strategy(self) -> StrategyChain:
        """Create an alternative strategy for comparison"""
        # Create a different strategic approach
        steps = [
            StrategyStep(
                action="Rapid Prototype Development",
                prerequisites=["Assemble core development team", "Define minimum viable product requirements"],
                outcome="Launch initial prototype to gather early user feedback and validate core concepts",
                risks=[
                    "Rushed development leading to technical debt",
                    "Insufficient testing causing reliability issues",
                ],
                confidence=0.7,
            ),
            StrategyStep(
                action="Community-Driven Growth",
                prerequisites=["Establish open-source development model", "Create developer incentive programs"],
                outcome="Build organic community growth through transparent development and contributor rewards",
                risks=["Loss of strategic control over direction", "Fragmentation of development efforts"],
                confidence=0.8,
            ),
            StrategyStep(
                action="Iterative Market Validation",
                prerequisites=["Deploy beta testing program", "Establish user feedback loops"],
                outcome="Validate product-market fit through rapid iteration based on real user data",
                risks=["Pivoting too frequently losing focus", "Insufficient resources for sustained iteration"],
                confidence=0.75,
            ),
        ]

        strategy = GenesisStrategy(
            title="Agile Market-First Approach",
            steps=steps,
            alignment_score={"Market Responsiveness": 4.8, "Development Speed": 4.5, "Community Engagement": 4.2},
            estimated_timeline="3-6 months",
            resource_requirements=[
                "Agile development team",
                "Beta testing infrastructure",
                "Community management resources",
                "Rapid deployment capabilities",
            ],
        )

        return StrategyChain(strategy=strategy, source_sample=99, temperature=0.8)  # Mark as synthetic

    @pytest.mark.asyncio
    async def test_load_cached_strategies(self):
        """Test that we can load cached strategies"""
        cache_data = self.load_cached_strategies()

        # Verify expected structure
        assert "trunk" in cache_data
        assert "twigs" in cache_data
        assert "summary" in cache_data
        assert "metadata" in cache_data

        # Check trunk strategy
        trunk = cache_data["trunk"]
        assert "title" in trunk
        assert "steps" in trunk
        assert len(trunk["steps"]) > 0

        print(f"✅ Loaded trunk strategy: {trunk['title']}")
        print(f"✅ Strategy has {len(trunk['steps'])} steps")

    @pytest.mark.asyncio
    async def test_convert_cached_to_strategy_chain(self):
        """Test converting cached strategy back to StrategyChain"""
        cache_data = self.load_cached_strategies()
        trunk_dict = cache_data["trunk"]

        # Convert back to StrategyChain
        trunk_chain = self.create_strategy_chain_from_dict(trunk_dict)

        # Verify conversion
        assert isinstance(trunk_chain, StrategyChain)
        assert isinstance(trunk_chain.strategy, GenesisStrategy)
        assert trunk_chain.strategy.title == trunk_dict["title"]
        assert len(trunk_chain.strategy.steps) == len(trunk_dict["steps"])

        # Check first step
        first_step = trunk_chain.strategy.steps[0]
        first_step_dict = trunk_dict["steps"][0]
        assert first_step.action == first_step_dict["action"]
        assert first_step.confidence == first_step_dict["confidence"]

        print(f"✅ Successfully converted {trunk_chain.strategy.title}")
        print(f"✅ First step: {first_step.action} (confidence: {first_step.confidence})")

    @pytest.mark.asyncio
    async def test_strategic_comparison_with_cached_trunk(self):
        """Test comparing cached trunk strategy with alternative"""
        cache_data = self.load_cached_strategies()
        trunk_dict = cache_data["trunk"]

        # Convert trunk to StrategyChain
        trunk_chain = self.create_strategy_chain_from_dict(trunk_dict)

        # Create alternative strategy
        alt_chain = self.create_alternative_strategy()

        # Perform comparison
        comparison_result = await self.evaluator.compare_strategies(
            trunk_chain, alt_chain, context="Comparing strategic approaches for Genesis AI system deployment"
        )

        # Verify comparison results
        assert isinstance(comparison_result, dict)
        assert "evaluation_text" in comparison_result
        assert "preferred_strategy" in comparison_result

        # Check that we got meaningful output
        evaluation_text = comparison_result["evaluation_text"]
        assert len(evaluation_text) > 100  # Should be substantial
        assert "strategy" in evaluation_text.lower()

        preferred = comparison_result["preferred_strategy"]
        assert preferred in [1, 2]  # Should prefer one strategy

        print("✅ Comparison completed")
        print(f"✅ Preferred strategy: {preferred}")
        print(f"✅ Evaluation length: {len(evaluation_text)} characters")
        print(f"✅ Evaluation excerpt: {evaluation_text[:200]}...")

    @pytest.mark.asyncio
    async def test_multiple_strategy_comparisons(self):
        """Test comparing multiple alternative strategies"""
        cache_data = self.load_cached_strategies()
        trunk_dict = cache_data["trunk"]
        trunk_chain = self.create_strategy_chain_from_dict(trunk_dict)

        # Create multiple alternative strategies
        alternatives = [
            self.create_alternative_strategy(),
            self.create_conservative_strategy(),
            self.create_aggressive_strategy(),
            self.create_hotdog_strategy(),
        ]

        results = []

        # Compare trunk against each alternative
        for i, alt_chain in enumerate(alternatives):
            print(f"Comparing trunk vs alternative {i+1}: {alt_chain.strategy.title}")

            result = await self.evaluator.compare_strategies(
                trunk_chain, alt_chain, context=f"Strategic comparison #{i+1} for Genesis AI system"
            )

            results.append(
                {
                    "alternative_title": alt_chain.strategy.title,
                    "preferred_strategy": result["preferred_strategy"],
                    "evaluation_excerpt": result["evaluation_text"][:100] + "...",  # Truncate for output
                }
            )

        # Verify all comparisons completed
        assert len(results) == 4

        # Count preferences
        trunk_wins = sum(1 for r in results if r["preferred_strategy"] == 1)
        alt_wins = sum(1 for r in results if r["preferred_strategy"] == 2)

        print(f"✅ Completed {len(results)} comparisons")
        print(f"✅ Trunk strategy wins: {trunk_wins}")
        print(f"✅ Alternative strategy wins: {alt_wins}")

        # Document results
        for i, result in enumerate(results):
            winner = "Trunk" if result["preferred_strategy"] == 1 else result["alternative_title"]
            print(f"  Comparison {i+1}: {winner} preferred")

    def create_conservative_strategy(self) -> StrategyChain:
        """Create a conservative alternative strategy"""
        steps = [
            StrategyStep(
                action="Extensive Research and Planning",
                prerequisites=["Conduct comprehensive market analysis", "Complete technical feasibility studies"],
                outcome="Develop detailed strategic roadmap with minimal risk exposure",
                risks=["Analysis paralysis delaying action", "Market conditions changing during research phase"],
                confidence=0.9,
            ),
            StrategyStep(
                action="Gradual Stakeholder Onboarding",
                prerequisites=["Establish formal partnership agreements", "Create detailed governance frameworks"],
                outcome="Build stable foundation of committed partners with clear roles",
                risks=["Slow progress losing competitive advantage", "Over-bureaucratization hindering innovation"],
                confidence=0.85,
            ),
        ]

        strategy = GenesisStrategy(
            title="Risk-Minimized Foundation Strategy",
            steps=steps,
            alignment_score={"Risk Management": 4.9, "Stakeholder Confidence": 4.7, "Long-term Stability": 4.8},
            estimated_timeline="12-18 months",
            resource_requirements=[
                "Comprehensive research capabilities",
                "Legal and compliance expertise",
                "Stakeholder management resources",
            ],
        )

        return StrategyChain(strategy=strategy, source_sample=98, temperature=0.8)

    def create_aggressive_strategy(self) -> StrategyChain:
        """Create an aggressive alternative strategy"""
        steps = [
            StrategyStep(
                action="Immediate Market Disruption",
                prerequisites=["Secure substantial funding rounds", "Recruit top-tier talent aggressively"],
                outcome="Establish dominant market position through rapid scaling and innovation",
                risks=["Unsustainable burn rate leading to failure", "Quality issues from rapid execution"],
                confidence=0.6,
            ),
            StrategyStep(
                action="Acquisition-Driven Growth",
                prerequisites=["Identify strategic acquisition targets", "Establish M&A capabilities"],
                outcome="Rapidly expand capabilities and market reach through strategic acquisitions",
                risks=["Integration challenges from rapid acquisitions", "Cultural misalignment with acquired teams"],
                confidence=0.65,
            ),
        ]

        strategy = GenesisStrategy(
            title="Aggressive Market Dominance Strategy",
            steps=steps,
            alignment_score={"Market Speed": 4.9, "Competitive Advantage": 4.8, "Growth Potential": 4.7},
            estimated_timeline="1-3 months",
            resource_requirements=[
                "Substantial capital reserves",
                "Experienced M&A team",
                "Rapid scaling infrastructure",
                "High-performance talent acquisition",
            ],
        )

        return StrategyChain(strategy=strategy, source_sample=97, temperature=0.8)

    def create_hotdog_strategy(self) -> StrategyChain:
        """Create a strategy to resolve the hotdog-sandwich belief conflict"""
        steps = [
            StrategyStep(
                action="Establish Taxonomic Framework Summit",
                prerequisites=[
                    "Convene panel of culinary experts, linguists, and food scientists",
                    "Create neutral venue free from partisan sandwich ideology",
                ],
                outcome="Develop comprehensive food categorization system that addresses structural, functional, and cultural definitions",
                risks=[
                    "Panel dominated by Big Sandwich lobby influence",
                    "Linguistic purists rejecting pragmatic compromise solutions",
                ],
                confidence=0.8,
            ),
            StrategyStep(
                action="Implement Contextual Classification Protocol",
                prerequisites=[
                    "Deploy AI-powered food recognition system",
                    "Train classification models on diverse global food traditions",
                ],
                outcome="Create dynamic categorization that allows hotdogs to be sandwiches when structurally appropriate, non-sandwiches when culturally distinct",
                risks=[
                    "Algorithm bias toward Western sandwich paradigms",
                    "Recursive classification loops with edge cases like wraps and burritos",
                ],
                confidence=0.75,
            ),
            StrategyStep(
                action="Launch Peaceful Coexistence Campaign",
                prerequisites=[
                    "Develop educational materials highlighting shared bread-and-filling heritage",
                    "Establish International Day of Food Category Tolerance",
                ],
                outcome="Achieve societal acceptance that food identity can be multifaceted and context-dependent",
                risks=[
                    "Extremist factions rejecting compromise positions",
                    "Slippery slope concerns about pizza becoming sandwich",
                ],
                confidence=0.9,
            ),
            StrategyStep(
                action="Codify The Great Compromise",
                prerequisites=[
                    "Draft constitutional amendment protecting food classification pluralism",
                    "Establish Supreme Court of Culinary Classification",
                ],
                outcome="Legal framework ensuring both 'hotdog-as-sandwich' and 'hotdog-as-unique-entity' perspectives have constitutional protection",
                risks=[
                    "Legislative gridlock over sub-sandwich definitions",
                    "Interstate commerce complications with different classification standards",
                ],
                confidence=0.85,
            ),
        ]

        strategy = GenesisStrategy(
            title="The Great Hotdog Reconciliation Initiative",
            steps=steps,
            alignment_score={
                "Culinary Harmony": 4.8,
                "Taxonomic Clarity": 4.5,
                "Social Cohesion": 4.9,
                "Constitutional Integrity": 4.7,
            },
            estimated_timeline="2-3 years (accounting for Supreme Court appeals)",
            resource_requirements=[
                "Interdisciplinary expert panel",
                "AI food classification infrastructure",
                "Constitutional law expertise",
                "Public education campaign resources",
                "Emergency bread reserves for demonstrations",
            ],
        )

        return StrategyChain(strategy=strategy, source_sample=42, temperature=0.8)

    @pytest.mark.asyncio
    async def test_comparison_quality_metrics(self):
        """Test that comparisons produce high-quality strategic analysis"""
        cache_data = self.load_cached_strategies()
        trunk_dict = cache_data["trunk"]
        trunk_chain = self.create_strategy_chain_from_dict(trunk_dict)
        alt_chain = self.create_alternative_strategy()

        result = await self.evaluator.compare_strategies(trunk_chain, alt_chain)

        evaluation_text = result["evaluation_text"]

        # Check for strategic analysis keywords
        strategic_keywords = [
            "viability",
            "execution",
            "risk",
            "resource",
            "timeline",
            "stakeholder",
            "strategic",
            "approach",
            "advantage",
            "implementation",
        ]

        found_keywords = [kw for kw in strategic_keywords if kw.lower() in evaluation_text.lower()]

        # Should contain multiple strategic concepts
        assert len(found_keywords) >= 3, f"Only found {len(found_keywords)} strategic keywords: {found_keywords}"

        # Should have substantial evaluation
        assert len(evaluation_text.split()) >= 20, "Evaluation should be more detailed"

        print(f"✅ Found {len(found_keywords)} strategic keywords: {found_keywords}")
        print(f"✅ Evaluation word count: {len(evaluation_text.split())}")

    @pytest.mark.asyncio
    async def test_hotdog_strategy_comparison(self):
        """Test the hotdog strategy against a cached trunk strategy (for maximum strategic contrast)"""
        cache_data = self.load_cached_strategies()
        trunk_dict = cache_data["trunk"]
        trunk_chain = self.create_strategy_chain_from_dict(trunk_dict)

        # Get our hotdog strategy
        hotdog_chain = self.create_hotdog_strategy()

        # This should be a hilarious strategic comparison
        result = await self.evaluator.compare_strategies(
            trunk_chain,
            hotdog_chain,
            context="Comparing different approaches to resolving complex belief conflicts and establishing consensus",
        )

        # Verify we got a real comparison
        assert isinstance(result, dict)
        assert "evaluation_text" in result
        assert "preferred_strategy" in result

        evaluation_text = result["evaluation_text"]

        # Check that the comparison acknowledges the different domains
        strategic_concepts = [
            "consensus",
            "stakeholder",
            "framework",
            "implementation",
            "governance",
            "classification",
            "authority",
            "reconciliation",
        ]

        found_concepts = [c for c in strategic_concepts if c.lower() in evaluation_text.lower()]
        assert len(found_concepts) >= 2, f"Should identify strategic concepts: {found_concepts}"

        print("✅ Hotdog vs Trunk comparison completed")
        print(f"✅ Preferred strategy: {'Trunk' if result['preferred_strategy'] == 1 else 'Hotdog'}")
        print(f"✅ Strategic concepts found: {found_concepts}")
        print(f"✅ Evaluation preview: {evaluation_text[:300]}...")


if __name__ == "__main__":
    pytest.main([__file__])
