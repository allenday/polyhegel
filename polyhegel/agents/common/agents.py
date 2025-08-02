"""
Common Cross-Domain Agent Implementations

Provides default agent implementations that work with common cross-domain techniques.
These agents serve as both functional tools and reference implementations.
"""

import logging
import uuid
from typing import Any, List
from pathlib import Path

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskArtifactUpdateEvent
from a2a.utils import new_agent_text_message, new_data_artifact

from ...techniques.common import (
    get_common_technique,
    TechniqueType,
)

logger = logging.getLogger(__name__)


class CommonAnalysisLeader(AgentExecutor):
    """
    Leader agent that coordinates cross-domain analytical techniques.

    This agent can orchestrate various common techniques like stakeholder analysis,
    SWOT analysis, trade-off analysis, risk assessment, consensus building, and
    scenario planning across any domain context.
    """

    def __init__(self, model: Any, max_techniques: int = 3):
        """
        Initialize the CommonAnalysisLeader.

        Args:
            model: The AI model to use for coordination and analysis
            max_techniques: Maximum number of techniques to recommend/coordinate
        """
        self.model = model
        self.max_techniques = max_techniques
        self.agent_id = "polyhegel-common-leader"

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Coordinate cross-domain analysis by selecting appropriate common techniques.

        Args:
            context: The request context containing user input and task information
            event_queue: Queue for sending events and messages back to the client
        """
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(new_agent_text_message("Error: No analysis request provided"))
                return

            await event_queue.enqueue_event(
                new_agent_text_message("🎯 Analyzing request and selecting appropriate techniques...")
            )

            # Analyze the request and recommend techniques
            recommended_techniques = self._analyze_and_recommend_techniques(user_input)

            # Create analysis plan
            analysis_plan = {
                "request": user_input,
                "recommended_techniques": [
                    {
                        "name": technique.name,
                        "type": technique.technique_type.value,
                        "complexity": technique.complexity.value,
                        "timeframe": technique.timeframe.value,
                        "rationale": f"Recommended because: {technique.description}",
                    }
                    for technique in recommended_techniques
                ],
                "coordination_approach": self._design_coordination_approach(recommended_techniques),
                "expected_outcomes": self._describe_expected_outcomes(recommended_techniques),
            }

            # Send analysis plan as artifact
            artifact = new_data_artifact(
                name=f"analysis_plan_{context.task_id}.json",
                data=analysis_plan,
                description="Cross-domain analysis plan with recommended techniques",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(
                new_agent_text_message(
                    f"✅ Created analysis plan with {len(recommended_techniques)} recommended techniques. "
                    f"Coordinate with specialized followers to execute: {', '.join(t.name for t in recommended_techniques)}"
                )
            )

        except Exception as e:
            logger.error(f"Error in CommonAnalysisLeader execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Analysis coordination error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancel the analysis coordination."""
        await event_queue.enqueue_event(new_agent_text_message("🚫 Analysis coordination cancelled"))

    def _analyze_and_recommend_techniques(self, request: str) -> List[Any]:
        """Analyze the request and recommend appropriate common techniques."""

        # Simple keyword-based technique selection (in practice, this would use the LLM)
        request_lower = request.lower()
        recommended = []

        # Stakeholder analysis for multi-party situations
        if any(word in request_lower for word in ["stakeholder", "people", "team", "group", "party", "user"]):
            if stakeholder_tech := get_common_technique("Stakeholder Analysis"):
                recommended.append(stakeholder_tech)

        # SWOT for strategic situations
        if any(word in request_lower for word in ["strategy", "position", "competitive", "strength", "weakness"]):
            if swot_tech := get_common_technique("SWOT Analysis"):
                recommended.append(swot_tech)

        # Trade-off analysis for decision situations
        if any(
            word in request_lower for word in ["decision", "choice", "option", "alternative", "compare", "evaluate"]
        ):
            if tradeoff_tech := get_common_technique("Trade-off Analysis"):
                recommended.append(tradeoff_tech)

        # Risk assessment for risk-related situations
        if any(word in request_lower for word in ["risk", "threat", "danger", "problem", "issue", "failure"]):
            if risk_tech := get_common_technique("Risk Assessment"):
                recommended.append(risk_tech)

        # Consensus building for conflict/agreement situations
        if any(word in request_lower for word in ["consensus", "agreement", "conflict", "negotiate", "align"]):
            if consensus_tech := get_common_technique("Consensus Building"):
                recommended.append(consensus_tech)

        # Scenario planning for future-oriented situations
        if any(word in request_lower for word in ["future", "scenario", "planning", "forecast", "uncertainty"]):
            if scenario_tech := get_common_technique("Scenario Planning"):
                recommended.append(scenario_tech)

        # If no specific matches, recommend a basic set
        if not recommended:
            recommended = [
                get_common_technique("Stakeholder Analysis"),
                get_common_technique("SWOT Analysis"),
                get_common_technique("Risk Assessment"),
            ]
            recommended = [tech for tech in recommended if tech is not None]

        return recommended[: self.max_techniques]

    def _design_coordination_approach(self, techniques: List[Any]) -> str:
        """Design the approach for coordinating multiple techniques."""
        if len(techniques) == 1:
            return f"Execute {techniques[0].name} as a focused analysis"
        elif len(techniques) == 2:
            return f"Execute {techniques[0].name} first to establish foundation, then {techniques[1].name} to build upon results"
        else:
            foundation = [t for t in techniques if t.technique_type == TechniqueType.ANALYSIS]
            planning = [t for t in techniques if t.technique_type == TechniqueType.PLANNING]
            coordination = [t for t in techniques if t.technique_type == TechniqueType.COORDINATION]
            evaluation = [t for t in techniques if t.technique_type == TechniqueType.EVALUATION]

            approach = "Multi-stage analysis: "
            if foundation:
                approach += f"1) Foundation analysis ({', '.join(t.name for t in foundation)}), "
            if evaluation:
                approach += f"2) Evaluation phase ({', '.join(t.name for t in evaluation)}), "
            if planning:
                approach += f"3) Planning phase ({', '.join(t.name for t in planning)}), "
            if coordination:
                approach += f"4) Coordination phase ({', '.join(t.name for t in coordination)})"

            return approach.rstrip(", ")

    def _describe_expected_outcomes(self, techniques: List[Any]) -> List[str]:
        """Describe expected outcomes from the recommended techniques."""
        outcomes = []
        for technique in techniques:
            outcomes.extend(technique.outputs_provided)
        return list(set(outcomes))  # Remove duplicates


class StakeholderAnalysisFollower(AgentExecutor):
    """Follower agent specialized in stakeholder identification and analysis."""

    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-stakeholder-follower"
        self.technique = get_common_technique("Stakeholder Analysis")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute stakeholder analysis."""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(
                    new_agent_text_message("Error: No stakeholder analysis request provided")
                )
                return

            await event_queue.enqueue_event(new_agent_text_message("👥 Conducting stakeholder analysis..."))

            # Load stakeholder analysis prompt
            prompt_path = (
                Path(__file__).parent.parent.parent / "techniques" / "common" / "prompts" / "stakeholder_analysis.md"
            )

            if prompt_path.exists():
                prompt_template = prompt_path.read_text()
                # Simple template substitution (in practice, use a proper template engine)
                prompt = prompt_template.replace("{{context}}", user_input)
                prompt = prompt.replace("{{scope}}", "comprehensive")
                prompt = prompt.replace("{{domain}}", "cross-domain")
            else:
                prompt = f"Conduct a comprehensive stakeholder analysis for: {user_input}"

            # This would integrate with the actual LLM model
            analysis_result = {
                "request": user_input,
                "technique_used": self.technique.name,
                "analysis_type": "stakeholder_identification_and_mapping",
                "placeholder_results": {
                    "stakeholders_identified": ["Primary Stakeholder 1", "Secondary Stakeholder 2", "Key Influencer 3"],
                    "engagement_strategy": "Multi-tiered approach based on interest/influence matrix",
                    "key_risks": ["Stakeholder misalignment", "Communication gaps"],
                    "next_steps": ["Conduct stakeholder interviews", "Develop communication plan"],
                },
                "prompt_used": prompt,
            }

            # Send results as artifact
            artifact = new_data_artifact(
                name=f"stakeholder_analysis_{context.task_id}.json",
                data=analysis_result,
                description="Stakeholder analysis results",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(new_agent_text_message("✅ Stakeholder analysis completed successfully"))

        except Exception as e:
            logger.error(f"Error in StakeholderAnalysisFollower execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Stakeholder analysis error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("🚫 Stakeholder analysis cancelled"))


class TradeoffAnalysisFollower(AgentExecutor):
    """Follower agent focused on systematic option evaluation and trade-off analysis."""

    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-tradeoff-follower"
        self.technique = get_common_technique("Trade-off Analysis")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute trade-off analysis."""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(new_agent_text_message("Error: No trade-off analysis request provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("⚖️ Conducting systematic trade-off analysis..."))

            # This would integrate with the actual LLM model and trade-off analysis prompt
            analysis_result = {
                "request": user_input,
                "technique_used": self.technique.name,
                "analysis_type": "multi_criteria_decision_analysis",
                "placeholder_results": {
                    "options_evaluated": ["Option A", "Option B", "Option C"],
                    "evaluation_criteria": ["Cost", "Performance", "Risk", "Timeline"],
                    "recommended_option": "Option B",
                    "trade_off_summary": "Option B provides best balance of performance and risk",
                    "sensitivity_analysis": "Results robust to moderate changes in cost weighting",
                },
            }

            # Send results as artifact
            artifact = new_data_artifact(
                name=f"tradeoff_analysis_{context.task_id}.json",
                data=analysis_result,
                description="Trade-off analysis results",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(new_agent_text_message("✅ Trade-off analysis completed successfully"))

        except Exception as e:
            logger.error(f"Error in TradeoffAnalysisFollower execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Trade-off analysis error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("🚫 Trade-off analysis cancelled"))


class RiskAssessmentFollower(AgentExecutor):
    """Follower agent specialized in risk identification and mitigation planning."""

    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-risk-follower"
        self.technique = get_common_technique("Risk Assessment")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute risk assessment."""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(new_agent_text_message("Error: No risk assessment request provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("🛡️ Conducting comprehensive risk assessment..."))

            # This would integrate with the actual LLM model and risk assessment prompt
            analysis_result = {
                "request": user_input,
                "technique_used": self.technique.name,
                "analysis_type": "comprehensive_risk_assessment",
                "placeholder_results": {
                    "risks_identified": [
                        {
                            "id": "R001",
                            "description": "Technical implementation risk",
                            "probability": 3,
                            "impact": 4,
                            "score": 12,
                        },
                        {
                            "id": "R002",
                            "description": "Resource availability risk",
                            "probability": 2,
                            "impact": 3,
                            "score": 6,
                        },
                        {
                            "id": "R003",
                            "description": "Stakeholder alignment risk",
                            "probability": 4,
                            "impact": 3,
                            "score": 12,
                        },
                    ],
                    "high_priority_risks": ["R001", "R003"],
                    "mitigation_strategies": {
                        "R001": "Proof of concept development and technical review",
                        "R003": "Stakeholder engagement and communication plan",
                    },
                    "monitoring_plan": "Weekly risk review with monthly comprehensive assessment",
                },
            }

            # Send results as artifact
            artifact = new_data_artifact(
                name=f"risk_assessment_{context.task_id}.json",
                data=analysis_result,
                description="Risk assessment results",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(new_agent_text_message("✅ Risk assessment completed successfully"))

        except Exception as e:
            logger.error(f"Error in RiskAssessmentFollower execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Risk assessment error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("🚫 Risk assessment cancelled"))


class ConsensusBuilderFollower(AgentExecutor):
    """Follower agent that facilitates multi-party agreement processes."""

    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-consensus-follower"
        self.technique = get_common_technique("Consensus Building")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute consensus building facilitation."""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(new_agent_text_message("Error: No consensus building request provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("🤝 Designing consensus building process..."))

            # This would integrate with the actual LLM model and consensus building prompt
            analysis_result = {
                "request": user_input,
                "technique_used": self.technique.name,
                "analysis_type": "consensus_building_process_design",
                "placeholder_results": {
                    "stakeholder_positions": {
                        "Group A": "Prefers rapid implementation",
                        "Group B": "Emphasizes risk mitigation",
                        "Group C": "Focuses on cost optimization",
                    },
                    "common_ground": ["All groups want successful outcome", "Shared concern about timeline"],
                    "process_design": {
                        "phase_1": "Foundation setting and relationship building",
                        "phase_2": "Interest exploration and option generation",
                        "phase_3": "Agreement development and implementation planning",
                    },
                    "facilitation_strategy": "Interest-based negotiation with structured dialogue",
                    "success_metrics": ["Agreement reached", "Implementation commitment", "Relationship quality"],
                },
            }

            # Send results as artifact
            artifact = new_data_artifact(
                name=f"consensus_building_{context.task_id}.json",
                data=analysis_result,
                description="Consensus building process design",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(
                new_agent_text_message("✅ Consensus building process designed successfully")
            )

        except Exception as e:
            logger.error(f"Error in ConsensusBuilderFollower execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Consensus building error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("🚫 Consensus building cancelled"))


class ScenarioPlanningFollower(AgentExecutor):
    """Follower agent specialized in scenario planning and future analysis."""

    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-scenario-follower"
        self.technique = get_common_technique("Scenario Planning")

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute scenario planning analysis."""
        try:
            user_input = context.get_user_input()
            if not user_input.strip():
                await event_queue.enqueue_event(new_agent_text_message("Error: No scenario planning request provided"))
                return

            await event_queue.enqueue_event(new_agent_text_message("🔮 Developing scenario planning analysis..."))

            # This would integrate with the actual LLM model and scenario planning prompt
            analysis_result = {
                "request": user_input,
                "technique_used": self.technique.name,
                "analysis_type": "multi_scenario_planning",
                "placeholder_results": {
                    "driving_forces": ["Technology adoption", "Market conditions", "Regulatory changes"],
                    "scenarios": [
                        {
                            "name": "Rapid Growth",
                            "probability": 0.3,
                            "key_characteristics": ["High adoption", "Favorable regulation"],
                        },
                        {
                            "name": "Steady Progress",
                            "probability": 0.5,
                            "key_characteristics": ["Moderate adoption", "Stable regulation"],
                        },
                        {
                            "name": "Challenging Environment",
                            "probability": 0.2,
                            "key_characteristics": ["Slow adoption", "Restrictive regulation"],
                        },
                    ],
                    "robust_strategies": ["Flexible architecture", "Diversified approach", "Strong partnerships"],
                    "early_indicators": ["Market adoption rates", "Regulatory announcements", "Competitive moves"],
                    "monitoring_plan": "Monthly indicator tracking with quarterly scenario review",
                },
            }

            # Send results as artifact
            artifact = new_data_artifact(
                name=f"scenario_planning_{context.task_id}.json",
                data=analysis_result,
                description="Scenario planning analysis results",
            )

            task_id = context.task_id or str(uuid.uuid4())
            artifact_event = TaskArtifactUpdateEvent(
                task_id=task_id, context_id=task_id, artifact=artifact, append=False, last_chunk=True
            )
            await event_queue.enqueue_event(artifact_event)

            await event_queue.enqueue_event(
                new_agent_text_message("✅ Scenario planning analysis completed successfully")
            )

        except Exception as e:
            logger.error(f"Error in ScenarioPlanningFollower execution: {e}")
            await event_queue.enqueue_event(new_agent_text_message(f"❌ Scenario planning error: {str(e)}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("🚫 Scenario planning cancelled"))
