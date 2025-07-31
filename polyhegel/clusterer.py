"""
Clustering module for strategy identification
"""

import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
import hdbscan
from sklearn_extra.cluster import KMedoids

from .models import StrategyChain
from .config import Config

logger = logging.getLogger(__name__)


class StrategyClusterer:
    """Handles clustering of strategies to identify trunk and twigs"""
    
    def __init__(self, 
                 min_cluster_size: int = None,
                 twig_threshold: float = None):
        """
        Initialize clusterer with parameters
        
        Args:
            min_cluster_size: Minimum size for a cluster
            twig_threshold: Threshold for identifying twigs
        """
        self.min_cluster_size = min_cluster_size or Config.DEFAULT_MIN_CLUSTER_SIZE
        self.twig_threshold = twig_threshold or Config.DEFAULT_TWIG_THRESHOLD
    
    def cluster_strategies(self, chains: List[StrategyChain]) -> Dict[str, any]:
        """
        Cluster strategies and identify trunk/twigs
        
        Args:
            chains: List of strategy chains with embeddings
            
        Returns:
            Dictionary with clustering results
        """
        if len(chains) < self.min_cluster_size:
            logger.warning(f"Not enough chains ({len(chains)}) for clustering")
            return self._handle_insufficient_chains(chains)
        
        # Stack embeddings
        embeddings = np.vstack([chain.embedding for chain in chains])
        
        # Perform HDBSCAN clustering
        logger.info("Performing HDBSCAN clustering")
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            metric='euclidean'
        )
        cluster_labels = clusterer.fit_predict(embeddings)
        
        # Assign cluster labels to chains
        for chain, label in zip(chains, cluster_labels):
            chain.cluster_label = label
        
        # Analyze clusters
        results = self._analyze_clusters(chains, cluster_labels, embeddings)
        
        return results
    
    def _handle_insufficient_chains(self, chains: List[StrategyChain]) -> Dict[str, any]:
        """Handle case when there aren't enough chains for clustering"""
        if chains:
            chains[0].is_trunk = True
            return {
                'trunk': chains[0],
                'twigs': [],
                'cluster_count': 1,
                'noise_count': 0
            }
        return {
            'trunk': None,
            'twigs': [],
            'cluster_count': 0,
            'noise_count': 0
        }
    
    def _analyze_clusters(self, 
                         chains: List[StrategyChain], 
                         cluster_labels: np.ndarray,
                         embeddings: np.ndarray) -> Dict[str, any]:
        """
        Analyze clustering results to identify trunk and twigs
        
        Args:
            chains: List of strategy chains
            cluster_labels: Cluster labels from HDBSCAN
            embeddings: Embedding matrix
            
        Returns:
            Dictionary with analysis results
        """
        unique_labels = set(cluster_labels) - {-1}  # Exclude noise
        
        results = {
            'trunk': None,
            'twigs': [],
            'cluster_count': len(unique_labels),
            'noise_count': np.sum(cluster_labels == -1),
            'cluster_sizes': {}
        }
        
        if not unique_labels:
            logger.warning("No clusters found, all points are noise")
            return results
        
        # Find largest cluster
        label_counts = {label: np.sum(cluster_labels == label) for label in unique_labels}
        largest_cluster = max(label_counts, key=label_counts.get)
        results['cluster_sizes'] = label_counts
        
        # Find trunk (medoid of largest cluster)
        trunk = self._find_trunk(chains, largest_cluster, embeddings)
        if trunk:
            trunk.is_trunk = True
            results['trunk'] = trunk
        
        # Find twigs
        twigs = self._find_twigs(chains, cluster_labels, largest_cluster, len(chains))
        for twig in twigs:
            twig.is_twig = True
        results['twigs'] = twigs
        
        logger.info(f"Clustering complete: {len(unique_labels)} clusters, "
                   f"trunk from cluster {largest_cluster}, {len(twigs)} twigs")
        
        return results
    
    def _find_trunk(self, 
                   chains: List[StrategyChain], 
                   cluster_label: int,
                   embeddings: np.ndarray) -> Optional[StrategyChain]:
        """
        Find the trunk (medoid) of the largest cluster
        
        Args:
            chains: List of all chains
            cluster_label: Label of the largest cluster
            embeddings: Embedding matrix
            
        Returns:
            The trunk strategy chain
        """
        cluster_chains = [c for c in chains if c.cluster_label == cluster_label]
        
        if not cluster_chains:
            return None
        
        if len(cluster_chains) == 1:
            return cluster_chains[0]
        
        # Get embeddings for this cluster
        cluster_indices = [i for i, c in enumerate(chains) if c.cluster_label == cluster_label]
        cluster_embeddings = embeddings[cluster_indices]
        
        # Find medoid using KMedoids
        logger.info(f"Finding medoid of cluster {cluster_label} with {len(cluster_chains)} members")
        kmedoids = KMedoids(n_clusters=1, metric='euclidean')
        kmedoids.fit(cluster_embeddings)
        medoid_idx = kmedoids.medoid_indices_[0]
        
        return cluster_chains[medoid_idx]
    
    def _find_twigs(self, 
                   chains: List[StrategyChain],
                   cluster_labels: np.ndarray,
                   trunk_cluster: int,
                   total_chains: int) -> List[StrategyChain]:
        """
        Identify twig strategies (small clusters and outliers)
        
        Args:
            chains: List of all chains
            cluster_labels: Cluster labels
            trunk_cluster: Label of the trunk cluster
            total_chains: Total number of chains
            
        Returns:
            List of twig strategies
        """
        twigs = []
        unique_labels = set(cluster_labels) - {-1}
        
        # Small clusters (not trunk)
        for label in unique_labels:
            if label != trunk_cluster:
                cluster_size = np.sum(cluster_labels == label)
                if cluster_size / total_chains < self.twig_threshold:
                    cluster_twigs = [c for c in chains if c.cluster_label == label]
                    twigs.extend(cluster_twigs)
        
        # Outliers (noise points)
        outlier_twigs = [c for c in chains if c.cluster_label == -1]
        twigs.extend(outlier_twigs)
        
        return twigs
    
    def compute_cluster_coherence(self, chains: List[StrategyChain]) -> Dict[int, float]:
        """
        Compute coherence scores for each cluster
        
        Args:
            chains: List of strategy chains with cluster labels
            
        Returns:
            Dictionary mapping cluster labels to coherence scores
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        coherence_scores = {}
        cluster_labels = set(chain.cluster_label for chain in chains)
        
        for label in cluster_labels:
            if label == -1:  # Skip noise
                continue
                
            cluster_chains = [c for c in chains if c.cluster_label == label]
            if len(cluster_chains) < 2:
                coherence_scores[label] = 1.0
                continue
            
            # Compute average pairwise similarity within cluster
            cluster_embeddings = np.vstack([c.embedding for c in cluster_chains])
            similarity_matrix = cosine_similarity(cluster_embeddings)
            
            # Average off-diagonal elements
            n = len(cluster_chains)
            total_similarity = (np.sum(similarity_matrix) - n) / (n * (n - 1))
            coherence_scores[label] = total_similarity
        
        return coherence_scores