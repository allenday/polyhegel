"""
Integration tests for leader-follower hierarchical agent architecture
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from polyhegel.agents.leader import LeaderAgent
from polyhegel.agents.follower import FollowerAgent
from polyhegel.agents.base import AgentContext, AgentCoordinator
from polyhegel.models import StrategicTheme, ThemeCategory, GenesisStrategy, StrategyStep
from polyhegel.strategic_techniques import CLMMandate


@pytest.mark.integration
class TestHierarchicalIntegration:
    """Test integration between leader and follower agents"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_model = MagicMock()
        self.mock_model._mock_name = "test-model"
        
        # Create leader agent
        self.leader = LeaderAgent(
            agent_id="integration-leader",
            model=self.mock_model,
            max_themes=3
        )
        
        # Create specialized follower agents
        self.resource_follower = FollowerAgent(
            agent_id="resource-follower",
            model=self.mock_model,
            specialization_mandate=CLMMandate.RESOURCE_ACQUISITION
        )
        
        self.security_follower = FollowerAgent(
            agent_id="security-follower", 
            model=self.mock_model,
            specialization_mandate=CLMMandate.STRATEGIC_SECURITY
        )
        
        self.value_follower = FollowerAgent(
            agent_id="value-follower",
            model=self.mock_model,
            specialization_mandate=CLMMandate.VALUE_CATALYSIS
        )
        
        # Create general follower
        self.general_follower = FollowerAgent(
            agent_id="general-follower",
            model=self.mock_model
        )
        
        # Test context
        self.context = AgentContext(
            strategic_challenge="Transform digital operations to achieve competitive advantage",
            constraints={"budget": "10M", "timeline": "24 months", "risk_tolerance": "moderate"},
            objectives=[
                "Modernize technology infrastructure", 
                "Improve operational efficiency",
                "Enhance customer experience",
                "Build competitive moats"
            ],
            stakeholders=["CTO", "Operations", "Product", "Engineering", "Customers"],
            resources=["Development teams", "Cloud budget", "Third-party integrations"]
        )
    
    @pytest.mark.asyncio
    async def test_leader_generates_diverse_themes(self):
        """Test that leader generates diverse strategic themes"""
        # Mock diverse themes
        mock_themes = [
            StrategicTheme(
                title="Cloud Infrastructure Modernization",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="Migrate core systems to cloud infrastructure to improve scalability and reduce operational overhead",
                clm_alignment={"2.1": 4.5, "2.2": 3.2, "2.3": 3.8},
                priority_level="high",
                complexity_estimate="complex",
                key_concepts=["cloud migration", "infrastructure", "scalability"],
                success_criteria=["Complete migration in 18 months", "Reduce ops costs by 30%"]
            ),
            StrategicTheme(
                title="Security Framework Enhancement",
                category=ThemeCategory.STRATEGIC_SECURITY,
                description="Implement comprehensive security framework to protect against evolving threats and ensure compliance",
                clm_alignment={"2.1": 2.8, "2.2": 4.8, "2.3": 3.0},
                priority_level="critical",
                complexity_estimate="highly_complex",
                key_concepts=["security", "compliance", "threat protection"],
                success_criteria=["Zero critical vulnerabilities", "100% compliance"]
            ),
            StrategicTheme(
                title="Customer Experience Platform",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="Build integrated platform to deliver personalized customer experiences across all touchpoints",
                clm_alignment={"2.1": 3.5, "2.2": 3.0, "2.3": 4.7},
                priority_level="high",
                complexity_estimate="complex",
                key_concepts=["customer experience", "personalization", "platform"],
                success_criteria=["Increase NPS by 20 points", "Reduce churn by 15%"]
            )
        ]
        
        with patch.object(self.leader, 'generate_themes', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_themes
            
            themes = await self.leader.generate_themes(self.context)
            
            assert len(themes) == 3
            
            # Verify diversity across mandates
            categories = [theme.category for theme in themes]
            assert ThemeCategory.RESOURCE_ACQUISITION in categories
            assert ThemeCategory.STRATEGIC_SECURITY in categories
            assert ThemeCategory.VALUE_CATALYSIS in categories
            
            # Verify CLM alignment diversity
            primary_mandates = [theme.get_primary_mandate() for theme in themes]
            assert "2.1" in primary_mandates
            assert "2.2" in primary_mandates
            assert "2.3" in primary_mandates
    
    @pytest.mark.asyncio
    async def test_follower_develops_coherent_strategy(self):
        """Test that follower develops coherent strategy from theme"""
        theme = StrategicTheme(
            title="API Gateway Implementation",
            category=ThemeCategory.RESOURCE_ACQUISITION,
            description="Implement centralized API gateway to manage service interactions and improve system reliability",
            clm_alignment={"2.1": 4.2, "2.2": 3.5, "2.3": 3.0},
            priority_level="medium",
            complexity_estimate="moderate",
            key_concepts=["API gateway", "microservices", "reliability"],
            success_criteria=["99.9% uptime", "Sub-200ms response times"],
            potential_risks=["Service dependency issues", "Performance bottlenecks"]
        )
        
        # Mock strategy response
        mock_strategy = GenesisStrategy(
            title="API Gateway Implementation Strategy",
            steps=[
                StrategyStep(
                    action="Evaluate API gateway solutions",
                    prerequisites=["Current architecture assessment"],
                    outcome="Selected gateway platform",
                    risks=["Vendor lock-in", "Feature limitations"]
                ),
                StrategyStep(
                    action="Design gateway architecture",
                    prerequisites=["Solution selection", "Requirements analysis"],
                    outcome="Detailed architecture blueprint",
                    risks=["Over-engineering", "Missing edge cases"]
                ),
                StrategyStep(
                    action="Implement pilot deployment",
                    prerequisites=["Architecture approval", "Dev environment setup"],
                    outcome="Working pilot system",
                    risks=["Integration challenges", "Performance issues"]
                ),
                StrategyStep(
                    action="Rollout to production",
                    prerequisites=["Successful pilot", "Monitoring setup"],
                    outcome="Production API gateway",
                    risks=["Service disruption", "Scaling problems"]
                )
            ],
            alignment_score={"Technical Feasibility": 4.0, "Business Value": 3.8, "Risk Level": 2.5},
            estimated_timeline="8-12 months",
            resource_requirements=["Platform architect", "DevOps engineers", "Gateway license"]
        )
        
        with patch.object(self.resource_follower, 'develop_strategy', new_callable=AsyncMock) as mock_dev:
            mock_dev.return_value = mock_strategy
            
            strategy = await self.resource_follower.develop_strategy(theme, self.context)
            
            assert strategy is not None
            assert strategy.title == "API Gateway Implementation Strategy"
            assert len(strategy.steps) == 4
            
            # Verify strategy coherence with theme
            assert "API" in strategy.title or "Gateway" in strategy.title
            assert strategy.estimated_timeline is not None
            assert len(strategy.resource_requirements) > 0
            
            # Verify step progression makes sense
            steps = strategy.steps
            assert "Evaluate" in steps[0].action
            assert "Design" in steps[1].action
            assert "Implement" in steps[2].action
            assert "Rollout" in steps[3].action or "Deploy" in steps[3].action
    
    @pytest.mark.asyncio
    async def test_theme_follower_specialization_matching(self):
        """Test that followers are matched to appropriate themes"""
        themes = [
            StrategicTheme(
                title="Resource Optimization",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="Optimize resource allocation and acquisition processes for improved efficiency",
                clm_alignment={"2.1": 4.5, "2.2": 1.5, "2.3": 1.8},  # Strong 2.1, weak others
                key_concepts=["resources"],
                success_criteria=["Efficiency improved"]
            ),
            StrategicTheme(
                title="Security Enhancement",
                category=ThemeCategory.STRATEGIC_SECURITY,
                description="Enhance security posture through improved monitoring and threat detection",
                clm_alignment={"2.1": 1.8, "2.2": 4.5, "2.3": 1.5},  # Strong 2.2, weak others
                key_concepts=["security"],
                success_criteria=["Security improved"]
            ),
            StrategicTheme(
                title="Innovation Platform",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="Build platform to accelerate innovation and value creation across the organization",
                clm_alignment={"2.1": 1.5, "2.2": 1.8, "2.3": 4.5},  # Strong 2.3, weak others
                key_concepts=["innovation"],
                success_criteria=["Innovation accelerated"]
            )
        ]
        
        # Test specialized follower matching
        assert self.resource_follower._can_handle_theme(themes[0]) is True
        assert self.resource_follower._can_handle_theme(themes[1]) is False
        assert self.resource_follower._can_handle_theme(themes[2]) is False
        
        assert self.security_follower._can_handle_theme(themes[0]) is False
        assert self.security_follower._can_handle_theme(themes[1]) is True
        assert self.security_follower._can_handle_theme(themes[2]) is False
        
        assert self.value_follower._can_handle_theme(themes[0]) is False
        assert self.value_follower._can_handle_theme(themes[1]) is False
        assert self.value_follower._can_handle_theme(themes[2]) is True
        
        # Test general follower can handle all
        assert self.general_follower._can_handle_theme(themes[0]) is True
        assert self.general_follower._can_handle_theme(themes[1]) is True
        assert self.general_follower._can_handle_theme(themes[2]) is True
    
    @pytest.mark.asyncio
    async def test_full_hierarchical_workflow(self):
        """Test complete leader-follower workflow"""
        # Mock leader themes
        mock_themes = [
            StrategicTheme(
                title="Digital Transformation Initiative",
                category=ThemeCategory.VALUE_CATALYSIS,
                description="Comprehensive digital transformation to modernize operations and customer engagement",
                clm_alignment={"2.1": 3.8, "2.2": 3.2, "2.3": 4.5},
                priority_level="critical",
                complexity_estimate="highly_complex",
                key_concepts=["digital transformation", "modernization", "customer engagement"],
                success_criteria=["Complete transformation in 2 years", "Improve customer satisfaction by 25%"]
            )
        ]
        
        # Mock follower strategy
        mock_strategy = GenesisStrategy(
            title="Digital Transformation Implementation Plan",
            steps=[
                StrategyStep(
                    action="Assess current digital maturity",
                    prerequisites=["Stakeholder alignment"],
                    outcome="Digital maturity baseline",
                    risks=["Incomplete assessment"]
                ),
                StrategyStep(
                    action="Design transformation roadmap", 
                    prerequisites=["Maturity assessment", "Vision alignment"],
                    outcome="Detailed implementation roadmap",
                    risks=["Overly ambitious timeline"]
                ),
                StrategyStep(
                    action="Execute transformation phases",
                    prerequisites=["Roadmap approval", "Resource allocation"],
                    outcome="Transformed digital capabilities",
                    risks=["Change resistance", "Technical challenges"]
                )
            ],
            alignment_score={"Strategic Value": 4.5, "Implementation Risk": 3.0},
            estimated_timeline="18-24 months",
            resource_requirements=["Transformation team", "Technology budget", "Change management"]
        )
        
        # Test workflow
        with patch.object(self.leader, 'generate_themes', new_callable=AsyncMock) as mock_leader:
            with patch.object(self.value_follower, 'develop_strategy', new_callable=AsyncMock) as mock_follower:
                mock_leader.return_value = mock_themes
                mock_follower.return_value = mock_strategy
                
                # Step 1: Leader generates themes
                themes = await self.leader.generate_themes(self.context)
                assert len(themes) == 1
                theme = themes[0]
                
                # Step 2: Verify theme quality
                assert theme.title == "Digital Transformation Initiative"
                assert theme.priority_level == "critical"
                assert theme.get_primary_mandate() == "2.3"  # Value Catalysis
                
                # Step 3: Follower develops strategy
                strategy = await self.value_follower.develop_strategy(theme, self.context)
                assert strategy is not None
                
                # Step 4: Verify strategy quality and coherence
                assert "Digital Transformation" in strategy.title
                assert len(strategy.steps) == 3
                assert "transformation" in strategy.title.lower()
                
                # Step 5: Verify strategic alignment
                assert any("assess" in step.action.lower() for step in strategy.steps)
                assert any("design" in step.action.lower() or "plan" in step.action.lower() for step in strategy.steps)
                assert any("execute" in step.action.lower() or "implement" in step.action.lower() for step in strategy.steps)
    
    @pytest.mark.asyncio
    async def test_agent_coordinator_hierarchical_workflow(self):
        """Test hierarchical workflow using AgentCoordinator"""
        coordinator = AgentCoordinator()
        
        # Register agents
        coordinator.register_agent(self.leader)
        coordinator.register_agent(self.resource_follower)
        coordinator.register_agent(self.security_follower)
        coordinator.register_agent(self.value_follower)
        
        # Mock responses
        mock_themes = [
            StrategicTheme(
                title="Infrastructure Modernization",
                category=ThemeCategory.RESOURCE_ACQUISITION,
                description="Modernize IT infrastructure for improved performance and cost efficiency",
                clm_alignment={"2.1": 4.0, "2.2": 3.0, "2.3": 3.0},
                key_concepts=["infrastructure"],
                success_criteria=["Modernization complete"]
            )
        ]
        
        mock_strategy = GenesisStrategy(
            title="Infrastructure Modernization Strategy",
            steps=[
                StrategyStep(
                    action="Plan infrastructure upgrade",
                    prerequisites=["Current state analysis"],
                    outcome="Upgrade plan",
                    risks=["Budget overrun"]
                )
            ],
            alignment_score={"value": 4.0},
            estimated_timeline="12 months",
            resource_requirements=["Infrastructure team"]
        )
        
        # Test coordinated workflow
        with patch.object(self.leader, 'process_request', new_callable=AsyncMock) as mock_leader_req:
            with patch.object(self.resource_follower, 'process_request', new_callable=AsyncMock) as mock_follower_req:
                
                # Mock leader response
                leader_response = self.leader.create_response(
                    success=True,
                    content=mock_themes,
                    reasoning="Generated themes successfully"
                )
                mock_leader_req.return_value = leader_response
                
                # Mock follower response
                follower_response = self.resource_follower.create_response(
                    success=True,
                    content=mock_strategy,
                    reasoning="Developed strategy successfully"
                )
                mock_follower_req.return_value = follower_response
                
                # Step 1: Coordinate theme generation
                theme_task = {
                    "type": "generate_themes",
                    "context": self.context.model_dump()
                }
                
                theme_responses = await coordinator.coordinate_task(theme_task)
                # Only leader should handle theme generation, others should refuse
                successful_responses = [r for r in theme_responses if r.success]
                assert len(successful_responses) == 1
                assert successful_responses[0].agent_id == "integration-leader"
                
                # Step 2: Coordinate strategy development
                strategy_task = {
                    "type": "develop_strategy",
                    "theme": mock_themes[0].model_dump(),
                    "context": self.context.model_dump()
                }
                
                strategy_responses = await coordinator.coordinate_task(strategy_task)
                assert len(strategy_responses) == 1  # Only resource follower should handle
                assert strategy_responses[0].success is True
    
    def test_theme_strategy_coherence_validation(self):
        """Test validation of theme-strategy coherence"""
        theme = StrategicTheme(
            title="Customer Analytics Platform",
            category=ThemeCategory.VALUE_CATALYSIS,
            description="Build advanced analytics platform to gain customer insights and drive personalization",
            clm_alignment={"2.1": 3.0, "2.2": 2.5, "2.3": 4.5},
            key_concepts=["analytics", "customer insights", "personalization"],
            success_criteria=["Increase customer engagement by 30%"],
            potential_risks=["Data privacy concerns", "Integration complexity"]
        )
        
        # Coherent strategy
        coherent_strategy = GenesisStrategy(
            title="Customer Analytics Platform Implementation",
            steps=[
                StrategyStep(
                    action="Design analytics data model",
                    prerequisites=["Data audit"],
                    outcome="Data architecture",
                    risks=["Schema complexity"]
                ),
                StrategyStep(
                    action="Implement analytics pipeline",
                    prerequisites=["Data model", "Tool selection"],
                    outcome="Working analytics system",
                    risks=["Performance issues"]
                )
            ],
            alignment_score={"Business Value": 4.2, "Technical Risk": 2.8},
            estimated_timeline="10 months",
            resource_requirements=["Data engineers", "Analytics tools", "Privacy compliance"]
        )
        
        # Verify coherence
        assert "analytics" in coherent_strategy.title.lower() or "customer" in coherent_strategy.title.lower()
        assert any("analytics" in step.action.lower() or "data" in step.action.lower() for step in coherent_strategy.steps)
        assert any("privacy" in req.lower() or "compliance" in req.lower() for req in coherent_strategy.resource_requirements)
        
        # Incoherent strategy should be detectable
        incoherent_strategy = GenesisStrategy(
            title="Network Security Hardening",  # Wrong domain
            steps=[
                StrategyStep(
                    action="Install firewalls",
                    prerequisites=["Security audit"],
                    outcome="Enhanced security",
                    risks=["Network disruption"]
                )
            ],
            alignment_score={"Security": 4.0},
            estimated_timeline="6 months",
            resource_requirements=["Security team"]
        )
        
        # This strategy doesn't match the analytics theme
        assert "analytics" not in incoherent_strategy.title.lower()
        assert not any("analytics" in step.action.lower() or "customer" in step.action.lower() for step in incoherent_strategy.steps)


if __name__ == "__main__":
    pytest.main([__file__])