"""
A2A AgentExecutor implementations for polyhegel agents

Minimal A2A protocol implementation for strategic simulation.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_data_artifact

from ..strategic_techniques import StrategyDomain

logger = logging.getLogger(__name__)


class LeaderAgentExecutor(AgentExecutor):
    """A2A AgentExecutor for strategic theme generation"""
    
    def __init__(self, model: Any, focus_domains: Optional[List[StrategyDomain]] = None, max_themes: int = 5):
        self.model = model
        self.focus_domains = focus_domains or []
        self.max_themes = max_themes
        
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Generate strategic themes via A2A protocol"""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(
                    new_agent_text_message("Error: No strategic challenge provided")
                )
                return
            
            await event_queue.enqueue_event(
                new_agent_text_message("🎯 Generating strategic themes...")
            )
            
            # Simple theme generation
            themes = [
                {"title": "Resource Optimization Strategy", "domain": "resource_acquisition"},
                {"title": "Risk Mitigation Framework", "domain": "strategic_security"}, 
                {"title": "Value Creation Pipeline", "domain": "value_catalysis"}
            ]
            
            artifact = new_data_artifact(
                name=f"strategic_themes_{context.task_id}.json",
                data={"themes": themes, "total_count": len(themes)},
                description="Strategic themes"
            )
            await event_queue.enqueue_event(artifact)
            
        except Exception as e:
            logger.error(f"Error in LeaderAgent execution: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"❌ Error: {str(e)}")
            )
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            new_agent_text_message("🚫 Theme generation cancelled")
        )


class FollowerAgentExecutor(AgentExecutor):
    """A2A AgentExecutor for strategy implementation"""
    
    def __init__(self, model: Any, specialization_domain: Optional[StrategyDomain] = None):
        self.model = model
        self.specialization_domain = specialization_domain
        
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Develop detailed strategy via A2A protocol"""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(
                    new_agent_text_message("Error: No theme provided")
                )
                return
            
            await event_queue.enqueue_event(
                new_agent_text_message("🛠️ Developing detailed strategy...")
            )
            
            # Simple strategy generation
            strategy = {
                "title": f"Implementation Strategy for {user_input[:50]}...",
                "steps": [
                    {"action": "Analyze requirements", "outcome": "Clear understanding"},
                    {"action": "Design approach", "outcome": "Implementation plan"},
                    {"action": "Execute strategy", "outcome": "Desired results"}
                ],
                "domain": self.specialization_domain.value if self.specialization_domain else "general"
            }
            
            artifact = new_data_artifact(
                name=f"strategy_{context.task_id}.json",
                data=strategy,
                description="Implementation strategy"
            )
            await event_queue.enqueue_event(artifact)
            
        except Exception as e:
            logger.error(f"Error in FollowerAgent execution: {e}")
            await event_queue.enqueue_event(
                new_agent_text_message(f"❌ Error: {str(e)}")
            )
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(
            new_agent_text_message("🚫 Strategy development cancelled")
        )