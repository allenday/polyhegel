# Strategic Simulation Guide

## Overview

Polyhegel's simulation system provides a controlled environment for testing and evaluating strategic scenarios. This guide covers how to set up, run, and interpret strategic simulations.

## Basic Simulation Usage

### Quick Start
```python
from polyhegel.simulator import PolyhegelSimulator

# Create simulator instance
simulator = PolyhegelSimulator(model_name="claude-3-haiku-20240307")

# Run basic simulation
results = await simulator.run_simulation(
    temperature_counts=[(0.7, 3), (0.9, 2)],
    system_prompt="Generate acquisition strategies",
    user_prompt="How to acquire new customers in competitive market",
    mode="temperature"
)

# Access results
for strategy_chain in results:
    print(f"Strategy: {strategy_chain.strategy.title}")
    print(f"Alignment Score: {strategy_chain.strategy.alignment_score}")
```

### Configuration Options

#### Temperature Sampling
Control strategy diversity through temperature settings:
```python
temperature_counts = [
    (0.3, 2),  # Conservative strategies (low temperature)
    (0.7, 3),  # Balanced strategies (medium temperature)
    (1.0, 2),  # Creative strategies (high temperature)
]
```

#### Selection Methods
Choose how strategies are selected and refined:
- **`tournament`**: Competitive selection based on performance
- **`clustering`**: Diversity-based selection using similarity clustering
- **`random`**: Random selection for baseline comparison

```python
results = await simulator.run_simulation(
    temperature_counts=[(0.7, 5)],
    selection_method="tournament",
    # ... other parameters
)
```

## Advanced Simulation Features

### Multi-Modal Strategy Generation
Combine different generation approaches:
```python
# Generate strategies using multiple techniques
results = await simulator.run_simulation(
    temperature_counts=[(0.5, 2), (0.8, 2)],
    mode="hybrid",  # Use both temperature and technique-based generation
    techniques=["resource_optimization", "risk_mitigation"],
    system_prompt="Comprehensive market entry strategy"
)
```

### Batch Simulation
Process multiple scenarios efficiently:
```python
scenarios = [
    {"prompt": "B2B market entry", "domain": "resource_acquisition"},
    {"prompt": "Competitive response", "domain": "strategic_security"},
    {"prompt": "Value proposition design", "domain": "value_catalysis"}
]

results = await simulator.batch_simulate(scenarios)
```

## Simulation Analysis

### Performance Metrics
Evaluate strategy quality using built-in metrics:
```python
from polyhegel.evaluation.metrics import MetricsCollector

collector = MetricsCollector()
metrics = collector.collect_metrics(results, execution_time)

print(f"Average Coherence: {metrics.coherence_score}")
print(f"Feasibility Score: {metrics.feasibility_score}")
print(f"Risk Management: {metrics.risk_management_score}")
```

### Custom Evaluation
Implement domain-specific evaluation criteria:
```python
class CustomEvaluator:
    def evaluate_strategy(self, strategy_chain):
        # Custom evaluation logic
        scores = {
            "market_fit": self.assess_market_fit(strategy_chain),
            "execution_complexity": self.assess_complexity(strategy_chain),
            "competitive_advantage": self.assess_advantage(strategy_chain)
        }
        return scores

evaluator = CustomEvaluator()
custom_scores = [evaluator.evaluate_strategy(s) for s in results]
```

## Simulation Scenarios

### Market Entry Simulation
```python
# Comprehensive market entry scenario
market_entry_config = {
    "system_prompt": """Generate market entry strategies considering:
    - Competitive landscape analysis
    - Resource requirements and constraints  
    - Risk mitigation approaches
    - Timeline and milestone planning""",
    
    "user_prompt": "Enter the European SaaS market with our project management tool",
    
    "temperature_counts": [(0.4, 2), (0.7, 3), (0.9, 1)],
    "selection_method": "tournament",
    "max_strategies": 6
}

results = await simulator.run_simulation(**market_entry_config)
```

### Crisis Response Simulation
```python
# Crisis response scenario testing
crisis_config = {
    "system_prompt": "Generate rapid response strategies for business disruption",
    "user_prompt": "Major supplier disruption affects 60% of production capacity",
    "temperature_counts": [(0.3, 3), (0.6, 2)],  # Focus on reliable strategies
    "selection_method": "clustering",  # Ensure diverse approaches
    "time_pressure": True  # Enable rapid generation mode
}

crisis_results = await simulator.run_simulation(**crisis_config)
```

## Integration with Refinement

### Automatic Refinement
Combine simulation with recursive refinement:
```python
from polyhegel.refinement.recursive import RecursiveRefinementEngine

# Run initial simulation
initial_results = await simulator.run_simulation(
    temperature_counts=[(0.7, 3)],
    system_prompt="Generate growth strategies",
    user_prompt="Scale from 10M to 100M ARR"
)

# Refine the best strategy
refinement_engine = RecursiveRefinementEngine()
best_strategy = max(initial_results, key=lambda x: x.strategy.alignment_score)

refined_session = await refinement_engine.refine_strategy(
    strategy=best_strategy,
    system_prompt="Focus on sustainable and scalable growth",
    user_prompt="Prioritize customer retention and expansion"
)

print(f"Original score: {best_strategy.strategy.alignment_score}")
print(f"Refined score: {refined_session.best_score}")
```

## Performance Optimization

### Resource Management
Configure simulation for optimal performance:
```python
# High-performance configuration
config = {
    "concurrent_generations": 3,  # Parallel strategy generation
    "cache_enabled": True,        # Cache model responses
    "timeout_seconds": 120,       # Prevent hanging simulations
    "memory_limit": "2GB"         # Memory usage cap
}

simulator = PolyhegelSimulator(
    model_name="claude-3-haiku-20240307",
    **config
)
```

### Monitoring and Telemetry
Track simulation performance:
```python
from polyhegel.telemetry import get_telemetry_collector

telemetry = get_telemetry_collector("simulation")

# Telemetry is automatically collected during simulation
results = await simulator.run_simulation(...)

# Access performance data
metrics = telemetry.get_metrics()
print(f"Generation time: {metrics['generation_time_avg']}")
print(f"Success rate: {metrics['simulation_success_rate']}")
```

## Best Practices

### Prompt Engineering
- **Be Specific**: Include context, constraints, and desired outcomes
- **Use Examples**: Provide sample scenarios when helpful
- **Set Boundaries**: Define what constitutes success and failure
- **Iterate**: Refine prompts based on initial results

### Temperature Selection
- **Low (0.1-0.4)**: Conservative, reliable strategies
- **Medium (0.5-0.7)**: Balanced creativity and reliability
- **High (0.8-1.0)**: Creative, innovative approaches

### Result Interpretation
- **Multiple Runs**: Execute several simulations for statistical significance
- **Cross-Validation**: Test strategies across different scenarios
- **Human Review**: Combine AI evaluation with expert judgment