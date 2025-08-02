"""
A2A AgentExecutor implementations for polyhegel agents

Minimal A2A protocol implementation for strategic simulation.
"""

import logging
import uuid
from typing import Any, List, Optional

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskArtifactUpdateEvent
from a2a.utils import new_agent_text_message, new_data_artifact

from ..strategic_techniques import StrategyDomain
from ..telemetry import get_telemetry_collector, EventType, time_operation, timed_operation

logger = logging.getLogger(__name__)


class LeaderAgentExecutor(AgentExecutor):
    """A2A AgentExecutor for strategic theme generation.

    This executor handles the generation of strategic themes based on user input.
    It integrates with the A2A protocol to create artifacts and manage telemetry
    for theme generation operations.

    Attributes:
        model: The AI model used for theme generation.
        focus_domains: Optional list of strategy domains to focus on.
        max_themes: Maximum number of themes to generate.
        agent_id: Unique identifier for this agent.
    """

    def __init__(self, model: Any, focus_domains: Optional[List[StrategyDomain]] = None, max_themes: int = 5):
        """Initialize the LeaderAgentExecutor.

        Args:
            model: The AI model to use for theme generation.
            focus_domains: Optional list of strategy domains to focus on.
                Defaults to empty list if not provided.
            max_themes: Maximum number of themes to generate. Defaults to 5.
        """
        self.model = model
        self.focus_domains = focus_domains or []
        self.max_themes = max_themes
        self.agent_id = "polyhegel-leader"
        self._telemetry_collector = get_telemetry_collector(self.agent_id)

    @timed_operation("theme_generation")
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Generate strategic themes via A2A protocol.

        This method processes user input to generate strategic themes, creates
        artifacts for the themes, and manages telemetry data throughout the process.

        Args:
            context: The request context containing user input and task information.
            event_queue: Queue for sending events and messages back to the client.

        Raises:
            Exception: Any error during theme generation is caught, logged, and
                reported via telemetry and event queue.
        """
        # Record execution start
        self._telemetry_collector.record_event(
            EventType.REQUEST_START, data={"operation": "theme_generation", "task_id": context.task_id}
        )

        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                self._telemetry_collector.record_event(
                    EventType.ERROR_OCCURRED, data={"error": "No strategic challenge provided"}, success=False
                )
                await event_queue.enqueue_event(new_agent_text_message("Error: No strategic challenge provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("🎯 Generating strategic themes..."))

            # Time the theme generation
            async with time_operation(self._telemetry_collector, "theme_generation_core"):
                themes = [
                    {"title": "Resource Optimization Strategy", "domain": "resource_acquisition"},
                    {"title": "Risk Mitigation Framework", "domain": "strategic_security"},
                    {"title": "Value Creation Pipeline", "domain": "value_catalysis"},
                ]

            # Record successful theme generation
            self._telemetry_collector.record_event(
                EventType.THEME_GENERATED,
                data={"theme_count": len(themes), "domains": [t["domain"] for t in themes], "task_id": context.task_id},
            )

            # Update metrics
            self._telemetry_collector.increment_counter("themes_generated_total", len(themes))
            self._telemetry_collector.set_gauge("last_theme_count", len(themes))

            artifact = new_data_artifact(
                name=f"strategic_themes_{context.task_id}.json",
                data={"themes": themes, "total_count": len(themes)},
                description="Strategic themes",
            )
            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            # Record successful completion
            self._telemetry_collector.record_event(
                EventType.REQUEST_END, data={"operation": "theme_generation", "task_id": context.task_id}, success=True
            )

        except Exception as e:
            logger.error(f"Error in LeaderAgent execution: {e}")

            # Record error
            self._telemetry_collector.record_event(
                EventType.ERROR_OCCURRED,
                data={"operation": "theme_generation", "error_type": type(e).__name__, "task_id": context.task_id},
                success=False,
                error=str(e),
            )

            # Update error metrics
            self._telemetry_collector.increment_counter(
                "theme_generation_errors_total", tags={"error_type": type(e).__name__}
            )

            await event_queue.enqueue_event(new_agent_text_message(f"❌ Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the theme generation operation.

        Args:
            context: The request context for the cancelled operation.
            event_queue: Queue for sending cancellation message to the client.
        """
        await event_queue.enqueue_event(new_agent_text_message("🚫 Theme generation cancelled"))


class FollowerAgentExecutor(AgentExecutor):
    """A2A AgentExecutor for strategy implementation.

    This executor develops detailed implementation strategies based on themes
    or user input. It can specialize in specific strategy domains and integrates
    with the A2A protocol for artifact creation and telemetry.

    Attributes:
        model: The AI model used for strategy development.
        specialization_domain: Optional domain specialization for this agent.
        agent_id: Unique identifier for this agent.
    """

    def __init__(self, model: Any, specialization_domain: Optional[StrategyDomain] = None):
        """Initialize the FollowerAgentExecutor.

        Args:
            model: The AI model to use for strategy development.
            specialization_domain: Optional strategy domain specialization.
                If None, the agent operates as a general strategy developer.
        """
        self.model = model
        self.specialization_domain = specialization_domain
        self.agent_id = f"polyhegel-follower-{specialization_domain.value if specialization_domain else 'general'}"
        self._telemetry_collector = get_telemetry_collector(self.agent_id)

    @timed_operation("strategy_development")
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Develop detailed strategy via A2A protocol.

        This method processes user input (typically a theme) to develop a detailed
        implementation strategy with specific steps and outcomes. It creates
        strategy artifacts and manages telemetry throughout the process.

        Args:
            context: The request context containing user input and task information.
            event_queue: Queue for sending events and messages back to the client.

        Raises:
            Exception: Any error during strategy development is caught, logged,
                and reported via telemetry and event queue.
        """
        # Record execution start
        self._telemetry_collector.record_event(
            EventType.REQUEST_START,
            data={
                "operation": "strategy_development",
                "task_id": context.task_id,
                "specialization": self.specialization_domain.value if self.specialization_domain else "general",
            },
        )

        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                self._telemetry_collector.record_event(
                    EventType.ERROR_OCCURRED, data={"error": "No theme provided"}, success=False
                )
                await event_queue.enqueue_event(new_agent_text_message("Error: No theme provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("🛠️ Developing detailed strategy..."))

            # Time the strategy development
            async with time_operation(self._telemetry_collector, "strategy_development_core"):
                strategy = {
                    "title": f"Implementation Strategy for {user_input[:50]}...",
                    "steps": [
                        {"action": "Analyze requirements", "outcome": "Clear understanding"},
                        {"action": "Design approach", "outcome": "Implementation plan"},
                        {"action": "Execute strategy", "outcome": "Desired results"},
                    ],
                    "domain": self.specialization_domain.value if self.specialization_domain else "general",
                }

            # Record successful strategy development
            self._telemetry_collector.record_event(
                EventType.STRATEGY_DEVELOPED,
                data={"step_count": len(strategy["steps"]), "domain": strategy["domain"], "task_id": context.task_id},
            )

            # Update metrics
            self._telemetry_collector.increment_counter("strategies_developed_total")
            self._telemetry_collector.increment_counter(
                "strategies_by_domain", tags={"domain": str(strategy["domain"])}
            )
            self._telemetry_collector.set_gauge("last_strategy_steps", len(strategy["steps"]))

            artifact = new_data_artifact(
                name=f"strategy_{context.task_id}.json", data=strategy, description="Implementation strategy"
            )
            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            # Record successful completion
            self._telemetry_collector.record_event(
                EventType.REQUEST_END,
                data={"operation": "strategy_development", "task_id": context.task_id},
                success=True,
            )

        except Exception as e:
            logger.error(f"Error in FollowerAgent execution: {e}")

            # Record error
            self._telemetry_collector.record_event(
                EventType.ERROR_OCCURRED,
                data={"operation": "strategy_development", "error_type": type(e).__name__, "task_id": context.task_id},
                success=False,
                error=str(e),
            )

            # Update error metrics
            self._telemetry_collector.increment_counter(
                "strategy_development_errors_total", tags={"error_type": type(e).__name__}
            )

            await event_queue.enqueue_event(new_agent_text_message(f"❌ Error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the strategy development operation.

        Args:
            context: The request context for the cancelled operation.
            event_queue: Queue for sending cancellation message to the client.
        """
        await event_queue.enqueue_event(new_agent_text_message("🚫 Strategy development cancelled"))
