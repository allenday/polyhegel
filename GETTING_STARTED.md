# Getting Started with Polyhegel

**Choose your path to get productive in under 5 minutes:**

## 🚀 Quick Start (0 minutes)

Try polyhegel immediately without any setup:

```bash
pip install polyhegel
polyhegel demo
```

**What you get:** Core strategic simulation capabilities with 6 built-in techniques.

---

## 🎯 Domain Expert (5 minutes)

Add strategic, product, and technical architecture domains:

```bash
# Clone repository
git clone https://github.com/allenday/polyhegel.git
cd polyhegel

# One-command setup
make dx-setup-examples
```

**What you get:** 15+ specialized techniques across multiple domains, A2A agents, full simulation capabilities.

**Usage:**
```python
from polyhegel.techniques.strategic import ALL_TECHNIQUES
from polyhegel.techniques.product import ALL_TECHNIQUES  
from polyhegel.techniques.technical_architecture import ALL_TECHNIQUES
```

---

## 🛠️ Developer/Integrator (10 minutes)

Full development environment with custom domain creation:

```bash
# Clone and setup development environment  
git clone https://github.com/allenday/polyhegel.git
cd polyhegel
make dx-setup-dev

# Create your custom domain
make dx-new-domain
# Enter domain name: marketing (example)
```

**What you get:** Development tools, testing setup, domain scaffolding, A2A agent servers, documentation.

---

## 🔍 Explore Capabilities

Discover what's available in your setup:

```bash
# See all available techniques and domains
make dx-discover

# Or via CLI
polyhegel discover

# Or via Python
python -c "from polyhegel.domain_manager import get_all_techniques; print(get_all_techniques())"
```

---

## ❓ Common Questions

### "I just want to try strategic planning techniques"
```bash
git clone https://github.com/allendy/polyhegel.git
cd polyhegel
make dx-setup-examples
python -c "from polyhegel.techniques.strategic import ALL_TECHNIQUES; print([t.name for t in ALL_TECHNIQUES])"
```

### "I need to create my own domain for healthcare analytics"
```bash
git clone https://github.com/allendy/polyhegel.git
cd polyhegel
make dx-setup-dev
make dx-new-domain  # Enter: healthcare-analytics
```

### "I want to run A2A agents for distributed simulation"
```bash
make dx-setup-dev
make agents-start  # Starts all A2A agent servers
polyhegel simulate --mode hierarchical "your strategic challenge"
```

### "How do I know what techniques are available?"
```bash
make dx-discover  # Interactive discovery
# or
polyhegel discover --domain strategic  # Specific domain
# or
polyhegel discover --format json  # Machine-readable
```

---

## 🏗️ Architecture Quick Reference

- **Core Package** (`polyhegel/`): Generic framework with common techniques
- **Examples Package** (`examples/polyhegel/`): Domain-specific extensions (strategic, product, tech-arch)
- **Custom Domains**: Your own extensions following the same pattern

**Import Structure:**
```python
# Core (always available)
from polyhegel.techniques.common import ALL_TECHNIQUES

# Domain extensions (requires examples setup)
from polyhegel.techniques.strategic import ALL_TECHNIQUES
from polyhegel.techniques.product import ALL_TECHNIQUES
from polyhegel.techniques.technical_architecture import ALL_TECHNIQUES

# Your custom domains  
from polyhegel.techniques.your_domain import ALL_TECHNIQUES
```

---

## 🆘 Troubleshooting

### "ImportError: No module named 'polyhegel.techniques.strategic'"
**Solution:** You need examples setup.
```bash
make dx-setup-examples
```

### "I created a custom domain but can't import it"
**Solution:** Check PYTHONPATH and test import.
```bash
# Check PYTHONPATH includes your examples directory
echo $PYTHONPATH

# Test your domain
make dx-test-domain  # Enter your domain name
```

### "A2A agents won't start"
**Solution:** Ensure development setup and check ports.
```bash
make dx-setup-dev
make agents-status  # Check what's running
make agents-restart  # Restart all agents
```

---

## 📚 Next Steps

- **[Architecture Deep Dive](DOMAIN_ARCHITECTURE.md)** - Understand the framework design
- **[Domain Loading Details](DOMAIN_LOADING.md)** - Technical details on namespace packaging
- **[Full Documentation](https://allendy.github.io/polyhegel/)** - Complete guides and API reference
- **[Contributing](DEVELOPMENT.md)** - Contribute to the project

**Still stuck?** File an issue with your setup details and we'll help optimize the DX further.