"""
Tests for LeaderAgent implementation
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from polyhegel.agents.leader import LeaderAgent
from polyhegel.agents.base import AgentContext, AgentResponse
from polyhegel.models import StrategicTheme, ThemeCategory
from polyhegel.strategic_techniques import CLMMandate


@pytest.mark.unit
class TestLeaderAgent:
    """Test LeaderAgent functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_model = MagicMock()
        self.mock_model._mock_name = "test-model"
        
        self.leader = LeaderAgent(
            agent_id="test-leader-1",
            model=self.mock_model,
            focus_mandates=[CLMMandate.RESOURCE_ACQUISITION, CLMMandate.VALUE_CATALYSIS],
            max_themes=3
        )
        
        self.context = AgentContext(
            strategic_challenge="Develop a competitive advantage in emerging markets",
            constraints={"budget": "10M", "timeline": "2 years"},
            objectives=["Increase market share", "Build local partnerships"],
            stakeholders=["Executive team", "Regional managers", "Local partners"],
            timeline="Q1 2025 - Q4 2026",
            resources=["Regional teams", "Technology platform", "Marketing budget"]
        )
    
    def test_leader_initialization(self):
        """Test leader agent initialization"""
        assert self.leader.agent_id == "test-leader-1"
        assert self.leader.role.name == "Strategic Leader"
        assert self.leader.role.hierarchy_level == 0
        assert self.leader.max_themes == 3
        assert len(self.leader.focus_mandates) == 2
        assert CLMMandate.RESOURCE_ACQUISITION in self.leader.focus_mandates
    
    def test_leader_capabilities(self):
        """Test leader agent capabilities"""
        assert self.leader.capabilities.can_generate_strategies is True
        assert self.leader.capabilities.can_evaluate_strategies is False
        assert self.leader.capabilities.can_coordinate_agents is True
        assert len(self.leader.capabilities.supported_mandates) == 2
    
    def test_theme_prompt_building(self):
        """Test theme generation prompt construction"""
        prompt = self.leader._build_theme_prompt()
        
        assert "Strategic Leader" in prompt
        assert "strategic themes" in prompt
        assert "organizational mandates" in prompt
        assert str(self.leader.max_themes) in prompt
    
    @pytest.mark.asyncio
    async def test_generate_themes_success(self):
        """Test successful theme generation"""
        # Create mock themes
        mock_themes = [
            StrategicTheme(
                title="Market Expansion Strategy",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="Expand into emerging markets through strategic partnerships and local presence",
                clm_alignment={"2.1": 4.5, "2.2": 3.0, "2.3": 3.5},
                priority_level="high",
                complexity_estimate="complex",
                key_concepts=["market expansion", "partnerships", "localization"],
                success_criteria=["20% market share in 2 years", "5 key partnerships"]
            ),
            StrategicTheme(
                title="Innovation Platform Development",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="Build an innovation platform to accelerate product development and customer value creation",
                clm_alignment={"2.1": 3.0, "2.2": 2.5, "2.3": 4.8},
                priority_level="high",
                complexity_estimate="highly_complex",
                key_concepts=["innovation", "platform", "value creation"],
                success_criteria=["Platform launch in 6 months", "10 new products in year 1"]
            )
        ]
        
        # Mock the theme agent
        with patch.object(self.leader, 'theme_agent') as mock_agent:
            mock_result = MagicMock()
            mock_result.data = mock_themes
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            themes = await self.leader.generate_themes(self.context)
            
            assert len(themes) == 2
            assert themes[0].title == "Market Expansion Strategy"
            assert themes[1].title == "Innovation Platform Development"
            
            # Verify interaction was recorded
            assert len(self.leader.interaction_history) == 1
            assert self.leader.interaction_history[0]["type"] == "theme_generation"
    
    @pytest.mark.asyncio
    async def test_generate_themes_with_filtering(self):
        """Test theme generation with mandate filtering"""
        # Create themes with different mandate alignments
        mock_themes = [
            StrategicTheme(
                title="Resource Theme",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="A theme focused on resource acquisition strategies for growth",
                clm_alignment={"2.1": 4.5, "2.2": 2.0, "2.3": 2.0},
                key_concepts=["resources"],
                success_criteria=["Acquire resources"]
            ),
            StrategicTheme(
                title="Security Theme",
                category=ThemeCategory.STRATEGIC_SECURITY,
                description="A theme focused on security and risk mitigation for organizational resilience",
                clm_alignment={"2.1": 2.0, "2.2": 4.5, "2.3": 2.0},
                key_concepts=["security"],
                success_criteria=["Enhance security"]
            ),
            StrategicTheme(
                title="Value Theme",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="A theme focused on value creation and innovation for competitive advantage",
                clm_alignment={"2.1": 2.0, "2.2": 2.0, "2.3": 4.5},
                key_concepts=["value"],
                success_criteria=["Create value"]
            )
        ]
        
        with patch.object(self.leader, 'theme_agent') as mock_agent:
            mock_result = MagicMock()
            mock_result.data = mock_themes
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            themes = await self.leader.generate_themes(self.context)
            
            # Should filter out security theme (not in focus mandates)
            assert len(themes) == 2
            theme_titles = [t.title for t in themes]
            assert "Resource Theme" in theme_titles
            assert "Value Theme" in theme_titles
            assert "Security Theme" not in theme_titles
    
    @pytest.mark.asyncio
    async def test_generate_themes_error_handling(self):
        """Test error handling in theme generation"""
        with patch.object(self.leader, 'theme_agent') as mock_agent:
            mock_agent.run = AsyncMock(side_effect=Exception("API error"))
            
            themes = await self.leader.generate_themes(self.context)
            
            assert themes == []
            assert len(self.leader.interaction_history) == 1
            assert self.leader.interaction_history[0]["type"] == "theme_generation_error"
    
    @pytest.mark.asyncio
    async def test_process_request_generate_themes(self):
        """Test processing generate_themes request"""
        request = {
            "type": "generate_themes",
            "context": self.context.model_dump()
        }
        
        mock_themes = [
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="A test theme for unit testing the leader agent functionality",
                key_concepts=["test"],
                success_criteria=["Test passes"]
            )
        ]
        
        with patch.object(self.leader, 'generate_themes', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_themes
            
            response = await self.leader.process_request(request)
            
            assert isinstance(response, AgentResponse)
            assert response.success is True
            assert response.agent_id == "test-leader-1"
            assert response.agent_role == "Strategic Leader"
            assert len(response.content) == 1
            assert response.content[0].title == "Test Theme"
            assert len(response.next_actions) > 0
            assert "follower agents" in response.next_actions[0].lower()
    
    @pytest.mark.asyncio
    async def test_process_request_invalid_type(self):
        """Test handling invalid request type"""
        request = {
            "type": "invalid_type",
            "context": self.context.model_dump()
        }
        
        response = await self.leader.process_request(request)
        
        assert response.success is False
        assert "only handles 'generate_themes'" in response.content
    
    @pytest.mark.asyncio
    async def test_process_request_no_context(self):
        """Test handling missing context"""
        request = {
            "type": "generate_themes"
        }
        
        response = await self.leader.process_request(request)
        
        assert response.success is False
        assert "No context provided" in response.content
    
    def test_get_capabilities_summary(self):
        """Test capabilities summary"""
        summary = self.leader.get_capabilities_summary()
        
        assert summary["agent_type"] == "leader"
        assert summary["max_themes"] == 3
        assert "2.1" in summary["focus_mandates"]
        assert "2.3" in summary["focus_mandates"]
        assert "2.2" not in summary["focus_mandates"]
        assert summary["can_coordinate"] is True
        assert summary["hierarchy_level"] == 0
    
    def test_format_constraints(self):
        """Test constraint formatting"""
        constraints = {"budget": "10M", "timeline": "2 years"}
        formatted = self.leader._format_constraints(constraints)
        
        assert "budget: 10M" in formatted
        assert "timeline: 2 years" in formatted
        
        # Test empty constraints
        assert self.leader._format_constraints({}) == "None specified"
    
    def test_format_list(self):
        """Test list formatting"""
        items = ["Item 1", "Item 2", "Item 3"]
        formatted = self.leader._format_list(items)
        
        assert "- Item 1" in formatted
        assert "- Item 2" in formatted
        assert "- Item 3" in formatted
        
        # Test empty list
        assert self.leader._format_list([]) == "None specified"
    
    def test_analyze_themes(self):
        """Test theme analysis"""
        themes = [
            StrategicTheme(
                title="High Priority Theme",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="A high priority theme for testing analysis functionality",
                clm_alignment={"2.1": 4.5, "2.2": 2.0, "2.3": 3.0},
                priority_level="high",
                complexity_estimate="complex",
                key_concepts=["test"],
                success_criteria=["Success"]
            ),
            StrategicTheme(
                title="Critical Cross-Cutting Theme",
                category=ThemeCategory.CROSS_CUTTING,
                description="A critical theme that spans multiple mandates for testing",
                clm_alignment={"2.1": 4.0, "2.2": 4.0, "2.3": 4.0},
                priority_level="critical",
                complexity_estimate="highly_complex",
                key_concepts=["cross-cutting"],
                success_criteria=["Multi-mandate success"]
            ),
            StrategicTheme(
                title="Medium Priority Theme",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="A medium priority theme for testing priority ordering",
                clm_alignment={"2.1": 2.0, "2.2": 2.0, "2.3": 4.5},
                priority_level="medium",
                complexity_estimate="moderate",
                key_concepts=["value"],
                success_criteria=["Value created"]
            )
        ]
        
        analysis = self.leader._analyze_themes(themes)
        
        # Check priority ordering
        assert analysis["priority_order"][0] == "Critical Cross-Cutting Theme"
        assert analysis["priority_order"][1] == "High Priority Theme"
        assert analysis["priority_order"][2] == "Medium Priority Theme"
        
        # Check mandate coverage
        assert "2.1" in analysis["mandate_coverage"]
        assert "2.3" in analysis["mandate_coverage"]
        
        # Check complexity distribution
        assert analysis["complexity_distribution"]["complex"] == 1
        assert analysis["complexity_distribution"]["highly_complex"] == 1
        assert analysis["complexity_distribution"]["moderate"] == 1
        
        # Check recommendations
        assert any("cross-cutting" in rec for rec in analysis["recommendations"])
    
    def test_leader_without_focus_mandates(self):
        """Test leader agent without specific mandate focus"""
        leader = LeaderAgent(
            agent_id="test-leader-2",
            model=self.mock_model,
            max_themes=5
        )
        
        # Should support all mandates
        assert len(leader.focus_mandates) == 3
        assert CLMMandate.RESOURCE_ACQUISITION in leader.focus_mandates
        assert CLMMandate.STRATEGIC_SECURITY in leader.focus_mandates
        assert CLMMandate.VALUE_CATALYSIS in leader.focus_mandates


if __name__ == "__main__":
    pytest.main([__file__])