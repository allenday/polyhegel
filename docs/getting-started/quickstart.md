# Quick Start

Get up and running with Polyhegel in minutes!

## Basic Simulation

Run a simple strategic simulation:

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

Set up API keys for LLM access:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

Or create a `.env` file:

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## Next Steps

- [Configuration Guide](configuration.md) - Detailed setup options
- [A2A Agents](../guide/a2a-agents.md) - Learn about distributed agents
- [Strategic Techniques](../guide/strategic-techniques.md) - Understanding the methodology