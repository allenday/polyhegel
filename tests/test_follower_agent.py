"""
Tests for FollowerAgent implementation
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from polyhegel.agents.follower import FollowerAgent
from polyhegel.agents.base import AgentContext, AgentResponse
from polyhegel.models import StrategicTheme, ThemeCategory, GenesisStrategy, StrategyStep
from polyhegel.strategic_techniques import CLMMandate


@pytest.mark.unit
class TestFollowerAgent:
    """Test FollowerAgent functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_model = MagicMock()
        self.mock_model._mock_name = "test-model"
        
        self.follower = FollowerAgent(
            agent_id="test-follower-1",
            model=self.mock_model,
            specialization_mandate=CLMMandate.RESOURCE_ACQUISITION,
            preferred_techniques=["Stakeholder Alignment Matrix", "Resource Optimization"]
        )
        
        self.context = AgentContext(
            strategic_challenge="Implement digital transformation initiative",
            constraints={"budget": "5M", "timeline": "18 months"},
            objectives=["Modernize systems", "Improve efficiency"],
            stakeholders=["IT team", "Business units", "Executive leadership"],
            resources=["Development team", "Cloud infrastructure", "Training budget"]
        )
        
        self.theme = StrategicTheme(
            title="Digital Infrastructure Modernization",
            category=ThemeCategory.RESOURCE_ACQUISITION,
            description="Modernize core digital infrastructure to support business growth and operational efficiency through cloud migration and system integration",
            clm_alignment={"2.1": 4.5, "2.2": 3.0, "2.3": 3.8},
            priority_level="high",
            complexity_estimate="complex",
            key_concepts=["cloud migration", "system integration", "infrastructure", "modernization"],
            success_criteria=[
                "Complete cloud migration within 12 months",
                "Achieve 99.9% uptime",
                "Reduce operational costs by 25%"
            ],
            potential_risks=[
                "Data migration challenges",
                "System downtime during transition"
            ]
        )
    
    def test_follower_initialization(self):
        """Test follower agent initialization"""
        assert self.follower.agent_id == "test-follower-1"
        assert self.follower.role.name == "Strategic Follower"
        assert self.follower.role.hierarchy_level == 1
        assert self.follower.specialization_mandate == CLMMandate.RESOURCE_ACQUISITION
        assert len(self.follower.preferred_techniques) == 2
    
    def test_follower_capabilities(self):
        """Test follower agent capabilities"""
        assert self.follower.capabilities.can_generate_strategies is True
        assert self.follower.capabilities.can_evaluate_strategies is False
        assert self.follower.capabilities.can_coordinate_agents is False
        assert CLMMandate.RESOURCE_ACQUISITION in self.follower.capabilities.supported_mandates
    
    def test_strategy_prompt_building(self):
        """Test strategy development prompt construction"""
        prompt = self.follower._build_strategy_prompt()
        
        assert "Strategic Follower" in prompt
        assert "detailed strategic implementations" in prompt
        assert "actionable steps" in prompt
        assert "GenesisStrategy" in prompt
    
    @pytest.mark.asyncio
    async def test_develop_strategy_success(self):
        """Test successful strategy development"""
        # Create mock strategy
        mock_strategy = GenesisStrategy(
            title="Digital Infrastructure Implementation Plan",
            steps=[
                StrategyStep(
                    action="Assess current infrastructure",
                    prerequisites=["Infrastructure audit"],
                    outcome="Complete system inventory",
                    risks=["Discovery of legacy dependencies"]
                ),
                StrategyStep(
                    action="Design cloud architecture",
                    prerequisites=["Requirements analysis"],
                    outcome="Cloud migration blueprint",
                    risks=["Over-engineering solution"]
                ),
                StrategyStep(
                    action="Execute phased migration",
                    prerequisites=["Architecture approval", "Resource allocation"],
                    outcome="Systems migrated to cloud",
                    risks=["Data loss", "Extended downtime"]
                )
            ],
            alignment_score={"Technical Feasibility": 4.2, "Business Value": 4.5},
            estimated_timeline="12-15 months",
            resource_requirements=["Cloud architect", "DevOps team", "Migration tools"]
        )
        
        # Mock the strategy agent
        with patch.object(self.follower, 'strategy_agent') as mock_agent:
            mock_result = MagicMock()
            mock_result.data = mock_strategy
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            strategy = await self.follower.develop_strategy(self.theme, self.context)
            
            assert strategy is not None
            assert strategy.title == "Digital Infrastructure Implementation Plan"
            assert len(strategy.steps) == 3
            assert strategy.steps[0].action == "Assess current infrastructure"
            
            # Verify interaction was recorded
            assert len(self.follower.interaction_history) == 1
            assert self.follower.interaction_history[0]["type"] == "strategy_development"
    
    @pytest.mark.asyncio
    async def test_develop_strategy_with_techniques(self):
        """Test strategy development with specific techniques"""
        mock_strategy = GenesisStrategy(
            title="Technique-Guided Strategy",
            steps=[
                StrategyStep(
                    action="Apply stakeholder analysis",
                    prerequisites=["Stakeholder mapping"],
                    outcome="Stakeholder alignment",
                    risks=["Resistance to change"]
                )
            ],
            alignment_score={"Stakeholder Alignment": 4.8},
            estimated_timeline="6 months",
            resource_requirements=["Change management", "Communication plan"]
        )
        
        with patch.object(self.follower, 'strategy_agent') as mock_agent:
            mock_result = MagicMock()
            mock_result.data = mock_strategy
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            strategy = await self.follower.develop_strategy(
                self.theme, 
                self.context, 
                use_techniques=["Stakeholder Alignment Matrix"]
            )
            
            assert strategy is not None
            assert strategy.title == "Technique-Guided Strategy"
    
    @pytest.mark.asyncio
    async def test_develop_strategy_error_handling(self):
        """Test error handling in strategy development"""
        with patch.object(self.follower, 'strategy_agent') as mock_agent:
            mock_agent.run = AsyncMock(side_effect=Exception("API error"))
            
            strategy = await self.follower.develop_strategy(self.theme, self.context)
            
            assert strategy is None
            assert len(self.follower.interaction_history) == 1
            assert self.follower.interaction_history[0]["type"] == "strategy_development_error"
    
    @pytest.mark.asyncio
    async def test_process_request_develop_strategy(self):
        """Test processing develop_strategy request"""
        request = {
            "type": "develop_strategy",
            "theme": self.theme.model_dump(),
            "context": self.context.model_dump()
        }
        
        mock_strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[
                StrategyStep(
                    action="Test Action",
                    prerequisites=["Test Prerequisites"],
                    outcome="Test Outcome",
                    risks=["Test Risk"]
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="3 months",
            resource_requirements=["Test Resources"]
        )
        
        with patch.object(self.follower, 'develop_strategy', new_callable=AsyncMock) as mock_dev:
            mock_dev.return_value = mock_strategy
            
            response = await self.follower.process_request(request)
            
            assert isinstance(response, AgentResponse)
            assert response.success is True
            assert response.agent_id == "test-follower-1"
            assert response.agent_role == "Strategic Follower"
            assert response.content.title == "Test Strategy"
            assert len(response.next_actions) > 0
            assert "strategy steps" in response.next_actions[0].lower()
    
    @pytest.mark.asyncio
    async def test_process_request_invalid_type(self):
        """Test handling invalid request type"""
        request = {
            "type": "invalid_type",
            "theme": self.theme.model_dump(),
            "context": self.context.model_dump()
        }
        
        response = await self.follower.process_request(request)
        
        assert response.success is False
        assert "only handles 'develop_strategy'" in response.content
    
    @pytest.mark.asyncio
    async def test_process_request_no_theme(self):
        """Test handling missing theme"""
        request = {
            "type": "develop_strategy",
            "context": self.context.model_dump()
        }
        
        response = await self.follower.process_request(request)
        
        assert response.success is False
        assert "No theme provided" in response.content
    
    @pytest.mark.asyncio
    async def test_process_request_no_context(self):
        """Test handling missing context"""
        request = {
            "type": "develop_strategy",
            "theme": self.theme.model_dump()
        }
        
        response = await self.follower.process_request(request)
        
        assert response.success is False
        assert "No context provided" in response.content
    
    @pytest.mark.asyncio
    async def test_process_request_theme_mismatch(self):
        """Test handling theme that doesn't match specialization"""
        # Create theme for different mandate
        security_theme = StrategicTheme(
            title="Security Framework",
            category=ThemeCategory.STRATEGIC_SECURITY,
            description="Implement comprehensive security framework for organizational protection",
            clm_alignment={"2.1": 2.0, "2.2": 4.8, "2.3": 2.5},
            key_concepts=["security"],
            success_criteria=["Enhanced security posture"]
        )
        
        request = {
            "type": "develop_strategy",
            "theme": security_theme.model_dump(),
            "context": self.context.model_dump()
        }
        
        response = await self.follower.process_request(request)
        
        assert response.success is False
        assert "doesn't match agent specialization" in response.reasoning
    
    def test_get_capabilities_summary(self):
        """Test capabilities summary"""
        summary = self.follower.get_capabilities_summary()
        
        assert summary["agent_type"] == "follower"
        assert summary["specialization_mandate"] == "2.1"
        assert "Stakeholder Alignment Matrix" in summary["preferred_techniques"]
        assert summary["can_generate"] is True
        assert summary["hierarchy_level"] == 1
    
    def test_select_techniques_requested(self):
        """Test technique selection with requested techniques"""
        techniques = self.follower._select_techniques(
            self.theme, 
            requested_techniques=["Stakeholder Alignment Matrix"]
        )
        
        assert len(techniques) >= 1
        assert any(t.name == "Stakeholder Alignment Matrix" for t in techniques)
    
    def test_select_techniques_from_theme(self):
        """Test technique selection based on theme mandate"""
        techniques = self.follower._select_techniques(self.theme)
        
        assert len(techniques) >= 1
        # Should select techniques for resource acquisition mandate
        assert all(t.mandate == CLMMandate.RESOURCE_ACQUISITION for t in techniques)
    
    def test_can_handle_theme_matching(self):
        """Test theme handling for matching specialization"""
        assert self.follower._can_handle_theme(self.theme) is True
    
    def test_can_handle_theme_non_matching(self):
        """Test theme handling for non-matching specialization"""
        security_theme = StrategicTheme(
            title="Security Theme",
            category=ThemeCategory.STRATEGIC_SECURITY,
            description="A security-focused theme for testing agent specialization handling",
            clm_alignment={"2.1": 1.0, "2.2": 4.8, "2.3": 2.0},
            key_concepts=["security"],
            success_criteria=["Security improved"]
        )
        
        assert self.follower._can_handle_theme(security_theme) is False
    
    def test_format_constraints(self):
        """Test constraint formatting"""
        constraints = {"budget": "5M", "timeline": "18 months"}
        formatted = self.follower._format_constraints(constraints)
        
        assert "budget: 5M" in formatted
        assert "timeline: 18 months" in formatted
        
        # Test empty constraints
        assert self.follower._format_constraints({}) == "None specified"
    
    def test_format_list(self):
        """Test list formatting"""
        items = ["Item 1", "Item 2", "Item 3"]
        formatted = self.follower._format_list(items)
        
        assert "- Item 1" in formatted
        assert "- Item 2" in formatted
        assert "- Item 3" in formatted
        
        # Test empty list
        assert self.follower._format_list([]) == "None specified"
    
    def test_analyze_strategy(self):
        """Test strategy analysis"""
        strategy = GenesisStrategy(
            title="Complex Strategy",
            steps=[
                StrategyStep(
                    action=f"Step {i}",
                    prerequisites=[f"Prereq {i}"],
                    outcome=f"Outcome {i}",
                    risks=[f"Risk {i}"]
                ) for i in range(10)  # Many steps
            ],
            alignment_score={"complexity": 4.0},
            estimated_timeline="24 months",
            resource_requirements=[f"Resource {i}" for i in range(15)]  # Many resources
        )
        
        analysis = self.follower._analyze_strategy(strategy, self.theme)
        
        assert analysis["step_count"] == 10
        assert analysis["resource_count"] == 15
        assert "many steps" in " ".join(analysis["recommendations"]).lower()
        assert "resource requirements" in " ".join(analysis["recommendations"]).lower()
    
    def test_general_follower_agent(self):
        """Test follower agent without specialization"""
        general_follower = FollowerAgent(
            agent_id="test-general-follower",
            model=self.mock_model
        )
        
        # Should handle any theme
        assert general_follower._can_handle_theme(self.theme) is True
        
        security_theme = StrategicTheme(
            title="Security Theme",
            category=ThemeCategory.STRATEGIC_SECURITY,
            description="A security theme for testing general follower capabilities",
            key_concepts=["security"],
            success_criteria=["Security enhanced"]
        )
        assert general_follower._can_handle_theme(security_theme) is True
        
        # Should support all mandates
        assert len(general_follower.capabilities.supported_mandates) == 3
    
    def test_cross_cutting_theme_handling(self):
        """Test handling of cross-cutting themes"""
        cross_cutting_theme = StrategicTheme(
            title="Digital Transformation",
            category=ThemeCategory.CROSS_CUTTING,
            description="Comprehensive digital transformation spanning multiple organizational areas",
            clm_alignment={"2.1": 4.0, "2.2": 3.8, "2.3": 4.2},
            key_concepts=["transformation", "digital", "cross-cutting"],
            success_criteria=["Transformation completed"]
        )
        
        # Specialized agent might handle if alignment is strong enough
        result = self.follower._can_handle_theme(cross_cutting_theme)
        assert isinstance(result, bool)  # Should return a boolean result


if __name__ == "__main__":
    pytest.main([__file__])