"""
Embedding module for strategy chains
"""

import logging
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from .models import StrategyChain
from .config import Config

logger = logging.getLogger(__name__)


class StrategyEmbedder:
    """Handles embedding of strategy chains for clustering"""

    def __init__(self, model_name: str = None):
        """
        Initialize embedder with specified model

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name or Config.DEFAULT_EMBEDDING_MODEL
        logger.info(f"Initializing embedder with model: {self.model_name}")
        self.embedder = SentenceTransformer(self.model_name)

    def embed_strategies(self, chains: List[StrategyChain]) -> None:
        """
        Create embeddings for each strategy chain

        Args:
            chains: List of strategy chains to embed
        """
        logger.info(f"Creating embeddings for {len(chains)} strategy chains")

        for chain in chains:
            text = self._extract_text_from_chain(chain)
            embedding_tensor = self.embedder.encode(text)
            # Convert tensor to numpy array
            chain.embedding = np.array(embedding_tensor)

    def _extract_text_from_chain(self, chain: StrategyChain) -> str:
        """
        Extract all relevant text from a strategy chain for embedding

        Args:
            chain: Strategy chain to process

        Returns:
            Concatenated text representation
        """
        text_parts = [
            chain.strategy.title,
            chain.strategy.estimated_timeline,
        ]

        # Add resource requirements
        text_parts.extend(chain.strategy.resource_requirements)

        # Add all step information
        for step in chain.strategy.steps:
            text_parts.extend([step.action, step.outcome, " ".join(step.prerequisites), " ".join(step.risks)])

        # Add alignment scores as text
        for domain, score in chain.strategy.alignment_score.items():
            text_parts.append(f"{domain}: {score}")

        return " ".join(filter(None, text_parts))

    def compute_similarity_matrix(self, chains: List[StrategyChain]) -> np.ndarray:
        """
        Compute pairwise similarity matrix for all chains

        Args:
            chains: List of strategy chains with embeddings

        Returns:
            Similarity matrix
        """
        if not chains:
            raise ValueError("No chains provided")

        # Filter valid embeddings
        valid_embeddings = [chain.embedding for chain in chains if chain.embedding is not None]
        if not valid_embeddings:
            raise ValueError("No valid embeddings found in chains")

        embeddings = np.vstack(valid_embeddings)

        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(embeddings)

        return np.array(similarity_matrix)

    def find_similar_strategies(
        self, target_chain: StrategyChain, chains: List[StrategyChain], top_k: int = 5
    ) -> List[Tuple[StrategyChain, float]]:
        """
        Find the most similar strategies to a target chain

        Args:
            target_chain: The chain to find similarities for
            chains: List of chains to search
            top_k: Number of similar strategies to return

        Returns:
            List of (chain, similarity_score) tuples
        """
        if target_chain.embedding is None:
            raise ValueError("Target chain must have embedding")

        from sklearn.metrics.pairwise import cosine_similarity

        similarities = []
        for chain in chains:
            if chain.embedding is not None and chain != target_chain:
                similarity = cosine_similarity([target_chain.embedding], [chain.embedding])[0][0]
                similarities.append((chain, similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
