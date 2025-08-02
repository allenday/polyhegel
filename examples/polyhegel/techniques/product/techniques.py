"""
Product Roadmap Reasoning Domain for Polyhegel

Defines product strategy technique categories for roadmap-guided generation of product solutions.

Based on common product management domains:
- Feature Prioritization: Feature analysis, trade-off assessment, and priority ranking
- Market Analysis: Market opportunity assessment, competitive landscape, and user research
- Strategic Planning: Product vision, roadmap planning, and milestone optimization
- Resource Management: Resource allocation, timeline planning, and capacity management
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class ProductRoadmapDomain(Enum):
    """Product roadmap domain categories"""

    FEATURE_PRIORITIZATION = "feature_prioritization"
    MARKET_ANALYSIS = "market_analysis"
    STRATEGIC_PLANNING = "strategic_planning"
    RESOURCE_MANAGEMENT = "resource_management"

    @property
    def display_name(self) -> str:
        """Human-readable display name for the domain"""
        return str(DOMAIN_METADATA[self]["display_name"])

    @property
    def tags(self) -> List[str]:
        """Tags associated with this domain"""
        return list(DOMAIN_METADATA[self]["tags"])

    @property
    def description(self) -> str:
        """Description of this domain"""
        return str(DOMAIN_METADATA[self]["description"])


# Domain metadata dictionary
DOMAIN_METADATA: Dict[ProductRoadmapDomain, Dict[str, Any]] = {
    ProductRoadmapDomain.FEATURE_PRIORITIZATION: {
        "display_name": "Feature Prioritization",
        "description": "Feature analysis, trade-off assessment, and priority ranking for product development",
        "tags": ["features", "prioritization", "trade-offs", "analysis", "value", "effort"],
    },
    ProductRoadmapDomain.MARKET_ANALYSIS: {
        "display_name": "Market Analysis",
        "description": "Market opportunity assessment, competitive landscape analysis, and user research",
        "tags": ["market", "competition", "users", "research", "opportunity", "landscape"],
    },
    ProductRoadmapDomain.STRATEGIC_PLANNING: {
        "display_name": "Strategic Planning",
        "description": "Product vision definition, roadmap planning, and milestone optimization",
        "tags": ["strategy", "vision", "roadmap", "planning", "milestones", "goals"],
    },
    ProductRoadmapDomain.RESOURCE_MANAGEMENT: {
        "display_name": "Resource Management",
        "description": "Resource allocation, timeline planning, and capacity management for product development",
        "tags": ["resources", "allocation", "timeline", "capacity", "planning", "optimization"],
    },
}


@dataclass
class ProductRoadmapTechnique:
    """Represents a product roadmap technique with metadata"""

    name: str
    description: str
    domain: ProductRoadmapDomain
    use_cases: List[str]
    complexity: str  # "low", "medium", "high"
    impact_potential: str  # "low", "medium", "high"
    trade_offs: List[str]  # Key trade-offs to consider


# Feature Prioritization Techniques
FEATURE_PRIORITIZATION_TECHNIQUES = [
    ProductRoadmapTechnique(
        name="MoSCoW Prioritization",
        description="Categorize features into Must have, Should have, Could have, and Won't have",
        domain=ProductRoadmapDomain.FEATURE_PRIORITIZATION,
        use_cases=[
            "Initial feature backlog organization",
            "Release planning and scope definition",
            "Stakeholder alignment on feature importance",
        ],
        complexity="low",
        impact_potential="medium",
        trade_offs=[
            "Simplicity vs granular prioritization",
            "Stakeholder consensus vs decision speed",
            "Fixed categories vs dynamic priority levels",
        ],
    ),
    ProductRoadmapTechnique(
        name="Weighted Scoring (RICE)",
        description="Score features based on Reach, Impact, Confidence, and Effort",
        domain=ProductRoadmapDomain.FEATURE_PRIORITIZATION,
        use_cases=[
            "Data-driven feature prioritization",
            "Comparing features across different domains",
            "Resource allocation optimization",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Analytical rigor vs estimation effort",
            "Quantitative scoring vs qualitative judgment",
            "Historical data availability vs forward-looking assumptions",
        ],
    ),
    ProductRoadmapTechnique(
        name="Kano Model Analysis",
        description="Categorize features based on customer satisfaction impact",
        domain=ProductRoadmapDomain.FEATURE_PRIORITIZATION,
        use_cases=[
            "Understanding customer satisfaction drivers",
            "Balancing basic needs vs delight features",
            "Product differentiation strategy",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Customer research depth vs analysis speed",
            "Feature categorization accuracy vs implementation simplicity",
            "Current needs vs evolving expectations",
        ],
    ),
    ProductRoadmapTechnique(
        name="Value vs Effort Matrix",
        description="Plot features on a 2x2 matrix of business value and implementation effort",
        domain=ProductRoadmapDomain.FEATURE_PRIORITIZATION,
        use_cases=[
            "Quick wins identification",
            "Resource-constrained prioritization",
            "Portfolio-level feature comparison",
        ],
        complexity="low",
        impact_potential="medium",
        trade_offs=[
            "Simplicity vs nuanced evaluation",
            "Estimation accuracy vs decision speed",
            "Single metric focus vs multi-dimensional analysis",
        ],
    ),
    ProductRoadmapTechnique(
        name="Story Mapping and User Journey",
        description="Prioritize features based on user workflow and journey optimization",
        domain=ProductRoadmapDomain.FEATURE_PRIORITIZATION,
        use_cases=[
            "User experience optimization",
            "Feature sequence planning",
            "Identifying workflow gaps and friction points",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "User-centric focus vs business metrics",
            "Journey mapping effort vs prioritization speed",
            "Current workflow vs aspirational user experience",
        ],
    ),
]

# Market Analysis Techniques
MARKET_ANALYSIS_TECHNIQUES = [
    ProductRoadmapTechnique(
        name="Competitive Landscape Analysis",
        description="Systematic analysis of competitors' products, strategies, and market positioning",
        domain=ProductRoadmapDomain.MARKET_ANALYSIS,
        use_cases=[
            "Market positioning strategy",
            "Feature gap identification",
            "Competitive threat assessment",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Analysis depth vs market dynamics speed",
            "Public information vs proprietary insights",
            "Reactive positioning vs innovative differentiation",
        ],
    ),
    ProductRoadmapTechnique(
        name="Total Addressable Market (TAM) Analysis",
        description="Quantify market size and opportunity across different segments",
        domain=ProductRoadmapDomain.MARKET_ANALYSIS,
        use_cases=[
            "Market opportunity sizing",
            "Investment decision support",
            "Product expansion planning",
        ],
        complexity="high",
        impact_potential="high",
        trade_offs=[
            "Market research rigor vs estimation uncertainty",
            "Broad market view vs niche segment focus",
            "Current market size vs growth projections",
        ],
    ),
    ProductRoadmapTechnique(
        name="Customer Segmentation and Persona Analysis",
        description="Define and analyze distinct customer segments and their specific needs",
        domain=ProductRoadmapDomain.MARKET_ANALYSIS,
        use_cases=[
            "Targeted product development",
            "Go-to-market strategy optimization",
            "Feature customization by segment",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Segmentation granularity vs implementation complexity",
            "Persona accuracy vs development speed",
            "Current customers vs potential market expansion",
        ],
    ),
    ProductRoadmapTechnique(
        name="Jobs-to-be-Done Framework",
        description="Understand the fundamental job customers hire your product to do",
        domain=ProductRoadmapDomain.MARKET_ANALYSIS,
        use_cases=[
            "Product-market fit optimization",
            "Innovation opportunity identification",
            "Customer needs validation",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Job definition clarity vs customer complexity",
            "Research depth vs actionable insights speed",
            "Functional jobs vs emotional and social dimensions",
        ],
    ),
    ProductRoadmapTechnique(
        name="Market Trend and Technology Analysis",
        description="Analyze emerging trends, technologies, and their impact on product strategy",
        domain=ProductRoadmapDomain.MARKET_ANALYSIS,
        use_cases=[
            "Future product planning",
            "Technology adoption strategy",
            "Disruptive threat assessment",
        ],
        complexity="high",
        impact_potential="medium",
        trade_offs=[
            "Trend prediction accuracy vs investment timing",
            "Technology monitoring breadth vs focus depth",
            "Early adoption risks vs competitive advantage",
        ],
    ),
]

# Strategic Planning Techniques
STRATEGIC_PLANNING_TECHNIQUES = [
    ProductRoadmapTechnique(
        name="OKRs (Objectives and Key Results)",
        description="Set measurable objectives with specific key results for product strategy",
        domain=ProductRoadmapDomain.STRATEGIC_PLANNING,
        use_cases=[
            "Strategic goal alignment",
            "Progress measurement and accountability",
            "Cross-functional coordination",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Goal specificity vs adaptability",
            "Measurement rigor vs creative exploration",
            "Short-term focus vs long-term vision",
        ],
    ),
    ProductRoadmapTechnique(
        name="North Star Framework",
        description="Define a single metric that captures core product value for users",
        domain=ProductRoadmapDomain.STRATEGIC_PLANNING,
        use_cases=[
            "Product vision alignment",
            "Decision-making guidance",
            "Team focus and motivation",
        ],
        complexity="low",
        impact_potential="high",
        trade_offs=[
            "Single metric focus vs multifaceted value",
            "Simplicity vs comprehensive measurement",
            "Current state vs aspirational goals",
        ],
    ),
    ProductRoadmapTechnique(
        name="Theme-Based Roadmapping",
        description="Organize roadmap around strategic themes rather than specific features",
        domain=ProductRoadmapDomain.STRATEGIC_PLANNING,
        use_cases=[
            "Flexible roadmap communication",
            "Strategic initiative alignment",
            "Stakeholder expectation management",
        ],
        complexity="low",
        impact_potential="medium",
        trade_offs=[
            "Strategic flexibility vs execution clarity",
            "High-level communication vs detailed planning",
            "Theme coherence vs feature independence",
        ],
    ),
    ProductRoadmapTechnique(
        name="Scenario Planning and What-If Analysis",
        description="Plan for multiple future scenarios and their strategic implications",
        domain=ProductRoadmapDomain.STRATEGIC_PLANNING,
        use_cases=[
            "Risk mitigation planning",
            "Strategic option evaluation",
            "Uncertainty management",
        ],
        complexity="high",
        impact_potential="medium",
        trade_offs=[
            "Scenario comprehensiveness vs analysis paralysis",
            "Preparation depth vs resource allocation",
            "Risk awareness vs execution focus",
        ],
    ),
    ProductRoadmapTechnique(
        name="Lean Startup Build-Measure-Learn",
        description="Iterative cycle of hypothesis testing and validated learning",
        domain=ProductRoadmapDomain.STRATEGIC_PLANNING,
        use_cases=[
            "New product development",
            "Feature validation and iteration",
            "Market uncertainty navigation",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Experimentation speed vs comprehensive planning",
            "Learning focus vs execution pressure",
            "Iteration flexibility vs roadmap predictability",
        ],
    ),
]

# Resource Management Techniques
RESOURCE_MANAGEMENT_TECHNIQUES = [
    ProductRoadmapTechnique(
        name="Capacity Planning and Resource Allocation",
        description="Plan and allocate development resources across product initiatives",
        domain=ProductRoadmapDomain.RESOURCE_MANAGEMENT,
        use_cases=[
            "Team capacity optimization",
            "Multi-project resource balancing",
            "Delivery timeline planning",
        ],
        complexity="medium",
        impact_potential="high",
        trade_offs=[
            "Planning accuracy vs resource flexibility",
            "Utilization optimization vs innovation time",
            "Predictable delivery vs opportunity responsiveness",
        ],
    ),
    ProductRoadmapTechnique(
        name="Agile Portfolio Management",
        description="Manage multiple products/initiatives using agile principles",
        domain=ProductRoadmapDomain.RESOURCE_MANAGEMENT,
        use_cases=[
            "Multiple product coordination",
            "Priority balancing across initiatives",
            "Resource reallocation agility",
        ],
        complexity="high",
        impact_potential="high",
        trade_offs=[
            "Portfolio coordination vs team autonomy",
            "Strategic alignment vs local optimization",
            "Governance overhead vs delivery speed",
        ],
    ),
    ProductRoadmapTechnique(
        name="Critical Path Analysis",
        description="Identify dependencies and critical path for product delivery",
        domain=ProductRoadmapDomain.RESOURCE_MANAGEMENT,
        use_cases=[
            "Timeline optimization",
            "Bottleneck identification",
            "Risk mitigation planning",
        ],
        complexity="medium",
        impact_potential="medium",
        trade_offs=[
            "Planning detail vs execution flexibility",
            "Dependency tracking vs team independence",
            "Timeline predictability vs scope adaptability",
        ],
    ),
    ProductRoadmapTechnique(
        name="Budget and ROI Planning",
        description="Allocate budget and track return on investment for product initiatives",
        domain=ProductRoadmapDomain.RESOURCE_MANAGEMENT,
        use_cases=[
            "Investment justification",
            "Financial performance tracking",
            "Resource allocation optimization",
        ],
        complexity="high",
        impact_potential="high",
        trade_offs=[
            "Financial rigor vs innovation flexibility",
            "ROI measurement vs long-term value",
            "Budget constraints vs opportunity capture",
        ],
    ),
    ProductRoadmapTechnique(
        name="Risk Assessment and Mitigation",
        description="Identify, assess, and plan mitigation for product development risks",
        domain=ProductRoadmapDomain.RESOURCE_MANAGEMENT,
        use_cases=[
            "Project risk management",
            "Contingency planning",
            "Stakeholder risk communication",
        ],
        complexity="medium",
        impact_potential="medium",
        trade_offs=[
            "Risk analysis depth vs action speed",
            "Mitigation preparation vs resource utilization",
            "Risk awareness vs execution confidence",
        ],
    ),
]

# All techniques combined
ALL_TECHNIQUES = (
    FEATURE_PRIORITIZATION_TECHNIQUES
    + MARKET_ANALYSIS_TECHNIQUES
    + STRATEGIC_PLANNING_TECHNIQUES
    + RESOURCE_MANAGEMENT_TECHNIQUES
)

# Technique lookup by name
TECHNIQUE_REGISTRY: Dict[str, ProductRoadmapTechnique] = {technique.name: technique for technique in ALL_TECHNIQUES}

# Techniques by domain
TECHNIQUES_BY_DOMAIN: Dict[ProductRoadmapDomain, List[ProductRoadmapTechnique]] = {
    ProductRoadmapDomain.FEATURE_PRIORITIZATION: FEATURE_PRIORITIZATION_TECHNIQUES,
    ProductRoadmapDomain.MARKET_ANALYSIS: MARKET_ANALYSIS_TECHNIQUES,
    ProductRoadmapDomain.STRATEGIC_PLANNING: STRATEGIC_PLANNING_TECHNIQUES,
    ProductRoadmapDomain.RESOURCE_MANAGEMENT: RESOURCE_MANAGEMENT_TECHNIQUES,
}

# Techniques by complexity
TECHNIQUES_BY_COMPLEXITY: Dict[str, List[ProductRoadmapTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.complexity == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.complexity == "medium"],
    "high": [t for t in ALL_TECHNIQUES if t.complexity == "high"],
}

# Techniques by impact potential
TECHNIQUES_BY_IMPACT: Dict[str, List[ProductRoadmapTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.impact_potential == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.impact_potential == "medium"],
    "high": [t for t in ALL_TECHNIQUES if t.impact_potential == "high"],
}


def get_techniques_for_domain(domain: ProductRoadmapDomain) -> List[ProductRoadmapTechnique]:
    """Get all techniques for a specific product roadmap domain"""
    return TECHNIQUES_BY_DOMAIN.get(domain, [])


def get_techniques_by_complexity(complexity: str) -> List[ProductRoadmapTechnique]:
    """Get techniques filtered by complexity level"""
    return TECHNIQUES_BY_COMPLEXITY.get(complexity, [])


def get_techniques_by_impact(impact: str) -> List[ProductRoadmapTechnique]:
    """Get techniques filtered by impact potential"""
    return TECHNIQUES_BY_IMPACT.get(impact, [])


def get_technique_by_name(name: str) -> Optional[ProductRoadmapTechnique]:
    """Get a specific technique by name"""
    return TECHNIQUE_REGISTRY.get(name)


def get_recommended_techniques(
    domain: Optional[ProductRoadmapDomain] = None,
    complexity: Optional[str] = None,
    impact_potential: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[ProductRoadmapTechnique]:
    """
    Get recommended techniques based on filtering criteria

    Args:
        domain: Filter by product roadmap domain (optional)
        complexity: Filter by complexity level (optional)
        impact_potential: Filter by impact potential (optional)
        limit: Maximum number of techniques to return (optional)

    Returns:
        List of matching product roadmap techniques
    """
    techniques = ALL_TECHNIQUES

    if domain:
        techniques = [t for t in techniques if t.domain == domain]

    if complexity:
        techniques = [t for t in techniques if t.complexity == complexity]

    if impact_potential:
        techniques = [t for t in techniques if t.impact_potential == impact_potential]

    if limit:
        techniques = techniques[:limit]

    return techniques


def format_technique_for_prompt(technique: ProductRoadmapTechnique) -> str:
    """Format a technique for use in LLM prompts"""
    trade_offs_text = "\n".join(f"- {trade_off}" for trade_off in technique.trade_offs)
    use_cases_text = "\n".join(f"- {use_case}" for use_case in technique.use_cases)

    return f"""**{technique.name}** ({technique.domain.value})
{technique.description}

Use cases:
{use_cases_text}

Key Trade-offs:
{trade_offs_text}

Complexity: {technique.complexity.title()}
Impact Potential: {technique.impact_potential.title()}"""


def get_techniques_prompt_text(
    domain: Optional[ProductRoadmapDomain] = None,
    complexity: Optional[str] = None,
    impact_potential: Optional[str] = None,
    limit: int = 3,
) -> str:
    """Generate formatted text of techniques for LLM prompts"""
    techniques = get_recommended_techniques(domain, complexity, impact_potential, limit)

    if not techniques:
        return "No techniques match the specified criteria."

    technique_texts = [format_technique_for_prompt(t) for t in techniques]
    return "\n\n".join(technique_texts)


def analyze_product_requirements(
    requirements: Dict[str, Any],
) -> Dict[ProductRoadmapDomain, List[ProductRoadmapTechnique]]:
    """
    Analyze product requirements and recommend techniques by domain

    Args:
        requirements: Dictionary containing product requirements
                     e.g., {"impact_focus": "high", "complexity_tolerance": "medium", "timeline": "aggressive"}

    Returns:
        Dictionary mapping domains to recommended techniques
    """
    recommendations = {}

    impact_focus = requirements.get("impact_focus", "medium")
    complexity_tolerance = requirements.get("complexity_tolerance", "medium")
    timeline = requirements.get("timeline", "normal")

    for domain in ProductRoadmapDomain:
        domain_techniques = get_techniques_for_domain(domain)

        # Filter by impact focus
        if impact_focus == "high":
            domain_techniques = [t for t in domain_techniques if t.impact_potential in ["medium", "high"]]
        elif impact_focus == "low":
            domain_techniques = [t for t in domain_techniques if t.impact_potential == "low"]

        # Filter by complexity tolerance
        if complexity_tolerance == "low":
            domain_techniques = [t for t in domain_techniques if t.complexity in ["low", "medium"]]
        elif complexity_tolerance == "high":
            # Include all complexity levels
            pass
        else:  # medium
            domain_techniques = [t for t in domain_techniques if t.complexity != "high"]

        # Adjust for timeline constraints
        if timeline == "aggressive":
            # Prefer lower complexity techniques for aggressive timelines
            domain_techniques = sorted(domain_techniques, key=lambda t: t.complexity == "low", reverse=True)
        elif timeline == "extended":
            # Allow higher impact techniques even if complex
            domain_techniques = sorted(domain_techniques, key=lambda t: t.impact_potential == "high", reverse=True)

        recommendations[domain] = domain_techniques[:3]  # Top 3 recommendations per domain

    return recommendations


def generate_roadmap_priorities(
    features: List[Dict[str, Any]], technique_name: str = "Weighted Scoring (RICE)"
) -> List[Dict[str, Any]]:
    """
    Generate feature priorities using specified prioritization technique

    Args:
        features: List of feature dictionaries with attributes like reach, impact, confidence, effort
        technique_name: Prioritization technique to use

    Returns:
        List of features with priority scores and rankings
    """
    technique = get_technique_by_name(technique_name)
    if not technique:
        raise ValueError(f"Unknown prioritization technique: {technique_name}")

    prioritized_features = []

    for i, feature in enumerate(features):
        if technique_name == "Weighted Scoring (RICE)":
            # RICE scoring: (Reach * Impact * Confidence) / Effort
            reach = feature.get("reach", 1)
            impact = feature.get("impact", 1)
            confidence = feature.get("confidence", 1)
            effort = feature.get("effort", 1)

            rice_score = (reach * impact * confidence) / max(effort, 1)

            prioritized_features.append(
                {
                    **feature,
                    "priority_score": rice_score,
                    "prioritization_method": technique_name,
                    "rank": 0,  # Will be set after sorting
                }
            )

        elif technique_name == "MoSCoW Prioritization":
            # Simple categorical scoring
            priority_map = {"must": 4, "should": 3, "could": 2, "wont": 1}
            category = feature.get("moscow_category", "could").lower()
            priority_score = priority_map.get(category, 2)

            prioritized_features.append(
                {
                    **feature,
                    "priority_score": priority_score,
                    "prioritization_method": technique_name,
                    "moscow_category": category,
                    "rank": 0,
                }
            )

        else:
            # Default simple scoring for other techniques
            priority_score = feature.get("priority_score", i + 1)
            prioritized_features.append(
                {
                    **feature,
                    "priority_score": priority_score,
                    "prioritization_method": technique_name,
                    "rank": 0,
                }
            )

    # Sort by priority score (descending) and assign ranks
    prioritized_features.sort(key=lambda x: x["priority_score"], reverse=True)
    for i, feature in enumerate(prioritized_features):
        feature["rank"] = i + 1

    return prioritized_features


def evaluate_market_opportunity(market_data: Dict[str, Any], analysis_techniques: List[str] = None) -> Dict[str, Any]:
    """
    Evaluate market opportunity using specified analysis techniques

    Args:
        market_data: Dictionary containing market information
        analysis_techniques: List of analysis technique names to apply

    Returns:
        Dictionary containing market analysis results
    """
    if analysis_techniques is None:
        analysis_techniques = ["Total Addressable Market (TAM) Analysis", "Competitive Landscape Analysis"]

    analysis_results = {
        "market_data": market_data,
        "techniques_applied": analysis_techniques,
        "opportunity_score": 0,
        "risk_factors": [],
        "recommendations": [],
    }

    for technique_name in analysis_techniques:
        technique = get_technique_by_name(technique_name)
        if not technique:
            continue

        if technique_name == "Total Addressable Market (TAM) Analysis":
            # TAM analysis
            tam = market_data.get("total_addressable_market", 0)
            growth_rate = market_data.get("market_growth_rate", 0)

            # Simple scoring: higher TAM and growth rate = higher opportunity
            tam_score = min(tam / 1000000, 10)  # Scale to 0-10 based on millions
            growth_score = min(growth_rate * 10, 10)  # Scale growth rate to 0-10

            opportunity_component = (tam_score + growth_score) / 2
            analysis_results["opportunity_score"] += opportunity_component

            if tam < 100000:
                analysis_results["risk_factors"].append("Small total addressable market")
            if growth_rate < 0.05:
                analysis_results["risk_factors"].append("Low market growth rate")

        elif technique_name == "Competitive Landscape Analysis":
            # Competitive analysis
            competitor_count = market_data.get("competitor_count", 0)
            market_maturity = market_data.get("market_maturity", "emerging")

            # More competitors may indicate larger market but also more competition
            competition_score = max(10 - competitor_count, 0)

            maturity_scores = {"emerging": 8, "growing": 6, "mature": 4, "declining": 2}
            maturity_score = maturity_scores.get(market_maturity, 5)

            opportunity_component = (competition_score + maturity_score) / 2
            analysis_results["opportunity_score"] += opportunity_component

            if competitor_count > 10:
                analysis_results["risk_factors"].append("Highly competitive market")
            if market_maturity == "declining":
                analysis_results["risk_factors"].append("Declining market trend")

    # Normalize opportunity score
    analysis_results["opportunity_score"] = min(analysis_results["opportunity_score"] / len(analysis_techniques), 10)

    # Generate recommendations based on analysis
    if analysis_results["opportunity_score"] > 7:
        analysis_results["recommendations"].append("Strong market opportunity - consider aggressive investment")
    elif analysis_results["opportunity_score"] > 4:
        analysis_results["recommendations"].append("Moderate opportunity - proceed with careful planning")
    else:
        analysis_results["recommendations"].append("Limited opportunity - consider alternative markets")

    return analysis_results
