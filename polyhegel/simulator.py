"""
Main simulator class for Polyhegel
"""

import logging
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import networkx as nx

from .config import Config
from .models import StrategyChain
from pydantic import BaseModel
from .model_manager import ModelManager
from .strategy_generator import StrategyGenerator
from .graph_builder import GraphBuilder
from .embedder import StrategyEmbedder
from .clusterer import StrategyClusterer
from .summarizer import StrategySummarizer
from .tournament import StrategyTournament
from .strategy_evaluator import StrategyEvaluator

logger = logging.getLogger(__name__)


class SimulationStatistics(BaseModel):
    """Statistics from a simulation run"""
    total_strategies: int
    average_steps: float
    temperature_distribution: Dict[float, int]
    cluster_distribution: Dict[int, int]


class PolyhegelSimulator:
    """Main simulator class for swarm AI genesis strategy identification"""

    def __init__(self, model_name: str = None, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the simulator

        Args:
            model_name: Name of the model to use
            api_key: Optional API key
            config: Optional configuration dictionary
        """
        self.model_name = model_name or Config.DEFAULT_MODEL
        self.api_key = api_key
        self.config = config or Config.get_default_config()

        # Initialize components
        self.model_manager = ModelManager()
        self.model = self.model_manager.get_model(self.model_name, self.api_key)

        # Component instances
        self.generator = StrategyGenerator(self.model)
        self.embedder = StrategyEmbedder(self.config["embedding_model"])
        self.clusterer = StrategyClusterer(
            min_cluster_size=self.config["min_cluster_size"], twig_threshold=self.config["twig_threshold"]
        )
        self.summarizer = StrategySummarizer(self.model)

        # Results storage
        self.chains: List[StrategyChain] = []
        self.trunk: Optional[StrategyChain] = None
        self.twigs: List[StrategyChain] = []
        self.cluster_results: Optional[Dict] = None

    def list_available_models(self) -> Dict[str, List[str]]:
        """List available models from model manager"""
        return self.model_manager.discover_available_models()

    def list_models_with_availability(self) -> Dict[str, Dict[str, Any]]:
        """List models with their availability status"""
        return self.model_manager.list_models_with_availability()

    def parse_temperature_counts(self, temperature_args: List[str]) -> List[Tuple[float, int]]:
        """
        Parse temperature:count pairs from CLI arguments

        Args:
            temperature_args: List of strings like ["0.1:1", "0.3:2", "0.7:5"]

        Returns:
            List of (temperature, count) tuples
        """
        temperature_counts = []

        for arg in temperature_args:
            if ":" in arg:
                try:
                    temp_str, count_str = arg.split(":")
                    temp = float(temp_str)
                    count = int(count_str)
                    temperature_counts.append((temp, count))
                except ValueError:
                    logger.warning(f"Invalid temperature:count format: {arg}, skipping")
            else:
                # Backward compatibility: single temperature = count of 1
                try:
                    temp = float(arg)
                    temperature_counts.append((temp, 1))
                except ValueError:
                    logger.warning(f"Invalid temperature format: {arg}, skipping")

        return temperature_counts

    async def run_simulation(
        self,
        temperature_counts: Optional[List[Tuple[float, int]]] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        mode: str = "temperature",
        selection_method: str = "clustering",
    ) -> Dict:
        """
        Run the complete simulation pipeline

        Args:
            temperature_counts: List of (temperature, count) tuples (for temperature mode)
            system_prompt: Optional custom system prompt
            user_prompt: Optional custom user prompt
            mode: Generation mode - "temperature" or "hierarchical"
            selection_method: Method for trunk selection - "clustering" or "tournament"

        Returns:
            Dictionary with simulation results
        """
        temperature_counts = temperature_counts or Config.DEFAULT_TEMPERATURE_COUNTS

        logger.info("Starting strategy simulation")

        try:
            # Step 1: Generate strategies
            if mode == "hierarchical":
                logger.info("Step 1: Generating strategies using hierarchical agents...")
                self.chains = await self._generate_hierarchical_strategies(
                    system_prompt=system_prompt, user_prompt=user_prompt
                )
            else:
                logger.info("Step 1: Generating diverse strategies using temperature sampling...")
                self.chains = await self.generator.generate_strategies(
                    temperature_counts=temperature_counts, custom_system_prompt=system_prompt, user_prompt=user_prompt
                )

            if not self.chains:
                raise ValueError("No strategies generated")

            # Step 2: Build DAGs
            logger.info("Step 2: Building strategy DAGs...")
            GraphBuilder.build_strategy_graphs(self.chains)

            # Step 3: Create embeddings
            logger.info("Step 3: Creating strategy embeddings...")
            self.embedder.embed_strategies(self.chains)

            # Step 4: Select trunk strategy using chosen method
            if selection_method == "tournament":
                logger.info("Step 4: Running tournament to select best strategy...")
                evaluator = StrategyEvaluator(self.model)
                tournament = StrategyTournament(evaluator)

                context = user_prompt or "Strategic planning situation requiring optimal approach selection"
                self.trunk, tournament_results = await tournament.run_tournament(
                    self.chains, context, num_comparisons=1, save_results=False
                )

                # Create compatible result structure for downstream processing
                self.cluster_results = {
                    "trunk": self.trunk,
                    "twigs": [chain for chain in self.chains if chain != self.trunk],
                    "tournament_results": tournament_results,
                    "selection_method": "tournament",
                }
                self.twigs = self.cluster_results["twigs"]

            else:  # clustering method (default)
                logger.info("Step 4: Clustering strategies...")
                self.cluster_results = self.clusterer.cluster_strategies(self.chains)
                self.trunk = self.cluster_results.get("trunk")
                self.twigs = self.cluster_results.get("twigs", [])

            # Step 5: Generate summary
            logger.info("Step 5: Generating summary...")
            summary = await self.summarizer.summarize_results(self.trunk, self.twigs, self._prepare_cluster_metrics())

            # Step 6: Compile results
            results = self._compile_results(summary, temperature_counts)

            logger.info("Simulation completed successfully")
            return results

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise

    def _prepare_cluster_metrics(self) -> Dict:
        """Prepare clustering metrics for summary"""
        if not self.cluster_results:
            return {}

        metrics = {
            "total_chains": len(self.chains),
            "cluster_count": self.cluster_results.get("cluster_count", 0),
            "noise_count": self.cluster_results.get("noise_count", 0),
            "cluster_sizes": self.cluster_results.get("cluster_sizes", {}),
        }

        # Add graph metrics
        graph_metrics = GraphBuilder.analyze_graph_metrics(self.chains)
        metrics.update(graph_metrics)

        # Add coherence scores
        coherence_scores = self.clusterer.compute_cluster_coherence(self.chains)
        metrics["cluster_coherence"] = coherence_scores

        return metrics

    def _compile_results(self, summary: str, temperature_counts: List[Tuple[float, int]]) -> Dict:
        """Compile all results into final output dictionary"""
        results = {
            "trunk": self._chain_to_dict(self.trunk) if self.trunk else None,
            "twigs": [self._chain_to_dict(twig) for twig in self.twigs],
            "summary": summary,
            "metadata": {
                "total_chains": len(self.chains),
                "model": self.model_name,
                "temperature_counts": temperature_counts,
                "clustering": self._clean_cluster_results() if self.cluster_results else {},
            },
        }

        # Add statistics
        if self.chains:
            results["statistics"] = self._compute_statistics().model_dump()

        return results

    def _chain_to_dict(self, chain: StrategyChain) -> Dict:
        """Convert a StrategyChain to dictionary for output"""
        return {
            "title": chain.strategy.title,
            "steps": [step.model_dump() for step in chain.strategy.steps],
            "alignment_score": chain.strategy.alignment_score,
            "estimated_timeline": chain.strategy.estimated_timeline,
            "resource_requirements": chain.strategy.resource_requirements,
            "metadata": {
                "source_sample": chain.source_sample,
                "temperature": chain.temperature,
                "cluster_label": chain.cluster_label,
                "is_trunk": chain.is_trunk,
                "is_twig": chain.is_twig,
            },
        }

    def _compute_statistics(self) -> SimulationStatistics:
        """Compute statistics about the generated strategies"""
        temperature_distribution: Dict[float, int] = {}
        cluster_distribution: Dict[int, int] = {}

        # Temperature distribution
        for chain in self.chains:
            temp = chain.temperature
            temperature_distribution[temp] = temperature_distribution.get(temp, 0) + 1

        # Cluster distribution
        for chain in self.chains:
            label = int(chain.cluster_label)  # Convert numpy types to int
            cluster_distribution[label] = cluster_distribution.get(label, 0) + 1

        return SimulationStatistics(
            total_strategies=len(self.chains),
            average_steps=float(np.mean([len(c.strategy.steps) for c in self.chains])),
            temperature_distribution=temperature_distribution,
            cluster_distribution=cluster_distribution,
        )

    def _clean_cluster_results(self) -> Dict:
        """Clean cluster results for JSON serialization"""
        if not self.cluster_results:
            return {}

        cleaned = {}
        for key, value in self.cluster_results.items():
            if key in ["trunk", "twigs"]:
                # Skip trunk/twigs as they're handled separately
                continue
            elif isinstance(value, (int, float, str, bool, list, dict)):
                cleaned[key] = value
            elif hasattr(value, "tolist"):  # numpy arrays
                cleaned[key] = value.tolist()
            else:
                # Convert to string for anything else
                cleaned[key] = str(value)

        return cleaned

    async def analyze_strategy(self, strategy_index: int) -> Dict:
        """
        Perform detailed analysis of a specific strategy

        Args:
            strategy_index: Index of the strategy in self.chains

        Returns:
            Detailed analysis dictionary
        """
        if strategy_index >= len(self.chains):
            raise ValueError(f"Invalid strategy index: {strategy_index}")

        strategy = self.chains[strategy_index]

        # Find similar strategies
        similar = self.embedder.find_similar_strategies(strategy, self.chains, top_k=5)

        # Extract narrative flow
        if strategy.graph:
            narrative_flow = GraphBuilder.extract_narrative_flow(strategy.graph)
        else:
            narrative_flow = list(range(len(strategy.strategy.steps)))

        return {
            "strategy": self._chain_to_dict(strategy),
            "similar_strategies": [{"title": s.strategy.title, "similarity": score} for s, score in similar],
            "narrative_flow": narrative_flow,
            "graph_metrics": {
                "nodes": strategy.graph.number_of_nodes() if strategy.graph else 0,
                "edges": strategy.graph.number_of_edges() if strategy.graph else 0,
                "is_dag": nx.is_directed_acyclic_graph(strategy.graph) if strategy.graph else True,
            },
        }

    async def _generate_hierarchical_strategies(
        self, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None
    ) -> List[StrategyChain]:
        """
        Generate strategies using A2A hierarchical agent delegation

        Args:
            system_prompt: Optional custom system prompt (unused in A2A mode)
            user_prompt: User prompt describing the strategic challenge

        Returns:
            List of StrategyChain objects generated by A2A agents
        """
        if not user_prompt:
            raise ValueError("User prompt is required for hierarchical generation")

        # Import A2A simulation function
        from .agents.a2a_simulation import generate_hierarchical_strategies_a2a

        # Define AgentContext locally (was previously in base.py)
        from pydantic import BaseModel
        from typing import Any, Dict, List

        class AgentContext(BaseModel):
            strategic_challenge: str
            constraints: Dict[str, Any] = {}
            objectives: List[str] = []
            stakeholders: List[str] = []
            resources: List[str] = []

        # Create agent context
        context = AgentContext(
            strategic_challenge=user_prompt, constraints={}, objectives=[], stakeholders=[], resources=[]
        )

        # Use A2A coordination for strategy generation
        logger.info("Starting A2A hierarchical strategy generation...")

        # Check for environment configuration
        import os

        leader_url = os.getenv("POLYHEGEL_LEADER_URL", "http://localhost:8001")
        follower_urls = {
            "resource": os.getenv("POLYHEGEL_FOLLOWER_RESOURCE_URL", "http://localhost:8002/resource"),
            "security": os.getenv("POLYHEGEL_FOLLOWER_SECURITY_URL", "http://localhost:8002/security"),
            "value": os.getenv("POLYHEGEL_FOLLOWER_VALUE_URL", "http://localhost:8002/value"),
            "general": os.getenv("POLYHEGEL_FOLLOWER_GENERAL_URL", "http://localhost:8002/general"),
        }

        try:
            # Generate strategies via A2A coordination
            strategy_chains = await generate_hierarchical_strategies_a2a(
                strategic_challenge=user_prompt,
                context=context.model_dump(),
                leader_url=leader_url,
                follower_urls=follower_urls,
                max_themes=5,
            )

            logger.info(f"A2A coordination generated {len(strategy_chains)} strategy chains")
            return strategy_chains

        except Exception as e:
            logger.error(f"A2A hierarchical generation failed: {e}")
            logger.info("Falling back to local simulation mode...")

            # Fallback: Generate a simple strategy chain locally
            from .models import GenesisStrategy, StrategyStep

            fallback_strategy = GenesisStrategy(
                title="Local Fallback Strategy",
                steps=[
                    StrategyStep(
                        action="Analyze strategic challenge locally",
                        prerequisites=["User prompt provided"],
                        outcome="Basic strategic understanding",
                        risks=["Limited strategic depth"],
                    )
                ],
                alignment_score={"2.1": 2.0, "2.2": 2.0, "2.3": 2.0},
                estimated_timeline="1 week",
                resource_requirements=["Local processing"],
            )

            fallback_chain = StrategyChain(strategy=fallback_strategy, source_sample=0, temperature=0.7)

            logger.warning("Generated fallback strategy due to A2A coordination failure")
            return [fallback_chain]
