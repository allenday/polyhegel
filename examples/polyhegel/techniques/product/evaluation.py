"""
Product Domain Evaluation Utilities

This module provides evaluation metrics and assessment tools for product roadmap
strategies and feature prioritization decisions.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class ProductStrategyEvaluation:
    """Evaluation results for a product strategy"""

    overall_score: float
    dimension_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    risk_factors: List[str]
    success_probability: float


def evaluate_product_strategy(
    strategy: Dict[str, Any], evaluation_criteria: Optional[Dict[str, float]] = None
) -> ProductStrategyEvaluation:
    """
    Evaluate a product strategy across multiple dimensions

    Args:
        strategy: Product strategy dictionary
        evaluation_criteria: Custom weights for evaluation dimensions

    Returns:
        ProductStrategyEvaluation with scores and recommendations
    """
    # Default evaluation weights
    default_criteria = {
        "market_alignment": 0.25,
        "strategic_coherence": 0.25,
        "feature_prioritization": 0.25,
        "implementation_viability": 0.25,
    }

    criteria = evaluation_criteria or default_criteria
    dimension_scores = {}

    # Evaluate market alignment
    dimension_scores["market_alignment"] = _evaluate_market_alignment(strategy)

    # Evaluate strategic coherence
    dimension_scores["strategic_coherence"] = _evaluate_strategic_coherence(strategy)

    # Evaluate feature prioritization quality
    dimension_scores["feature_prioritization"] = _evaluate_feature_prioritization(strategy)

    # Evaluate implementation viability
    dimension_scores["implementation_viability"] = _evaluate_implementation_viability(strategy)

    # Calculate overall weighted score
    overall_score = sum(score * criteria.get(dimension, 0.25) for dimension, score in dimension_scores.items())

    # Generate strengths, weaknesses, and recommendations
    strengths = _identify_strengths(dimension_scores, strategy)
    weaknesses = _identify_weaknesses(dimension_scores, strategy)
    recommendations = _generate_recommendations(dimension_scores, strategy)
    risk_factors = _assess_risk_factors(strategy)

    # Calculate success probability based on scores and risk factors
    success_probability = _calculate_success_probability(overall_score, risk_factors)

    return ProductStrategyEvaluation(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        risk_factors=risk_factors,
        success_probability=success_probability,
    )


def _evaluate_market_alignment(strategy: Dict[str, Any]) -> float:
    """Evaluate market alignment dimension (1-5 scale)"""
    score = 3.0  # Base score

    # Check for market research and validation
    if "market_analysis" in strategy:
        market_data = strategy["market_analysis"]
        if market_data.get("total_addressable_market", 0) > 1000000:
            score += 0.5
        if market_data.get("market_growth_rate", 0) > 0.1:
            score += 0.5
        if market_data.get("competitor_count", 0) < 5:
            score += 0.3
        else:
            score -= 0.2

    # Check for customer segmentation
    if "customer_segments" in strategy:
        segments = strategy["customer_segments"]
        if len(segments) >= 2:
            score += 0.4
        if any("persona" in str(segment).lower() for segment in segments):
            score += 0.3

    # Check for competitive positioning
    if "competitive_analysis" in strategy:
        score += 0.4

    return min(max(score, 1.0), 5.0)


def _evaluate_strategic_coherence(strategy: Dict[str, Any]) -> float:
    """Evaluate strategic coherence dimension (1-5 scale)"""
    score = 3.0  # Base score

    # Check for vision and objectives
    if "vision" in strategy or "objectives" in strategy:
        score += 0.5

    # Check for OKRs or similar goal framework
    if "okrs" in strategy or "key_results" in strategy:
        score += 0.5

    # Check for strategic themes or priorities
    if "strategic_themes" in strategy or "priorities" in strategy:
        score += 0.4

    # Check for stakeholder alignment considerations
    if "stakeholder_alignment" in strategy:
        score += 0.3

    # Check for success metrics
    if "success_metrics" in strategy:
        metrics = strategy["success_metrics"]
        if len(metrics) >= 3:
            score += 0.3

    return min(max(score, 1.0), 5.0)


def _evaluate_feature_prioritization(strategy: Dict[str, Any]) -> float:
    """Evaluate feature prioritization quality (1-5 scale)"""
    score = 3.0  # Base score

    # Check for prioritization methodology
    if "prioritization_method" in strategy:
        method = strategy["prioritization_method"].lower()
        if any(framework in method for framework in ["rice", "moscow", "kano", "value"]):
            score += 0.6

    # Check for feature priorities with scores
    if "feature_priorities" in strategy:
        priorities = strategy["feature_priorities"]
        if len(priorities) >= 3:
            score += 0.4
            # Check if features have quantitative scores
            if any("priority_score" in feature for feature in priorities):
                score += 0.3
            # Check if features have effort estimates
            if any("effort" in feature for feature in priorities):
                score += 0.2

    # Check for trade-off analysis
    if "trade_offs" in strategy or any("trade_off" in str(item).lower() for item in strategy.values()):
        score += 0.3

    return min(max(score, 1.0), 5.0)


def _evaluate_implementation_viability(strategy: Dict[str, Any]) -> float:
    """Evaluate implementation viability (1-5 scale)"""
    score = 3.0  # Base score

    # Check for resource planning
    if "resource_requirements" in strategy:
        score += 0.4

    # Check for timeline planning
    if "timeline" in strategy or "milestones" in strategy:
        score += 0.4

    # Check for risk assessment
    if "risk_factors" in strategy or "risks" in strategy:
        score += 0.3

    # Check for implementation steps
    if "implementation_steps" in strategy:
        steps = strategy["implementation_steps"]
        if len(steps) >= 3:
            score += 0.4

    # Check for success measurement plan
    if "success_metrics" in strategy and "tracking" in str(strategy).lower():
        score += 0.3

    # Penalize if complexity is very high without adequate planning
    complexity_indicators = ["complex", "sophisticated", "advanced", "enterprise"]
    if any(indicator in str(strategy).lower() for indicator in complexity_indicators):
        if "risk_mitigation" not in strategy:
            score -= 0.3

    return min(max(score, 1.0), 5.0)


def _identify_strengths(dimension_scores: Dict[str, float], strategy: Dict[str, Any]) -> List[str]:
    """Identify strategy strengths based on high-scoring dimensions"""
    strengths = []

    # Identify top-performing dimensions
    sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)

    for dimension, score in sorted_dimensions:
        if score >= 4.0:
            if dimension == "market_alignment":
                strengths.append("Strong market research and competitive positioning")
            elif dimension == "strategic_coherence":
                strengths.append("Clear strategic vision and well-defined objectives")
            elif dimension == "feature_prioritization":
                strengths.append("Rigorous feature prioritization with data-driven methodology")
            elif dimension == "implementation_viability":
                strengths.append("Realistic implementation plan with adequate resource planning")

    # Look for specific strengths in strategy content
    if "rice" in str(strategy).lower():
        strengths.append("Uses RICE scoring methodology for quantitative prioritization")

    if "okr" in str(strategy).lower():
        strengths.append("Incorporates OKR framework for goal alignment")

    if len(strategy.get("success_metrics", [])) >= 5:
        strengths.append("Comprehensive success measurement framework")

    return strengths[:5]  # Limit to top 5 strengths


def _identify_weaknesses(dimension_scores: Dict[str, float], strategy: Dict[str, Any]) -> List[str]:
    """Identify strategy weaknesses based on low-scoring dimensions"""
    weaknesses = []

    # Identify low-performing dimensions
    sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1])

    for dimension, score in sorted_dimensions:
        if score < 3.0:
            if dimension == "market_alignment":
                weaknesses.append("Limited market validation and competitive analysis")
            elif dimension == "strategic_coherence":
                weaknesses.append("Unclear strategic vision or poorly defined objectives")
            elif dimension == "feature_prioritization":
                weaknesses.append("Weak feature prioritization methodology or rationale")
            elif dimension == "implementation_viability":
                weaknesses.append("Unrealistic implementation plan or inadequate resource planning")

    # Look for specific gaps
    if "risk" not in str(strategy).lower():
        weaknesses.append("Missing risk assessment and mitigation strategies")

    if not strategy.get("success_metrics"):
        weaknesses.append("Lacks clear success metrics and measurement framework")

    if not strategy.get("timeline") and not strategy.get("milestones"):
        weaknesses.append("Missing timeline and milestone planning")

    return weaknesses[:5]  # Limit to top 5 weaknesses


def _generate_recommendations(dimension_scores: Dict[str, float], strategy: Dict[str, Any]) -> List[str]:
    """Generate improvement recommendations based on evaluation"""
    recommendations = []

    # Recommendations based on low scores
    if dimension_scores.get("market_alignment", 3.0) < 3.5:
        recommendations.append("Conduct additional market research and competitive analysis")
        recommendations.append("Validate customer segments and personas with primary research")

    if dimension_scores.get("strategic_coherence", 3.0) < 3.5:
        recommendations.append("Define clearer strategic objectives and success criteria")
        recommendations.append("Implement OKR framework for goal alignment and tracking")

    if dimension_scores.get("feature_prioritization", 3.0) < 3.5:
        recommendations.append("Adopt rigorous prioritization methodology like RICE or Kano model")
        recommendations.append("Include quantitative impact and effort estimates for all features")

    if dimension_scores.get("implementation_viability", 3.0) < 3.5:
        recommendations.append("Develop detailed resource allocation and capacity planning")
        recommendations.append("Create comprehensive risk assessment and mitigation strategies")

    # General recommendations
    recommendations.append("Establish regular strategy review and adjustment processes")
    recommendations.append("Improve stakeholder communication and alignment mechanisms")

    return recommendations[:6]  # Limit to top 6 recommendations


def _assess_risk_factors(strategy: Dict[str, Any]) -> List[str]:
    """Identify potential risk factors in the strategy"""
    risk_factors = []

    # Market risks
    market_data = strategy.get("market_analysis", {})
    if market_data.get("competitor_count", 0) > 10:
        risk_factors.append("Highly competitive market with many established players")

    if market_data.get("market_growth_rate", 0) < 0.05:
        risk_factors.append("Low market growth rate may limit expansion opportunities")

    # Resource risks
    if not strategy.get("resource_requirements"):
        risk_factors.append("Unclear resource requirements may lead to under-estimation")

    # Timeline risks
    if "aggressive" in str(strategy).lower() or "urgent" in str(strategy).lower():
        risk_factors.append("Aggressive timeline increases execution risk")

    # Complexity risks
    if "complex" in str(strategy).lower() or "sophisticated" in str(strategy).lower():
        if not strategy.get("risk_mitigation"):
            risk_factors.append("High complexity without adequate risk mitigation")

    # Stakeholder risks
    if not strategy.get("stakeholder_alignment"):
        risk_factors.append("Lack of stakeholder alignment may cause implementation delays")

    return risk_factors


def _calculate_success_probability(overall_score: float, risk_factors: List[str]) -> float:
    """Calculate probability of strategy success"""
    # Base probability from overall score
    base_probability = (overall_score - 1.0) / 4.0  # Convert 1-5 scale to 0-1

    # Adjust for risk factors
    risk_penalty = len(risk_factors) * 0.05  # 5% penalty per risk factor

    probability = max(0.1, min(0.95, base_probability - risk_penalty))

    return round(probability, 2)


def compare_product_strategies(
    strategies: List[Dict[str, Any]], strategy_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare multiple product strategies and provide ranking

    Args:
        strategies: List of product strategy dictionaries
        strategy_names: Optional names for strategies

    Returns:
        Comparison analysis with rankings and recommendations
    """
    if not strategy_names:
        strategy_names = [f"Strategy {i+1}" for i in range(len(strategies))]

    evaluations = []
    for strategy in strategies:
        evaluation = evaluate_product_strategy(strategy)
        evaluations.append(evaluation)

    # Rank strategies by overall score
    strategy_rankings = sorted(zip(strategy_names, evaluations), key=lambda x: x[1].overall_score, reverse=True)

    comparison_result = {
        "rankings": [
            {
                "rank": i + 1,
                "name": name,
                "overall_score": eval_result.overall_score,
                "success_probability": eval_result.success_probability,
                "dimension_scores": eval_result.dimension_scores,
                "key_strengths": eval_result.strengths[:3],
                "key_weaknesses": eval_result.weaknesses[:3],
            }
            for i, (name, eval_result) in enumerate(strategy_rankings)
        ],
        "summary": {
            "best_strategy": strategy_rankings[0][0],
            "score_range": {
                "highest": strategy_rankings[0][1].overall_score,
                "lowest": strategy_rankings[-1][1].overall_score,
            },
            "average_score": statistics.mean([eval_result.overall_score for _, eval_result in strategy_rankings]),
        },
        "dimension_comparison": _compare_dimensions(evaluations, strategy_names),
        "recommendations": _generate_comparison_recommendations(strategy_rankings),
    }

    return comparison_result


def _compare_dimensions(evaluations: List[ProductStrategyEvaluation], strategy_names: List[str]) -> Dict[str, Any]:
    """Compare strategies across different dimensions"""
    dimensions = ["market_alignment", "strategic_coherence", "feature_prioritization", "implementation_viability"]

    dimension_comparison = {}
    for dimension in dimensions:
        scores = [eval_result.dimension_scores[dimension] for eval_result in evaluations]

        # Find best and worst performers for this dimension
        best_idx = scores.index(max(scores))
        worst_idx = scores.index(min(scores))

        dimension_comparison[dimension] = {
            "best_performer": strategy_names[best_idx],
            "best_score": scores[best_idx],
            "worst_performer": strategy_names[worst_idx],
            "worst_score": scores[worst_idx],
            "average_score": statistics.mean(scores),
            "score_range": max(scores) - min(scores),
        }

    return dimension_comparison


def _generate_comparison_recommendations(strategy_rankings: List[Tuple[str, ProductStrategyEvaluation]]) -> List[str]:
    """Generate recommendations based on strategy comparison"""
    recommendations = []

    best_strategy_name, best_evaluation = strategy_rankings[0]

    recommendations.append(
        f"Recommend {best_strategy_name} as primary strategy with {best_evaluation.overall_score:.1f}/5.0 overall score"
    )

    # Look for strategies that excel in specific dimensions
    # all_evaluations = [eval_result for _, eval_result in strategy_rankings]  # Currently unused

    # Find dimension leaders
    dimensions = ["market_alignment", "strategic_coherence", "feature_prioritization", "implementation_viability"]
    for dimension in dimensions:
        dimension_scores = [(name, eval_result.dimension_scores[dimension]) for name, eval_result in strategy_rankings]
        dimension_leader = max(dimension_scores, key=lambda x: x[1])

        if dimension_leader[0] != best_strategy_name and dimension_leader[1] >= 4.0:
            recommendations.append(
                f"Consider incorporating {dimension.replace('_', ' ')} elements from {dimension_leader[0]}"
            )

    # General recommendations
    avg_score = statistics.mean([eval_result.overall_score for _, eval_result in strategy_rankings])
    if avg_score < 3.5:
        recommendations.append(
            "All strategies need significant improvement - consider hybrid approach or additional analysis"
        )

    recommendations.append("Validate selected strategy with stakeholders before implementation")
    recommendations.append("Plan for iterative strategy refinement based on market feedback")

    return recommendations
