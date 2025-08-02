# Strategic Techniques Guide

## Overview

Strategic techniques provide domain-specific approaches for generating and evaluating strategies. This guide covers how to use built-in techniques and create custom ones for specialized strategic planning needs.

## Built-in Strategic Domains

### Resource Acquisition
**Focus**: Optimizing resource allocation, acquisition, and utilization

**Key Concepts**:
- Resource mapping and gap analysis
- Acquisition strategy planning
- Capacity optimization
- Cost-benefit evaluation

**Example Usage**:
```python
from polyhegel.strategic_techniques import StrategyDomain
from polyhegel.strategy_generator import StrategyGenerator

# Generate resource-focused strategies
generator = StrategyGenerator(
    model_name="claude-3-sonnet-20240229",
    domain=StrategyDomain.RESOURCE_ACQUISITION
)

strategies = await generator.generate_strategies(
    temperature_counts=[(0.6, 3)],
    system_prompt="Focus on resource optimization and scalable acquisition",
    user_prompt="Build a data science team of 20 people within 6 months"
)
```

**Common Applications**:
- Hiring and team building strategies
- Technology stack decisions
- Infrastructure scaling plans
- Budget allocation optimization

### Strategic Security
**Focus**: Risk management, threat mitigation, and security planning

**Key Concepts**:
- Threat modeling and assessment
- Defense strategy planning
- Risk mitigation approaches
- Compliance and governance

**Example Usage**:
```python
# Generate security-focused strategies
security_strategies = await generator.generate_strategies(
    temperature_counts=[(0.4, 2), (0.7, 2)],  # Lower temperature for reliability
    system_prompt="Prioritize comprehensive risk management and defensive measures",
    user_prompt="Secure customer data while enabling rapid product development",
    domain=StrategyDomain.STRATEGIC_SECURITY
)

# Evaluate with security-specific criteria
for strategy in security_strategies:
    print(f"Risk Management Score: {strategy.strategy.alignment_score.get('strategic_security', 0)}")
```

**Common Applications**:
- Data protection strategies
- Incident response planning
- Regulatory compliance approaches
- Business continuity planning

### Value Catalysis
**Focus**: Value creation, innovation acceleration, and market positioning

**Key Concepts**:
- Value proposition development
- Innovation pipeline management
- Market positioning strategies
- Stakeholder value alignment

**Example Usage**:
```python
# Generate value-creation strategies
value_strategies = await generator.generate_strategies(
    temperature_counts=[(0.8, 3)],  # Higher temperature for innovation
    system_prompt="Focus on innovative value creation and market differentiation",
    user_prompt="Transform our traditional consulting firm into a digital-first advisory",
    domain=StrategyDomain.VALUE_CATALYSIS
)
```

**Common Applications**:
- Business model innovation
- Product differentiation strategies
- Market entry and expansion
- Partnership and ecosystem development

## Custom Technique Development

### Creating Domain-Specific Techniques

```python
from polyhegel.strategic_techniques import StrategyTechnique, StrategyDomain
from polyhegel.models import StrategyChain, StrategyContext

class CustomManufacturingTechnique(StrategyTechnique):
    domain = StrategyDomain.RESOURCE_ACQUISITION
    name = "lean_manufacturing"
    description = "Lean manufacturing optimization techniques"
    
    def __init__(self):
        self.focus_areas = [
            "waste_elimination",
            "continuous_improvement", 
            "value_stream_optimization",
            "quality_management"
        ]
    
    async def generate_strategy(self, context: StrategyContext) -> StrategyChain:
        # Custom strategy generation logic
        enhanced_prompt = self._enhance_prompt_with_lean_principles(context.user_prompt)
        
        # Use base generation with enhanced prompts
        strategy = await self._base_generation(enhanced_prompt, context)
        
        # Apply lean-specific post-processing
        return self._apply_lean_validation(strategy)
    
    def _enhance_prompt_with_lean_principles(self, original_prompt: str) -> str:
        lean_context = """
        Apply lean manufacturing principles:
        1. Identify and eliminate waste (muda, mura, muri)
        2. Focus on continuous improvement (kaizen)
        3. Optimize value streams
        4. Implement pull-based systems
        5. Pursue perfection through iteration
        """
        return f"{lean_context}\n\nOriginal challenge: {original_prompt}"
    
    def _apply_lean_validation(self, strategy: StrategyChain) -> StrategyChain:
        # Add lean-specific validation and scoring
        lean_score = self._calculate_lean_alignment(strategy)
        
        # Enhance strategy with lean metrics
        strategy.strategy.alignment_score["lean_manufacturing"] = lean_score
        return strategy
```

### Technique Registration and Usage

```python
# Register custom technique
from polyhegel.strategic_techniques import register_technique

@register_technique(domain=StrategyDomain.RESOURCE_ACQUISITION)
class AgileTransformationTechnique(StrategyTechnique):
    name = "agile_transformation"
    description = "Organizational agile transformation methodology"
    
    async def generate_strategy(self, context: StrategyContext) -> StrategyChain:
        # Implement agile-specific strategy generation
        pass

# Use custom technique
from polyhegel.strategic_techniques import get_technique

technique = get_technique("agile_transformation", StrategyDomain.RESOURCE_ACQUISITION)
strategy = await technique.generate_strategy(context)
```

## Advanced Technique Integration

### Multi-Technique Strategy Generation

```python
from polyhegel.strategic_techniques import TechniqueOrchestrator

class HybridStrategyGenerator:
    def __init__(self):
        self.orchestrator = TechniqueOrchestrator()
    
    async def generate_comprehensive_strategy(self, challenge: str):
        # Use multiple techniques for comprehensive coverage
        techniques = [
            ("resource_optimization", StrategyDomain.RESOURCE_ACQUISITION),
            ("risk_management", StrategyDomain.STRATEGIC_SECURITY), 
            ("value_innovation", StrategyDomain.VALUE_CATALYSIS)
        ]
        
        strategies = []
        for technique_name, domain in techniques:
            technique = get_technique(technique_name, domain)
            context = StrategyContext(user_prompt=challenge, domain=domain)
            strategy = await technique.generate_strategy(context)
            strategies.append(strategy)
        
        # Synthesize into comprehensive strategy
        return self.orchestrator.synthesize_strategies(strategies)

# Usage
hybrid_generator = HybridStrategyGenerator()
comprehensive_strategy = await hybrid_generator.generate_comprehensive_strategy(
    "Transform our startup from MVP to enterprise-ready platform"
)
```

### Technique-Specific Evaluation

```python
from polyhegel.evaluation.technique_evaluator import TechniqueEvaluator

class TechniqueAwareEvaluator:
    def __init__(self):
        self.evaluator = TechniqueEvaluator()
    
    async def evaluate_with_technique_context(self, strategy: StrategyChain, technique: StrategyTechnique):
        # Standard strategic metrics
        base_metrics = await self.evaluator.evaluate_strategy(strategy)
        
        # Technique-specific evaluation
        technique_metrics = await technique.evaluate_strategy(strategy)
        
        # Combine and weight appropriately
        combined_score = self._combine_evaluation_scores(base_metrics, technique_metrics)
        
        return {
            "overall_score": combined_score,
            "base_metrics": base_metrics,
            "technique_metrics": technique_metrics,
            "technique_name": technique.name,
            "domain": technique.domain.value
        }
```

## Technique Configuration and Tuning

### Performance Optimization

```python
from polyhegel.strategic_techniques import TechniqueConfig

class OptimizedTechnique(StrategyTechnique):
    def __init__(self, config: TechniqueConfig = None):
        self.config = config or TechniqueConfig()
        self.performance_cache = {}
    
    async def generate_strategy(self, context: StrategyContext) -> StrategyChain:
        # Check cache for similar contexts
        cache_key = self._generate_cache_key(context)
        if cache_key in self.performance_cache:
            cached_result = self.performance_cache[cache_key]
            return self._adapt_cached_strategy(cached_result, context)
        
        # Generate new strategy
        strategy = await self._generate_new_strategy(context)
        
        # Cache result for future use
        self.performance_cache[cache_key] = strategy
        return strategy
    
    def _generate_cache_key(self, context: StrategyContext) -> str:
        # Create semantic hash of context for caching
        import hashlib
        content = f"{context.user_prompt}:{context.domain.value}:{str(context.constraints)}"
        return hashlib.md5(content.encode()).hexdigest()
```

### A/B Testing Framework

```python
from polyhegel.strategic_techniques import TechniqueVariant

class A_BTechniqueTest:
    def __init__(self, base_technique: StrategyTechnique):
        self.base_technique = base_technique
        self.variants = []
        self.test_results = []
    
    def add_variant(self, variant: TechniqueVariant):
        self.variants.append(variant)
    
    async def run_comparative_test(self, test_contexts: List[StrategyContext]):
        results = {"base": [], "variants": {}}
        
        # Test base technique
        for context in test_contexts:
            strategy = await self.base_technique.generate_strategy(context)
            evaluation = await self._evaluate_strategy(strategy, context)
            results["base"].append(evaluation)
        
        # Test variants
        for i, variant in enumerate(self.variants):
            variant_results = []
            for context in test_contexts:
                strategy = await variant.generate_strategy(context)
                evaluation = await self._evaluate_strategy(strategy, context)
                variant_results.append(evaluation)
            results["variants"][f"variant_{i}"] = variant_results
        
        return self._analyze_test_results(results)
```

## Integration with Refinement System

### Technique-Aware Refinement

```python
from polyhegel.refinement.recursive import RecursiveRefinementEngine
from polyhegel.refinement.technique_aware import TechniqueAwareRefinement

class TechniqueRefinementIntegration:
    def __init__(self, technique: StrategyTechnique):
        self.technique = technique
        self.refinement_engine = RecursiveRefinementEngine()
    
    async def refine_with_technique_guidance(self, strategy: StrategyChain, context: StrategyContext):
        # Configure refinement with technique-specific parameters
        config = self._create_technique_specific_config()
        self.refinement_engine.config = config
        
        # Create technique-aware feedback system
        feedback_system = TechniqueAwareRefinement(self.technique)
        self.refinement_engine.feedback_loop = feedback_system
        
        # Execute refinement
        session = await self.refinement_engine.refine_strategy(
            strategy=strategy,
            system_prompt=self.technique.get_system_prompt(),
            user_prompt=context.user_prompt
        )
        
        return session
    
    def _create_technique_specific_config(self):
        # Technique-specific refinement configuration
        from polyhegel.refinement.recursive import RefinementConfiguration
        
        return RefinementConfiguration(
            max_generations=self.technique.max_refinement_generations,
            convergence_threshold=self.technique.convergence_threshold,
            improvement_priorities=self.technique.improvement_priorities
        )
```

## Best Practices

### Technique Selection Guidelines

**Choose Resource Acquisition when**:
- Planning team growth or organizational scaling
- Optimizing budget allocation and resource utilization
- Designing acquisition or procurement strategies
- Managing capacity and infrastructure needs

**Choose Strategic Security when**:
- Addressing risk management and threat mitigation
- Planning compliance and governance approaches
- Designing incident response and business continuity
- Implementing security frameworks and controls

**Choose Value Catalysis when**:
- Innovating business models and value propositions
- Planning market entry and competitive positioning
- Developing partnership and ecosystem strategies
- Accelerating innovation and product development

### Performance Optimization

1. **Cache Strategy Results**: Implement intelligent caching for similar contexts
2. **Parallel Technique Execution**: Run multiple techniques concurrently when appropriate
3. **Progressive Refinement**: Start with fast techniques, refine with specialized ones
4. **Metrics-Driven Selection**: Use historical performance to guide technique selection

### Quality Assurance

1. **Cross-Technique Validation**: Validate strategies across multiple technique perspectives
2. **Domain Expert Review**: Incorporate human expertise for technique-specific evaluation
3. **Continuous Learning**: Update technique parameters based on real-world outcomes
4. **Bias Detection**: Monitor for technique-specific biases and blind spots