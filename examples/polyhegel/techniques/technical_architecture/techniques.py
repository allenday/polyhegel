"""
Technical Architecture Domain for Polyhegel

Defines technical architecture technique categories for architecture-guided generation of technical solutions.

Based on common technical architecture domains:
- Backend Architecture: Server-side systems, APIs, databases, and data processing
- Frontend Architecture: User interfaces, client-side systems, and user experience
- Infrastructure Architecture: Cloud systems, deployment, scaling, and operations
- Security Architecture: Security patterns, authentication, authorization, and threat mitigation
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class TechnicalArchitectureDomain(Enum):
    """Technical architecture domain categories"""

    BACKEND_ARCHITECTURE = "backend_architecture"
    FRONTEND_ARCHITECTURE = "frontend_architecture"
    INFRASTRUCTURE_ARCHITECTURE = "infrastructure_architecture"
    SECURITY_ARCHITECTURE = "security_architecture"

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
DOMAIN_METADATA: Dict[TechnicalArchitectureDomain, Dict[str, Any]] = {
    TechnicalArchitectureDomain.BACKEND_ARCHITECTURE: {
        "display_name": "Backend Architecture",
        "description": "Server-side systems, APIs, databases, and data processing architecture",
        "tags": ["backend", "api", "database", "server", "microservices", "data"],
    },
    TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE: {
        "display_name": "Frontend Architecture",
        "description": "User interfaces, client-side systems, and user experience architecture",
        "tags": ["frontend", "ui", "ux", "client", "browser", "mobile"],
    },
    TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE: {
        "display_name": "Infrastructure Architecture",
        "description": "Cloud systems, deployment, scaling, and operations architecture",
        "tags": ["infrastructure", "cloud", "deployment", "scaling", "devops", "containers"],
    },
    TechnicalArchitectureDomain.SECURITY_ARCHITECTURE: {
        "display_name": "Security Architecture",
        "description": "Security patterns, authentication, authorization, and threat mitigation",
        "tags": ["security", "authentication", "authorization", "encryption", "compliance"],
    },
}


@dataclass
class TechnicalArchitectureTechnique:
    """Represents a technical architecture technique with metadata"""

    name: str
    description: str
    domain: TechnicalArchitectureDomain
    use_cases: List[str]
    complexity: str  # "low", "medium", "high"
    scalability_impact: str  # "low", "medium", "high"
    trade_offs: List[str]  # Key trade-offs to consider


# Backend Architecture Techniques
BACKEND_ARCHITECTURE_TECHNIQUES = [
    TechnicalArchitectureTechnique(
        name="Microservices Architecture",
        description="Decompose application into small, independent services that communicate via APIs",
        domain=TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
        use_cases=[
            "Large-scale applications with multiple teams",
            "Systems requiring independent scaling of components",
            "Applications with diverse technology requirements",
        ],
        complexity="high",
        scalability_impact="high",
        trade_offs=[
            "Increased operational complexity vs independent deployments",
            "Network latency vs service isolation",
            "Distributed debugging vs fault isolation",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Event-Driven Architecture",
        description="Design system components to communicate through events and message passing",
        domain=TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
        use_cases=[
            "Real-time data processing systems",
            "Decoupled system integration",
            "Audit trails and system monitoring",
        ],
        complexity="medium",
        scalability_impact="high",
        trade_offs=[
            "Loose coupling vs eventual consistency",
            "Event ordering complexity vs system responsiveness",
            "Message queue overhead vs system resilience",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="API Gateway Pattern",
        description="Single entry point for all client requests with routing, composition, and protocol translation",
        domain=TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
        use_cases=[
            "Microservices API management",
            "Cross-cutting concerns like authentication",
            "API versioning and backward compatibility",
        ],
        complexity="medium",
        scalability_impact="medium",
        trade_offs=[
            "Single point of failure vs centralized management",
            "Additional latency vs simplified client integration",
            "Gateway complexity vs service independence",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Database Sharding",
        description="Horizontal partitioning of database across multiple servers",
        domain=TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
        use_cases=[
            "High-volume transactional systems",
            "Geographic data distribution",
            "Performance scaling beyond single server limits",
        ],
        complexity="high",
        scalability_impact="high",
        trade_offs=[
            "Query complexity vs performance scaling",
            "Cross-shard transactions vs data locality",
            "Rebalancing overhead vs uniform distribution",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="CQRS (Command Query Responsibility Segregation)",
        description="Separate read and write operations using different models",
        domain=TechnicalArchitectureDomain.BACKEND_ARCHITECTURE,
        use_cases=[
            "Complex domain models with different read/write patterns",
            "Performance optimization for read-heavy workloads",
            "Event sourcing implementations",
        ],
        complexity="high",
        scalability_impact="medium",
        trade_offs=[
            "Model complexity vs performance optimization",
            "Data consistency vs read/write independence",
            "Development overhead vs query flexibility",
        ],
    ),
]

# Frontend Architecture Techniques
FRONTEND_ARCHITECTURE_TECHNIQUES = [
    TechnicalArchitectureTechnique(
        name="Component-Based Architecture",
        description="Build UI using reusable, encapsulated components with well-defined interfaces",
        domain=TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        use_cases=[
            "Large-scale web applications",
            "Design system implementation",
            "Team collaboration on UI development",
        ],
        complexity="medium",
        scalability_impact="medium",
        trade_offs=[
            "Initial setup complexity vs long-term maintainability",
            "Component granularity vs reusability",
            "Prop drilling vs component coupling",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Micro-Frontend Architecture",
        description="Decompose frontend into independent, deployable applications",
        domain=TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        use_cases=[
            "Large organizations with multiple frontend teams",
            "Legacy system modernization",
            "Technology diversity requirements",
        ],
        complexity="high",
        scalability_impact="high",
        trade_offs=[
            "Team autonomy vs user experience consistency",
            "Bundle size vs independent deployments",
            "Integration complexity vs development independence",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Progressive Web App (PWA)",
        description="Web applications with native app-like capabilities and offline functionality",
        domain=TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        use_cases=[
            "Mobile-first web applications",
            "Offline-capable applications",
            "App store distribution without native development",
        ],
        complexity="medium",
        scalability_impact="low",
        trade_offs=[
            "Development complexity vs native app capabilities",
            "Browser compatibility vs advanced features",
            "Cache management vs data freshness",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Server-Side Rendering (SSR)",
        description="Render web pages on the server before sending to client",
        domain=TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        use_cases=[
            "SEO-critical applications",
            "Improved initial page load performance",
            "Social media content sharing",
        ],
        complexity="medium",
        scalability_impact="medium",
        trade_offs=[
            "Server load vs client performance",
            "Development complexity vs SEO benefits",
            "Caching strategies vs dynamic content",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="State Management Architecture",
        description="Centralized application state management with predictable state transitions",
        domain=TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE,
        use_cases=[
            "Complex application state interactions",
            "Predictable state debugging",
            "Time-travel debugging and state persistence",
        ],
        complexity="medium",
        scalability_impact="low",
        trade_offs=[
            "Boilerplate code vs predictable state management",
            "Learning curve vs debugging capabilities",
            "Performance overhead vs state consistency",
        ],
    ),
]

# Infrastructure Architecture Techniques
INFRASTRUCTURE_ARCHITECTURE_TECHNIQUES = [
    TechnicalArchitectureTechnique(
        name="Container Orchestration",
        description="Automated deployment, scaling, and management of containerized applications",
        domain=TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        use_cases=[
            "Microservices deployment and scaling",
            "Multi-environment application delivery",
            "Resource optimization and high availability",
        ],
        complexity="high",
        scalability_impact="high",
        trade_offs=[
            "Operational complexity vs deployment flexibility",
            "Resource overhead vs isolation benefits",
            "Learning curve vs automation capabilities",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Infrastructure as Code (IaC)",
        description="Define and provision infrastructure through machine-readable definition files",
        domain=TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        use_cases=[
            "Reproducible infrastructure deployments",
            "Version-controlled infrastructure changes",
            "Multi-environment consistency",
        ],
        complexity="medium",
        scalability_impact="medium",
        trade_offs=[
            "Initial setup time vs long-term maintainability",
            "Tool-specific syntax vs infrastructure portability",
            "State management complexity vs deployment automation",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Auto-Scaling Architecture",
        description="Automatically adjust resource allocation based on demand metrics",
        domain=TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        use_cases=[
            "Variable traffic applications",
            "Cost optimization for cloud resources",
            "Performance maintenance under load",
        ],
        complexity="medium",
        scalability_impact="high",
        trade_offs=[
            "Scaling latency vs resource efficiency",
            "Metric complexity vs scaling accuracy",
            "Over-provisioning vs under-provisioning risks",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Multi-Region Deployment",
        description="Deploy applications across multiple geographic regions for availability and performance",
        domain=TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        use_cases=[
            "Global application availability",
            "Disaster recovery and business continuity",
            "Latency optimization for global users",
        ],
        complexity="high",
        scalability_impact="high",
        trade_offs=[
            "Deployment complexity vs availability guarantees",
            "Data consistency vs geographic performance",
            "Cost overhead vs risk mitigation",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Serverless Architecture",
        description="Run applications without managing server infrastructure, using Function-as-a-Service",
        domain=TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE,
        use_cases=[
            "Event-driven processing applications",
            "Variable or unpredictable workloads",
            "Rapid prototyping and development",
        ],
        complexity="low",
        scalability_impact="high",
        trade_offs=[
            "Cold start latency vs automatic scaling",
            "Vendor lock-in vs operational simplicity",
            "Debugging complexity vs infrastructure management",
        ],
    ),
]

# Security Architecture Techniques
SECURITY_ARCHITECTURE_TECHNIQUES = [
    TechnicalArchitectureTechnique(
        name="Zero Trust Architecture",
        description="Security model that requires verification for every user and device",
        domain=TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        use_cases=[
            "Remote work and BYOD environments",
            "Cloud-native application security",
            "Compliance with strict security requirements",
        ],
        complexity="high",
        scalability_impact="medium",
        trade_offs=[
            "Security rigor vs user experience",
            "Implementation complexity vs threat protection",
            "Performance overhead vs comprehensive verification",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="OAuth 2.0 / OpenID Connect",
        description="Delegated authorization and authentication protocols for secure API access",
        domain=TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        use_cases=[
            "Third-party application integration",
            "Single sign-on (SSO) implementations",
            "Mobile and web application authentication",
        ],
        complexity="medium",
        scalability_impact="low",
        trade_offs=[
            "Protocol complexity vs security standardization",
            "Token management vs session security",
            "Redirect flows vs user experience",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="API Security Gateway",
        description="Centralized security enforcement for API access control and threat protection",
        domain=TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        use_cases=[
            "Microservices security enforcement",
            "API rate limiting and DDoS protection",
            "Centralized security policy management",
        ],
        complexity="medium",
        scalability_impact="medium",
        trade_offs=[
            "Central control vs distributed security",
            "Gateway performance vs security features",
            "Policy complexity vs security coverage",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Encryption at Rest and in Transit",
        description="Comprehensive data protection through encryption in storage and communication",
        domain=TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        use_cases=[
            "Sensitive data protection requirements",
            "Regulatory compliance (GDPR, HIPAA)",
            "Multi-tenant application security",
        ],
        complexity="medium",
        scalability_impact="low",
        trade_offs=[
            "Performance overhead vs data protection",
            "Key management complexity vs security assurance",
            "Encryption granularity vs operational simplicity",
        ],
    ),
    TechnicalArchitectureTechnique(
        name="Security Monitoring and SIEM",
        description="Continuous security monitoring with automated threat detection and response",
        domain=TechnicalArchitectureDomain.SECURITY_ARCHITECTURE,
        use_cases=[
            "Real-time threat detection",
            "Compliance auditing and reporting",
            "Incident response automation",
        ],
        complexity="high",
        scalability_impact="medium",
        trade_offs=[
            "Monitoring overhead vs threat visibility",
            "False positive rates vs detection sensitivity",
            "Tool complexity vs security coverage",
        ],
    ),
]

# All techniques combined
ALL_TECHNIQUES = (
    BACKEND_ARCHITECTURE_TECHNIQUES
    + FRONTEND_ARCHITECTURE_TECHNIQUES
    + INFRASTRUCTURE_ARCHITECTURE_TECHNIQUES
    + SECURITY_ARCHITECTURE_TECHNIQUES
)

# Technique lookup by name
TECHNIQUE_REGISTRY: Dict[str, TechnicalArchitectureTechnique] = {
    technique.name: technique for technique in ALL_TECHNIQUES
}

# Techniques by domain
TECHNIQUES_BY_DOMAIN: Dict[TechnicalArchitectureDomain, List[TechnicalArchitectureTechnique]] = {
    TechnicalArchitectureDomain.BACKEND_ARCHITECTURE: BACKEND_ARCHITECTURE_TECHNIQUES,
    TechnicalArchitectureDomain.FRONTEND_ARCHITECTURE: FRONTEND_ARCHITECTURE_TECHNIQUES,
    TechnicalArchitectureDomain.INFRASTRUCTURE_ARCHITECTURE: INFRASTRUCTURE_ARCHITECTURE_TECHNIQUES,
    TechnicalArchitectureDomain.SECURITY_ARCHITECTURE: SECURITY_ARCHITECTURE_TECHNIQUES,
}

# Techniques by complexity
TECHNIQUES_BY_COMPLEXITY: Dict[str, List[TechnicalArchitectureTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.complexity == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.complexity == "medium"],
    "high": [t for t in ALL_TECHNIQUES if t.complexity == "high"],
}

# Techniques by scalability impact
TECHNIQUES_BY_SCALABILITY: Dict[str, List[TechnicalArchitectureTechnique]] = {
    "low": [t for t in ALL_TECHNIQUES if t.scalability_impact == "low"],
    "medium": [t for t in ALL_TECHNIQUES if t.scalability_impact == "medium"],
    "high": [t for t in ALL_TECHNIQUES if t.scalability_impact == "high"],
}


def get_techniques_for_domain(domain: TechnicalArchitectureDomain) -> List[TechnicalArchitectureTechnique]:
    """Get all techniques for a specific technical architecture domain"""
    return TECHNIQUES_BY_DOMAIN.get(domain, [])


def get_techniques_by_complexity(complexity: str) -> List[TechnicalArchitectureTechnique]:
    """Get techniques filtered by complexity level"""
    return TECHNIQUES_BY_COMPLEXITY.get(complexity, [])


def get_techniques_by_scalability(scalability: str) -> List[TechnicalArchitectureTechnique]:
    """Get techniques filtered by scalability impact"""
    return TECHNIQUES_BY_SCALABILITY.get(scalability, [])


def get_technique_by_name(name: str) -> Optional[TechnicalArchitectureTechnique]:
    """Get a specific technique by name"""
    return TECHNIQUE_REGISTRY.get(name)


def get_recommended_techniques(
    domain: Optional[TechnicalArchitectureDomain] = None,
    complexity: Optional[str] = None,
    scalability_impact: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[TechnicalArchitectureTechnique]:
    """
    Get recommended techniques based on filtering criteria

    Args:
        domain: Filter by technical architecture domain (optional)
        complexity: Filter by complexity level (optional)
        scalability_impact: Filter by scalability impact (optional)
        limit: Maximum number of techniques to return (optional)

    Returns:
        List of matching technical architecture techniques
    """
    techniques = ALL_TECHNIQUES

    if domain:
        techniques = [t for t in techniques if t.domain == domain]

    if complexity:
        techniques = [t for t in techniques if t.complexity == complexity]

    if scalability_impact:
        techniques = [t for t in techniques if t.scalability_impact == scalability_impact]

    if limit:
        techniques = techniques[:limit]

    return techniques


def format_technique_for_prompt(technique: TechnicalArchitectureTechnique) -> str:
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
Scalability Impact: {technique.scalability_impact.title()}"""


def get_techniques_prompt_text(
    domain: Optional[TechnicalArchitectureDomain] = None,
    complexity: Optional[str] = None,
    scalability_impact: Optional[str] = None,
    limit: int = 3,
) -> str:
    """Generate formatted text of techniques for LLM prompts"""
    techniques = get_recommended_techniques(domain, complexity, scalability_impact, limit)

    if not techniques:
        return "No techniques match the specified criteria."

    technique_texts = [format_technique_for_prompt(t) for t in techniques]
    return "\n\n".join(technique_texts)


def analyze_architecture_requirements(
    requirements: Dict[str, Any],
) -> Dict[TechnicalArchitectureDomain, List[TechnicalArchitectureTechnique]]:
    """
    Analyze architecture requirements and recommend techniques by domain

    Args:
        requirements: Dictionary containing architecture requirements
                     e.g., {"scalability": "high", "complexity_tolerance": "medium"}

    Returns:
        Dictionary mapping domains to recommended techniques
    """
    recommendations = {}

    scalability_req = requirements.get("scalability", "medium")
    complexity_tolerance = requirements.get("complexity_tolerance", "medium")

    for domain in TechnicalArchitectureDomain:
        domain_techniques = get_techniques_for_domain(domain)

        # Filter by scalability requirements
        if scalability_req == "high":
            domain_techniques = [t for t in domain_techniques if t.scalability_impact in ["medium", "high"]]
        elif scalability_req == "low":
            domain_techniques = [t for t in domain_techniques if t.scalability_impact == "low"]

        # Filter by complexity tolerance
        if complexity_tolerance == "low":
            domain_techniques = [t for t in domain_techniques if t.complexity in ["low", "medium"]]
        elif complexity_tolerance == "high":
            # Include all complexity levels
            pass
        else:  # medium
            domain_techniques = [t for t in domain_techniques if t.complexity != "high"]

        recommendations[domain] = domain_techniques[:3]  # Top 3 recommendations per domain

    return recommendations
