# Quick Start

Get up and running with Polyhegel in minutes!

## Try It Now (No Setup Required)

Explore Polyhegel immediately with the demo mode:

```bash
polyhegel demo
```

Or try it with your own strategic challenge:

```bash
polyhegel demo "Launch a new social media platform"
```

The demo shows how Polyhegel works without requiring API keys or any configuration.

## Basic Simulation

Once you have API keys set up, run a real strategic simulation:

```bash
polyhegel simulate "Develop a go-to-market strategy for a new AI product"
```

This will:

1. Generate multiple strategic approaches using temperature sampling
2. Cluster similar strategies together
3. Identify the optimal "trunk" strategy
4. Provide a comprehensive analysis

## Understanding the Output

The simulation produces:

- **Trunk Strategy**: The optimal approach based on clustering analysis
- **Twig Strategies**: Alternative approaches that may be valuable in specific contexts
- **Analysis Summary**: Detailed breakdown of the strategic landscape

## Advanced Options

### Temperature Sampling

Control strategy diversity:

```bash
polyhegel simulate "Market entry strategy" --temperatures 0.1:2 0.5:3 0.9:2
```

This generates:
- 2 strategies at temperature 0.1 (conservative approaches)
- 3 strategies at temperature 0.5 (balanced approaches)  
- 2 strategies at temperature 0.9 (creative approaches)

### Tournament Mode

Use competitive selection instead of clustering:

```bash
polyhegel simulate "Product launch strategy" --selection-method tournament
```

### A2A Agent Mode

For distributed strategic planning:

```bash
# Start the agent ecosystem
make agents-start

# Run hierarchical simulation
polyhegel simulate "Digital transformation strategy" --mode hierarchical
```

## Configuration

### Quick Start Without API Keys

No configuration needed for the demo:

```bash
polyhegel demo  # Works immediately!
```

### Set Up API Keys for Real Simulations

To run actual strategic simulations, set up at least one API key:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

Or create a `.env` file:

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

Check which models are available:

```bash
polyhegel models --with-availability
```

## Python API Usage

After trying the CLI, explore the Python API:

```python
from polyhegel import PolyhegelSimulator

# Initialize simulator
simulator = PolyhegelSimulator()

# Run simulation
results = await simulator.run_simulation(
    temperature_counts=[(0.7, 5), (0.9, 3)],
    user_prompt="Develop a sustainable growth strategy",
    mode="temperature"
)

# Analyze results
if results['trunk']:
    print(f"Best Strategy: {results['trunk']['strategy']['title']}")
```

See [examples/quickstart_python_api.py](../../examples/quickstart_python_api.py) for comprehensive examples.

## Common Issues

### Missing API Keys
```bash
❌ API Key Error: Polyhegel requires API keys to generate strategies.
```
**Solution**: Try the demo first (`polyhegel demo`) or set up API keys.

### No Prompt Provided
```bash
Error: Please provide a strategic challenge either as:
  polyhegel simulate 'your strategic challenge'
  polyhegel simulate --user-prompt-file challenge.txt
```
**Solution**: Include your prompt directly in the command.

## Next Steps

- [Configuration Guide](configuration.md) - Detailed setup options
- [Python Examples](../../examples/quickstart_python_api.py) - Comprehensive API usage
- [A2A Agents](../guide/a2a-agents.md) - Learn about distributed agents
- [Strategic Techniques](../guide/strategic-techniques.md) - Understanding the methodology