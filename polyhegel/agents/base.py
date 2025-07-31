"""
Base agent classes for hierarchical strategic planning

This module defines the foundational agent architecture for polyhegel's
hierarchical planning system, inspired by LLM-As-Hierarchical-Policy.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic_ai import Agent
from pydantic import BaseModel

from ..strategic_techniques import StrategicTechnique, CLMMandate

logger = logging.getLogger(__name__)


class AgentRole(BaseModel):
    """Defines an agent's role and responsibilities"""
    name: str
    description: str
    mandate: Optional[CLMMandate] = None
    specialization: Optional[str] = None
    hierarchy_level: int = 0  # 0 = leader, 1+ = follower levels


class AgentCapabilities(BaseModel):
    """Defines an agent's capabilities and constraints"""
    can_generate_strategies: bool = False
    can_evaluate_strategies: bool = False
    can_coordinate_agents: bool = False
    max_strategy_steps: Optional[int] = None
    preferred_techniques: List[str] = []
    supported_mandates: List[CLMMandate] = []


class AgentContext(BaseModel):
    """Context information for agent operations"""
    strategic_challenge: str
    constraints: Dict[str, Any] = {}
    objectives: List[str] = []
    stakeholders: List[str] = []
    timeline: Optional[str] = None
    resources: List[str] = []


class AgentResponse(BaseModel):
    """Base response structure for agent outputs"""
    agent_id: str
    agent_role: str
    success: bool
    content: Any
    reasoning: Optional[str] = None
    confidence: float = 1.0
    next_actions: List[str] = []
    recommendations: List[str] = []


class BaseAgent(ABC):
    """
    Abstract base class for all polyhegel agents
    
    This class defines the common interface and behavior patterns
    for both leader and follower agents in the hierarchical system.
    """
    
    def __init__(self,
                 agent_id: str,
                 role: AgentRole,
                 capabilities: AgentCapabilities,
                 model: Any,
                 system_prompt: Optional[str] = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique identifier for this agent
            role: Agent role definition
            capabilities: Agent capabilities
            model: pydantic-ai model instance
            system_prompt: Optional custom system prompt
        """
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.model = model
        
        # Build system prompt
        self.system_prompt = system_prompt or self._build_system_prompt()
        
        # Initialize pydantic-ai agent (skip for mock models in tests)
        if hasattr(model, '_mock_name') or str(type(model)).find('Mock') != -1:
            # This is a mock model, don't initialize pydantic agent
            self.pydantic_agent = None
        else:
            self.pydantic_agent = Agent(
                self.model,
                system_prompt=self.system_prompt
            )
        
        # State tracking
        self.context: Optional[AgentContext] = None
        self.interaction_history: List[Dict] = []
        
        logger.info(f"Initialized {self.role.name} agent: {self.agent_id}")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on role and capabilities"""
        prompt_parts = [
            f"You are a {self.role.name} in a hierarchical strategic planning system.",
            f"Role: {self.role.description}",
        ]
        
        if self.role.mandate:
            prompt_parts.append(f"Primary CLM Mandate: {self.role.mandate.value}")
        
        if self.role.specialization:
            prompt_parts.append(f"Specialization: {self.role.specialization}")
        
        # Add capability-specific instructions
        if self.capabilities.can_generate_strategies:
            prompt_parts.append("You can generate strategic plans and recommendations.")
        
        if self.capabilities.can_evaluate_strategies:
            prompt_parts.append("You can evaluate and compare strategic approaches.")
        
        if self.capabilities.can_coordinate_agents:
            prompt_parts.append("You can coordinate with other agents and delegate tasks.")
        
        if self.capabilities.preferred_techniques:
            techniques_str = ", ".join(self.capabilities.preferred_techniques)
            prompt_parts.append(f"Preferred strategic techniques: {techniques_str}")
        
        # Add hierarchy-specific behavior
        if self.role.hierarchy_level == 0:
            prompt_parts.append("As a leader agent, focus on high-level strategic themes and direction.")
        else:
            prompt_parts.append("As a follower agent, focus on detailed implementation and execution.")
        
        prompt_parts.append("Always provide clear reasoning for your recommendations.")
        
        return "\n\n".join(prompt_parts)
    
    def set_context(self, context: AgentContext):
        """Set the strategic context for this agent"""
        self.context = context
        logger.debug(f"Agent {self.agent_id} context set: {context.strategic_challenge}")
    
    def add_interaction(self, interaction_type: str, content: Any, metadata: Dict = None):
        """Add interaction to history for context tracking"""
        interaction = {
            "type": interaction_type,
            "content": content,
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "agent", logging.INFO, "", 0, "", (), None
            )) if logger.handlers else "unknown",
            "metadata": metadata or {}
        }
        self.interaction_history.append(interaction)
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a request and return response
        
        Args:
            request: Request dictionary with task details
            
        Returns:  
            AgentResponse with results
        """
        pass
    
    @abstractmethod
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Return summary of agent capabilities for coordination"""
        pass
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that this agent can handle the request"""
        request_type = request.get("type", "")
        
        # Check basic capability alignment
        if request_type == "generate_strategy" and not self.capabilities.can_generate_strategies:
            return False
        
        if request_type == "evaluate_strategy" and not self.capabilities.can_evaluate_strategies:
            return False
        
        # Check mandate alignment if specified
        if "mandate" in request:
            required_mandate = CLMMandate(request["mandate"])
            if (self.capabilities.supported_mandates and 
                required_mandate not in self.capabilities.supported_mandates):
                return False
        
        return True
    
    def create_response(self,
                       success: bool,
                       content: Any,
                       reasoning: Optional[str] = None,
                       confidence: float = 1.0,
                       next_actions: List[str] = None,
                       recommendations: List[str] = None) -> AgentResponse:
        """Create standardized agent response"""
        return AgentResponse(
            agent_id=self.agent_id,
            agent_role=self.role.name,
            success=success,
            content=content,
            reasoning=reasoning,
            confidence=confidence,
            next_actions=next_actions or [],
            recommendations=recommendations or []
        )
    
    async def collaborate_with(self, other_agent: 'BaseAgent', task: Dict[str, Any]) -> AgentResponse:
        """
        Collaborate with another agent on a task
        
        Args:
            other_agent: Agent to collaborate with
            task: Task definition
            
        Returns:
            Combined response from collaboration
        """
        if not self.capabilities.can_coordinate_agents:
            return self.create_response(
                success=False,
                content="Agent cannot coordinate with others",
                reasoning="Coordination capability not enabled"
            )
        
        # Basic collaboration pattern - can be overridden by subclasses
        logger.info(f"Agent {self.agent_id} collaborating with {other_agent.agent_id}")
        
        # Validate other agent can handle the task
        if not other_agent.validate_request(task):
            return self.create_response(
                success=False,
                content="Collaborating agent cannot handle task",
                reasoning=f"Agent {other_agent.agent_id} lacks required capabilities"
            )
        
        # Delegate task to other agent
        response = await other_agent.process_request(task)
        
        # Record collaboration
        self.add_interaction("collaboration", {
            "partner_agent": other_agent.agent_id,
            "task": task,
            "response": response.model_dump()
        })
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.model_dump(),
            "capabilities": self.capabilities.model_dump(),
            "context_set": self.context is not None,
            "interaction_count": len(self.interaction_history),
            "last_interaction": self.interaction_history[-1] if self.interaction_history else None
        }
    
    def reset(self):
        """Reset agent state"""
        self.context = None
        self.interaction_history = []
        logger.info(f"Agent {self.agent_id} state reset")
    
    def __str__(self) -> str:
        """String representation of agent"""
        return f"{self.role.name}Agent({self.agent_id})"
    
    def __repr__(self) -> str:
        """Detailed representation of agent"""
        return (f"{self.__class__.__name__}("
                f"agent_id='{self.agent_id}', "
                f"role='{self.role.name}', "
                f"hierarchy_level={self.role.hierarchy_level})")


class AgentCoordinator:
    """Coordinates interactions between multiple agents"""
    
    def __init__(self):
        """Initialize agent coordinator"""
        self.agents: Dict[str, BaseAgent] = {}
        self.coordination_history: List[Dict] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_role(self, role_name: str) -> List[BaseAgent]:
        """Get all agents with specific role"""
        return [agent for agent in self.agents.values() 
                if agent.role.name == role_name]
    
    def get_agents_by_mandate(self, mandate: CLMMandate) -> List[BaseAgent]:
        """Get all agents supporting specific mandate"""
        return [agent for agent in self.agents.values()
                if mandate in agent.capabilities.supported_mandates]
    
    async def coordinate_task(self, task: Dict[str, Any]) -> List[AgentResponse]:
        """
        Coordinate a task across multiple agents
        
        Args:
            task: Task definition with agent requirements
            
        Returns:
            List of responses from participating agents
        """
        responses = []
        task_type = task.get("type", "")
        
        # Find capable agents
        capable_agents = [
            agent for agent in self.agents.values()
            if agent.validate_request(task)
        ]
        
        if not capable_agents:
            logger.warning(f"No agents capable of handling task type: {task_type}")
            return responses
        
        # Execute task with capable agents
        for agent in capable_agents:
            try:
                response = await agent.process_request(task)
                responses.append(response)
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} failed task: {e}")
                error_response = agent.create_response(
                    success=False,
                    content=f"Task execution failed: {e}",
                    reasoning="Exception during task processing"
                )
                responses.append(error_response)
        
        # Record coordination
        self.coordination_history.append({
            "task": task,
            "participating_agents": [agent.agent_id for agent in capable_agents],
            "responses": [r.model_dump() for r in responses]
        })
        
        return responses
    
    def get_coordination_summary(self) -> Dict[str, Any]:
        """Get summary of coordination activities"""
        return {
            "registered_agents": len(self.agents),
            "agent_roles": list(set(agent.role.name for agent in self.agents.values())),
            "coordination_events": len(self.coordination_history),
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()}
        }