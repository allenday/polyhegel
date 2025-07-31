"""
Graph building module for strategy DAGs
"""

import logging
from typing import List
import networkx as nx

from .models import StrategyChain

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds directed acyclic graphs from strategy chains"""
    
    @staticmethod
    def build_strategy_graphs(chains: List[StrategyChain]) -> None:
        """
        Convert strategy steps into directed acyclic graphs
        
        Args:
            chains: List of strategy chains to process
        """
        logger.info(f"Building DAGs for {len(chains)} strategy chains")
        
        for chain in chains:
            G = nx.DiGraph()
            
            # Add nodes for each step
            for i, step in enumerate(chain.strategy.steps):
                G.add_node(i, **step.model_dump())
            
            # Add edges based on prerequisites
            for i, step in enumerate(chain.strategy.steps):
                for j in range(i):
                    prev_step = chain.strategy.steps[j]
                    # Check if previous step's outcome matches current prerequisites
                    if GraphBuilder._check_dependency(prev_step.outcome, step.prerequisites):
                        G.add_edge(j, i)
            
            # Ensure it's a DAG by adding sequential edges where needed
            for i in range(len(chain.strategy.steps) - 1):
                if not G.has_edge(i, i + 1) and not nx.has_path(G, i, i + 1):
                    G.add_edge(i, i + 1)
            
            chain.graph = G
            
            # Validate DAG
            if not nx.is_directed_acyclic_graph(G):
                logger.warning(f"Graph for chain {chain.source_sample} contains cycles")
    
    @staticmethod
    def _check_dependency(outcome: str, prerequisites: List[str]) -> bool:
        """
        Check if an outcome satisfies any of the prerequisites
        
        Args:
            outcome: The outcome string to check
            prerequisites: List of prerequisite strings
            
        Returns:
            True if there's a dependency relationship
        """
        outcome_lower = outcome.lower()
        for prereq in prerequisites:
            prereq_lower = prereq.lower()
            # Check for substring match or semantic similarity
            if prereq_lower in outcome_lower or outcome_lower in prereq_lower:
                return True
            # Check for common keywords
            outcome_keywords = set(outcome_lower.split())
            prereq_keywords = set(prereq_lower.split())
            if len(outcome_keywords & prereq_keywords) >= 2:  # At least 2 common keywords
                return True
        return False
    
    @staticmethod
    def extract_narrative_flow(graph: nx.DiGraph) -> List[int]:
        """
        Extract a narrative flow from a strategy graph
        
        Args:
            graph: NetworkX directed graph
            
        Returns:
            List of node IDs in narrative order
        """
        try:
            # Try topological sort first
            return list(nx.topological_sort(graph))
        except nx.NetworkXError:
            # If graph has cycles, use alternative ordering
            logger.warning("Graph has cycles, using in-degree ordering")
            in_degrees = dict(graph.in_degree())
            return sorted(graph.nodes(), key=lambda x: (in_degrees[x], x))
    
    @staticmethod
    def analyze_graph_metrics(chains: List[StrategyChain]) -> dict:
        """
        Analyze graph metrics for all chains
        
        Args:
            chains: List of strategy chains with graphs
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'total_chains': len(chains),
            'avg_steps': 0,
            'avg_edges': 0,
            'max_parallelism': 0,
            'linear_chains': 0
        }
        
        if not chains:
            return metrics
        
        total_steps = 0
        total_edges = 0
        max_parallelism_sum = 0
        
        for chain in chains:
            if chain.graph:
                total_steps += chain.graph.number_of_nodes()
                total_edges += chain.graph.number_of_edges()
                
                # Calculate max parallelism (max nodes at same depth)
                if chain.graph.number_of_nodes() > 0:
                    try:
                        lengths = nx.single_source_shortest_path_length(chain.graph, 0)
                        depth_counts = {}
                        for node, depth in lengths.items():
                            depth_counts[depth] = depth_counts.get(depth, 0) + 1
                        max_parallelism_sum += max(depth_counts.values())
                    except:
                        max_parallelism_sum += 1
                
                # Check if chain is linear
                if chain.graph.number_of_edges() == chain.graph.number_of_nodes() - 1:
                    metrics['linear_chains'] += 1
        
        metrics['avg_steps'] = total_steps / len(chains) if chains else 0
        metrics['avg_edges'] = total_edges / len(chains) if chains else 0
        metrics['max_parallelism'] = max_parallelism_sum / len(chains) if chains else 0
        
        return metrics