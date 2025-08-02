# Troubleshooting

Common issues and their solutions when getting started with Polyhegel.

## Quick Solutions

### "I just want to see how this works!"

```bash
polyhegel demo
```

The demo works immediately without any setup and shows real examples of strategy generation.

### "Command not found: polyhegel"

**Problem**: The CLI isn't available after installation.

**Solutions**:
1. Check if installed: `pip list | grep polyhegel`
2. Try with python module: `python -m polyhegel demo`
3. Reinstall: `pip uninstall polyhegel && pip install polyhegel`

### "Cannot import name 'PolyhegelSimulator'"

**Problem**: Import error when trying to use Python API.

**Solutions**:
1. Check installation: `python -c "import polyhegel; print('OK')"`
2. The simulator has optional dependencies - install with: `pip install polyhegel[dev]`
3. Try importing just the models: `from polyhegel import StrategyStep, GenesisStrategy`

## CLI Issues

### "Must provide either a prompt argument or --user-prompt-file"

**Problem**: No strategic challenge provided to simulate command.

**Solutions**:
```bash
# ✅ Correct: Direct prompt
polyhegel simulate "your strategic challenge"

# ✅ Correct: From file  
polyhegel simulate --user-prompt-file challenge.txt

# ❌ Wrong: No prompt
polyhegel simulate --output results/
```

### "API Key Error"

**Problem**: Missing API keys for real simulations.

**Solutions**:
1. **Try demo first**: `polyhegel demo` (no keys needed)
2. **Set API key**: `export ANTHROPIC_API_KEY=your_key`
3. **Use .env file**: Create `.env` with `ANTHROPIC_API_KEY=your_key`
4. **Check available models**: `polyhegel models --with-availability`

### "Prompt file not found"

**Problem**: Missing prompt template files.

**This should be fixed automatically, but if you see this error**:
```bash
# Check if prompts directory exists
ls polyhegel/prompts/strategic/

# If empty, the package may not be installed correctly
pip uninstall polyhegel && pip install polyhegel
```

## Python API Issues

### "No module named 'polyhegel'"

**Problem**: Package not installed or not in Python path.

**Solutions**:
1. Install: `pip install polyhegel`
2. Check Python path: `python -c "import sys; print(sys.path)"`
3. Use absolute imports if running from source

### "Simulation returns empty results"

**Problem**: No strategies generated or clustering fails.

**Common causes**:
1. **No API keys**: Strategies aren't actually generated
2. **Insufficient strategies**: Need at least 2-3 for meaningful clustering
3. **All strategies are identical**: No variation to cluster

**Solutions**:
```python
# Check if strategies were actually generated
results = await simulator.run_simulation(...)
print(f"Generated {results['metadata']['total_chains']} strategies")

# Increase strategy count
results = await simulator.run_simulation(
    temperature_counts=[(0.5, 5), (0.8, 5)],  # More strategies
    user_prompt=prompt
)

# Try tournament selection instead of clustering
results = await simulator.run_simulation(
    temperature_counts=[(0.7, 3)],
    user_prompt=prompt,
    selection_method="tournament"
)
```

### "AttributeError: 'dict' object has no attribute..."

**Problem**: Trying to access strategy attributes incorrectly.

**Solution**: Check the data structure:
```python
# ✅ Correct
if results['trunk']:
    strategy = results['trunk']['strategy']
    print(strategy['title'])

# ❌ Wrong - strategies are dicts, not objects
strategy = results['trunk'].strategy  # AttributeError
```

## A2A Agent Issues

### "A2A agents require running agent servers"

**Problem**: Trying to use hierarchical mode without agents.

**Solutions**:
1. **Use demo mode**: `polyhegel demo` 
2. **Use temperature mode**: `polyhegel simulate "prompt"` (default)
3. **Start agents**: `make agents-start` then use `--mode hierarchical`

### "Connection refused" or "Agent not available"

**Problem**: A2A agents aren't running or misconfigured.

**Solutions**:
1. **Check agent status**: `make agents-status`
2. **Restart agents**: `make agents-restart`
3. **Check ports**: Ensure ports 8001, 8002 etc. are available
4. **Use temperature mode**: Skip A2A agents entirely

## Performance Issues

### "Simulation takes too long"

**Problem**: Large number of strategies or complex processing.

**Solutions**:
```bash
# Reduce strategy count
polyhegel simulate "prompt" --temperatures 0.7:3 0.9:2

# Use faster model
polyhegel simulate "prompt" --model claude-3-haiku-20240307

# Skip expensive operations
polyhegel simulate "prompt" --selection-method tournament  # Usually faster than clustering
```

### "Memory errors or crashes"

**Problem**: Large models or too many strategies.

**Solutions**:
1. **Reduce batch size**: Use fewer strategies at once
2. **Use lighter models**: Try `claude-3-haiku-20240307` instead of larger models
3. **Monitor memory**: `htop` or Activity Monitor
4. **Restart Python session**: Clear memory between runs

## Getting Help

### "I found a bug!"

1. **Try the demo first**: `polyhegel demo` to verify basic functionality
2. **Check the logs**: Look for error messages and stack traces
3. **Minimal example**: Create the smallest possible example that reproduces the issue
4. **Report it**: [GitHub Issues](https://github.com/allenday/polyhegel/issues)

### "I need help with strategy design"

The technical tool is working, but you need help with strategic thinking:

1. **Read the guides**: [Strategic Techniques](../guide/strategic-techniques.md)
2. **Try different prompts**: More specific prompts usually give better results
3. **Experiment with temperatures**: Lower (0.3) = conservative, higher (0.9) = creative
4. **Use tournament mode**: `--selection-method tournament` for competitive evaluation

### "I want to contribute"

Great! See [DEVELOPMENT.md](../../DEVELOPMENT.md) for:
- Development setup
- Testing guidelines  
- Code style standards
- Contributing workflow

## Debug Information

When reporting issues, include:

```bash
# Python and package versions
python --version
pip list | grep polyhegel

# Try basic import
python -c "import polyhegel; print('✅ Import OK')"

# Test demo mode
polyhegel demo

# Check available models (if you have API keys)
polyhegel models --with-availability
```