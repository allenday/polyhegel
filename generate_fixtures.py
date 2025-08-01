#!/usr/bin/env python3
"""
Generate test fixtures for polyhegel strategic simulations

This script creates hotdog-focused strategic simulation data following the
leader-follower architecture pattern. Outputs both JSON and Markdown for easy QA.
"""

import asyncio
import json
from pathlib import Path
from polyhegel.simulator import PolyhegelSimulator
from polyhegel.config import Config


async def generate_strategic_fixtures():
    """Generate strategic simulation fixtures for testing"""

    print("🌭 Generating hotdog strategic simulation fixtures...")

    # Create fixtures directory
    fixtures_dir = Path("tests/fixtures")
    fixtures_dir.mkdir(exist_ok=True)

    # Initialize simulator with test configuration
    simulator = PolyhegelSimulator()

    # The Great Hotdog Reconciliation Challenge
    # This follows leader-follower architecture:
    # Leader Agent: Identifies high-level strategic themes for resolving belief conflicts
    # Follower Agents: Develop specific implementation strategies for each theme

    hotdog_scenario = {
        "system_prompt": """You are a LEADER AGENT in a strategic planning system. Your role is to identify high-level strategic themes and frameworks for complex consensus-building challenges.

You work with follower agents who will implement specific strategies based on your strategic themes. Focus on:
- Identifying core conflict dimensions and stakeholder groups
- Establishing framework principles for resolution
- Setting success criteria and evaluation metrics
- Defining implementation phases and priorities

Provide strategic guidance that follower agents can operationalize into specific action plans.""",
        "user_prompt": """STRATEGIC CHALLENGE: The Great Hotdog-Sandwich Classification Controversy

**The Core Question:** IS A HOTDOG A SANDWICH?

**Background:** A bitter ideological divide has split society over this fundamental taxonomic question. Some people firmly believe that hotdogs ARE sandwiches based on structural criteria (bread + filling = sandwich), while others vehemently maintain that hotdogs are NOT sandwiches and constitute a unique food category with distinct cultural and culinary identity.

**Stakeholders:**
- **Sandwich Purists**: Advocate for strict structural definitions
- **Hotdog Traditionalists**: Defend unique cultural classification  
- **Culinary Professionals**: Seek practical operational standards
- **Linguistic Scholars**: Focus on etymological and semantic precision
- **General Public**: Want simple, intuitive food categories

**Core Challenge:** Design a comprehensive strategic framework to achieve societal consensus on hotdog classification that:
1. Respects both structural and cultural perspectives
2. Establishes legitimate taxonomic authority
3. Creates mechanisms for peaceful coexistence of viewpoints
4. Prevents escalation into broader food classification conflicts
5. Maintains practical utility for restaurants, regulations, and consumers

**Strategic Question:** How do we transform this belief conflict into a collaborative framework that strengthens rather than divides our food culture?

**Leader Agent Task:** Provide 3-5 high-level strategic themes that follower agents can develop into specific implementation strategies. Focus on conflict resolution principles that could apply to other consensus-building challenges.""",
    }

    print("📊 Generating Leader Agent output for hotdog reconciliation...")

    try:
        # Generate the strategic simulation
        results = await simulator.run_simulation(
            temperature_counts=Config.DEFAULT_TEMPERATURE_COUNTS,  # [(0.7, 30)]
            system_prompt=hotdog_scenario["system_prompt"],
            user_prompt=hotdog_scenario["user_prompt"],
        )

        # Save complete results as JSON for programmatic access
        json_file = fixtures_dir / "hotdog_reconciliation_simulation.json"

        def json_converter(obj):
            """Convert numpy types to native Python types for JSON serialization"""
            import numpy as np

            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return str(obj)

        def clean_dict_keys(obj):
            """Recursively clean dictionary keys to ensure JSON compatibility"""
            import numpy as np

            if isinstance(obj, dict):
                return {str(k): clean_dict_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_dict_keys(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj

        # Clean the results first
        clean_results = clean_dict_keys(results)

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False, default=json_converter)

        # Save trunk strategy as JSON for tests
        if results.get("trunk"):
            trunk_json = fixtures_dir / "hotdog_reconciliation_trunk.json"
            with open(trunk_json, "w", encoding="utf-8") as f:
                json.dump(clean_dict_keys(results["trunk"]), f, indent=2, ensure_ascii=False, default=json_converter)

        # Save individual run outputs - this is what you wanted to see!
        individual_runs_dir = fixtures_dir / "individual_runs"
        individual_runs_dir.mkdir(exist_ok=True)

        # Access the raw strategy chains to get individual LLM outputs
        if hasattr(simulator, "chains") and simulator.chains:
            for i, chain in enumerate(simulator.chains):
                # Save individual strategy as markdown for easy QA
                individual_md = individual_runs_dir / f"run_{i+1}_temp_{chain.temperature}.md"
                with open(individual_md, "w", encoding="utf-8") as f:
                    f.write(f"# Individual LLM Run #{i+1}\n\n")
                    f.write(f"**Temperature:** {chain.temperature}\n")
                    f.write(f"**Sample Index:** {chain.source_sample}\n")
                    f.write(f"**Model:** {results['metadata']['model']}\n\n")
                    f.write("## Raw LLM Response\n\n")
                    f.write("This is the individual strategic plan generated by the Leader Agent:\n\n")
                    f.write(f"### {chain.strategy.title}\n\n")
                    f.write(f"**Timeline:** {chain.strategy.estimated_timeline}\n\n")

                    for j, step in enumerate(chain.strategy.steps, 1):
                        f.write(f"#### Step {j}: {step.action}\n\n")
                        f.write("**Prerequisites:**\n")
                        for prereq in step.prerequisites:
                            f.write(f"- {prereq}\n")
                        f.write(f"\n**Expected Outcome:** {step.outcome}\n\n")
                        f.write("**Key Risks:**\n")
                        for risk in step.risks:
                            f.write(f"- {risk}\n")
                        f.write(f"\n**Confidence:** {step.confidence}\n\n")

                    f.write("### Strategic Alignment\n\n")
                    for metric, score in chain.strategy.alignment_score.items():
                        f.write(f"- **{metric}:** {score}/5.0\n")
                    f.write("\n")

                    f.write("### Resource Requirements\n\n")
                    for resource in chain.strategy.resource_requirements:
                        f.write(f"- {resource}\n")

                # Also save as JSON for programmatic access
                individual_json = individual_runs_dir / f"run_{i+1}_temp_{chain.temperature}.json"
                chain_dict = {
                    "title": chain.strategy.title,
                    "steps": [step.model_dump() for step in chain.strategy.steps],
                    "alignment_score": chain.strategy.alignment_score,
                    "estimated_timeline": chain.strategy.estimated_timeline,
                    "resource_requirements": chain.strategy.resource_requirements,
                    "metadata": {
                        "source_sample": chain.source_sample,
                        "temperature": chain.temperature,
                        "cluster_label": getattr(chain, "cluster_label", None),
                        "is_trunk": getattr(chain, "is_trunk", False),
                        "is_twig": getattr(chain, "is_twig", False),
                    },
                }
                with open(individual_json, "w", encoding="utf-8") as f:
                    json.dump(clean_dict_keys(chain_dict), f, indent=2, ensure_ascii=False, default=json_converter)

            print(f"✅ Saved {len(simulator.chains)} individual run outputs to individual_runs/")

        # Save detailed markdown report for easy QA
        md_file = fixtures_dir / "hotdog_reconciliation_report.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("# The Great Hotdog Reconciliation Initiative\n\n")
            f.write("**Strategic Challenge:** Resolving the hotdog-sandwich classification conflict\n\n")
            f.write("## Leader Agent Prompt\n\n")
            f.write("**System Role:** Leader Agent for Strategic Planning\n\n")
            f.write(f"**User Prompt:**\n```\n{hotdog_scenario['user_prompt']}\n```\n\n")

            f.write("## Simulation Results\n\n")
            f.write(f"- **Total Strategies Generated:** {results['metadata']['total_chains']}\n")
            f.write(f"- **Model Used:** {results['metadata']['model']}\n")
            f.write(f"- **Temperature Settings:** {results['metadata']['temperature_counts']}\n")
            f.write(f"- **Trunk Strategy Identified:** {'Yes' if results.get('trunk') else 'No'}\n")
            f.write(f"- **Alternative Strategies:** {len(results.get('twigs', []))}\n\n")

            if results.get("trunk"):
                trunk = results["trunk"]
                f.write("## Trunk Strategy: Leader Agent Output\n\n")
                f.write(f"**Title:** {trunk['title']}\n\n")
                f.write(f"**Timeline:** {trunk['estimated_timeline']}\n\n")

                f.write("### Strategic Steps (for Follower Agent Implementation)\n\n")
                for i, step in enumerate(trunk["steps"], 1):
                    f.write(f"#### {i}. {step['action']}\n\n")
                    f.write("**Prerequisites:**\n")
                    for prereq in step["prerequisites"]:
                        f.write(f"- {prereq}\n")
                    f.write(f"\n**Expected Outcome:** {step['outcome']}\n\n")
                    f.write("**Key Risks:**\n")
                    for risk in step["risks"]:
                        f.write(f"- {risk}\n")
                    f.write(f"\n**Confidence Level:** {step['confidence']}\n\n")

                f.write("### Strategic Alignment Scores\n\n")
                for metric, score in trunk["alignment_score"].items():
                    f.write(f"- **{metric}:** {score}/5.0\n")
                f.write("\n")

                f.write("### Resource Requirements\n\n")
                for resource in trunk["resource_requirements"]:
                    f.write(f"- {resource}\n")
                f.write("\n")

            if results.get("twigs"):
                f.write("## Alternative Strategies (Twigs)\n\n")
                for i, twig in enumerate(results["twigs"], 1):
                    f.write(f"### Alternative {i}: {twig['title']}\n\n")
                    f.write(f"**Timeline:** {twig['estimated_timeline']}\n\n")
                    for j, step in enumerate(twig["steps"], 1):
                        f.write(f"{j}. **{step['action']}** (confidence: {step['confidence']})\n")
                    f.write("\n")

            f.write("## Strategic Analysis Summary\n\n")
            if results.get("summary"):
                f.write(results["summary"])
            f.write("\n\n")

            f.write("## Follower Agent Implementation Notes\n\n")
            f.write("This Leader Agent output provides strategic themes that Follower Agents should develop into:\n\n")
            f.write("1. **Detailed Implementation Plans** - Specific actions, timelines, and resource allocation\n")
            f.write("2. **Stakeholder Engagement Protocols** - Communication strategies for each group\n")
            f.write("3. **Consensus Mechanisms** - Voting systems, mediation processes, compromise frameworks\n")
            f.write("4. **Success Metrics** - Measurable outcomes and progress indicators\n")
            f.write("5. **Risk Mitigation Strategies** - Specific contingency plans for identified risks\n\n")
            f.write("The hotdog reconciliation framework demonstrates strategic principles applicable to:\n")
            f.write("- Belief system conflicts\n")
            f.write("- Taxonomic authority disputes\n")
            f.write("- Multi-stakeholder consensus building\n")
            f.write("- Cultural vs. technical standards conflicts\n")

        print("✅ Generated hotdog reconciliation fixtures (JSON + Markdown)")

    except Exception as e:
        print(f"❌ Failed to generate hotdog fixtures: {e}")
        raise

    # Generate a minimal test fixture for fast unit tests
    print("🚀 Generating minimal test fixture...")

    minimal_results = {
        "trunk": {
            "title": "Minimal Hotdog Test Strategy",
            "steps": [
                {
                    "action": "Establish Test Hotdog Council",
                    "prerequisites": ["Set up test environment", "Configure mock stakeholders"],
                    "outcome": "Functional testing infrastructure with hotdog classification framework",
                    "risks": ["Insufficient sandwich representation", "Mock hotdog limitations"],
                    "confidence": 0.9,
                }
            ],
            "alignment_score": {"Culinary Harmony": 4.5, "Test Coverage": 4.8},
            "estimated_timeline": "1-2 hours",
            "resource_requirements": ["Test hotdogs", "Mock sandwich council", "Taxonomic framework"],
            "metadata": {
                "source_sample": 0,
                "temperature": 0.8,
                "cluster_label": -1,
                "is_trunk": True,
                "is_twig": False,
            },
        },
        "twigs": [],
        "summary": "Minimal hotdog reconciliation strategy for unit testing. Provides basic structure without requiring expensive LLM generation.",
        "metadata": {
            "total_chains": 1,
            "model": "test-fixture",
            "temperature_counts": [[0.8, 1]],
            "clustering": {"trunk": "test", "twigs": [], "cluster_count": 1, "noise_count": 0},
        },
    }

    minimal_file = fixtures_dir / "minimal_hotdog_test.json"
    with open(minimal_file, "w", encoding="utf-8") as f:
        json.dump(minimal_results, f, indent=2, ensure_ascii=False, default=json_converter)

    print("✅ Generated minimal hotdog test fixture")

    # Create fixtures index
    index_file = fixtures_dir / "README.md"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write("# Polyhegel Test Fixtures: The Great Hotdog Reconciliation\n\n")
        f.write(
            "This directory contains pre-generated strategic simulation results focused on resolving the hotdog-sandwich classification conflict.\n\n"
        )
        f.write("## Leader-Follower Architecture\n\n")
        f.write("These fixtures follow the LLM-As-Hierarchical-Policy pattern:\n")
        f.write("- **Leader Agent**: Identifies high-level strategic themes (this fixture)\n")
        f.write("- **Follower Agents**: Develop specific implementation strategies (future work)\n\n")
        f.write("## Available Fixtures\n\n")
        f.write("### Main Hotdog Reconciliation Simulation\n")
        f.write("- `hotdog_reconciliation_simulation.json` - Complete simulation results (JSON)\n")
        f.write("- `hotdog_reconciliation_trunk.json` - Trunk strategy only (JSON)\n")
        f.write("- `hotdog_reconciliation_report.md` - Full report with QA formatting (Markdown)\n\n")
        f.write("### Test Utilities\n")
        f.write("- `minimal_hotdog_test.json` - Lightweight fixture for unit tests\n\n")
        f.write("## Strategic Challenge Overview\n\n")
        f.write(
            "The hotdog classification conflict represents a perfect test case for strategic consensus-building because it:\n"
        )
        f.write("- Contains real stakeholder disagreement (structural vs. cultural perspectives)\n")
        f.write("- Requires taxonomic authority and governance frameworks\n")
        f.write("- Involves multi-stakeholder negotiation and compromise\n")
        f.write("- Tests conflict resolution without political sensitivity\n")
        f.write("- Demonstrates principles applicable to other belief system conflicts\n\n")
        f.write("## Usage\n\n")
        f.write("Load fixtures in tests to avoid expensive LLM calls:\n\n")
        f.write("```python\n")
        f.write("import json\n")
        f.write("from pathlib import Path\n\n")
        f.write("# Load full simulation\n")
        f.write("fixture_path = Path(__file__).parent / 'fixtures' / 'hotdog_reconciliation_simulation.json'\n")
        f.write("with open(fixture_path) as f:\n")
        f.write("    hotdog_results = json.load(f)\n\n")
        f.write("# Load minimal fixture for fast tests\n")
        f.write("minimal_path = Path(__file__).parent / 'fixtures' / 'minimal_hotdog_test.json'\n")
        f.write("with open(minimal_path) as f:\n")
        f.write("    minimal_results = json.load(f)\n")
        f.write("```\n")

    print("📋 Generated fixtures index")
    print(f"\n🌭 All hotdog reconciliation fixtures generated in {fixtures_dir}")
    print("\nFixtures created:")
    for file in sorted(fixtures_dir.glob("*")):
        print(f"  - {file.name}")


if __name__ == "__main__":
    asyncio.run(generate_strategic_fixtures())
