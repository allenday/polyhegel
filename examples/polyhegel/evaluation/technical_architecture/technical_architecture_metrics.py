"""
Technical Architecture Evaluation Metrics

Domain-specific metrics for evaluating technical architecture solutions,
including architecture quality assessment, technology stack decisions,
and performance/scalability frameworks.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import json

from ..technical_architecture import TechnicalArchitectureDomain


class MetricCategory(Enum):
    """Categories of technical architecture metrics"""

    QUALITY_ATTRIBUTES = "quality_attributes"
    TECHNICAL_EXCELLENCE = "technical_excellence"
    IMPLEMENTATION_FEASIBILITY = "implementation_feasibility"
    BUSINESS_ALIGNMENT = "business_alignment"


class MetricType(Enum):
    """Types of metric measurements"""

    SCORE = "score"  # 1-5 scale
    PERCENTAGE = "percentage"  # 0-100%
    BOOLEAN = "boolean"  # True/False
    DURATION = "duration"  # Time-based
    COST = "cost"  # Cost-based
    COUNT = "count"  # Numeric count


@dataclass
class ArchitectureMetric:
    """Represents a technical architecture evaluation metric"""

    name: str
    description: str
    category: MetricCategory
    metric_type: MetricType
    domain_relevance: List[TechnicalArchitectureDomain]
    weight: float  # 0.0 to 1.0, importance weight
    measurement_criteria: str
    target_range: Optional[Dict[str, Union[int, float]]] = None


# Quality Attributes Metrics
QUALITY_ATTRIBUTES_METRICS = [
    ArchitectureMetric(
        name="Scalability",
        description="Ability of the system to handle increased load through horizontal or vertical scaling",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.9,
        measurement_criteria="Rate 1-5 based on scaling mechanisms, bottleneck identification, and load handling",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Performance",
        description="System responsiveness, throughput, and resource efficiency",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.8,
        measurement_criteria="Rate 1-5 based on response times, throughput, and resource utilization",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Reliability",
        description="System availability, fault tolerance, and error recovery capabilities",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.9,
        measurement_criteria="Rate 1-5 based on failure handling, redundancy, and recovery mechanisms",
        target_range={"min": 4, "max": 5},
    ),
    ArchitectureMetric(
        name="Security",
        description="Protection against threats, data security, and compliance adherence",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[TechnicalArchitectureDomain.SECURITY_ARCHITECTURE],
        weight=1.0,
        measurement_criteria="Rate 1-5 based on security controls, threat mitigation, and compliance",
        target_range={"min": 4, "max": 5},
    ),
    ArchitectureMetric(
        name="Maintainability",
        description="Ease of modifying, updating, and extending the system",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        ],
        weight=0.7,
        measurement_criteria="Rate 1-5 based on code organization, modularity, and change impact",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Usability",
        description="User experience quality and interface effectiveness",
        category=MetricCategory.QUALITY_ATTRIBUTES,
        metric_type=MetricType.SCORE,
        domain_relevance=[TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE],
        weight=0.8,
        measurement_criteria="Rate 1-5 based on UX design, accessibility, and user satisfaction",
        target_range={"min": 3, "max": 5},
    ),
]

# Technical Excellence Metrics
TECHNICAL_EXCELLENCE_METRICS = [
    ArchitectureMetric(
        name="Architecture Pattern Appropriateness",
        description="Suitability of chosen architectural patterns for the problem domain",
        category=MetricCategory.TECHNICAL_EXCELLENCE,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.8,
        measurement_criteria="Rate 1-5 based on pattern selection, implementation quality, and problem fit",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Technology Stack Quality",
        description="Appropriateness and maturity of selected technologies",
        category=MetricCategory.TECHNICAL_EXCELLENCE,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.7,
        measurement_criteria="Rate 1-5 based on technology maturity, community support, and ecosystem fit",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Code Quality",
        description="Quality of implementation including structure, documentation, and testing",
        category=MetricCategory.TECHNICAL_EXCELLENCE,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        ],
        weight=0.6,
        measurement_criteria="Rate 1-5 based on code structure, documentation, test coverage, and best practices",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="API Design Quality",
        description="Quality of API design including consistency, documentation, and versioning",
        category=MetricCategory.TECHNICAL_EXCELLENCE,
        metric_type=MetricType.SCORE,
        domain_relevance=[TechnicalArchitectureDomain.BACKEND_ARCHITECTURE],
        weight=0.7,
        measurement_criteria="Rate 1-5 based on REST/GraphQL design, documentation, and versioning strategy",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Data Architecture Quality",
        description="Quality of data modeling, storage, and access patterns",
        category=MetricCategory.TECHNICAL_EXCELLENCE,
        metric_type=MetricType.SCORE,
        domain_relevance=[TechnicalArchitectureDomain.BACKEND_ARCHITECTURE],
        weight=0.8,
        measurement_criteria="Rate 1-5 based on data modeling, consistency, and access patterns",
        target_range={"min": 3, "max": 5},
    ),
]

# Implementation Feasibility Metrics
IMPLEMENTATION_FEASIBILITY_METRICS = [
    ArchitectureMetric(
        name="Implementation Complexity",
        description="Overall complexity of implementing the proposed architecture",
        category=MetricCategory.IMPLEMENTATION_FEASIBILITY,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
            TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        ],
        weight=0.8,
        measurement_criteria="Rate 1-5 (1=very complex, 5=simple) based on implementation difficulty",
        target_range={"min": 2, "max": 5},
    ),
    ArchitectureMetric(
        name="Development Time Estimate",
        description="Estimated time required for implementation in person-months",
        category=MetricCategory.IMPLEMENTATION_FEASIBILITY,
        metric_type=MetricType.DURATION,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
            TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        ],
        weight=0.7,
        measurement_criteria="Estimate in person-months based on scope and complexity",
        target_range={"min": 1, "max": 24},
    ),
    ArchitectureMetric(
        name="Team Skill Requirements",
        description="Level of specialized skills required for implementation",
        category=MetricCategory.IMPLEMENTATION_FEASIBILITY,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
            TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        ],
        weight=0.6,
        measurement_criteria="Rate 1-5 based on skill level required (1=expert, 5=junior friendly)",
        target_range={"min": 2, "max": 5},
    ),
    ArchitectureMetric(
        name="Infrastructure Cost",
        description="Estimated monthly infrastructure and operational costs",
        category=MetricCategory.IMPLEMENTATION_FEASIBILITY,
        metric_type=MetricType.COST,
        domain_relevance=[TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE],
        weight=0.8,
        measurement_criteria="Estimate monthly costs in USD based on resource requirements",
        target_range={"min": 100, "max": 50000},
    ),
    ArchitectureMetric(
        name="Third-party Dependencies",
        description="Number and complexity of external dependencies",
        category=MetricCategory.IMPLEMENTATION_FEASIBILITY,
        metric_type=MetricType.COUNT,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        ],
        weight=0.5,
        measurement_criteria="Count of critical third-party dependencies",
        target_range={"min": 0, "max": 10},
    ),
]

# Business Alignment Metrics
BUSINESS_ALIGNMENT_METRICS = [
    ArchitectureMetric(
        name="Requirements Coverage",
        description="Percentage of functional requirements addressed by the architecture",
        category=MetricCategory.BUSINESS_ALIGNMENT,
        metric_type=MetricType.PERCENTAGE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        ],
        weight=1.0,
        measurement_criteria="Percentage of stated requirements covered by the solution",
        target_range={"min": 90, "max": 100},
    ),
    ArchitectureMetric(
        name="Business Value Delivery",
        description="How well the architecture enables business value creation",
        category=MetricCategory.BUSINESS_ALIGNMENT,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.9,
        measurement_criteria="Rate 1-5 based on business value enablement and strategic alignment",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Time to Market",
        description="How quickly the solution can be delivered to users",
        category=MetricCategory.BUSINESS_ALIGNMENT,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.7,
        measurement_criteria="Rate 1-5 based on delivery speed (1=slow, 5=fast)",
        target_range={"min": 3, "max": 5},
    ),
    ArchitectureMetric(
        name="Future Adaptability",
        description="Ability to adapt to changing business requirements",
        category=MetricCategory.BUSINESS_ALIGNMENT,
        metric_type=MetricType.SCORE,
        domain_relevance=[
            TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
            TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
            TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        ],
        weight=0.8,
        measurement_criteria="Rate 1-5 based on flexibility and extensibility",
        target_range={"min": 3, "max": 5},
    ),
]

# All metrics combined
ALL_METRICS = (
    QUALITY_ATTRIBUTES_METRICS
    + TECHNICAL_EXCELLENCE_METRICS
    + IMPLEMENTATION_FEASIBILITY_METRICS
    + BUSINESS_ALIGNMENT_METRICS
)

# Metrics organized by category
METRICS_BY_CATEGORY = {
    MetricCategory.QUALITY_ATTRIBUTES: QUALITY_ATTRIBUTES_METRICS,
    MetricCategory.TECHNICAL_EXCELLENCE: TECHNICAL_EXCELLENCE_METRICS,
    MetricCategory.IMPLEMENTATION_FEASIBILITY: IMPLEMENTATION_FEASIBILITY_METRICS,
    MetricCategory.BUSINESS_ALIGNMENT: BUSINESS_ALIGNMENT_METRICS,
}

# Metrics organized by domain
METRICS_BY_DOMAIN = {}
for domain in TechnicalArchitectureDomain:
    METRICS_BY_DOMAIN[domain] = [metric for metric in ALL_METRICS if domain in metric.domain_relevance]


@dataclass
class MetricEvaluation:
    """Represents an evaluation result for a specific metric"""

    metric: ArchitectureMetric
    value: Union[int, float, bool, str]
    justification: str
    confidence: str  # "high", "medium", "low"
    evidence: List[str]  # Supporting evidence


@dataclass
class ArchitectureEvaluationResult:
    """Complete evaluation result for a technical architecture solution"""

    solution_id: str
    domain: TechnicalArchitectureDomain
    metric_evaluations: List[MetricEvaluation]
    overall_score: float
    category_scores: Dict[MetricCategory, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    evaluation_timestamp: str


class TechnicalArchitectureEvaluator:
    """Evaluator for technical architecture solutions using domain-specific metrics"""

    def __init__(self, domain: Optional[TechnicalArchitectureDomain] = None):
        """Initialize evaluator for specific domain or all domains."""
        self.domain = domain
        self.metrics = METRICS_BY_DOMAIN.get(domain, ALL_METRICS) if domain else ALL_METRICS

    def get_relevant_metrics(
        self, domain: Optional[TechnicalArchitectureDomain] = None, category: Optional[MetricCategory] = None
    ) -> List[ArchitectureMetric]:
        """Get metrics relevant to specific domain and/or category."""
        metrics = self.metrics

        if domain:
            metrics = [m for m in metrics if domain in m.domain_relevance]

        if category:
            metrics = [m for m in metrics if m.category == category]

        return metrics

    def calculate_weighted_score(self, evaluations: List[MetricEvaluation]) -> float:
        """Calculate weighted overall score from metric evaluations."""
        if not evaluations:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for evaluation in evaluations:
            if evaluation.metric.metric_type == MetricType.SCORE:
                # Normalize score to 0-1 range (assuming 1-5 scale)
                normalized_score = (float(evaluation.value) - 1) / 4
                total_weighted_score += normalized_score * evaluation.metric.weight
                total_weight += evaluation.metric.weight
            elif evaluation.metric.metric_type == MetricType.PERCENTAGE:
                # Percentage already in 0-100 range, normalize to 0-1
                normalized_score = float(evaluation.value) / 100
                total_weighted_score += normalized_score * evaluation.metric.weight
                total_weight += evaluation.metric.weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def calculate_category_scores(self, evaluations: List[MetricEvaluation]) -> Dict[MetricCategory, float]:
        """Calculate scores for each metric category."""
        category_scores = {}

        for category in MetricCategory:
            category_evaluations = [e for e in evaluations if e.metric.category == category]
            if category_evaluations:
                category_scores[category] = self.calculate_weighted_score(category_evaluations)

        return category_scores

    def generate_evaluation_summary(self, result: ArchitectureEvaluationResult) -> str:
        """Generate human-readable evaluation summary."""
        summary_parts = [
            "Technical Architecture Evaluation Summary",
            f"Domain: {result.domain.display_name}",
            f"Overall Score: {result.overall_score:.2f}/1.00",
            "",
            "Category Scores:",
        ]

        for category, score in result.category_scores.items():
            summary_parts.append(f"- {category.value.replace('_', ' ').title()}: {score:.2f}")

        summary_parts.extend(
            [
                "",
                "Key Strengths:",
            ]
        )
        for strength in result.strengths:
            summary_parts.append(f"- {strength}")

        summary_parts.extend(
            [
                "",
                "Areas for Improvement:",
            ]
        )
        for weakness in result.weaknesses:
            summary_parts.append(f"- {weakness}")

        summary_parts.extend(
            [
                "",
                "Recommendations:",
            ]
        )
        for recommendation in result.recommendations:
            summary_parts.append(f"- {recommendation}")

        return "\n".join(summary_parts)

    def export_evaluation_to_json(self, result: ArchitectureEvaluationResult) -> str:
        """Export evaluation result to JSON format."""
        export_data = {
            "solution_id": result.solution_id,
            "domain": result.domain.value,
            "overall_score": result.overall_score,
            "category_scores": {cat.value: score for cat, score in result.category_scores.items()},
            "metric_evaluations": [
                {
                    "metric_name": eval.metric.name,
                    "category": eval.metric.category.value,
                    "value": eval.value,
                    "justification": eval.justification,
                    "confidence": eval.confidence,
                    "evidence": eval.evidence,
                }
                for eval in result.metric_evaluations
            ],
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "recommendations": result.recommendations,
            "evaluation_timestamp": result.evaluation_timestamp,
        }

        return json.dumps(export_data, indent=2)


def get_metrics_for_domain(domain: TechnicalArchitectureDomain) -> List[ArchitectureMetric]:
    """Get all metrics relevant to a specific technical architecture domain."""
    return METRICS_BY_DOMAIN.get(domain, [])


def get_metrics_by_category(category: MetricCategory) -> List[ArchitectureMetric]:
    """Get all metrics in a specific category."""
    return METRICS_BY_CATEGORY.get(category, [])


def create_evaluation_template(
    domain: TechnicalArchitectureDomain, categories: Optional[List[MetricCategory]] = None
) -> Dict[str, Any]:
    """Create an evaluation template for a specific domain and categories."""
    relevant_metrics = get_metrics_for_domain(domain)

    if categories:
        relevant_metrics = [m for m in relevant_metrics if m.category in categories]

    template = {
        "domain": domain.value,
        "metrics": [
            {
                "name": metric.name,
                "description": metric.description,
                "category": metric.category.value,
                "metric_type": metric.metric_type.value,
                "weight": metric.weight,
                "measurement_criteria": metric.measurement_criteria,
                "target_range": metric.target_range,
                "value": None,  # To be filled during evaluation
                "justification": "",  # To be filled during evaluation
                "confidence": "",  # To be filled during evaluation
                "evidence": [],  # To be filled during evaluation
            }
            for metric in relevant_metrics
        ],
    }

    return template
