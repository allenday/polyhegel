#!/usr/bin/env python3
"""
Polyhegel Domain Creation Tool

Scaffolds a new custom domain for polyhegel following best practices:
- Creates proper directory structure
- Generates template files
- Sets up namespace packaging
- Includes example techniques and agents

Usage:
  ./scripts/polyhegel-create-domain.py <domain_name> [--output-dir custom_domains/]
"""

import argparse
from pathlib import Path
from typing import Optional


class DomainScaffolder:
    """Creates scaffolding for new polyhegel domains"""

    def __init__(self, domain_name: str, output_dir: Optional[Path] = None):
        self.domain_name = domain_name.lower().replace("-", "_")
        self.domain_title = domain_name.replace("_", " ").replace("-", " ").title()

        # Default to examples/ directory structure for consistency
        self.output_dir = output_dir or Path("examples")
        self.domain_path = self.output_dir / "polyhegel" / "techniques" / self.domain_name
        self.agents_path = self.output_dir / "polyhegel" / "agents" / self.domain_name
        self.servers_path = self.output_dir / "polyhegel" / "servers" / self.domain_name

    def create_domain(self) -> bool:
        """Create the complete domain structure"""
        print(f"🏗️  Creating {self.domain_title} domain...")

        try:
            # Create directory structure
            self._create_directories()

            # Create core files
            self._create_techniques_module()
            self._create_agents_module()
            self._create_servers_module()
            self._create_prompts()
            self._create_documentation()

            print(f"✅ {self.domain_title} domain created successfully!")
            print(f"📁 Location: {self.domain_path.parent.parent}")
            print("\\n🚀 Next steps:")
            print(f'   1. Add PYTHONPATH: export PYTHONPATH="{self.output_dir}:$PYTHONPATH"')
            print(f"   2. Edit techniques: {self.domain_path}/techniques.py")
            print(
                f'   3. Test: python -c "from polyhegel.techniques.{self.domain_name} import ALL_TECHNIQUES; print(len(ALL_TECHNIQUES))"'
            )
            print(f"   4. Start servers: python -m polyhegel.servers.{self.domain_name}.leader_server")

            return True

        except Exception as e:
            print(f"❌ Failed to create domain: {e}")
            return False

    def _create_directories(self):
        """Create directory structure"""
        directories = [
            self.domain_path,
            self.domain_path / "prompts",
            self.agents_path,
            self.servers_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {directory}")

    def _create_techniques_module(self):
        """Create techniques module with example techniques"""

        # Create safe class name for Python
        class_name = self.domain_title.replace(" ", "").replace("-", "")

        # Main techniques.py
        techniques_content = f'''"""
{self.domain_title} Techniques for Polyhegel

Domain-specific techniques for {self.domain_name} analysis and strategy.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import base classes from core
from polyhegel.techniques.common.techniques import (
    CommonTechnique, 
    TechniqueType,
    TechniqueComplexity,
    TechniqueTimeframe
)


class {class_name}TechniqueType(Enum):
    """{self.domain_title}-specific technique types"""
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    OPTIMIZATION = "optimization"
    EVALUATION = "evaluation"


class {class_name}Technique(CommonTechnique):
    """Base class for {self.domain_name} techniques"""
    
    def __init__(
        self,
        name: str,
        description: str,
        technique_type: "{class_name}TechniqueType",
        complexity: TechniqueComplexity = TechniqueComplexity.MEDIUM,
        timeframe: TechniqueTimeframe = TechniqueTimeframe.SHORT_TERM,
        prerequisites: Optional[List[str]] = None,
        outcomes: Optional[List[str]] = None,
        prompts_dir: Optional[str] = None
    ):
        # Map domain-specific types to common types
        common_type_mapping = {{
            "{class_name}TechniqueType.ANALYSIS": TechniqueType.ANALYTICAL,
            "{class_name}TechniqueType.STRATEGY": TechniqueType.STRATEGIC,
            "{class_name}TechniqueType.OPTIMIZATION": TechniqueType.OPTIMIZATION,
            "{class_name}TechniqueType.EVALUATION": TechniqueType.EVALUATIVE,
        }}
        
        super().__init__(
            name=name,
            description=description,
            technique_type=common_type_mapping.get(str(technique_type), TechniqueType.STRATEGIC),
            complexity=complexity,
            timeframe=timeframe,
            prerequisites=prerequisites or [],
            outcomes=outcomes or []
        )
        
        self.domain_technique_type = technique_type
        self.prompts_dir = prompts_dir or str(Path(__file__).parent / "prompts")


# Example techniques
class Example{class_name}AnalysisTechnique({class_name}Technique):
    """Example analysis technique for {self.domain_name}"""
    
    def __init__(self):
        super().__init__(
            name="example_{self.domain_name}_analysis",
            description=f"Comprehensive analysis technique for {self.domain_name} domain",
            technique_type="{class_name}TechniqueType.ANALYSIS",
            complexity=TechniqueComplexity.MEDIUM,
            timeframe=TechniqueTimeframe.SHORT_TERM,
        )


class Example{class_name}StrategyTechnique({class_name}Technique):
    """Example strategy technique for {self.domain_name}"""
    
    def __init__(self):
        super().__init__(
            name="example_{self.domain_name}_strategy", 
            description=f"Strategic planning technique for {self.domain_name} domain",
            technique_type="{class_name}TechniqueType.STRATEGY",
            complexity=TechniqueComplexity.HIGH,
            timeframe=TechniqueTimeframe.MEDIUM_TERM,
        )


# Registry
ALL_TECHNIQUES = [
    Example{class_name}AnalysisTechnique(),
    Example{class_name}StrategyTechnique(),
]

TECHNIQUE_REGISTRY = {{tech.name: tech for tech in ALL_TECHNIQUES}}


def get_{self.domain_name}_technique(name: str) -> Optional["{class_name}Technique"]:
    """Get a technique by name"""
    return TECHNIQUE_REGISTRY.get(name)


def get_{self.domain_name}_techniques_by_type(technique_type: str) -> List["{class_name}Technique"]:
    """Get techniques by type"""
    return [tech for tech in ALL_TECHNIQUES if str(tech.domain_technique_type) == technique_type]
'''

        with open(self.domain_path / "techniques.py", "w") as f:
            f.write(techniques_content)

        # __init__.py
        init_content = f'''"""
{self.domain_title} Techniques Package

This package provides {self.domain_name}-specific techniques for the polyhegel framework.
"""

from .techniques import (
    {class_name}Technique,
    {class_name}TechniqueType,
    Example{class_name}AnalysisTechnique,
    Example{class_name}StrategyTechnique,
    ALL_TECHNIQUES,
    TECHNIQUE_REGISTRY,
    get_{self.domain_name}_technique,
    get_{self.domain_name}_techniques_by_type,
)

__all__ = [
    "{class_name}Technique",
    "{class_name}TechniqueType", 
    "Example{class_name}AnalysisTechnique",
    "Example{class_name}StrategyTechnique",
    "ALL_TECHNIQUES",
    "TECHNIQUE_REGISTRY",
    "get_{self.domain_name}_technique",
    "get_{self.domain_name}_techniques_by_type",
]
'''

        with open(self.domain_path / "__init__.py", "w") as f:
            f.write(init_content)

        print(f"✓ Created techniques module: {self.domain_path}/techniques.py")

    def _create_agents_module(self):
        """Create simple agents module"""

        class_name = self.domain_title.replace(" ", "").replace("-", "")

        # agents.py
        agents_content = f'''"""
{self.domain_title} Agents for Polyhegel A2A

Simple A2A agent implementations for {self.domain_name} domain.
"""

from typing import Dict, Any, List


class {class_name}LeaderAgent:
    """Leader agent for {self.domain_name} domain coordination"""
    
    def __init__(self):
        self.domain = "{self.domain_name}"
    
    async def coordinate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate {self.domain_name} analysis across follower agents"""
        return {{"domain": self.domain, "coordination": "success", "context": context}}


class {class_name}AnalysisFollower:
    """Follower agent for {self.domain_name} analysis"""
    
    def __init__(self):
        self.specialty = "{self.domain_name}_analysis"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform {self.domain_name} analysis"""
        return {{"specialty": self.specialty, "analysis": f"Analysis for: {{context.get('challenge', 'Unknown')}}"}}


class {class_name}StrategyFollower:
    """Follower agent for {self.domain_name} strategy"""
    
    def __init__(self):
        self.specialty = "{self.domain_name}_strategy"
    
    async def strategize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop {self.domain_name} strategy"""
        return {{"specialty": self.specialty, "strategy": f"Strategy for: {{context.get('challenge', 'Unknown')}}"}}
'''

        with open(self.agents_path / "agents.py", "w") as f:
            f.write(agents_content)

        # __init__.py
        with open(self.agents_path / "__init__.py", "w") as f:
            f.write(f'"""{self.domain_title} Agents Package"""')

        print(f"✓ Created agents module: {self.agents_path}/")

    def _create_servers_module(self):
        """Create server modules for A2A agents"""

        class_name = self.domain_title.replace(" ", "").replace("-", "")

        # leader_server.py
        leader_server_content = f'''#!/usr/bin/env python3
"""
{self.domain_title} Leader Server

A2A leader server for {self.domain_name} domain coordination.
"""

import uvicorn
from fastapi import FastAPI
from polyhegel.agents.{self.domain_name}.agents import {class_name}LeaderAgent

app = FastAPI(title="{self.domain_title} Leader Server")
agent = {class_name}LeaderAgent()

@app.get("/health")
async def health():
    return {{"status": "healthy", "domain": "{self.domain_name}", "role": "leader"}}

@app.post("/{self.domain_name}/coordinate")
async def coordinate(request: dict):
    """Coordinate {self.domain_name} analysis"""
    return await agent.coordinate(request)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 9001
    
    print(f"🚀 Starting {self.domain_title} Leader Server...")
    print(f"   Host: {{HOST}}")
    print(f"   Port: {{PORT}}")
    
    uvicorn.run(app, host=HOST, port=PORT)
'''

        with open(self.servers_path / "leader_server.py", "w") as f:
            f.write(leader_server_content)

        # __init__.py
        with open(self.servers_path / "__init__.py", "w") as f:
            f.write(f'"""{self.domain_title} Servers Package"""')

        print(f"✓ Created servers module: {self.servers_path}/")

    def _create_prompts(self):
        """Create prompt templates"""

        prompts = {
            "analyze.md": f"""# {self.domain_title} Analysis Prompt

Analyze the following {self.domain_name} challenge:

## Challenge
{{challenge}}

## Analysis Framework

1. **Context Assessment**
   - Current situation analysis
   - Key stakeholders identification
   - Available resources evaluation

2. **Problem Definition**
   - Core issues identification
   - Constraints and limitations
   - Success criteria definition

3. **Analysis Methods**
   - Relevant analytical approaches
   - Data requirements
   - Risk factors

4. **Recommendations**
   - Specific actionable recommendations
   - Implementation approach
   - Success metrics

## Output Format
Provide structured analysis with clear sections and actionable insights.
""",
            "strategize.md": f"""# {self.domain_title} Strategy Development Prompt

Develop a comprehensive strategy for the following {self.domain_name} challenge:

## Challenge Context
{{context}}

## Strategic Framework

1. **Vision & Objectives**
   - Clear strategic vision
   - Specific measurable objectives
   - Success indicators

2. **Analysis & Assessment**
   - Current state analysis
   - Gap analysis
   - Competitive landscape

3. **Strategic Options**
   - Alternative approaches
   - Trade-offs evaluation
   - Recommendation rationale

4. **Implementation Plan**
   - Detailed action steps
   - Timeline and milestones
   - Resource requirements

## Output Format
Provide a comprehensive strategy document with clear structure and actionable components.
""",
        }

        for filename, content in prompts.items():
            with open(self.domain_path / "prompts" / filename, "w") as f:
                f.write(content)

        print(f"✓ Created prompts: {self.domain_path}/prompts/")

    def _create_documentation(self):
        """Create documentation files"""

        readme_content = f"""# {self.domain_title} Domain for Polyhegel

This package provides {self.domain_name}-specific techniques and agents for the polyhegel framework.

## Quick Start

```python
# Import techniques
from polyhegel.techniques.{self.domain_name} import ALL_TECHNIQUES

print(f"Available {self.domain_name} techniques: {{len(ALL_TECHNIQUES)}}")

# Use specific technique
from polyhegel.techniques.{self.domain_name} import get_{self.domain_name}_technique

technique = get_{self.domain_name}_technique("example_{self.domain_name}_analysis")
if technique:
    print(f"Using technique: {{technique.name}}")
```

## Available Techniques

- **Example {self.domain_title} Analysis**: Comprehensive analysis for {self.domain_name} domain
- **Example {self.domain_title} Strategy**: Strategic planning for {self.domain_name} domain

## Available Agents

- **{self.domain_title} Leader Agent**: Coordinates {self.domain_name} analysis across follower agents
- **{self.domain_title} Analysis Follower**: Specializes in {self.domain_name} analysis
- **{self.domain_title} Strategy Follower**: Specializes in {self.domain_name} strategy development

## Server Usage

Start the leader server:

```bash
python -m polyhegel.servers.{self.domain_name}.leader_server
```

## Setup

Add this domain to your PYTHONPATH:

```bash
export PYTHONPATH="{self.output_dir}:$PYTHONPATH"
```

Or use the setup automation:

```bash
./scripts/polyhegel-setup.py with-examples
```
"""

        with open(self.domain_path.parent.parent / f"{self.domain_name}_README.md", "w") as f:
            f.write(readme_content)

        print(f"✓ Created documentation: {self.domain_name}_README.md")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new polyhegel domain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./scripts/polyhegel-create-domain.py marketing
  ./scripts/polyhegel-create-domain.py hr-analytics --output-dir custom_domains/
  ./scripts/polyhegel-create-domain.py supply-chain
        """,
    )

    parser.add_argument("domain_name", help="Name of the domain to create")
    parser.add_argument("--output-dir", type=Path, help="Output directory (default: examples/)")

    args = parser.parse_args()

    scaffolder = DomainScaffolder(args.domain_name, args.output_dir)
    success = scaffolder.create_domain()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
