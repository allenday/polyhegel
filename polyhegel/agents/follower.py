"""
Follower agent implementation for detailed strategy development

Follower agents develop detailed strategic implementations based on
high-level themes provided by leader agents.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic_ai import Agent

from ..models import GenesisStrategy, StrategicTheme
from ..strategic_techniques import (
    CLMMandate, get_techniques_for_mandate, get_technique_by_name,
    format_technique_for_prompt
)
from .base import (
    BaseAgent, AgentRole, AgentCapabilities, AgentContext, AgentResponse
)

logger = logging.getLogger(__name__)


class FollowerAgent(BaseAgent):
    """
    Follower agent for developing detailed strategies from themes
    
    Follower agents take high-level strategic themes from leader agents
    and develop them into concrete, actionable strategic implementations.
    """
    
    def __init__(self,
                 agent_id: str,
                 model: Any,
                 specialization_mandate: Optional[CLMMandate] = None,
                 preferred_techniques: Optional[List[str]] = None):
        """
        Initialize follower agent
        
        Args:
            agent_id: Unique identifier for this agent
            model: pydantic-ai model instance
            specialization_mandate: CLM mandate this agent specializes in
            preferred_techniques: List of preferred technique names
        """
        # Define follower role
        role = AgentRole(
            name="Strategic Follower",
            description="Develops detailed strategies from strategic themes",
            mandate=specialization_mandate,
            specialization=f"{specialization_mandate.value} Implementation" if specialization_mandate else "Strategy Implementation", 
            hierarchy_level=1  # Follower level
        )
        
        # Define follower capabilities
        capabilities = AgentCapabilities(
            can_generate_strategies=True,
            can_evaluate_strategies=False,
            can_coordinate_agents=False,
            supported_mandates=[specialization_mandate] if specialization_mandate else list(CLMMandate),
            preferred_techniques=preferred_techniques or []
        )
        
        # Initialize base agent
        super().__init__(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            model=model
        )
        
        self.specialization_mandate = specialization_mandate
        self.preferred_techniques = preferred_techniques or []
        
        # Configure strategy generation agent
        if self.pydantic_agent:
            self.strategy_agent = Agent(
                self.model,
                system_prompt=self._build_strategy_prompt(),
                result_type=GenesisStrategy
            )
        else:
            # For mock models in tests
            self.strategy_agent = None
    
    def _build_strategy_prompt(self) -> str:
        """Build specialized prompt for strategy development"""
        base_prompt = self._build_system_prompt()
        
        strategy_prompt = f"""{base_prompt}

Your primary task is to develop detailed strategic implementations from
high-level strategic themes. For each theme, you should:

1. Break down the theme into concrete, actionable steps
2. Identify prerequisites and dependencies for each step
3. Assess risks and mitigation strategies
4. Estimate timelines and resource requirements
5. Ensure alignment with organizational mandates and constraints

When developing strategies:
- Focus on practical implementation details
- Consider stakeholder impacts and change management
- Balance ambition with feasibility
- Identify key success metrics and milestones
- Plan for iteration and adaptation

Strategic Development Process:
1. Analyze the theme's objectives and constraints
2. Select appropriate strategic techniques
3. Design step-by-step implementation approach
4. Validate against organizational capabilities
5. Optimize for sustainable execution

Generate a complete GenesisStrategy with detailed steps.
"""
        
        return strategy_prompt
    
    async def develop_strategy(self, 
                             theme: StrategicTheme, 
                             context: AgentContext,
                             use_techniques: Optional[List[str]] = None) -> Optional[GenesisStrategy]:
        """
        Develop detailed strategy from strategic theme
        
        Args:
            theme: Strategic theme to develop
            context: Strategic context and constraints
            use_techniques: Optional list of technique names to use
            
        Returns:
            Detailed GenesisStrategy or None if failed
        """
        self.set_context(context)
        
        # Select techniques to use
        techniques_to_use = self._select_techniques(theme, use_techniques)
        
        # Build strategy development prompt
        prompt = f"""Strategic Theme: {theme.title}

Theme Description: {theme.description}

Theme Category: {theme.category.value}

CLM Alignment: {theme.get_alignment_summary()}

Priority: {theme.priority_level}
Complexity: {theme.complexity_estimate}

Key Concepts: {', '.join(theme.key_concepts)}

Success Criteria:
{self._format_list(theme.success_criteria)}

Potential Risks:
{self._format_list(theme.potential_risks)}

Strategic Context: {context.strategic_challenge}

Organizational Constraints:
{self._format_constraints(context.constraints)}

Stakeholders:
{self._format_list(context.stakeholders)}

Strategic Techniques to Apply:
{self._format_techniques(techniques_to_use)}

Develop a detailed implementation strategy that transforms this theme into 
concrete action steps. The strategy should be practical, achievable, and 
aligned with the organizational context and constraints.
"""
        
        try:
            # Generate strategy using pydantic-ai agent
            if not self.strategy_agent:
                # For testing - return None
                return None
                
            result = await self.strategy_agent.run(prompt)
            strategy = result.data
            
            # Record generation
            self.add_interaction("strategy_development", {
                "theme": theme.model_dump(),
                "context": context.model_dump(),
                "techniques_used": [t.name for t in techniques_to_use],
                "strategy": strategy.model_dump()
            })
            
            logger.info(f"Follower {self.agent_id} developed strategy: {strategy.title}")
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy development failed: {e}")
            self.add_interaction("strategy_development_error", {
                "error": str(e),
                "theme": theme.model_dump(),
                "prompt": prompt
            })
            return None
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that this follower agent can handle the request"""
        request_type = request.get("type", "")
        
        # Follower agents only handle develop_strategy requests
        if request_type != "develop_strategy":
            return False
        
        # Check if theme is provided and matches specialization
        theme_data = request.get("theme", {})
        if theme_data:
            try:
                theme = StrategicTheme(**theme_data)
                return self._can_handle_theme(theme)
            except Exception:
                return False
        
        return True
    
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a request to develop strategy from theme
        
        Args:
            request: Request with theme and context information
            
        Returns:
            AgentResponse with developed strategy
        """
        request_type = request.get("type", "")
        
        if request_type != "develop_strategy":
            return self.create_response(
                success=False,
                content="FollowerAgent only handles 'develop_strategy' requests",
                reasoning=f"Received request type: {request_type}"
            )
        
        # Extract theme from request
        theme_data = request.get("theme", {})
        if not theme_data:
            return self.create_response(
                success=False,
                content="No theme provided for strategy development",
                reasoning="Strategic theme is required"
            )
        
        # Extract context from request
        context_data = request.get("context", {})
        if not context_data:
            return self.create_response(
                success=False,
                content="No context provided for strategy development",
                reasoning="Strategic context is required"
            )
        
        # Create objects
        try:
            theme = StrategicTheme(**theme_data)
            context = AgentContext(**context_data)
        except Exception as e:
            return self.create_response(
                success=False,
                content=f"Invalid theme or context: {e}",
                reasoning="Failed to parse theme or context data"
            )
        
        # Check if this agent can handle the theme
        if not self._can_handle_theme(theme):
            return self.create_response(
                success=False,
                content=f"Agent specializes in {self.specialization_mandate.value if self.specialization_mandate else 'general'} but theme is {theme.category.value}",
                reasoning="Theme doesn't match agent specialization"
            )
        
        # Develop strategy
        techniques = request.get("techniques", [])
        strategy = await self.develop_strategy(theme, context, techniques)
        
        if not strategy:
            return self.create_response(
                success=False,
                content="No strategy developed",
                reasoning="Strategy development failed or returned empty"
            )
        
        # Analyze strategy for recommendations
        analysis = self._analyze_strategy(strategy, theme)
        
        return self.create_response(
            success=True,
            content=strategy,
            reasoning=f"Developed {len(strategy.steps)}-step strategy for theme: {theme.title}",
            confidence=0.8,
            next_actions=[
                f"Review strategy steps for feasibility and dependencies",
                f"Validate resource requirements: {', '.join(strategy.resource_requirements[:3])}",
                f"Begin implementation with step 1: {strategy.steps[0].action}"
            ],
            recommendations=analysis['recommendations']
        )
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Return summary of follower capabilities"""
        return {
            "agent_type": "follower",
            "specialization": self.role.specialization,
            "specialization_mandate": self.specialization_mandate.value if self.specialization_mandate else None,
            "preferred_techniques": self.preferred_techniques,
            "can_generate": self.capabilities.can_generate_strategies,
            "hierarchy_level": self.role.hierarchy_level
        }
    
    def _select_techniques(self, 
                          theme: StrategicTheme, 
                          requested_techniques: Optional[List[str]] = None) -> List[Any]:
        """Select strategic techniques to use for development"""
        techniques = []
        
        # Use requested techniques if provided
        if requested_techniques:
            for tech_name in requested_techniques:
                technique = get_technique_by_name(tech_name)
                if technique:
                    techniques.append(technique)
        
        # If no requested techniques or none found, select based on theme
        if not techniques:
            # Get techniques for primary mandate
            primary_mandate = theme.get_primary_mandate()
            if primary_mandate:
                mandate_key_map = {
                    "2.1": CLMMandate.RESOURCE_ACQUISITION,
                    "2.2": CLMMandate.STRATEGIC_SECURITY,
                    "2.3": CLMMandate.VALUE_CATALYSIS
                }
                mandate = mandate_key_map.get(primary_mandate)
                if mandate:
                    available_techniques = get_techniques_for_mandate(mandate)
                    # Select preferred techniques or first 2
                    for tech in available_techniques[:2]:
                        if not self.preferred_techniques or tech.name in self.preferred_techniques:
                            techniques.append(tech)
        
        # Fallback to agent's preferred techniques
        if not techniques and self.preferred_techniques:
            for tech_name in self.preferred_techniques[:2]:
                technique = get_technique_by_name(tech_name)
                if technique:
                    techniques.append(technique)
        
        return techniques[:3]  # Limit to 3 techniques
    
    def _can_handle_theme(self, theme: StrategicTheme) -> bool:
        """Check if this agent can handle the given theme"""
        if not self.specialization_mandate:
            return True  # General agent can handle any theme
        
        # Check if theme aligns with specialization
        if theme.clm_alignment:
            mandate_key_map = {
                CLMMandate.RESOURCE_ACQUISITION: "2.1",
                CLMMandate.STRATEGIC_SECURITY: "2.2", 
                CLMMandate.VALUE_CATALYSIS: "2.3"
            }
            specialization_key = mandate_key_map.get(self.specialization_mandate)
            if specialization_key and specialization_key in theme.clm_alignment:
                # Must have strong alignment (>= 4.0) AND be the primary mandate
                my_score = theme.clm_alignment[specialization_key]
                if my_score < 4.0:
                    return False
                
                # Check if this is the highest scoring mandate (primary)
                primary_mandate = theme.get_primary_mandate()
                return primary_mandate == specialization_key
        
        # Check category alignment
        category_mandate_map = {
            "resource_acquisition": CLMMandate.RESOURCE_ACQUISITION,
            "strategic_security": CLMMandate.STRATEGIC_SECURITY,
            "value_catalysis": CLMMandate.VALUE_CATALYSIS
        }
        
        return category_mandate_map.get(theme.category.value) == self.specialization_mandate
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraints for prompt"""
        if not constraints:
            return "None specified"
        
        lines = []
        for key, value in constraints.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for prompt"""
        if not items:
            return "None specified"
        
        return "\n".join(f"- {item}" for item in items)
    
    def _format_techniques(self, techniques: List[Any]) -> str:
        """Format techniques for prompt"""
        if not techniques:
            return "None specified - use general strategic planning approach"
        
        lines = []
        for technique in techniques:
            lines.append(format_technique_for_prompt(technique))
        
        return "\n\n".join(lines)
    
    def _analyze_strategy(self, strategy: GenesisStrategy, theme: StrategicTheme) -> Dict[str, Any]:
        """Analyze developed strategy for insights"""
        analysis = {
            "recommendations": [],
            "step_count": len(strategy.steps),
            "estimated_timeline": strategy.estimated_timeline,
            "resource_count": len(strategy.resource_requirements)
        }
        
        # Check strategy complexity vs theme complexity
        complexity_map = {"simple": 1, "moderate": 2, "complex": 3, "highly_complex": 4}
        theme_complexity = complexity_map.get(theme.complexity_estimate, 2)
        
        if analysis["step_count"] > theme_complexity * 3:
            analysis["recommendations"].append(
                "Strategy has many steps - consider phasing or simplification"
            )
        
        if analysis["step_count"] < 3:
            analysis["recommendations"].append(
                "Strategy may need more detailed steps for successful implementation"
            )
        
        # Check resource requirements
        if analysis["resource_count"] > 8:
            analysis["recommendations"].append(
                "High resource requirements - ensure availability and prioritization"
            )
        
        # Check alignment with theme success criteria
        if len(theme.success_criteria) > 3:
            analysis["recommendations"].append(
                "Multiple success criteria - establish measurement and tracking systems"
            )
        
        return analysis