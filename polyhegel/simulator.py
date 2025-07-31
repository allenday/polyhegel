"""
Main simulator class for Polyhegel
"""

import asyncio
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np

from .config import Config
from .models import StrategyChain, GenesisStrategy
from .model_manager import ModelManager
from .strategy_generator import StrategyGenerator
from .graph_builder import GraphBuilder
from .embedder import StrategyEmbedder
from .clusterer import StrategyClusterer
from .summarizer import StrategySummarizer
from .agents import LeaderAgent, FollowerAgent, AgentContext, AgentCoordinator
from .strategic_techniques import CLMMandate

logger = logging.getLogger(__name__)


class PolyhegelSimulator:
    """Main simulator class for swarm AI genesis strategy identification"""
    
    def __init__(self, 
                 model_name: str = None,
                 api_key: Optional[str] = None,
                 config: Optional[Dict] = None):
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
        self.embedder = StrategyEmbedder(self.config['embedding_model'])
        self.clusterer = StrategyClusterer(
            min_cluster_size=self.config['min_cluster_size'],
            twig_threshold=self.config['twig_threshold']
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
    
    def list_models_with_availability(self) -> Dict[str, Dict[str, any]]:
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
            if ':' in arg:
                try:
                    temp_str, count_str = arg.split(':')
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
    
    async def run_simulation(self,
                           temperature_counts: Optional[List[Tuple[float, int]]] = None,
                           system_prompt: Optional[str] = None,
                           user_prompt: Optional[str] = None,
                           mode: str = "temperature") -> Dict:
        """
        Run the complete simulation pipeline
        
        Args:
            temperature_counts: List of (temperature, count) tuples (for temperature mode)
            system_prompt: Optional custom system prompt
            user_prompt: Optional custom user prompt
            mode: Generation mode - "temperature" or "hierarchical"
            
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
                    system_prompt=system_prompt,
                    user_prompt=user_prompt
                )
            else:
                logger.info("Step 1: Generating diverse strategies using temperature sampling...")
                self.chains = await self.generator.generate_strategies(
                    temperature_counts=temperature_counts,
                    custom_system_prompt=system_prompt,
                    user_prompt=user_prompt
                )
            
            if not self.chains:
                raise ValueError("No strategies generated")
            
            # Step 2: Build DAGs
            logger.info("Step 2: Building strategy DAGs...")
            GraphBuilder.build_strategy_graphs(self.chains)
            
            # Step 3: Create embeddings
            logger.info("Step 3: Creating strategy embeddings...")
            self.embedder.embed_strategies(self.chains)
            
            # Step 4: Cluster strategies
            logger.info("Step 4: Clustering strategies...")
            self.cluster_results = self.clusterer.cluster_strategies(self.chains)
            self.trunk = self.cluster_results.get('trunk')
            self.twigs = self.cluster_results.get('twigs', [])
            
            # Step 5: Generate summary
            logger.info("Step 5: Generating summary...")
            summary = await self.summarizer.summarize_results(
                self.trunk,
                self.twigs,
                self._prepare_cluster_metrics()
            )
            
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
            'total_chains': len(self.chains),
            'cluster_count': self.cluster_results.get('cluster_count', 0),
            'noise_count': self.cluster_results.get('noise_count', 0),
            'cluster_sizes': self.cluster_results.get('cluster_sizes', {})
        }
        
        # Add graph metrics
        graph_metrics = GraphBuilder.analyze_graph_metrics(self.chains)
        metrics.update(graph_metrics)
        
        # Add coherence scores
        coherence_scores = self.clusterer.compute_cluster_coherence(self.chains)
        metrics['cluster_coherence'] = coherence_scores
        
        return metrics
    
    def _compile_results(self, 
                        summary: str,
                        temperature_counts: List[Tuple[float, int]]) -> Dict:
        """Compile all results into final output dictionary"""
        results = {
            'trunk': self._chain_to_dict(self.trunk) if self.trunk else None,
            'twigs': [self._chain_to_dict(twig) for twig in self.twigs],
            'summary': summary,
            'metadata': {
                'total_chains': len(self.chains),
                'model': self.model_name,
                'temperature_counts': temperature_counts,
                'clustering': self.cluster_results if self.cluster_results else {}
            }
        }
        
        # Add statistics
        if self.chains:
            results['statistics'] = self._compute_statistics()
        
        return results
    
    def _chain_to_dict(self, chain: StrategyChain) -> Dict:
        """Convert a StrategyChain to dictionary for output"""
        return {
            'title': chain.strategy.title,
            'steps': [step.model_dump() for step in chain.strategy.steps],
            'alignment_score': chain.strategy.alignment_score,
            'estimated_timeline': chain.strategy.estimated_timeline,
            'resource_requirements': chain.strategy.resource_requirements,
            'metadata': {
                'source_sample': chain.source_sample,
                'temperature': chain.temperature,
                'cluster_label': chain.cluster_label,
                'is_trunk': chain.is_trunk,
                'is_twig': chain.is_twig
            }
        }
    
    def _compute_statistics(self) -> Dict:
        """Compute statistics about the generated strategies"""
        stats = {
            'total_strategies': len(self.chains),
            'average_steps': np.mean([len(c.strategy.steps) for c in self.chains]),
            'temperature_distribution': {},
            'cluster_distribution': {}
        }
        
        # Temperature distribution
        for chain in self.chains:
            temp = chain.temperature
            stats['temperature_distribution'][temp] = stats['temperature_distribution'].get(temp, 0) + 1
        
        # Cluster distribution
        for chain in self.chains:
            label = chain.cluster_label
            stats['cluster_distribution'][label] = stats['cluster_distribution'].get(label, 0) + 1
        
        return stats
    
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
            'strategy': self._chain_to_dict(strategy),
            'similar_strategies': [
                {'title': s.strategy.title, 'similarity': score}
                for s, score in similar
            ],
            'narrative_flow': narrative_flow,
            'graph_metrics': {
                'nodes': strategy.graph.number_of_nodes() if strategy.graph else 0,
                'edges': strategy.graph.number_of_edges() if strategy.graph else 0,
                'is_dag': nx.is_directed_acyclic_graph(strategy.graph) if strategy.graph else True
            }
        }
    
    async def _generate_hierarchical_strategies(self,
                                              system_prompt: Optional[str] = None,
                                              user_prompt: Optional[str] = None) -> List[StrategyChain]:
        """
        Generate strategies using hierarchical leader-follower agent architecture
        
        Args:
            system_prompt: Optional custom system prompt
            user_prompt: User prompt describing the strategic challenge
            
        Returns:
            List of StrategyChain objects generated by hierarchical agents
        """
        if not user_prompt:
            raise ValueError("User prompt is required for hierarchical generation")
        
        # Create agent context from prompts
        context = AgentContext(
            strategic_challenge=user_prompt,
            constraints={},
            objectives=[],
            stakeholders=[],
            resources=[]
        )
        
        # Initialize hierarchical agents
        coordinator = AgentCoordinator()
        
        # Create leader agent
        leader = LeaderAgent(
            agent_id="hierarchical-leader",
            model=self.model,
            max_themes=5
        )
        coordinator.register_agent(leader)
        
        # Create specialized follower agents
        followers = [
            FollowerAgent(
                agent_id="resource-follower",
                model=self.model,
                specialization_mandate=CLMMandate.RESOURCE_ACQUISITION
            ),
            FollowerAgent(
                agent_id="security-follower", 
                model=self.model,
                specialization_mandate=CLMMandate.STRATEGIC_SECURITY
            ),
            FollowerAgent(
                agent_id="value-follower",
                model=self.model,
                specialization_mandate=CLMMandate.VALUE_CATALYSIS
            ),
            FollowerAgent(
                agent_id="general-follower",
                model=self.model
            )
        ]
        
        for follower in followers:
            coordinator.register_agent(follower)
        
        # Step 1: Generate strategic themes using leader
        logger.info("Generating strategic themes with leader agent...")
        theme_task = {
            "type": "generate_themes",
            "context": context.model_dump()
        }
        
        theme_responses = await coordinator.coordinate_task(theme_task)
        successful_theme_responses = [r for r in theme_responses if r.success]
        
        if not successful_theme_responses:
            raise ValueError("No themes generated by leader agent")
        
        themes = successful_theme_responses[0].content
        logger.info(f"Generated {len(themes)} strategic themes")
        
        # Step 2: Develop strategies from themes using followers
        logger.info("Developing strategies with follower agents...")
        strategies = []
        
        for theme in themes:
            strategy_task = {
                "type": "develop_strategy",
                "theme": theme.model_dump(),
                "context": context.model_dump()
            }
            
            strategy_responses = await coordinator.coordinate_task(strategy_task)
            successful_strategy_responses = [r for r in strategy_responses if r.success]
            
            for response in successful_strategy_responses:
                strategy = response.content
                if strategy:
                    strategies.append(strategy)
        
        logger.info(f"Generated {len(strategies)} strategies from hierarchical agents")
        
        # Convert to StrategyChain objects
        strategy_chains = []
        for i, strategy in enumerate(strategies):
            chain = StrategyChain(
                strategy=strategy,
                source_sample=i,
                temperature=0.7  # Default temperature for hierarchical mode
            )
            strategy_chains.append(chain)
        
        return strategy_chains