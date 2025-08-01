"""
Integration tests for A2A agent architecture

Tests A2A AgentCards, AgentSkills, client/server communication,
and integration with polyhegel simulator.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from polyhegel.agents.a2a_cards import (
    create_leader_agent_card,
    create_follower_agent_card,
    create_simulation_agent_card,
    create_all_agent_cards
)
from polyhegel.agents.a2a_executors import LeaderAgentExecutor, FollowerAgentExecutor
from polyhegel.clients import PolyhegelA2AClient, A2AAgentEndpoints
from polyhegel.strategic_techniques import StrategyDomain


class TestA2AAgentCards:
    """Test A2A AgentCard definitions"""
    
    def test_leader_agent_card_creation(self):
        """Test leader agent card creation"""
        card = create_leader_agent_card("http://localhost:8001")
        
        assert card.name == "Polyhegel Strategic Leader Agent"
        assert card.url == "http://localhost:8001"
        assert card.version == "1.0.0"
        assert card.capabilities.streaming is True
        assert len(card.skills) > 0
        
        # Check for theme generation skill
        theme_skill = next((s for s in card.skills if s.id == 'generate_strategic_themes'), None)
        assert theme_skill is not None
        assert 'strategy' in theme_skill.tags
        assert len(theme_skill.examples) > 0
    
    def test_follower_agent_card_creation(self):
        """Test follower agent card creation with specialization"""
        card = create_follower_agent_card(
            StrategyDomain.RESOURCE_ACQUISITION,
            "http://localhost:8002"
        )
        
        assert "Resource Acquisition" in card.name
        assert card.url == "http://localhost:8002"
        assert len(card.skills) > 0
        
        # Check for specialized skill
        resource_skill = next((s for s in card.skills if 'resource' in s.id), None)
        assert resource_skill is not None
    
    def test_general_follower_agent_card(self):
        """Test general follower agent without specialization"""
        card = create_follower_agent_card(None, "http://localhost:8005")
        
        assert "General" in card.name
        assert card.url == "http://localhost:8005"
        # Should have base strategy development skill
        base_skill = next((s for s in card.skills if s.id == 'develop_detailed_strategy'), None)
        assert base_skill is not None
    
    def test_simulation_agent_card(self):
        """Test simulation agent card creation"""
        card = create_simulation_agent_card("http://localhost:8000")
        
        assert "Simulation Orchestrator" in card.name
        assert card.url == "http://localhost:8000"
        assert len(card.skills) > 0
    
    def test_all_polyhegel_cards(self):
        """Test complete card ecosystem creation"""
        cards = create_all_agent_cards()
        
        expected_agents = ['simulation', 'leader', 'follower_resource', 
                          'follower_security', 'follower_value', 'follower_general']
        
        assert set(cards.keys()) == set(expected_agents)
        
        # Verify each card is valid
        for agent_name, card in cards.items():
            assert card.name is not None
            assert card.url is not None
            assert len(card.skills) > 0


class TestA2AAgentExecutors:
    """Test A2A AgentExecutor implementations"""
    
    @pytest.fixture
    def mock_model(self):
        """Mock model for testing"""
        return MagicMock()
    
    def test_leader_executor_creation(self, mock_model):
        """Test LeaderAgentExecutor creation"""
        executor = LeaderAgentExecutor(
            model=mock_model,
            focus_domains=[StrategyDomain.RESOURCE_ACQUISITION],
            max_themes=3
        )
        
        assert executor.model == mock_model
        assert StrategyDomain.RESOURCE_ACQUISITION in executor.focus_domains
        assert executor.max_themes == 3
    
    def test_follower_executor_creation(self, mock_model):
        """Test FollowerAgentExecutor creation"""
        executor = FollowerAgentExecutor(
            model=mock_model,
            specialization_domain=StrategyDomain.STRATEGIC_SECURITY
        )
        
        assert executor.model == mock_model
        assert executor.specialization_domain == StrategyDomain.STRATEGIC_SECURITY
    
    @pytest.mark.asyncio
    async def test_leader_executor_execute(self, mock_model):
        """Test LeaderAgentExecutor execute method"""
        executor = LeaderAgentExecutor(mock_model, max_themes=2)
        
        # Mock request context and event queue
        mock_context = MagicMock()
        mock_context.get_user_input.return_value = "Test strategic challenge"
        mock_context.task_id = "test-task-123"
        
        mock_event_queue = AsyncMock()
        
        # Execute should complete without error
        await executor.execute(mock_context, mock_event_queue)
        
        # Verify events were queued
        assert mock_event_queue.enqueue_event.call_count > 0
    
    @pytest.mark.asyncio  
    async def test_follower_executor_execute(self, mock_model):
        """Test FollowerAgentExecutor execute method"""
        executor = FollowerAgentExecutor(
            mock_model, 
            specialization_domain=StrategyDomain.VALUE_CATALYSIS
        )
        
        # Mock request context and event queue
        mock_context = MagicMock()
        mock_context.get_user_input.return_value = "Test theme for strategy development"
        mock_context.task_id = "test-task-456"
        
        mock_event_queue = AsyncMock()
        
        # Execute should complete without error
        await executor.execute(mock_context, mock_event_queue)
        
        # Verify events were queued
        assert mock_event_queue.enqueue_event.call_count > 0


class TestA2AClientIntegration:
    """Test A2A client and server communication"""
    
    def test_agent_endpoints_creation(self):
        """Test A2AAgentEndpoints configuration"""
        endpoints = A2AAgentEndpoints(
            leader_url="http://test-leader:8001",
            follower_resource_url="http://test-resource:8002"
        )
        
        assert endpoints.leader_url == "http://test-leader:8001"
        assert endpoints.follower_resource_url == "http://test-resource:8002"
        
        follower_urls = endpoints.get_follower_urls()
        assert follower_urls["resource"] == "http://test-resource:8002"
    
    def test_agent_endpoints_from_env(self):
        """Test endpoint creation from environment variables"""
        with patch.dict('os.environ', {
            'POLYHEGEL_LEADER_URL': 'http://env-leader:9001',
            'POLYHEGEL_FOLLOWER_RESOURCE_URL': 'http://env-resource:9002'
        }):
            endpoints = A2AAgentEndpoints.from_env()
            assert endpoints.leader_url == "http://env-leader:9001"
            assert endpoints.follower_resource_url == "http://env-resource:9002"
    
    @pytest.mark.asyncio
    async def test_a2a_client_agent_verification(self):
        """Test A2A client agent availability verification"""
        endpoints = A2AAgentEndpoints()
        
        # Mock HTTP responses
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful agent card responses
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            async with PolyhegelA2AClient(endpoints) as client:
                availability = await client.verify_agent_availability()
                
                # All agents should be reported as available
                assert availability["leader"] is True
                assert availability["follower_resource"] is True
                assert availability["follower_security"] is True
                assert availability["follower_value"] is True
                assert availability["follower_general"] is True
    
    @pytest.mark.asyncio
    async def test_a2a_client_unavailable_agents(self):
        """Test A2A client with unavailable agents"""
        endpoints = A2AAgentEndpoints()
        
        # Mock HTTP client that fails connections
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock connection failures
            mock_client.get.side_effect = Exception("Connection refused")
            
            async with PolyhegelA2AClient(endpoints) as client:
                availability = await client.verify_agent_availability()
                
                # All agents should be reported as unavailable
                assert all(not available for available in availability.values())
    
    @pytest.mark.asyncio
    async def test_hierarchical_strategy_generation(self):
        """Test hierarchical strategy generation via A2A client"""
        endpoints = A2AAgentEndpoints()
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            # Mock successful availability check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            async with PolyhegelA2AClient(endpoints) as client:
                # Mock the internal A2A client calls
                with patch.object(client, 'generate_themes') as mock_generate_themes:
                    with patch.object(client, 'develop_strategy') as mock_develop_strategy:
                        
                        # Mock theme generation
                        mock_generate_themes.return_value = [
                            {"title": "Test Theme 1", "domain": "resource_acquisition"},
                            {"title": "Test Theme 2", "domain": "strategic_security"}
                        ]
                        
                        # Mock strategy development
                        mock_develop_strategy.return_value = {
                            "title": "Test Strategy",
                            "steps": [{"action": "Test action", "outcome": "Test outcome"}],
                            "domain": "resource_acquisition"
                        }
                        
                        strategies = await client.generate_hierarchical_strategies(
                            "Test strategic challenge",
                            max_themes=2
                        )
                        
                        assert len(strategies) == 2
                        assert all(hasattr(strategy, 'strategy') for strategy in strategies)
                        assert all(hasattr(strategy, 'source_sample') for strategy in strategies)


class TestA2ASimulatorIntegration:
    """Test A2A integration with polyhegel simulator"""
    
    @pytest.mark.asyncio
    async def test_a2a_simulation_with_available_agents(self):
        """Test A2A simulation when agents are available"""
        from polyhegel.agents.a2a_simulation import generate_hierarchical_strategies_a2a
        
        with patch('polyhegel.clients.PolyhegelA2AClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock agent availability
            mock_client.verify_agent_availability.return_value = {
                "leader": True, "follower_resource": True, "follower_security": True,
                "follower_value": True, "follower_general": True
            }
            
            # Mock strategy generation
            from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep
            mock_strategy = GenesisStrategy(
                title="Test A2A Strategy",
                steps=[StrategyStep(
                    action="Test action",
                    prerequisites=["Test prerequisite"],
                    outcome="Test outcome",
                    risks=["Test risk"]
                )],
                alignment_score={"resource_acquisition": 4.0},
                estimated_timeline="2 weeks",
                resource_requirements=["Test resources"]
            )
            
            mock_strategy_chain = StrategyChain(
                strategy=mock_strategy,
                source_sample=0,
                temperature=0.8
            )
            
            mock_client.generate_hierarchical_strategies.return_value = [mock_strategy_chain]
            
            # Test the function
            result = await generate_hierarchical_strategies_a2a(
                strategic_challenge="Test challenge",
                context={},
                leader_url="http://localhost:8001",
                follower_urls={"resource": "http://localhost:8002"},
                max_themes=1
            )
            
            assert len(result) == 1
            assert result[0].strategy.title == "Test A2A Strategy"
    
    @pytest.mark.asyncio
    async def test_a2a_simulation_fallback_to_mock(self):
        """Test A2A simulation fallback when agents unavailable"""
        from polyhegel.agents.a2a_simulation import generate_hierarchical_strategies_a2a
        
        with patch('polyhegel.clients.PolyhegelA2AClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock no agents available
            mock_client.verify_agent_availability.return_value = {
                "leader": False, "follower_resource": False, "follower_security": False,
                "follower_value": False, "follower_general": False
            }
            
            # Test the function - should fall back to mock
            result = await generate_hierarchical_strategies_a2a(
                strategic_challenge="Test challenge",
                context={},
                leader_url="http://localhost:8001",
                follower_urls={"resource": "http://localhost:8002"},
                max_themes=3
            )
            
            # Should get mock strategies
            assert len(result) == 3
            assert all("A2A Generated Strategy" in strategy.strategy.title for strategy in result)


@pytest.mark.integration
class TestFullA2AIntegration:
    """Full integration tests for A2A architecture"""
    
    @pytest.mark.asyncio
    async def test_simulator_hierarchical_mode_a2a(self):
        """Test simulator hierarchical mode with A2A integration"""
        from polyhegel.simulator import PolyhegelSimulator
        
        # Use a fast model for testing
        simulator = PolyhegelSimulator(model_name="claude-3-haiku-20240307")
        
        # Mock the A2A client to avoid actual network calls
        with patch('polyhegel.agents.a2a_simulation.generate_hierarchical_strategies_a2a') as mock_a2a:
            # Mock A2A strategy generation
            from polyhegel.models import StrategyChain, GenesisStrategy, StrategyStep
            
            mock_strategy = GenesisStrategy(
                title="Integration Test Strategy",
                steps=[StrategyStep(
                    action="Execute integration test",
                    prerequisites=["Test setup complete"],
                    outcome="Test validation",
                    risks=["Test failure"]
                )],
                alignment_score={"resource_acquisition": 3.5, "strategic_security": 4.0},
                estimated_timeline="1 week",
                resource_requirements=["Test infrastructure"]
            )
            
            mock_strategy_chain = StrategyChain(
                strategy=mock_strategy,
                source_sample=0,
                temperature=0.8
            )
            
            mock_a2a.return_value = [mock_strategy_chain]
            
            # Run simulation in hierarchical mode
            result = await simulator.run_simulation(
                system_prompt="Test system prompt",
                user_prompt="Test A2A integration challenge",
                mode="hierarchical"
            )
            
            # Verify results
            assert result is not None
            assert result["metadata"]["total_chains"] == 1
            assert result["trunk"]["title"] == "Integration Test Strategy"
            
            # Verify A2A function was called
            mock_a2a.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])