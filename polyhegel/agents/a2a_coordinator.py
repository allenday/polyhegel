"""
A2A-based agent coordination for polyhegel

This module replaces the custom AgentCoordinator with A2A-based
client/server communication for distributed agent coordination.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard, 
    MessageSendParams, 
    SendMessageRequest,
    SendStreamingMessageRequest,
    Message,
    TextPart
)

from ..models import StrategicTheme, GenesisStrategy
from ..strategic_techniques import CLMMandate
from .base import AgentContext

logger = logging.getLogger(__name__)


@dataclass
class A2AAgentEndpoint:
    """Configuration for an A2A agent endpoint"""
    agent_id: str
    base_url: str
    capabilities: List[str]  # Skills this agent supports
    specialization: Optional[CLMMandate] = None
    description: str = ""


class A2ACoordinator:
    """
    A2A-based agent coordinator for distributed strategic agents
    
    Replaces the custom AgentCoordinator with standardized A2A 
    client/server communication patterns.
    """
    
    def __init__(self, httpx_client: Optional[httpx.AsyncClient] = None):
        """
        Initialize A2A coordinator
        
        Args:
            httpx_client: Optional shared HTTP client for agent communication
        """
        self.httpx_client = httpx_client
        self._own_client = httpx_client is None
        self.agent_endpoints: Dict[str, A2AAgentEndpoint] = {}
        self.agent_cards: Dict[str, AgentCard] = {}
        self.clients: Dict[str, A2AClient] = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self._own_client:
            self.httpx_client = httpx.AsyncClient()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._own_client and self.httpx_client:
            await self.httpx_client.aclose()
    
    async def register_agent_endpoint(self, endpoint: A2AAgentEndpoint) -> bool:
        """
        Register an A2A agent endpoint and fetch its AgentCard
        
        Args:
            endpoint: Agent endpoint configuration
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Fetch agent card
            resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=endpoint.base_url
            )
            
            agent_card = await resolver.get_agent_card()
            
            # Create A2A client
            client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=agent_card
            )
            
            # Store agent info
            self.agent_endpoints[endpoint.agent_id] = endpoint
            self.agent_cards[endpoint.agent_id] = agent_card
            self.clients[endpoint.agent_id] = client
            
            logger.info(f"Registered A2A agent: {endpoint.agent_id} at {endpoint.base_url}")
            logger.info(f"Agent skills: {[skill.name for skill in agent_card.skills]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {endpoint.agent_id}: {e}")
            return False
    
    def get_agents_for_skill(self, skill_id: str) -> List[str]:
        """
        Get agent IDs that support a specific skill
        
        Args:
            skill_id: The skill ID to search for
            
        Returns:
            List of agent IDs that support the skill
        """
        matching_agents = []
        
        for agent_id, card in self.agent_cards.items():
            if any(skill.id == skill_id for skill in card.skills):
                matching_agents.append(agent_id)
        
        return matching_agents
    
    def get_agents_for_specialization(self, specialization: CLMMandate) -> List[str]:
        """
        Get agent IDs with specific CLM mandate specialization
        
        Args:
            specialization: CLM mandate specialization
            
        Returns:
            List of agent IDs with that specialization
        """
        matching_agents = []
        
        for agent_id, endpoint in self.agent_endpoints.items():
            if endpoint.specialization == specialization:
                matching_agents.append(agent_id)
        
        return matching_agents
    
    async def send_theme_generation_request(
        self, 
        agent_id: str, 
        strategic_challenge: str,
        context: Optional[AgentContext] = None
    ) -> List[StrategicTheme]:
        """
        Send strategic theme generation request to leader agent
        
        Args:
            agent_id: ID of the leader agent
            strategic_challenge: Strategic challenge description
            context: Optional agent context
            
        Returns:
            List of generated strategic themes
        """
        if agent_id not in self.clients:
            raise ValueError(f"Agent {agent_id} not registered")
        
        client = self.clients[agent_id]
        
        # Create message request
        message = Message(
            role="user",
            parts=[TextPart(kind="text", text=strategic_challenge)],
            message_id=uuid.uuid4().hex
        )
        
        # Add context as metadata if provided
        metadata = {}
        if context:
            metadata = {
                "constraints": context.constraints,
                "objectives": context.objectives,
                "stakeholders": context.stakeholders,
                "timeline": context.timeline,
                "resources": context.resources
            }
        
        params = MessageSendParams(
            message=message,
            metadata=metadata
        )
        
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=params
        )
        
        try:
            logger.info(f"Sending theme generation request to {agent_id}")
            
            # Send streaming request to get real-time updates
            streaming_request = SendStreamingMessageRequest(
                id=request.id,
                params=params
            )
            
            themes = []
            stream_response = client.send_message_streaming(streaming_request)
            
            async for chunk in stream_response:
                logger.info(f"Received chunk from {agent_id}: {chunk.model_dump_json()}")
                
                # Look for artifacts containing theme data
                if hasattr(chunk, 'artifacts') and chunk.artifacts:
                    logger.info(f"Found {len(chunk.artifacts)} artifacts")
                    for artifact in chunk.artifacts:
                        logger.info(f"Processing artifact: {type(artifact)}")
                        if hasattr(artifact, 'parts') and artifact.parts:
                            for part in artifact.parts:
                                logger.info(f"Processing part: {type(part)}")
                                # A2A Part structure: part.root contains the actual DataPart
                                if hasattr(part, 'root') and hasattr(part.root, 'data'):
                                    data = part.root.data
                                    if isinstance(data, dict) and 'themes' in data:
                                        logger.info(f"Found themes data: {len(data['themes'])} themes")
                                        theme_data = data['themes']
                                        for theme_dict in theme_data:
                                            theme = StrategicTheme(**theme_dict)
                                            themes.append(theme)
                                # Legacy direct data access
                                elif hasattr(part, 'data') and isinstance(part.data, dict) and 'themes' in part.data:
                                    logger.info(f"Found themes data: {len(part.data['themes'])} themes")
                                    theme_data = part.data['themes']
                                    for theme_dict in theme_data:
                                        theme = StrategicTheme(**theme_dict)
                                        themes.append(theme)
                        elif hasattr(artifact, 'data') and isinstance(artifact.data, dict) and 'themes' in artifact.data:
                            # Direct artifact data access
                            logger.info(f"Found direct themes data: {len(artifact.data['themes'])} themes")
                            theme_data = artifact.data['themes']
                            for theme_dict in theme_data:
                                theme = StrategicTheme(**theme_dict)
                                themes.append(theme)
            
            logger.info(f"Received {len(themes)} themes from {agent_id}")
            return themes
            
        except Exception as e:
            logger.error(f"Failed to get themes from {agent_id}: {e}")
            raise
    
    async def send_strategy_development_request(
        self,
        agent_id: str,
        theme: StrategicTheme,
        context: Optional[AgentContext] = None
    ) -> Optional[GenesisStrategy]:
        """
        Send strategy development request to follower agent
        
        Args:
            agent_id: ID of the follower agent
            theme: Strategic theme to develop
            context: Optional agent context
            
        Returns:
            Developed genesis strategy or None if failed
        """
        if agent_id not in self.clients:
            raise ValueError(f"Agent {agent_id} not registered")
        
        client = self.clients[agent_id]
        
        # Create structured request with theme and context
        request_data = {
            "theme": theme.model_dump(),
            "context": context.model_dump() if context else {}
        }
        
        import json
        message_text = json.dumps(request_data)
        
        message = Message(
            role="user",
            parts=[TextPart(kind="text", text=message_text)],
            message_id=uuid.uuid4().hex
        )
        
        params = MessageSendParams(message=message)
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=params
        )
        
        try:
            logger.info(f"Sending strategy development request to {agent_id}")
            
            # Send streaming request
            streaming_request = SendStreamingMessageRequest(
                id=request.id,
                params=params
            )
            
            strategy = None
            stream_response = client.send_message_streaming(streaming_request)
            
            async for chunk in stream_response:
                logger.info(f"Received chunk from {agent_id}")
                
                # Look for artifacts containing strategy data
                if hasattr(chunk, 'artifacts') and chunk.artifacts:
                    for artifact in chunk.artifacts:
                        if hasattr(artifact, 'parts') and artifact.parts:
                            for part in artifact.parts:
                                # A2A Part structure: part.root contains the actual DataPart
                                if hasattr(part, 'root') and hasattr(part.root, 'data'):
                                    data = part.root.data
                                    if isinstance(data, dict) and 'strategy' in data:
                                        strategy_data = data['strategy']
                                        strategy = GenesisStrategy(**strategy_data)
                                # Legacy direct data access
                                elif hasattr(part, 'data') and isinstance(part.data, dict) and 'strategy' in part.data:
                                    strategy_data = part.data['strategy']
                                    strategy = GenesisStrategy(**strategy_data)
            
            if strategy:
                logger.info(f"Received strategy '{strategy.title}' from {agent_id}")
            else:
                logger.warning(f"No strategy received from {agent_id}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to get strategy from {agent_id}: {e}")
            return None
    
    async def coordinate_hierarchical_generation(
        self,
        strategic_challenge: str,
        context: Optional[AgentContext] = None,
        leader_agent_id: str = "leader",
        max_themes: int = 5
    ) -> List[GenesisStrategy]:
        """
        Coordinate full hierarchical strategy generation workflow
        
        Args:
            strategic_challenge: Strategic challenge description
            context: Optional agent context
            leader_agent_id: ID of leader agent to use
            max_themes: Maximum themes to generate
            
        Returns:
            List of developed strategies
        """
        strategies = []
        
        try:
            # Step 1: Generate themes with leader agent
            logger.info("Step 1: Generating strategic themes...")
            themes = await self.send_theme_generation_request(
                leader_agent_id, 
                strategic_challenge, 
                context
            )
            
            if not themes:
                logger.warning("No themes generated by leader agent")
                return strategies
            
            # Limit themes if needed
            if len(themes) > max_themes:
                themes = themes[:max_themes]
                logger.info(f"Limited to {max_themes} themes")
            
            # Step 2: Develop strategies with follower agents
            logger.info(f"Step 2: Developing strategies from {len(themes)} themes...")
            
            for theme in themes:
                # Find best follower agent for this theme
                follower_agent_id = self._select_follower_for_theme(theme)
                
                if follower_agent_id:
                    strategy = await self.send_strategy_development_request(
                        follower_agent_id, 
                        theme, 
                        context
                    )
                    
                    if strategy:
                        strategies.append(strategy)
                else:
                    logger.warning(f"No suitable follower found for theme: {theme.title}")
            
            logger.info(f"Generated {len(strategies)} strategies via A2A coordination")
            return strategies
            
        except Exception as e:
            logger.error(f"Hierarchical generation coordination failed: {e}")
            raise
    
    def _select_follower_for_theme(self, theme: StrategicTheme) -> Optional[str]:
        """
        Select best follower agent for developing a theme
        
        Args:
            theme: Strategic theme to develop
            
        Returns:
            Agent ID of best follower or None
        """
        # Get primary mandate for theme
        primary_mandate_key = theme.get_primary_mandate()
        
        if primary_mandate_key:
            # Map mandate key to CLMMandate enum
            mandate_mapping = {
                "2.1": CLMMandate.RESOURCE_ACQUISITION,
                "2.2": CLMMandate.STRATEGIC_SECURITY,
                "2.3": CLMMandate.VALUE_CATALYSIS
            }
            
            mandate = mandate_mapping.get(primary_mandate_key)
            if mandate:
                # Find specialized follower
                specialized_agents = self.get_agents_for_specialization(mandate)
                if specialized_agents:
                    return specialized_agents[0]  # Use first available
        
        # Fallback to general follower
        general_followers = [
            agent_id for agent_id, endpoint in self.agent_endpoints.items()
            if endpoint.specialization is None and "develop_detailed_strategy" in endpoint.capabilities
        ]
        
        return general_followers[0] if general_followers else None
    
    def get_coordination_summary(self) -> Dict[str, Any]:
        """Get summary of A2A coordination setup"""
        
        specializations = {}
        for agent_id, endpoint in self.agent_endpoints.items():
            if endpoint.specialization:
                spec_name = endpoint.specialization.value
                if spec_name not in specializations:
                    specializations[spec_name] = []
                specializations[spec_name].append(agent_id)
        
        return {
            "total_agents": len(self.agent_endpoints),
            "agent_endpoints": {
                agent_id: {"url": endpoint.base_url, "capabilities": endpoint.capabilities}
                for agent_id, endpoint in self.agent_endpoints.items()
            },
            "specializations": specializations,
            "skills_available": list(set(
                skill.id 
                for card in self.agent_cards.values() 
                for skill in card.skills
            ))
        }