# Polyhegel DX Cheat Sheet

**Quick reference for common development workflows and troubleshooting.**

## 🚀 Quick Start Commands

| Goal | Command | Time |
|------|---------|------|
| **Try polyhegel immediately** | `pip install polyhegel && polyhegel demo` | 0 min |
| **Get strategic techniques** | `git clone repo && make dx-setup-examples` | 5 min |
| **Full development setup** | `git clone repo && make dx-setup-dev` | 10 min |
| **Health check system** | `make dx-doctor` | 1 min |

## 🔍 Discovery & Exploration

```bash
# Discover all capabilities
make dx-discover                    # Interactive overview
polyhegel discover                  # CLI version
polyhegel discover --domain strategic  # Specific domain
polyhegel discover --format json   # Machine readable

# Check what's working  
make dx-doctor                      # Diagnose issues
make dx-doctor-fix                  # Auto-fix problems
```

## 🏗️ Development Workflows

### Creating Custom Domains
```bash
# Interactive domain creation
make dx-new-domain
# Enter: marketing (example)

# Test your new domain
make dx-test-domain
# Enter: marketing

# Manual domain creation
./scripts/polyhegel-create-domain.py healthcare-analytics
```

### A2A Agent Development
```bash
# Start all agents
make agents-start

# Check agent status
make agents-status

# Use with hierarchical simulation
polyhegel simulate --mode hierarchical "your challenge"
```

### Testing & Quality
```bash
# Quick tests
make test-quick              # Fast unit tests
make test-no-llm            # Tests without API calls

# Full test suite
make test-all               # All tests
make test-coverage          # With coverage

# Code quality
make format                 # Format code
make lint                   # Lint checks
make typecheck              # Type checking
```

## 🔧 Troubleshooting Guide

### Import Errors

**Problem:** `ImportError: No module named 'polyhegel.techniques.strategic'`

**Solutions:**
```bash
# Option 1: Auto-setup
make dx-setup-examples

# Option 2: Manual PYTHONPATH
export PYTHONPATH="/path/to/polyhegel/examples:$PYTHONPATH"

# Option 3: Health check + fix
make dx-doctor-fix
```

### Custom Domain Issues

**Problem:** Can't import custom domain techniques

**Solutions:**
```bash
# Check domain structure
ls examples/polyhegel/techniques/your_domain/

# Verify PYTHONPATH
echo $PYTHONPATH

# Test specific domain
make dx-test-domain

# Re-run setup
make dx-setup-examples
```

### API Key Configuration

**Problem:** No API keys configured

**Solutions:**
```bash
# Set environment variables
export ANTHROPIC_API_KEY=your_key
export OPENAI_API_KEY=your_key

# Or create .env file
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Test with demo mode (no keys needed)
polyhegel demo
```

### A2A Agent Issues

**Problem:** Agents won't start or connect

**Solutions:**
```bash
# Check agent status
make agents-status

# Restart agents
make agents-restart

# Check ports
netstat -an | grep 800[1-5]  # Strategic agents
netstat -an | grep 700[1-6]  # Common agents
```

## 📚 Code Patterns

### Using Core Techniques
```python
from polyhegel.techniques.common import ALL_TECHNIQUES

print(f"Core techniques: {len(ALL_TECHNIQUES)}")
for tech in ALL_TECHNIQUES:
    print(f"- {tech.name}: {tech.description}")
```

### Using Domain Extensions
```python
# Requires: make dx-setup-examples
from polyhegel.techniques.strategic import ALL_TECHNIQUES as STRATEGIC
from polyhegel.techniques.product import ALL_TECHNIQUES as PRODUCT

print(f"Strategic: {len(STRATEGIC)} techniques")
print(f"Product: {len(PRODUCT)} techniques")
```

### Custom Domain Development
```python
# After: make dx-new-domain
from polyhegel.techniques.your_domain import ALL_TECHNIQUES
from polyhegel.techniques.your_domain import get_your_domain_technique

# Use specific technique
technique = get_your_domain_technique("example_analysis")
if technique:
    print(f"Using: {technique.name}")
```

### A2A Agent Integration
```python
from polyhegel.clients import PolyhegelA2AClient, A2AAgentEndpoints

# Configure endpoints
endpoints = A2AAgentEndpoints.from_env()
client = PolyhegelA2AClient(endpoints)

# Generate strategies
strategies = await client.generate_hierarchical_strategies(
    "Launch AI product",
    max_themes=5
)
```

## 🎯 Workflow Examples

### New User Journey
```bash
# 1. Try immediately
pip install polyhegel
polyhegel demo

# 2. Explore capabilities  
git clone https://github.com/allendy/polyhegel.git
cd polyhegel
make dx-discover

# 3. Get extended functionality
make dx-setup-examples
polyhegel discover --domain strategic

# 4. Run real simulation
export ANTHROPIC_API_KEY=your_key
polyhegel simulate "develop market entry strategy"
```

### Developer Journey
```bash
# 1. Full setup
git clone repo && cd polyhegel
make dx-setup-dev

# 2. Create custom domain
make dx-new-domain  # Enter: fintech

# 3. Test and iterate
make dx-test-domain  # Enter: fintech
make test-quick

# 4. Start agents for distributed work
make agents-start
polyhegel simulate --mode hierarchical "fintech challenge"
```

### Debugging Journey
```bash
# 1. Health check
make dx-doctor

# 2. Auto-fix issues
make dx-doctor-fix

# 3. Verify specific domain
make dx-test-domain

# 4. Check logs if agents fail
tail -f /tmp/polyhegel-agents/*.log
```

## 📖 Reference Links

- **[Getting Started Guide](GETTING_STARTED.md)** - Choose your setup path
- **[Domain Architecture](DOMAIN_ARCHITECTURE.md)** - Technical architecture details  
- **[Domain Loading](DOMAIN_LOADING.md)** - Namespace packaging details
- **[Development Guide](DEVELOPMENT.md)** - Contributing and development
- **[Full Documentation](https://allendy.github.io/polyhegel/)** - Complete API reference

## 💡 Pro Tips

1. **Use `make dx-doctor` first** when encountering issues
2. **Start with core, expand to examples** - progressive complexity
3. **Create activation scripts** for persistent PYTHONPATH setup
4. **Use domain discovery** to understand available capabilities
5. **Test custom domains** immediately after creation
6. **Health check before reporting issues** - most problems auto-fixable

## ⚡ One-Liners

```bash
# Complete setup for strategic work
git clone repo && cd polyhegel && make dx-setup-examples && polyhegel discover --domain strategic

# Create and test new domain
make dx-new-domain && make dx-setup-examples && make dx-test-domain

# Full development environment
make dx-setup-dev && make agents-start && make test-quick

# Emergency troubleshooting
make dx-doctor-fix && make dx-discover && polyhegel demo
```