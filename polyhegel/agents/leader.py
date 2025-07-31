"""
Leader agent implementation for strategic theme generation

Leader agents generate high-level strategic themes that guide
follower agents in developing detailed implementation strategies.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic_ai import Agent

from ..models import StrategicTheme, ThemeCategory
from ..strategic_techniques import CLMMandate, get_techniques_for_mandate
from .base import (
    BaseAgent, AgentRole, AgentCapabilities, AgentContext, AgentResponse
)

logger = logging.getLogger(__name__)


class LeaderAgent(BaseAgent):
    """
    Leader agent for generating strategic themes
    
    Leader agents focus on high-level strategic direction,
    identifying key themes and priorities that align with
    organizational mandates and objectives.
    """
    
    def __init__(self,
                 agent_id: str,
                 model: Any,
                 focus_mandates: Optional[List[CLMMandate]] = None,
                 max_themes: int = 5):
        """
        Initialize leader agent
        
        Args:
            agent_id: Unique identifier for this agent
            model: pydantic-ai model instance
            focus_mandates: Optional list of CLM mandates to focus on
            max_themes: Maximum number of themes to generate
        """
        # Define leader role
        role = AgentRole(
            name="Strategic Leader",
            description="Generates high-level strategic themes and priorities",
            mandate=None,  # Leaders work across mandates
            specialization="Strategic Theme Development",
            hierarchy_level=0  # Leader level
        )
        
        # Define leader capabilities
        capabilities = AgentCapabilities(
            can_generate_strategies=True,
            can_evaluate_strategies=False,
            can_coordinate_agents=True,
            supported_mandates=focus_mandates or list(CLMMandate),
            preferred_techniques=[]
        )
        
        # Initialize base agent
        super().__init__(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities,
            model=model
        )
        
        self.focus_mandates = focus_mandates or list(CLMMandate)
        self.max_themes = max_themes
        
        # Configure theme generation agent
        if self.pydantic_agent:
            self.theme_agent = Agent(
                self.model,
                system_prompt=self._build_theme_prompt(),
                result_type=List[StrategicTheme]
            )
        else:
            # For mock models in tests
            self.theme_agent = None
    
    def _build_theme_prompt(self) -> str:
        """Build specialized prompt for theme generation"""
        base_prompt = self._build_system_prompt()
        
        theme_prompt = f"""{base_prompt}

Your primary task is to generate strategic themes that provide clear direction
for detailed strategy development. Each theme should:

1. Address a specific strategic opportunity or challenge
2. Align with one or more organizational mandates
3. Be actionable and implementable
4. Consider stakeholder needs and constraints
5. Balance ambition with feasibility

Focus areas for theme generation:
- Resource optimization and acquisition strategies
- Security and resilience mechanisms
- Value creation and catalysis opportunities
- Cross-functional integration possibilities
- Innovation and competitive differentiation

Generate {self.max_themes} strategic themes maximum.
Ensure themes are diverse and complementary, not redundant.
"""
        
        return theme_prompt
    
    async def generate_themes(self, context: AgentContext) -> List[StrategicTheme]:
        """
        Generate strategic themes based on context
        
        Args:
            context: Strategic context with challenge and constraints
            
        Returns:
            List of strategic themes
        """
        self.set_context(context)
        
        # Build theme generation prompt
        prompt = f"""Strategic Challenge: {context.strategic_challenge}

Constraints:
{self._format_constraints(context.constraints)}

Objectives:
{self._format_list(context.objectives)}

Stakeholders:
{self._format_list(context.stakeholders)}

Generate strategic themes that address this challenge while respecting constraints
and achieving objectives. Consider all stakeholder perspectives.

Focus on themes that align with these mandates:
{self._format_mandates()}
"""
        
        try:
            # Generate themes using pydantic-ai agent
            if not self.theme_agent:
                # For testing - just return empty list
                return []
                
            result = await self.theme_agent.run(prompt)
            themes = result.data
            
            # Filter themes by focus mandates if specified
            if self.focus_mandates:
                themes = self._filter_themes_by_mandate(themes)
            
            # Limit to max themes
            themes = themes[:self.max_themes]
            
            # Record generation
            self.add_interaction("theme_generation", {
                "prompt": prompt,
                "themes_generated": len(themes),
                "themes": [t.model_dump() for t in themes]
            })
            
            logger.info(f"Leader {self.agent_id} generated {len(themes)} themes")
            return themes
            
        except Exception as e:
            logger.error(f"Theme generation failed: {e}")
            self.add_interaction("theme_generation_error", {
                "error": str(e),
                "prompt": prompt
            })
            return []
    
    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate that this leader agent can handle the request"""
        request_type = request.get("type", "")
        
        # Leader agents only handle generate_themes requests
        return request_type == "generate_themes"
    
    async def process_request(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process a request to generate themes
        
        Args:
            request: Request with context information
            
        Returns:
            AgentResponse with generated themes
        """
        request_type = request.get("type", "")
        
        if request_type != "generate_themes":
            return self.create_response(
                success=False,
                content="LeaderAgent only handles 'generate_themes' requests",
                reasoning=f"Received request type: {request_type}"
            )
        
        # Extract context from request
        context_data = request.get("context", {})
        if not context_data:
            return self.create_response(
                success=False,
                content="No context provided for theme generation",
                reasoning="Strategic context is required"
            )
        
        # Create context object
        try:
            context = AgentContext(**context_data)
        except Exception as e:
            return self.create_response(
                success=False,
                content=f"Invalid context: {e}",
                reasoning="Failed to parse context data"
            )
        
        # Generate themes
        themes = await self.generate_themes(context)
        
        if not themes:
            return self.create_response(
                success=False,
                content="No themes generated",
                reasoning="Theme generation failed or returned empty"
            )
        
        # Analyze themes for recommendations
        analysis = self._analyze_themes(themes)
        
        return self.create_response(
            success=True,
            content=themes,
            reasoning=f"Generated {len(themes)} strategic themes addressing the challenge",
            confidence=0.85,
            next_actions=[
                f"Assign follower agents to develop detailed strategies for each theme",
                f"Prioritize themes based on: {', '.join(analysis['priority_order'][:3])}",
                f"Consider cross-theme synergies for integrated approach"
            ],
            recommendations=analysis['recommendations']
        )
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Return summary of leader capabilities"""
        return {
            "agent_type": "leader",
            "specialization": self.role.specialization,
            "max_themes": self.max_themes,
            "focus_mandates": [m.value for m in self.focus_mandates],
            "can_coordinate": self.capabilities.can_coordinate_agents,
            "hierarchy_level": self.role.hierarchy_level
        }
    
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
    
    def _format_mandates(self) -> str:
        """Format focus mandates for prompt"""
        lines = []
        for mandate in self.focus_mandates:
            lines.append(f"- {mandate.value}")
            # Add some techniques as examples
            techniques = get_techniques_for_mandate(mandate)[:2]
            for tech in techniques:
                lines.append(f"  * {tech.name}: {tech.description}")
        return "\n".join(lines)
    
    def _filter_themes_by_mandate(self, themes: List[StrategicTheme]) -> List[StrategicTheme]:
        """Filter themes to focus on specified mandates"""
        filtered = []
        
        for theme in themes:
            # Check if theme aligns with any focus mandate
            if theme.clm_alignment:
                mandate_map = {
                    "2.1": CLMMandate.RESOURCE_ACQUISITION,
                    "2.2": CLMMandate.STRATEGIC_SECURITY,
                    "2.3": CLMMandate.VALUE_CATALYSIS
                }
                
                for mandate_key, score in theme.clm_alignment.items():
                    if score > 3.0 and mandate_map.get(mandate_key) in self.focus_mandates:
                        filtered.append(theme)
                        break
            else:
                # If no alignment specified, include if category matches
                category_mandate_map = {
                    ThemeCategory.RESOURCE_ACQUISITION: CLMMandate.RESOURCE_ACQUISITION,
                    ThemeCategory.STRATEGIC_SECURITY: CLMMandate.STRATEGIC_SECURITY,
                    ThemeCategory.VALUE_CATALYSIS: CLMMandate.VALUE_CATALYSIS
                }
                
                if category_mandate_map.get(theme.category) in self.focus_mandates:
                    filtered.append(theme)
        
        return filtered
    
    def _analyze_themes(self, themes: List[StrategicTheme]) -> Dict[str, Any]:
        """Analyze generated themes for insights"""
        analysis = {
            "priority_order": [],
            "recommendations": [],
            "mandate_coverage": {},
            "complexity_distribution": {}
        }
        
        # Sort by priority
        priority_values = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_themes = sorted(
            themes,
            key=lambda t: priority_values.get(t.priority_level, 2),
            reverse=True
        )
        analysis["priority_order"] = [t.title for t in sorted_themes]
        
        # Analyze mandate coverage
        for theme in themes:
            primary = theme.get_primary_mandate()
            if primary:
                analysis["mandate_coverage"][primary] = \
                    analysis["mandate_coverage"].get(primary, 0) + 1
        
        # Analyze complexity
        for theme in themes:
            complexity = theme.complexity_estimate
            analysis["complexity_distribution"][complexity] = \
                analysis["complexity_distribution"].get(complexity, 0) + 1
        
        # Generate recommendations
        if len(themes) > 3:
            analysis["recommendations"].append(
                "Consider phased implementation starting with highest priority themes"
            )
        
        if analysis["complexity_distribution"].get("highly_complex", 0) > 1:
            analysis["recommendations"].append(
                "Multiple highly complex themes identified - ensure adequate resources"
            )
        
        # Check for cross-cutting themes
        cross_cutting = [t for t in themes if t.is_cross_cutting()]
        if cross_cutting:
            analysis["recommendations"].append(
                f"{len(cross_cutting)} cross-cutting themes identified - "
                "consider integrated implementation approach"
            )
        
        return analysis