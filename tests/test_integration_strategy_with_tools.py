"""
Integration tests for strategy generation using web and git tools

Tests verify that StrategyGenerator and other agents can successfully use
both web and git tools during strategy generation workflows.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pydantic_ai.models.test import TestModel

from polyhegel.strategy_generator import StrategyGenerator
from polyhegel.strategy_evaluator import StrategyEvaluator
from polyhegel.web_tools import WEB_SEARCH_TOOL, WEB_FETCH_TOOL
from polyhegel.git_tools import GIT_REPO_TOOL, LOCAL_REPO_TOOL
from polyhegel.models import GenesisStrategy, StrategyChain


class TestStrategyGenerationWithTools:
    """Integration tests for strategy generation using web and git tools"""

    @pytest.fixture
    def mock_model(self):
        """Create a test model for strategy generation"""
        return TestModel()

    @pytest.fixture
    def enhanced_strategy_generator(self, mock_model):
        """Create strategy generator with tools enabled"""
        generator = StrategyGenerator(mock_model)
        # Re-enable tools for integration testing
        from pydantic_ai import Agent
        generator.agent = Agent(
            mock_model,
            output_type=GenesisStrategy,
            system_prompt=generator.system_prompt,
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL, GIT_REPO_TOOL, LOCAL_REPO_TOOL]
        )
        return generator

    @pytest.fixture 
    def enhanced_strategy_evaluator(self, mock_model):
        """Create strategy evaluator with tools enabled"""
        evaluator = StrategyEvaluator(mock_model)
        # Add tools to evaluator
        from pydantic_ai import Agent
        evaluator.agent = Agent(
            mock_model,
            output_type=str,
            system_prompt=evaluator.system_prompt,
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL, GIT_REPO_TOOL, LOCAL_REPO_TOOL]
        )
        return evaluator

    @pytest.mark.asyncio
    async def test_strategy_generation_with_web_research(self, enhanced_strategy_generator):
        """Test strategy generation that incorporates web research"""
        
        # Mock web search results
        search_results = """Search results for: cloud migration best practices 2024

1. AWS Cloud Migration Framework
   URL: https://aws.amazon.com/cloud-migration/
   Comprehensive guide to migrating applications to AWS cloud infrastructure

2. Microsoft Azure Migration Guide  
   URL: https://docs.microsoft.com/azure/migrate/
   Step-by-step process for enterprise cloud migration with Azure tools

3. Cloud Migration Security Checklist
   URL: https://example.com/security-checklist
   Essential security considerations for safe cloud migration processes
"""
        
        # Mock web fetch results
        detailed_guide = """Content from https://aws.amazon.com/cloud-migration/:

# AWS Cloud Migration Framework

## 6R Migration Strategy
1. **Rehost** - Lift and shift to cloud
2. **Replatform** - Lift, tinker, and shift  
3. **Refactor** - Re-architect for cloud-native
4. **Retire** - Decommission unused applications
5. **Retain** - Keep on-premises for now
6. **Repurchase** - Move to SaaS solutions

## Migration Phases
- Assessment and planning
- Proof of concept
- Production migration
- Optimization and innovation

## Key Success Factors
- Executive sponsorship
- Skills development
- Security and compliance
- Cost optimization
"""

        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=search_results), \
             patch.object(WEB_FETCH_TOOL.function, '__call__', return_value=detailed_guide):
            
            # Configure model to use web tools and generate strategy
            enhanced_strategy_generator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a cloud migration strategy. Research current best practices first.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll research current cloud migration best practices.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {
                            'query': 'cloud migration best practices 2024',
                            'max_results': 5
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': search_results
                },
                {
                    'role': 'assistant',
                    'content': 'Let me get more detailed information from the AWS framework.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {
                            'url': 'https://aws.amazon.com/cloud-migration/'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_fetch_tool',
                    'content': detailed_guide
                },
                {
                    'role': 'assistant',
                    'content': '''Based on my research of current cloud migration best practices, here's a comprehensive strategy:

{
  "title": "Enterprise Cloud Migration Strategy 2024",
  "steps": [
    {
      "action": "Migration Assessment and Planning",
      "prerequisites": ["Executive sponsorship", "Cross-functional team formation"],
      "outcome": "Complete application portfolio assessment using 6R framework",
      "risks": ["Incomplete application discovery", "Underestimated dependencies"],
      "resource_requirements": ["Cloud architects", "Assessment tools", "3-4 weeks timeline"]
    },
    {
      "action": "Proof of Concept Migration",
      "prerequisites": ["Assessment completed", "Target applications selected"],
      "outcome": "Successful migration of 2-3 pilot applications",
      "risks": ["Technical blockers", "Performance issues"],
      "resource_requirements": ["DevOps engineers", "Testing resources", "Cloud credits"]
    },
    {
      "action": "Security and Compliance Framework",
      "prerequisites": ["PoC validation", "Security team engagement"],
      "outcome": "Cloud security policies and compliance validation",
      "risks": ["Regulatory compliance gaps", "Security misconfigurations"],
      "resource_requirements": ["Security specialists", "Compliance tools", "Policy documentation"]
    },
    {
      "action": "Production Migration Waves",
      "prerequisites": ["Security framework approved", "Migration runbooks"],
      "outcome": "Systematic migration of application portfolio",
      "risks": ["Business disruption", "Data migration issues"],
      "resource_requirements": ["Migration team", "Backup systems", "Rollback procedures"]
    },
    {
      "action": "Optimization and Innovation",
      "prerequisites": ["Core applications migrated", "Performance baseline"],
      "outcome": "Cloud-native optimizations and cost improvements",
      "risks": ["Over-engineering", "Vendor lock-in"],
      "resource_requirements": ["Cloud specialists", "Monitoring tools", "Innovation budget"]
    }
  ],
  "estimated_timeline": "12-18 months",
  "resource_requirements": ["Cloud architects", "Migration specialists", "Security team", "Training budget"],
  "alignment_score": {
    "cost_optimization": 8.5,
    "operational_efficiency": 9.0,
    "innovation_enablement": 8.0,
    "security_posture": 9.5
  }
}'''
                }
            ])
            
            # Generate strategy using the enhanced generator
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Generate a cloud migration strategy. Research current best practices first."
            )
            
            assert len(chains) == 1
            strategy = chains[0].strategy
            assert "cloud migration" in strategy.title.lower()
            assert len(strategy.steps) >= 4
            assert any("migration" in step.action.lower() for step in strategy.steps)
            assert any("security" in step.action.lower() for step in strategy.steps)

    @pytest.mark.asyncio
    async def test_strategy_generation_with_codebase_analysis(self, enhanced_strategy_generator):
        """Test strategy generation that analyzes existing codebases"""
        
        # Mock repository analysis
        repo_analysis = """Repository content from https://github.com/company/legacy-app:

# Legacy Monolith Application

Large Django application with 50+ models, complex business logic.

## Architecture Analysis
- Monolithic Django application (Django 2.2 - needs upgrade)
- PostgreSQL database with 200+ tables
- Complex interdependencies between modules
- Limited test coverage (~30%)
- Manual deployment processes

## Technical Debt Assessment
- Outdated dependencies with security vulnerabilities
- Tight coupling between business logic and presentation
- Lack of API layer for external integrations
- Performance bottlenecks in core modules

## Migration Opportunities
- Microservices extraction candidates identified
- API-first architecture potential
- Container deployment readiness assessment needed
"""

        with patch.object(GIT_REPO_TOOL.function, '__call__', return_value=repo_analysis):
            
            enhanced_strategy_generator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a legacy system modernization strategy. Analyze our current codebase at https://github.com/company/legacy-app first.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze the legacy codebase to understand the current architecture.',
                    'tool_calls': [{
                        'tool_name': 'git_repo_to_md_tool',
                        'args': {
                            'repo_url': 'https://github.com/company/legacy-app',
                            'output_format': 'markdown',
                            'include_structure': True
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': repo_analysis
                },
                {
                    'role': 'assistant',
                    'content': '''Based on the codebase analysis, here's a modernization strategy:

{
  "title": "Legacy System Modernization Strategy",
  "steps": [
    {
      "action": "Technical Debt Assessment and Prioritization",
      "prerequisites": ["Development team availability", "Code analysis tools"],
      "outcome": "Prioritized technical debt backlog with security focus",
      "risks": ["Analysis paralysis", "Scope creep"],
      "resource_requirements": ["Senior developers", "Static analysis tools", "2 weeks analysis time"]
    },
    {
      "action": "Django Framework Upgrade",
      "prerequisites": ["Technical debt assessment", "Testing infrastructure"],
      "outcome": "Django 2.2 to 4.x upgrade with improved security",
      "risks": ["Breaking changes", "Third-party compatibility"],
      "resource_requirements": ["Django expertise", "Comprehensive testing", "Migration scripts"]
    },
    {
      "action": "API Layer Development",
      "prerequisites": ["Framework upgrade", "API design patterns"],
      "outcome": "RESTful API layer enabling microservices extraction",
      "risks": ["Performance impact", "Data consistency issues"],
      "resource_requirements": ["API developers", "Documentation tools", "Integration testing"]
    },
    {
      "action": "Microservices Extraction",
      "prerequisites": ["API layer deployed", "Service boundaries identified"],
      "outcome": "Core business functions extracted as independent services",
      "risks": ["Distributed system complexity", "Data synchronization"],
      "resource_requirements": ["Microservices architects", "Container platform", "Service mesh"]
    },
    {
      "action": "Containerization and CI/CD",
      "prerequisites": ["Services defined", "DevOps infrastructure"],
      "outcome": "Automated deployment pipeline with container orchestration",
      "risks": ["Infrastructure complexity", "Deployment failures"],
      "resource_requirements": ["DevOps engineers", "Container platform", "Monitoring stack"]
    }
  ],
  "estimated_timeline": "18-24 months",
  "resource_requirements": ["Senior developers", "DevOps engineers", "Modernization budget", "Training programs"],
  "alignment_score": {
    "maintainability": 9.0,
    "scalability": 8.5,
    "security": 9.5,
    "developer_productivity": 8.0
  }
}'''
                }
            ])
            
            chains = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Generate a legacy system modernization strategy. Analyze our current codebase at https://github.com/company/legacy-app first."
            )
            
            assert len(chains) == 1
            strategy = chains[0].strategy
            assert "modernization" in strategy.title.lower()
            assert len(strategy.steps) >= 4
            assert any("django" in step.action.lower() or "upgrade" in step.action.lower() for step in strategy.steps)
            assert any("api" in step.action.lower() for step in strategy.steps)

    @pytest.mark.asyncio
    async def test_strategy_evaluation_with_research(self, enhanced_strategy_evaluator):
        """Test strategy evaluation that incorporates external research"""
        
        # Create mock strategies for comparison
        strategy1 = StrategyChain(
            strategy=GenesisStrategy(
                title="Kubernetes Migration Strategy",
                steps=[],
                estimated_timeline="6 months",
                resource_requirements=["DevOps team", "Training"],
                alignment_score={"scalability": 9.0, "complexity": 7.0}
            ),
            source_sample=1,
            temperature=0.7
        )
        
        strategy2 = StrategyChain(
            strategy=GenesisStrategy(
                title="Docker Swarm Migration Strategy", 
                steps=[],
                estimated_timeline="3 months",
                resource_requirements=["DevOps team"],
                alignment_score={"scalability": 7.0, "complexity": 5.0}
            ),
            source_sample=2,
            temperature=0.7
        )
        
        # Mock research results
        k8s_research = """Search results for: kubernetes vs docker swarm 2024

1. Kubernetes vs Docker Swarm: Complete Comparison 2024
   URL: https://example.com/k8s-swarm-comparison
   Detailed analysis of orchestration platforms for enterprise deployment

2. Production Kubernetes: Lessons Learned
   URL: https://example.com/k8s-production
   Real-world experiences and best practices from enterprise Kubernetes deployments
"""
        
        comparison_details = """Content from https://example.com/k8s-swarm-comparison:

# Kubernetes vs Docker Swarm 2024

## Kubernetes Advantages
- Massive ecosystem and community support
- Advanced scheduling and resource management
- Extensive monitoring and logging integrations
- Multi-cloud portability
- Enterprise-grade security features

## Docker Swarm Advantages  
- Simpler setup and configuration
- Lower resource overhead
- Easier learning curve
- Native Docker integration
- Faster deployment for simple workloads

## Production Considerations
- Kubernetes: Better for complex, large-scale deployments
- Docker Swarm: Suitable for smaller teams and simpler architectures
- Kubernetes has 85% market adoption in enterprises
- Docker Swarm maintenance mode concerns
"""

        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=k8s_research), \
             patch.object(WEB_FETCH_TOOL.function, '__call__', return_value=comparison_details):
            
            enhanced_strategy_evaluator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Compare these container orchestration strategies. Research current market trends first.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll research current container orchestration trends to inform the comparison.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {
                            'query': 'kubernetes vs docker swarm 2024',
                            'max_results': 3
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': k8s_research
                },
                {
                    'role': 'assistant',
                    'content': 'Let me get detailed comparison information.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {
                            'url': 'https://example.com/k8s-swarm-comparison'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_fetch_tool',
                    'content': comparison_details
                },
                {
                    'role': 'assistant',
                    'content': '''Based on current market research and platform comparison:

**Strategy Evaluation: Kubernetes vs Docker Swarm**

**Kubernetes Migration Strategy Analysis:**
- **Market Alignment**: Excellent - 85% enterprise adoption rate
- **Long-term Viability**: High - active development and ecosystem growth  
- **Complexity Trade-off**: Higher initial complexity but better scalability
- **Resource Investment**: Justified for enterprise-scale deployments
- **Risk Assessment**: Lower long-term risk due to industry standardization

**Docker Swarm Migration Strategy Analysis:**
- **Market Alignment**: Concerning - maintenance mode status
- **Long-term Viability**: Limited - declining community support
- **Complexity Trade-off**: Lower initial complexity but limited scalability
- **Resource Investment**: Lower upfront but potential migration costs later
- **Risk Assessment**: Higher long-term risk due to platform uncertainty

**Recommendation**: Kubernetes Migration Strategy is preferred.

**Reasoning**: While Docker Swarm offers simplicity, current market trends strongly favor Kubernetes for enterprise deployments. The 85% market adoption rate and active ecosystem development make Kubernetes the more strategic choice despite higher initial complexity.

**Preferred Strategy Index: 1**'''
                }
            ])
            
            result = await enhanced_strategy_evaluator.compare_strategies(
                strategy1,
                strategy2,
                context="Container orchestration platform selection for enterprise deployment"
            )
            
            assert result['preferred_strategy'] == 1
            assert "kubernetes" in result['evaluation_text'].lower()
            assert "market" in result['evaluation_text'].lower()
            assert "85%" in result['evaluation_text']

    @pytest.mark.asyncio
    async def test_end_to_end_strategy_workflow_with_tools(self, enhanced_strategy_generator, enhanced_strategy_evaluator):
        """Test complete strategy workflow using multiple tools"""
        
        # Mock comprehensive research and analysis
        market_research = """Search results for: digital transformation trends 2024

1. Digital Transformation Report 2024
   URL: https://example.com/dt-report-2024
   Comprehensive analysis of digital transformation trends and ROI metrics

2. Enterprise AI Adoption Survey
   URL: https://example.com/ai-survey-2024  
   Latest statistics on AI adoption in enterprise environments
"""
        
        detailed_report = """Content from https://example.com/dt-report-2024:

# Digital Transformation Report 2024

## Key Findings
- 78% of enterprises accelerated digital initiatives post-2023
- Average ROI of 240% within 24 months for successful transformations
- Cloud adoption reached 94% across enterprises
- AI integration in 67% of business processes

## Success Factors
1. Executive leadership and vision
2. Employee upskilling and change management
3. Data-driven decision making
4. Agile methodology adoption
5. Customer-centric design thinking

## Technology Priorities
- Cloud infrastructure (89% priority)
- Data analytics and AI (84% priority)  
- Process automation (78% priority)
- Cybersecurity modernization (92% priority)
"""

        competitor_analysis = """Repository content from https://github.com/competitor/platform:

# Competitor Digital Platform

Modern cloud-native platform with microservices architecture.

## Technology Stack
- React frontend with TypeScript
- Node.js microservices with Express
- PostgreSQL with Redis caching
- Kubernetes orchestration
- CI/CD with GitHub Actions

## Business Capabilities
- Real-time analytics dashboard
- Mobile-first customer experience
- API-first architecture
- Automated customer onboarding
- AI-powered recommendations

## Performance Metrics
- 99.9% uptime SLA
- Sub-200ms API response times
- 50M+ monthly active users
- 15+ countries deployment
"""

        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=market_research), \
             patch.object(WEB_FETCH_TOOL.function, '__call__', return_value=detailed_report), \
             patch.object(GIT_REPO_TOOL.function, '__call__', return_value=competitor_analysis):
            
            # Step 1: Generate strategy with research
            enhanced_strategy_generator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a digital transformation strategy. Research market trends and analyze competitor platform at https://github.com/competitor/platform.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll research digital transformation trends first.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {'query': 'digital transformation trends 2024', 'max_results': 5}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': market_research
                },
                {
                    'role': 'assistant',
                    'content': 'Now let me get detailed market data.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {'url': 'https://example.com/dt-report-2024'}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_fetch_tool',
                    'content': detailed_report
                },
                {
                    'role': 'assistant',
                    'content': 'Let me analyze the competitor platform architecture.',
                    'tool_calls': [{
                        'tool_name': 'git_repo_to_md_tool',
                        'args': {
                            'repo_url': 'https://github.com/competitor/platform',
                            'output_format': 'markdown'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': competitor_analysis
                },
                {
                    'role': 'assistant',
                    'content': '''Based on comprehensive market research and competitive analysis:

{
  "title": "Enterprise Digital Transformation Strategy 2024",
  "steps": [
    {
      "action": "Digital Foundation Assessment",
      "prerequisites": ["Executive sponsorship", "Cross-functional team"],
      "outcome": "Current state analysis and transformation roadmap",
      "risks": ["Incomplete assessment", "Resistance to change"],
      "resource_requirements": ["Digital consultants", "Assessment tools", "6 weeks timeline"]
    },
    {
      "action": "Cloud Infrastructure Modernization",
      "prerequisites": ["Assessment completed", "Cloud strategy approved"],
      "outcome": "Scalable cloud infrastructure supporting 99.9% uptime",
      "risks": ["Migration complexity", "Downtime during transition"],
      "resource_requirements": ["Cloud architects", "DevOps team", "Infrastructure budget"]
    },
    {
      "action": "API-First Platform Development",
      "prerequisites": ["Cloud infrastructure", "Development team upskilling"],
      "outcome": "Microservices platform with sub-200ms response times",
      "risks": ["Technical complexity", "Integration challenges"],
      "resource_requirements": ["Full-stack developers", "API management tools", "Testing infrastructure"]
    },
    {
      "action": "AI and Analytics Integration",
      "prerequisites": ["Platform deployed", "Data pipeline established"],
      "outcome": "AI-powered insights and automated decision making",
      "risks": ["Data quality issues", "Model accuracy concerns"],
      "resource_requirements": ["Data scientists", "ML engineers", "AI/ML platforms"]
    },
    {
      "action": "Customer Experience Optimization",
      "prerequisites": ["AI integration", "User research completed"],
      "outcome": "Mobile-first experience with personalized recommendations",
      "risks": ["User adoption challenges", "Privacy concerns"],
      "resource_requirements": ["UX designers", "Mobile developers", "Customer research"]
    }
  ],
  "estimated_timeline": "18-24 months",
  "resource_requirements": ["Digital transformation team", "Technology investments", "Training programs", "Change management"],
  "alignment_score": {
    "market_competitiveness": 9.5,
    "operational_efficiency": 9.0,
    "customer_satisfaction": 8.5,
    "innovation_capability": 9.0
  }
}'''
                }
            ])
            
            # Generate the strategy
            strategies = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Generate a digital transformation strategy. Research market trends and analyze competitor platform at https://github.com/competitor/platform."
            )
            
            # Verify strategy incorporates research insights
            assert len(strategies) == 1
            strategy = strategies[0]
            assert "digital transformation" in strategy.strategy.title.lower()
            assert len(strategy.strategy.steps) >= 4
            assert any("cloud" in step.action.lower() for step in strategy.strategy.steps)
            assert any("api" in step.action.lower() for step in strategy.strategy.steps)
            assert any("ai" in step.action.lower() for step in strategy.strategy.steps)
            
            # Step 2: Evaluate the strategy with additional research
            enhanced_strategy_evaluator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Evaluate this digital transformation strategy for feasibility and market alignment.'
                },
                {
                    'role': 'assistant',
                    'content': '''Strategy Evaluation: Enterprise Digital Transformation Strategy 2024

**Strategic Viability: 9.0/10**
- Well-aligned with market trends (78% of enterprises accelerating digital initiatives)
- Realistic timeline of 18-24 months matches industry benchmarks
- Technology choices align with competitor analysis findings

**Coherence: 8.5/10**  
- Clear progression from infrastructure to customer experience
- Prerequisites properly sequenced
- Each step builds logically on previous outcomes

**Risk Management: 8.0/10**
- Key risks identified for each phase
- Mitigation strategies implicit in resource requirements
- Change management considerations included

**Resource Efficiency: 8.5/10**
- Resource allocation matches complexity of each phase
- ROI potential of 240% within 24 months based on market data
- Investment priorities align with industry benchmarks (cloud 89%, AI 84%)

**Overall Assessment: 8.5/10**
This strategy demonstrates strong market alignment and technical feasibility. The competitive analysis informed realistic performance targets (99.9% uptime, sub-200ms APIs). The phased approach reduces risk while building organizational capability progressively.

**Key Strengths:**
- Market-driven approach based on current trends
- Competitive benchmarking influences technical targets  
- Comprehensive scope covering infrastructure to customer experience

**Recommendations:**
- Consider parallel workstreams to accelerate timeline
- Ensure change management resources are adequate
- Plan for continuous competitor monitoring during execution'''
                }
            ])
            
            evaluation = await enhanced_strategy_evaluator.evaluate_strategy(
                strategy,
                context="Enterprise seeking competitive advantage through digital transformation"
            )
            
            assert "viability" in evaluation['evaluation_text'].lower()
            assert "8" in evaluation['evaluation_text'] or "9" in evaluation['evaluation_text']  # Scores
            assert "market" in evaluation['evaluation_text'].lower()
            assert "competitive" in evaluation['evaluation_text'].lower()

    @pytest.mark.asyncio 
    async def test_tool_usage_in_strategy_techniques(self, enhanced_strategy_generator):
        """Test that strategic techniques can leverage web and git tools"""
        
        technique_research = """Search results for: blue ocean strategy examples 2024

1. Blue Ocean Strategy Success Stories
   URL: https://example.com/blue-ocean-examples
   Recent examples of companies creating uncontested market spaces

2. Market Disruption Analysis 2024
   URL: https://example.com/market-disruption
   Analysis of industries ripe for blue ocean innovation
"""
        
        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=technique_research):
            
            enhanced_strategy_generator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Use Blue Ocean Strategy technique to address market differentiation challenge.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll research current Blue Ocean Strategy examples to inform the approach.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {
                            'query': 'blue ocean strategy examples 2024',
                            'max_results': 3
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': technique_research
                },
                {
                    'role': 'assistant',
                    'content': '''Based on current Blue Ocean Strategy research and examples:

{
  "title": "Blue Ocean Market Differentiation Strategy",
  "steps": [
    {
      "action": "Value Innovation Discovery",
      "prerequisites": ["Market research", "Customer journey mapping"],
      "outcome": "Identified uncontested market space with unique value proposition",
      "risks": ["Market assumptions incorrect", "Value proposition unclear"],
      "resource_requirements": ["Market researchers", "Customer interviews", "Competitive analysis"]
    },
    {
      "action": "Four Actions Framework Implementation",
      "prerequisites": ["Value innovation identified", "Current offering analysis"],
      "outcome": "Clear strategy canvas showing eliminate-reduce-raise-create actions",
      "risks": ["Operational complexity", "Resource reallocation challenges"],
      "resource_requirements": ["Strategy team", "Operations analysis", "Change management"]
    },
    {
      "action": "Blue Ocean Product Development",
      "prerequisites": ["Strategy canvas completed", "Development resources"],
      "outcome": "MVP targeting uncontested market space",
      "risks": ["Technical feasibility", "Market timing"],
      "resource_requirements": ["Product team", "R&D budget", "Rapid prototyping tools"]
    }
  ],
  "estimated_timeline": "9-12 months",
  "resource_requirements": ["Strategy consultants", "Product development", "Market research budget"],
  "alignment_score": {
    "market_differentiation": 9.5,
    "competitive_advantage": 9.0,
    "innovation_potential": 8.5
  }
}'''
                }
            ])
            
            strategies = await enhanced_strategy_generator.generate_with_technique(
                strategic_challenge="Market differentiation in competitive landscape",
                technique_name="Blue Ocean Strategy",
                temperature=0.7,
                count=1
            )
            
            assert len(strategies) == 1
            strategy = strategies[0]
            assert "blue ocean" in strategy.strategy.title.lower()
            assert strategy.technique_name == "Blue Ocean Strategy"
            assert len(strategy.strategy.steps) >= 3

    @pytest.mark.asyncio
    async def test_tools_error_resilience_in_workflows(self, enhanced_strategy_generator):
        """Test that strategy generation continues gracefully when tools fail"""
        
        # Mock tool failure and recovery
        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value="Web search failed: Network timeout"), \
             patch.object(GIT_REPO_TOOL.function, '__call__', return_value="Repository content from backup analysis: Basic microservices architecture identified"):
            
            enhanced_strategy_generator.agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a microservices migration strategy. Research best practices and analyze our codebase.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll research microservices best practices.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {'query': 'microservices migration best practices', 'max_results': 5}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': "Web search failed: Network timeout"
                },
                {
                    'role': 'assistant',
                    'content': 'Web search failed, but I can still analyze the codebase for insights.',
                    'tool_calls': [{
                        'tool_name': 'git_repo_to_md_tool',
                        'args': {
                            'repo_url': 'https://github.com/company/monolith',
                            'output_format': 'markdown'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': "Repository content from backup analysis: Basic microservices architecture identified"
                },
                {
                    'role': 'assistant',
                    'content': '''Despite web search limitations, based on codebase analysis:

{
  "title": "Microservices Migration Strategy",
  "steps": [
    {
      "action": "Service Boundary Identification",
      "prerequisites": ["Architecture review", "Business domain analysis"],
      "outcome": "Clear service boundaries based on business capabilities",
      "risks": ["Incorrect service sizing", "Data consistency challenges"],
      "resource_requirements": ["Senior architects", "Domain experts", "Modeling tools"]
    },
    {
      "action": "Strangler Fig Implementation",
      "prerequisites": ["Service boundaries defined", "API contracts"],
      "outcome": "Gradual extraction of services from monolith",
      "risks": ["Performance degradation", "Operational complexity"],
      "resource_requirements": ["Development team", "Infrastructure setup", "Monitoring tools"]
    }
  ],
  "estimated_timeline": "12-15 months",
  "resource_requirements": ["Microservices expertise", "Infrastructure investment", "DevOps tooling"],
  "alignment_score": {
    "scalability": 8.0,
    "maintainability": 7.5,
    "team_autonomy": 8.5
  }
}'''
                }
            ])
            
            strategies = await enhanced_strategy_generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt="Generate a microservices migration strategy. Research best practices and analyze our codebase."
            )
            
            # Verify strategy was still generated despite tool failures
            assert len(strategies) == 1
            strategy = strategies[0].strategy
            assert "microservices" in strategy.title.lower()
            assert len(strategy.steps) >= 2