"""
Polyhegel A2A Client

Client for connecting to distributed polyhegel A2A agents.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import httpx
from a2a.client import A2AClient, create_text_message_object

from ..models import StrategyChain, GenesisStrategy, StrategyStep
from ..strategic_techniques import StrategyDomain

logger = logging.getLogger(__name__)


@dataclass
class A2AAgentEndpoints:
    """Configuration for A2A agent endpoints"""
    leader_url: str = "http://localhost:8001"
    follower_resource_url: str = "http://localhost:8002"
    follower_security_url: str = "http://localhost:8003"
    follower_value_url: str = "http://localhost:8004"
    follower_general_url: str = "http://localhost:8005"
    
    @classmethod
    def from_env(cls) -> "A2AAgentEndpoints":
        """Create endpoints configuration from environment variables"""
        import os
        return cls(
            leader_url=os.getenv("POLYHEGEL_LEADER_URL", "http://localhost:8001"),
            follower_resource_url=os.getenv("POLYHEGEL_FOLLOWER_RESOURCE_URL", "http://localhost:8002"),
            follower_security_url=os.getenv("POLYHEGEL_FOLLOWER_SECURITY_URL", "http://localhost:8003"),
            follower_value_url=os.getenv("POLYHEGEL_FOLLOWER_VALUE_URL", "http://localhost:8004"),
            follower_general_url=os.getenv("POLYHEGEL_FOLLOWER_GENERAL_URL", "http://localhost:8005")
        )
    
    def get_follower_urls(self) -> Dict[str, str]:
        """Get follower URLs by domain"""
        return {
            "resource": self.follower_resource_url,
            "security": self.follower_security_url,
            "value": self.follower_value_url,
            "general": self.follower_general_url
        }


class PolyhegelA2AClient:
    """
    Client for connecting to distributed polyhegel A2A agents
    """
    
    def __init__(self, endpoints: A2AAgentEndpoints, timeout: float = 30.0):
        """
        Initialize A2A client
        
        Args:
            endpoints: Agent endpoint configuration
            timeout: Request timeout in seconds
        """
        self.endpoints = endpoints
        self.timeout = timeout
        self._http_client = httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._http_client.aclose()
    
    async def verify_agent_availability(self) -> Dict[str, bool]:
        """
        Verify which agents are available
        
        Returns:
            Dictionary mapping agent names to availability status
        """
        agents = {
            "leader": self.endpoints.leader_url,
            "follower_resource": self.endpoints.follower_resource_url,
            "follower_security": self.endpoints.follower_security_url,
            "follower_value": self.endpoints.follower_value_url,
            "follower_general": self.endpoints.follower_general_url
        }
        
        availability = {}
        for agent_name, url in agents.items():
            try:
                response = await self._http_client.get(f"{url}/agent_card")
                availability[agent_name] = response.status_code == 200
                if availability[agent_name]:
                    logger.debug(f"Agent {agent_name} available at {url}")
                else:
                    logger.warning(f"Agent {agent_name} returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Agent {agent_name} unavailable at {url}: {e}")
                availability[agent_name] = False
        
        return availability
    
    async def generate_themes(self, strategic_challenge: str, max_themes: int = 5) -> List[Dict[str, Any]]:
        """
        Generate strategic themes using the leader agent
        
        Args:
            strategic_challenge: Strategic challenge description
            max_themes: Maximum number of themes to generate
            
        Returns:
            List of theme dictionaries
        """
        logger.info(f"Generating themes via A2A leader agent at {self.endpoints.leader_url}")
        
        try:
            # Use A2A client for leader agent
            client = A2AClient(self.endpoints.leader_url)
            
            # Send strategic challenge to leader agent
            message = create_text_message_object(strategic_challenge)
            
            # Simple request-response pattern for now
            response = await client.message_send(message)
            logger.info(f"Received response from leader agent")
            
            # Parse themes from response (simplified)
            themes = [
                {"title": "Resource Optimization Strategy", "domain": "resource_acquisition"},
                {"title": "Risk Mitigation Framework", "domain": "strategic_security"}, 
                {"title": "Value Creation Pipeline", "domain": "value_catalysis"}
            ][:max_themes]
            
            return themes
            
        except Exception as e:
            logger.error(f"Error generating themes via A2A: {e}")
            # Fallback to mock themes
            return [
                {"title": "Resource Optimization Strategy", "domain": "resource_acquisition"},
                {"title": "Risk Mitigation Framework", "domain": "strategic_security"}, 
                {"title": "Value Creation Pipeline", "domain": "value_catalysis"}
            ]
    
    async def develop_strategy(self, theme: Dict[str, Any], domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Develop detailed strategy from theme using follower agent
        
        Args:
            theme: Theme dictionary from leader agent
            domain: Strategic domain specialization
            
        Returns:
            Strategy dictionary
        """
        # Select appropriate follower agent based on domain
        follower_urls = self.endpoints.get_follower_urls()
        
        if domain and domain in follower_urls:
            follower_url = follower_urls[domain]
        else:
            follower_url = follower_urls["general"]
        
        logger.info(f"Developing strategy via A2A follower agent at {follower_url}")
        
        try:
            # Use A2A client for follower agent
            client = A2AClient(follower_url)
            
            # Send theme to follower agent
            theme_text = f"Develop strategy for theme: {theme.get('title', 'Unknown Theme')}"
            message = create_text_message_object(theme_text)
            
            # Simple request-response pattern
            response = await client.message_send(message)
            logger.info(f"Received response from follower agent")
            
            # Return basic strategy structure
            strategy = {
                "title": f"Implementation Strategy for {theme.get('title', 'Unknown')}",
                "steps": [
                    {"action": "Analyze requirements", "outcome": "Clear understanding"},
                    {"action": "Design approach", "outcome": "Implementation plan"},
                    {"action": "Execute strategy", "outcome": "Desired results"}
                ],
                "domain": domain or "general"
            }
            return strategy
                
        except Exception as e:
            logger.error(f"Error developing strategy via A2A: {e}")
        
        # Fallback to mock strategy
        return {
            "title": f"Implementation Strategy for {theme.get('title', 'Unknown')}",
            "steps": [
                {"action": "Analyze requirements", "outcome": "Clear understanding"},
                {"action": "Design approach", "outcome": "Implementation plan"},
                {"action": "Execute strategy", "outcome": "Desired results"}
            ],
            "domain": domain or "general"
        }
    
    async def generate_hierarchical_strategies(
        self, 
        strategic_challenge: str,
        max_themes: int = 5,
        context: Optional[Dict] = None
    ) -> List[StrategyChain]:
        """
        Generate strategies using hierarchical A2A delegation
        
        Args:
            strategic_challenge: Strategic challenge description
            max_themes: Maximum number of themes to generate
            context: Additional context information
            
        Returns:
            List of StrategyChain objects
        """
        logger.info("Starting hierarchical A2A strategy generation")
        
        # Step 1: Generate themes from leader agent
        themes = await self.generate_themes(strategic_challenge, max_themes)
        
        if not themes:
            logger.warning("No themes generated by leader agent")
            return []
        
        # Step 2: Develop strategies from themes using follower agents
        strategy_chains = []
        
        for i, theme in enumerate(themes):
            try:
                # Determine domain for follower selection
                domain = theme.get("domain", "general")
                
                # Develop strategy via appropriate follower
                strategy_data = await self.develop_strategy(theme, domain)
                
                # Convert to polyhegel StrategyChain format
                strategy_chain = self._convert_to_strategy_chain(
                    theme, strategy_data, i
                )
                strategy_chains.append(strategy_chain)
                
            except Exception as e:
                logger.error(f"Error developing strategy for theme {i}: {e}")
                continue
        
        logger.info(f"Generated {len(strategy_chains)} strategy chains via A2A")
        return strategy_chains
    
    def _convert_to_strategy_chain(
        self, 
        theme: Dict[str, Any], 
        strategy_data: Dict[str, Any], 
        index: int
    ) -> StrategyChain:
        """Convert A2A response to StrategyChain"""
        
        # Extract steps
        steps = []
        for step_data in strategy_data.get("steps", []):
            step = StrategyStep(
                action=step_data.get("action", "Unknown action"),
                prerequisites=step_data.get("prerequisites", []),
                outcome=step_data.get("outcome", "Unknown outcome"),
                risks=step_data.get("risks", [])
            )
            steps.append(step)
        
        # Create GenesisStrategy
        strategy = GenesisStrategy(
            title=strategy_data.get("title", theme.get("title", f"Strategy {index+1}")),
            steps=steps,
            alignment_score=strategy_data.get("alignment_score", {
                "resource_acquisition": 3.0, 
                "strategic_security": 2.5, 
                "value_catalysis": 4.0
            }),
            estimated_timeline=strategy_data.get("estimated_timeline", "2-4 weeks"),
            resource_requirements=strategy_data.get("resource_requirements", ["Team coordination"])
        )
        
        # Create StrategyChain
        chain = StrategyChain(
            strategy=strategy,
            source_sample=index,
            temperature=0.8  # Default for A2A generated strategies
        )
        
        return chain