# Extending Polyhegel - Developer Guide

**Create Custom Domains and Techniques**

## Overview

Polyhegel's extensible architecture makes it easy to add custom domains while leveraging the existing framework. This guide shows how to create your own analytical techniques and agents.

## Quick Start: Create a Custom Domain

### 1. Create Domain Structure

```bash
# Create your custom domain
mkdir -p my_domains/polyhegel/techniques/finance
cd my_domains/polyhegel/techniques/finance

# Create required files
touch __init__.py
touch techniques.py
mkdir prompts
```

### 2. Implement Techniques

**File: `techniques.py`**
```python
from enum import Enum
from typing import List
from dataclasses import dataclass
from polyhegel.techniques.common import TechniqueType, TechniqueComplexity, TechniqueTimeframe

class FinanceDomain(Enum):
    VALUATION = "valuation"
    RISK_MANAGEMENT = "risk_management"
    INVESTMENT_ANALYSIS = "investment_analysis"

@dataclass
class FinanceTechnique:
    name: str
    description: str
    domain: FinanceDomain
    technique_type: TechniqueType
    complexity: TechniqueComplexity
    timeframe: TechniqueTimeframe
    use_cases: List[str]
    inputs_required: List[str]
    outputs_provided: List[str]

# Define your techniques
DiscountedCashFlowTechnique = FinanceTechnique(
    name="Discounted Cash Flow Analysis",
    description="Value assets based on projected future cash flows",
    domain=FinanceDomain.VALUATION,
    technique_type=TechniqueType.ANALYSIS,
    complexity=TechniqueComplexity.HIGH,
    timeframe=TechniqueTimeframe.SHORT_TERM,
    use_cases=[
        "Company valuation for M&A",
        "Investment decision analysis",
        "Project feasibility assessment"
    ],
    inputs_required=[
        "Historical financial data",
        "Growth projections",
        "Discount rate assumptions"
    ],
    outputs_provided=[
        "Net Present Value calculation",
        "Sensitivity analysis",
        "Valuation range estimate"
    ]
)

# Registry for framework integration
ALL_TECHNIQUES = [DiscountedCashFlowTechnique]
TECHNIQUE_REGISTRY = {tech.name: tech for tech in ALL_TECHNIQUES}
```

### 3. Setup Namespace Extension

**File: `__init__.py`**
```python
"""Finance Domain for Polyhegel"""

# Enable namespace extension
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .techniques import (
    ALL_TECHNIQUES,
    TECHNIQUE_REGISTRY,
    FinanceTechnique,
    DiscountedCashFlowTechnique,
)

__all__ = [
    "ALL_TECHNIQUES",
    "TECHNIQUE_REGISTRY", 
    "FinanceTechnique",
    "DiscountedCashFlowTechnique",
]
```

### 4. Test Your Domain

```bash
# Enable your custom domain
export PYTHONPATH="$(pwd)/my_domains:$PYTHONPATH"

# Test integration
python -c "from polyhegel.techniques.finance import ALL_TECHNIQUES; print(f'{len(ALL_TECHNIQUES)} finance techniques')"

# Discover capabilities
polyhegel discover --domain all
```

## Advanced: Create Custom Agents

### 1. Agent Implementation

**File: `agents.py`**
```python
import logging
from typing import Any
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message, new_data_artifact

from ..techniques import get_finance_technique

logger = logging.getLogger(__name__)

class FinanceAnalysisLeader(AgentExecutor):
    """Leader agent for financial analysis coordination"""
    
    def __init__(self, model: Any):
        self.model = model
        self.agent_id = "polyhegel-finance-leader"
    
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Coordinate financial analysis"""
        try:
            request = context.request.get("user_prompt", "")
            
            # Analyze request and select appropriate techniques
            selected_techniques = self._select_techniques(request)
            
            await event_queue.enqueue_event(
                new_agent_text_message(f"🏦 Starting financial analysis with {len(selected_techniques)} techniques...")
            )
            
            # Coordinate analysis (simplified example)
            for technique in selected_techniques:
                result = await self._apply_technique(technique, request)
                await event_queue.enqueue_event(new_data_artifact(
                    f"{technique.name} Analysis",
                    result,
                    artifact_type="financial_analysis"
                ))
                
        except Exception as e:
            await event_queue.enqueue_event(
                new_agent_text_message(f"❌ Financial analysis error: {str(e)}")
            )
    
    def _select_techniques(self, request: str) -> List[Any]:
        """Select appropriate financial techniques based on request"""
        # Implement your technique selection logic
        from ..techniques import ALL_TECHNIQUES
        return ALL_TECHNIQUES[:2]  # Simplified example
    
    async def _apply_technique(self, technique: Any, request: str) -> dict:
        """Apply a financial technique to the request"""
        # Implement your technique application logic
        return {
            "technique": technique.name,
            "analysis": f"Analysis results for: {request}",
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
```

### 2. A2A Agent Cards

**File: `cards.py`**
```python
from typing import List
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

def create_finance_leader_card(base_url: str = "http://localhost:8010") -> AgentCard:
    """Create A2A AgentCard for FinanceAnalysisLeader"""
    
    finance_skill = AgentSkill(
        id="financial_analysis_coordination",
        name="Financial Analysis Coordination",
        description="Coordinates comprehensive financial analysis including valuation, risk assessment, and investment analysis.",
        tags=["finance", "valuation", "risk", "investment", "analysis"],
        examples=[
            "DCF valuation for acquisition target",
            "Investment portfolio risk analysis", 
            "Project feasibility financial modeling"
        ],
        input_modes=["text/plain"],
        output_modes=["application/json", "text/plain"],
    )
    
    return AgentCard(
        name="Polyhegel Finance Analysis Leader",
        description="Specialized agent for financial analysis and valuation across investment and corporate finance contexts.",
        url=base_url,
        version="1.0.0",
        default_input_modes=["text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, state_transition_history=True),
        skills=[finance_skill],
        supports_authenticated_extended_card=False,
    )
```

### 3. Server Implementation

**File: `servers/finance_leader_server.py`**
```python
#!/usr/bin/env python3
import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from polyhegel.model_manager import ModelManager
from ..agents import FinanceAnalysisLeader
from ..cards import create_finance_leader_card

def create_finance_server(host: str = "0.0.0.0", port: int = 8010, model_name: str = "claude-3-haiku-20240307"):
    model_manager = ModelManager()
    model = model_manager.get_model(model_name)
    
    agent_executor = FinanceAnalysisLeader(model=model)
    agent_card = create_finance_leader_card(base_url=f"http://{host}:{port}")
    
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )
    
    return A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

def main():
    host = os.getenv("POLYHEGEL_FINANCE_HOST", "0.0.0.0")
    port = int(os.getenv("POLYHEGEL_FINANCE_PORT", "8010"))
    model_name = os.getenv("POLYHEGEL_FINANCE_MODEL", "claude-3-haiku-20240307")
    
    server = create_finance_server(host=host, port=port, model_name=model_name)
    uvicorn.run(server.build(), host=host, port=port)

if __name__ == "__main__":
    main()
```

## Best Practices

### 1. Follow Existing Patterns

- **Study Examples:** Look at `examples/polyhegel/techniques/strategic/` for reference
- **Consistent Structure:** Use same file organization and naming conventions
- **Namespace Extension:** Always include `pkgutil.extend_path()` in `__init__.py`

### 2. Technique Design

- **Clear Naming:** Use descriptive technique names
- **Comprehensive Metadata:** Include use cases, inputs, outputs, complexity
- **Domain-Specific:** Focus on your domain expertise while leveraging common techniques

### 3. Agent Integration

- **A2A Protocol:** Follow existing agent patterns for consistency
- **Error Handling:** Implement proper error handling and logging
- **Service Discovery:** Create proper AgentCard definitions

### 4. Testing

```python
# Test your techniques
def test_finance_techniques():
    from polyhegel.techniques.finance import ALL_TECHNIQUES
    assert len(ALL_TECHNIQUES) > 0
    assert all(hasattr(tech, 'name') for tech in ALL_TECHNIQUES)

# Test namespace integration
def test_namespace_extension():
    import polyhegel.techniques.finance
    assert hasattr(polyhegel.techniques.finance, 'ALL_TECHNIQUES')
```

## Deployment

### 1. Package Structure

```
my_domains/
└── polyhegel/
    └── techniques/
        └── finance/
            ├── __init__.py          # Namespace extension
            ├── techniques.py        # Core technique definitions
            ├── agents.py           # Agent implementations
            ├── cards.py            # A2A service discovery
            ├── servers/            # Server implementations
            └── prompts/            # LLM prompt templates
                ├── dcf_analysis.md
                └── risk_assessment.md
```

### 2. Environment Setup

```bash
# Development
export PYTHONPATH="/path/to/my_domains:/path/to/examples:$PYTHONPATH"

# Production
export PYTHONPATH="/opt/polyhegel/domains:/opt/polyhegel/examples:$PYTHONPATH"
```

### 3. Integration Verification

```bash
# Verify techniques are discoverable
polyhegel discover --domain all

# Test technique imports
python -c "from polyhegel.techniques.finance import ALL_TECHNIQUES; print('✓ Finance domain ready')"

# Test agent integration
python -c "from polyhegel.agents.finance import FinanceAnalysisLeader; print('✓ Finance agents ready')"
```

## Examples

### Finance Domain
- Techniques: DCF Analysis, Risk Assessment, Portfolio Optimization
- Use Cases: Investment analysis, valuation, risk management

### Healthcare Domain  
- Techniques: Clinical Decision Support, Epidemiological Analysis
- Use Cases: Treatment protocols, population health, clinical research

### Legal Domain
- Techniques: Contract Analysis, Risk Assessment, Compliance Review
- Use Cases: Legal research, document review, regulatory compliance

## Contributing Back

Consider contributing useful domains back to the polyhegel examples:

1. **Fork Repository:** Create your own fork of polyhegel
2. **Add Domain:** Implement domain in `examples/polyhegel/techniques/your_domain/`
3. **Documentation:** Add comprehensive documentation and examples
4. **Submit PR:** Submit pull request with your domain implementation

## Resources

- **Examples Reference:** `examples/polyhegel/techniques/strategic/`
- **A2A Documentation:** Agent-to-Agent protocol specifications
- **Core Architecture:** [Core vs Examples Guide](../architecture/core-vs-examples.md)
- **Contributing:** [Contribution Guidelines](../contributing.md)

---

*Need help extending polyhegel? Open an issue on [GitHub](https://github.com/allendy/polyhegel/issues) with the `extension` label.*