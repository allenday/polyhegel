# Polyhegel Test Fixtures: The Great Hotdog Reconciliation

This directory contains pre-generated strategic simulation results focused on resolving the hotdog-sandwich classification conflict.

## Leader-Follower Architecture

These fixtures follow the LLM-As-Hierarchical-Policy pattern:
- **Leader Agent**: Identifies high-level strategic themes (this fixture)
- **Follower Agents**: Develop specific implementation strategies (future work)

## Available Fixtures

### Main Hotdog Reconciliation Simulation
- `hotdog_reconciliation_simulation.json` - Complete simulation results (JSON)
- `hotdog_reconciliation_trunk.json` - Trunk strategy only (JSON)
- `hotdog_reconciliation_report.md` - Full report with QA formatting (Markdown)

### Test Utilities
- `minimal_hotdog_test.json` - Lightweight fixture for unit tests

## Strategic Challenge Overview

The hotdog classification conflict represents a perfect test case for strategic consensus-building because it:
- Contains real stakeholder disagreement (structural vs. cultural perspectives)
- Requires taxonomic authority and governance frameworks
- Involves multi-stakeholder negotiation and compromise
- Tests conflict resolution without political sensitivity
- Demonstrates principles applicable to other belief system conflicts

## Usage

Load fixtures in tests to avoid expensive LLM calls:

```python
import json
from pathlib import Path

# Load full simulation
fixture_path = Path(__file__).parent / 'fixtures' / 'hotdog_reconciliation_simulation.json'
with open(fixture_path) as f:
    hotdog_results = json.load(f)

# Load minimal fixture for fast tests
minimal_path = Path(__file__).parent / 'fixtures' / 'minimal_hotdog_test.json'
with open(minimal_path) as f:
    minimal_results = json.load(f)
```
