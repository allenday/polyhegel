"""
Tests for base agent classes and coordination
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from polyhegel.agents.base import (
    BaseAgent, AgentRole, AgentCapabilities, AgentContext, AgentResponse,
    AgentCoordinator
)
from polyhegel.strategic_techniques import CLMMandate


class TestAgentRole:
    """Test AgentRole model"""
    
    def test_agent_role_creation(self):
        """Test creating agent role"""
        role = AgentRole(
            name="TestAgent",
            description="Test agent for unit testing",
            mandate=CLMMandate.RESOURCE_ACQUISITION,
            specialization="Testing",
            hierarchy_level=1
        )
        
        assert role.name == "TestAgent"
        assert role.description == "Test agent for unit testing"
        assert role.mandate == CLMMandate.RESOURCE_ACQUISITION
        assert role.specialization == "Testing"
        assert role.hierarchy_level == 1

    def test_agent_role_defaults(self):
        """Test agent role with defaults"""
        role = AgentRole(
            name="MinimalAgent",
            description="Minimal agent definition"
        )
        
        assert role.mandate is None
        assert role.specialization is None
        assert role.hierarchy_level == 0


class TestAgentCapabilities:
    """Test AgentCapabilities model"""
    
    def test_capabilities_creation(self):
        """Test creating agent capabilities"""
        capabilities = AgentCapabilities(
            can_generate_strategies=True,
            can_evaluate_strategies=True,
            can_coordinate_agents=False,
            max_strategy_steps=5,
            preferred_techniques=["Stakeholder Alignment Matrix"],
            supported_mandates=[CLMMandate.RESOURCE_ACQUISITION]
        )
        
        assert capabilities.can_generate_strategies is True
        assert capabilities.can_evaluate_strategies is True
        assert capabilities.can_coordinate_agents is False
        assert capabilities.max_strategy_steps == 5
        assert "Stakeholder Alignment Matrix" in capabilities.preferred_techniques
        assert CLMMandate.RESOURCE_ACQUISITION in capabilities.supported_mandates

    def test_capabilities_defaults(self):
        """Test capabilities with defaults"""
        capabilities = AgentCapabilities()
        
        assert capabilities.can_generate_strategies is False
        assert capabilities.can_evaluate_strategies is False
        assert capabilities.can_coordinate_agents is False
        assert capabilities.max_strategy_steps is None
        assert capabilities.preferred_techniques == []
        assert capabilities.supported_mandates == []


class TestAgentContext:
    """Test AgentContext model"""
    
    def test_context_creation(self):
        """Test creating agent context"""
        context = AgentContext(
            strategic_challenge="Build a strategic planning system",
            constraints={"budget": 100000, "timeline": "6 months"},
            objectives=["Improve decision making", "Reduce planning time"],
            stakeholders=["Product team", "Engineering", "Leadership"],
            timeline="Q2 2024",
            resources=["Development team", "Computing resources"]
        )
        
        assert context.strategic_challenge == "Build a strategic planning system"
        assert context.constraints["budget"] == 100000
        assert len(context.objectives) == 2
        assert "Product team" in context.stakeholders
        assert context.timeline == "Q2 2024"
        assert "Development team" in context.resources


class TestAgentResponse:
    """Test AgentResponse model"""
    
    def test_response_creation(self):
        """Test creating agent response"""
        response = AgentResponse(
            agent_id="test-agent-1",
            agent_role="TestAgent",
            success=True,
            content="Test response content",
            reasoning="This is test reasoning",
            confidence=0.85,
            next_actions=["Action 1", "Action 2"],
            recommendations=["Recommendation 1"]
        )
        
        assert response.agent_id == "test-agent-1"
        assert response.agent_role == "TestAgent"
        assert response.success is True
        assert response.content == "Test response content"
        assert response.reasoning == "This is test reasoning"
        assert response.confidence == 0.85
        assert len(response.next_actions) == 2
        assert len(response.recommendations) == 1


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing"""
    
    async def process_request(self, request):
        """Test implementation of abstract method"""
        return self.create_response(
            success=True,
            content=f"Processed request: {request.get('type', 'unknown')}",
            reasoning="Test agent processing"
        )
    
    def get_capabilities_summary(self):
        """Test implementation of abstract method"""
        return {
            "can_generate": self.capabilities.can_generate_strategies,
            "can_evaluate": self.capabilities.can_evaluate_strategies,
            "supported_mandates": [m.value for m in self.capabilities.supported_mandates]
        }


class TestBaseAgent:
    """Test BaseAgent functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_model = MagicMock()
        
        self.role = AgentRole(
            name="TestAgent",
            description="Agent for testing",
            mandate=CLMMandate.RESOURCE_ACQUISITION,
            hierarchy_level=1
        )
        
        self.capabilities = AgentCapabilities(
            can_generate_strategies=True,
            can_evaluate_strategies=False,
            supported_mandates=[CLMMandate.RESOURCE_ACQUISITION]
        )
        
        self.agent = ConcreteTestAgent(
            agent_id="test-agent-1",
            role=self.role,
            capabilities=self.capabilities,
            model=self.mock_model
        )

    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent.agent_id == "test-agent-1"
        assert self.agent.role.name == "TestAgent"
        assert self.agent.capabilities.can_generate_strategies is True
        assert self.agent.model == self.mock_model
        assert self.agent.context is None
        assert len(self.agent.interaction_history) == 0

    def test_system_prompt_building(self):
        """Test system prompt construction"""
        prompt = self.agent.system_prompt
        
        assert "TestAgent" in prompt
        assert "Agent for testing" in prompt
        assert "2.1" in prompt  # CLM mandate
        assert "follower agent" in prompt  # hierarchy level 1
        assert "generate strategic plans" in prompt  # capability

    def test_set_context(self):
        """Test setting agent context"""
        context = AgentContext(
            strategic_challenge="Test challenge",
            objectives=["Objective 1"],
            stakeholders=["Stakeholder 1"]
        )
        
        self.agent.set_context(context)
        assert self.agent.context == context
        assert self.agent.context.strategic_challenge == "Test challenge"

    def test_add_interaction(self):
        """Test adding interactions to history"""
        self.agent.add_interaction("test", "test content", {"meta": "data"})
        
        assert len(self.agent.interaction_history) == 1
        interaction = self.agent.interaction_history[0]
        assert interaction["type"] == "test"
        assert interaction["content"] == "test content"
        assert interaction["metadata"]["meta"] == "data"

    @pytest.mark.asyncio
    async def test_process_request(self):
        """Test processing requests"""
        request = {"type": "test_request", "data": "test"}
        response = await self.agent.process_request(request)
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_id == "test-agent-1"
        assert "test_request" in response.content

    def test_validate_request(self):
        """Test request validation"""
        # Valid request for this agent
        valid_request = {
            "type": "generate_strategy",
            "mandate": "2.1"
        }
        assert self.agent.validate_request(valid_request) is True
        
        # Invalid request - wrong capability
        invalid_request = {
            "type": "evaluate_strategy"
        }
        assert self.agent.validate_request(invalid_request) is False
        
        # Invalid request - wrong mandate
        wrong_mandate_request = {
            "type": "generate_strategy", 
            "mandate": "2.2"
        }
        assert self.agent.validate_request(wrong_mandate_request) is False

    def test_create_response(self):
        """Test response creation"""
        response = self.agent.create_response(
            success=True,
            content="Test content",
            reasoning="Test reasoning",
            confidence=0.9
        )
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.content == "Test content"
        assert response.reasoning == "Test reasoning"
        assert response.confidence == 0.9
        assert response.agent_id == "test-agent-1"

    @pytest.mark.asyncio
    async def test_collaboration_without_capability(self):
        """Test collaboration when agent lacks coordination capability"""
        # Create another agent
        other_agent = ConcreteTestAgent(
            agent_id="other-agent",
            role=self.role,
            capabilities=self.capabilities,
            model=self.mock_model
        )
        
        # Try to collaborate (agent lacks coordination capability)
        task = {"type": "test_task"}
        response = await self.agent.collaborate_with(other_agent, task)
        
        assert response.success is False
        assert "cannot coordinate" in response.content

    @pytest.mark.asyncio
    async def test_collaboration_with_capability(self):
        """Test collaboration when agent has coordination capability"""
        # Create agent with coordination capability
        coord_capabilities = AgentCapabilities(
            can_generate_strategies=True,
            can_coordinate_agents=True,
            supported_mandates=[CLMMandate.RESOURCE_ACQUISITION]
        )
        
        coord_agent = ConcreteTestAgent(
            agent_id="coordinator",
            role=self.role,
            capabilities=coord_capabilities,
            model=self.mock_model
        )
        
        # Create target agent
        target_agent = ConcreteTestAgent(
            agent_id="target",
            role=self.role,
            capabilities=self.capabilities,
            model=self.mock_model
        )
        
        # Test collaboration
        task = {"type": "generate_strategy", "mandate": "2.1"}
        response = await coord_agent.collaborate_with(target_agent, task)
        
        assert response.success is True
        assert response.agent_id == "target"  # Response comes from target agent

    def test_get_status(self):
        """Test getting agent status"""
        status = self.agent.get_status()
        
        assert status["agent_id"] == "test-agent-1"
        assert "role" in status
        assert "capabilities" in status
        assert status["context_set"] is False
        assert status["interaction_count"] == 0

    def test_reset(self):
        """Test agent reset"""
        # Set some state
        context = AgentContext(strategic_challenge="Test")
        self.agent.set_context(context)
        self.agent.add_interaction("test", "content")
        
        # Verify state is set
        assert self.agent.context is not None
        assert len(self.agent.interaction_history) > 0
        
        # Reset and verify
        self.agent.reset()
        assert self.agent.context is None
        assert len(self.agent.interaction_history) == 0

    def test_string_representations(self):
        """Test string representations"""
        str_repr = str(self.agent)
        assert "TestAgentAgent(test-agent-1)" == str_repr
        
        repr_str = repr(self.agent)
        assert "ConcreteTestAgent" in repr_str
        assert "test-agent-1" in repr_str


class TestAgentCoordinator:
    """Test AgentCoordinator functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.coordinator = AgentCoordinator()
        self.mock_model = MagicMock()
        
        # Create test agents
        self.agent1 = ConcreteTestAgent(
            agent_id="agent-1",
            role=AgentRole(name="TestAgent1", description="First test agent"),
            capabilities=AgentCapabilities(
                can_generate_strategies=True,
                supported_mandates=[CLMMandate.RESOURCE_ACQUISITION]
            ),
            model=self.mock_model
        )
        
        self.agent2 = ConcreteTestAgent(
            agent_id="agent-2", 
            role=AgentRole(name="TestAgent2", description="Second test agent", mandate=CLMMandate.STRATEGIC_SECURITY),
            capabilities=AgentCapabilities(
                can_evaluate_strategies=True,
                supported_mandates=[CLMMandate.STRATEGIC_SECURITY]
            ),
            model=self.mock_model
        )

    def test_coordinator_initialization(self):
        """Test coordinator initialization"""
        assert len(self.coordinator.agents) == 0
        assert len(self.coordinator.coordination_history) == 0

    def test_register_agent(self):
        """Test agent registration"""
        self.coordinator.register_agent(self.agent1)
        
        assert len(self.coordinator.agents) == 1
        assert "agent-1" in self.coordinator.agents
        assert self.coordinator.agents["agent-1"] == self.agent1

    def test_get_agent(self):
        """Test getting agent by ID"""
        self.coordinator.register_agent(self.agent1)
        
        retrieved = self.coordinator.get_agent("agent-1")
        assert retrieved == self.agent1
        
        not_found = self.coordinator.get_agent("nonexistent")
        assert not_found is None

    def test_get_agents_by_role(self):
        """Test getting agents by role"""
        self.coordinator.register_agent(self.agent1)
        self.coordinator.register_agent(self.agent2)
        
        test_agents = self.coordinator.get_agents_by_role("TestAgent1")
        assert len(test_agents) == 1
        assert test_agents[0] == self.agent1

    def test_get_agents_by_mandate(self):
        """Test getting agents by mandate"""
        self.coordinator.register_agent(self.agent1)
        self.coordinator.register_agent(self.agent2)
        
        resource_agents = self.coordinator.get_agents_by_mandate(CLMMandate.RESOURCE_ACQUISITION)
        assert len(resource_agents) == 1
        assert resource_agents[0] == self.agent1
        
        security_agents = self.coordinator.get_agents_by_mandate(CLMMandate.STRATEGIC_SECURITY)
        assert len(security_agents) == 1
        assert security_agents[0] == self.agent2

    @pytest.mark.asyncio
    async def test_coordinate_task(self):
        """Test task coordination"""
        self.coordinator.register_agent(self.agent1)
        self.coordinator.register_agent(self.agent2)
        
        # Task that agent1 can handle
        task = {
            "type": "generate_strategy",
            "mandate": "2.1"
        }
        
        responses = await self.coordinator.coordinate_task(task)
        
        assert len(responses) == 1  # Only agent1 should handle this
        assert responses[0].agent_id == "agent-1"
        assert responses[0].success is True

    @pytest.mark.asyncio
    async def test_coordinate_task_no_capable_agents(self):
        """Test coordination when no agents can handle task"""
        self.coordinator.register_agent(self.agent1)
        
        # Task that no agent can handle
        task = {
            "type": "unknown_task_type"
        }
        
        responses = await self.coordinator.coordinate_task(task)
        assert len(responses) == 0

    def test_get_coordination_summary(self):
        """Test getting coordination summary"""
        self.coordinator.register_agent(self.agent1)
        self.coordinator.register_agent(self.agent2)
        
        summary = self.coordinator.get_coordination_summary()
        
        assert summary["registered_agents"] == 2
        assert "TestAgent1" in summary["agent_roles"]
        assert "TestAgent2" in summary["agent_roles"]
        assert summary["coordination_events"] == 0
        assert "agent-1" in summary["agents"]
        assert "agent-2" in summary["agents"]


if __name__ == "__main__":
    pytest.main([__file__])