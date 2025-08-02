#!/usr/bin/env python3
"""
Polyhegel Python API Quickstart Examples

This file shows practical examples of using Polyhegel programmatically.
Run these examples to understand how to integrate Polyhegel into your applications.
"""

import asyncio
import os
from pathlib import Path

# Import Polyhegel components
import sys

# Add the main package to path so we import from the real polyhegel package
sys.path.insert(0, str(Path(__file__).parent.parent))

from polyhegel import StrategyChain, GenesisStrategy, StrategyStep

# PolyhegelSimulator requires extra dependencies, import conditionally
try:
    from polyhegel import PolyhegelSimulator
except ImportError:
    PolyhegelSimulator = None


def check_api_keys():
    """Check if API keys are configured"""
    api_keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    }

    available_keys = {k: v for k, v in api_keys.items() if v}

    if not available_keys:
        print("❌ No API keys found!")
        print("Set at least one API key to run real simulations:")
        print("  export ANTHROPIC_API_KEY=your_key")
        print("  export OPENAI_API_KEY=your_key")
        print("  export GOOGLE_API_KEY=your_key")
        print("\\nOr create a .env file with your keys.")
        return False

    print(f"✅ Found API keys: {list(available_keys.keys())}")
    return True


async def example_1_basic_simulation():
    """Example 1: Basic strategy simulation"""
    print("\\n" + "=" * 60)
    print("📊 EXAMPLE 1: Basic Strategy Simulation")
    print("=" * 60)

    if not check_api_keys():
        print("⏭️  Skipping (requires API keys)")
        return

    if PolyhegelSimulator is None:
        print("⏭️  Skipping (PolyhegelSimulator not available)")
        return

    # Initialize simulator
    simulator = PolyhegelSimulator()

    # Run simulation with default settings
    prompt = "Develop a sustainable growth strategy for a tech startup"

    print(f"🎯 Challenge: {prompt}")
    print("🔄 Generating strategies...")

    try:
        results = await simulator.run_simulation(
            temperature_counts=[(0.7, 3), (0.9, 2)],  # 3 balanced + 2 creative strategies
            user_prompt=prompt,
            mode="temperature",
        )

        print(f"✅ Generated {results['metadata']['total_chains']} strategies")

        if results["trunk"]:
            trunk = results["trunk"]
            print(f"🏆 Best Strategy: {trunk['strategy']['title']}")
            print(f"📅 Timeline: {trunk['strategy']['estimated_timeline']}")
            print(f"📈 Steps: {len(trunk['strategy']['steps'])}")

        print(f"🌿 Alternative strategies: {len(results['twigs'])}")

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        print("💡 Try: polyhegel demo  # for a working example without API keys")


async def example_2_custom_temperatures():
    """Example 2: Custom temperature sampling"""
    print("\\n" + "=" * 60)
    print("🌡️  EXAMPLE 2: Custom Temperature Sampling")
    print("=" * 60)

    if not check_api_keys():
        print("⏭️  Skipping (requires API keys)")
        return

    if PolyhegelSimulator is None:
        print("⏭️  Skipping (PolyhegelSimulator not available)")
        return

    simulator = PolyhegelSimulator()

    # Custom temperature distribution
    temperature_counts = [
        (0.1, 2),  # Very conservative approaches
        (0.5, 3),  # Moderate approaches
        (0.8, 4),  # Creative approaches
        (1.0, 1),  # Highly creative approach
    ]

    prompt = "Launch a new product in a competitive market"

    print(f"🎯 Challenge: {prompt}")
    print("🌡️  Temperature distribution:")
    for temp, count in temperature_counts:
        approach = (
            "Conservative"
            if temp < 0.4
            else "Moderate" if temp < 0.7 else "Creative" if temp < 0.9 else "Highly Creative"
        )
        print(f"   {temp}: {count} strategies ({approach})")

    try:
        results = await simulator.run_simulation(
            temperature_counts=temperature_counts, user_prompt=prompt, mode="temperature"
        )

        print(f"\\n✅ Results: {results['metadata']['total_chains']} total strategies")

        # Analyze by temperature
        if results.get("strategy_chains"):
            temp_analysis = {}
            for chain in results["strategy_chains"]:
                temp = chain.get("temperature", 0)
                temp_range = "Conservative" if temp < 0.4 else "Moderate" if temp < 0.7 else "Creative"
                temp_analysis[temp_range] = temp_analysis.get(temp_range, 0) + 1

            print("📊 Strategy distribution:")
            for range_name, count in temp_analysis.items():
                print(f"   {range_name}: {count} strategies")

    except Exception as e:
        print(f"❌ Simulation failed: {e}")


async def example_3_tournament_selection():
    """Example 3: Tournament-based strategy selection"""
    print("\\n" + "=" * 60)
    print("🏟️  EXAMPLE 3: Tournament Selection")
    print("=" * 60)

    if not check_api_keys():
        print("⏭️  Skipping (requires API keys)")
        return

    if PolyhegelSimulator is None:
        print("⏭️  Skipping (PolyhegelSimulator not available)")
        return

    simulator = PolyhegelSimulator()

    prompt = "Develop a digital transformation strategy"

    print(f"🎯 Challenge: {prompt}")
    print("🏟️  Using tournament selection instead of clustering...")

    try:
        results = await simulator.run_simulation(
            temperature_counts=[(0.6, 2), (0.8, 2), (1.0, 2)],
            user_prompt=prompt,
            mode="temperature",
            selection_method="tournament",  # Use tournament instead of clustering
        )

        print("✅ Tournament complete!")

        if results["trunk"]:
            winner = results["trunk"]
            print(f"🏆 Tournament Winner: {winner['strategy']['title']}")
            print("📊 Selected through competitive evaluation")

        print(f"🥈 Runner-ups: {len(results['twigs'])} alternative strategies")

    except Exception as e:
        print(f"❌ Tournament failed: {e}")


def example_4_mock_strategies():
    """Example 4: Working with strategy objects (no API required)"""
    print("\\n" + "=" * 60)
    print("🔧 EXAMPLE 4: Working with Strategy Objects")
    print("=" * 60)

    print("📦 Creating mock strategies (no API keys required)...")

    # Create a sample strategy
    strategy = GenesisStrategy(
        title="Agile Market Entry Strategy",
        steps=[
            StrategyStep(
                action="Conduct rapid market validation",
                prerequisites=["Market research budget", "User interview access"],
                outcome="Validated product-market fit assumptions",
                risks=["Limited sample size", "Selection bias in user interviews"],
            ),
            StrategyStep(
                action="Build minimum viable product (MVP)",
                prerequisites=["Development team", "Technical requirements"],
                outcome="Testable product prototype",
                risks=["Technical complexity", "Resource constraints"],
            ),
            StrategyStep(
                action="Launch beta program",
                prerequisites=["MVP complete", "Beta user community"],
                outcome="Real-world usage data and feedback",
                risks=["User adoption challenges", "Product quality issues"],
            ),
        ],
        alignment_score={"resource_acquisition": 4.2, "strategic_security": 3.8, "value_catalysis": 4.5},
        estimated_timeline="4-6 months",
        resource_requirements=[
            "Development team of 3-5 engineers",
            "Market research budget ($10-20K)",
            "Beta user community (50-100 users)",
        ],
    )

    # Wrap in a strategy chain
    chain = StrategyChain(strategy=strategy, source_sample=1, temperature=0.7)

    print(f"✅ Created strategy: {strategy.title}")
    print(f"📅 Timeline: {strategy.estimated_timeline}")
    print(f"🎯 Steps: {len(strategy.steps)}")
    print("📊 Alignment scores:")
    for domain, score in strategy.alignment_score.items():
        print(f"   {domain.replace('_', ' ').title()}: {score:.1f}/5.0")

    print("\\n🔍 Strategy Analysis:")
    total_score = sum(strategy.alignment_score.values())
    print(f"   Total alignment: {total_score:.1f}")
    print(f"   Temperature: {chain.temperature} (balanced approach)")
    print(f"   Resource requirements: {len(strategy.resource_requirements)} items")

    # Demonstrate accessing strategy data
    print("\\n📋 Execution Steps:")
    for i, step in enumerate(strategy.steps, 1):
        print(f"   {i}. {step.action}")
        print(f"      → {step.outcome}")
        if step.risks:
            print(f"      ⚠️  Risk: {step.risks[0]}")


async def example_5_a2a_agents():
    """Example 5: A2A Agent coordination (advanced)"""
    print("\\n" + "=" * 60)
    print("🤖 EXAMPLE 5: A2A Agent Coordination")
    print("=" * 60)

    print("🚧 A2A agents require running agent servers.")
    print("To try this mode:")
    print("1. Start agents: make agents-start")
    print("2. Check status: make agents-status")
    print("3. Run simulation: polyhegel simulate --mode hierarchical 'your prompt'")
    print("\\n💡 This uses distributed agents for more sophisticated strategy generation.")


def show_next_steps():
    """Show what users can do next"""
    print("\\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("=" * 60)

    print("\\n1. 🚀 Quick Demo (no setup required):")
    print("   polyhegel demo")
    print("   polyhegel demo 'your strategic challenge'")

    print("\\n2. 🔑 Set up API keys for real simulations:")
    print("   export ANTHROPIC_API_KEY=your_key")
    print("   # or create a .env file")

    print("\\n3. 🖥️  Try the CLI:")
    print("   polyhegel simulate 'develop a pricing strategy'")
    print("   polyhegel simulate --help  # see all options")

    print("\\n4. 🐍 Use in your Python code:")
    print("   from polyhegel import PolyhegelSimulator")
    print("   simulator = PolyhegelSimulator()")
    print("   results = await simulator.run_simulation(...)")

    print("\\n5. 📚 Read the docs:")
    print("   https://allendy.github.io/polyhegel/")

    print("\\n6. 🤖 Try advanced A2A agents:")
    print("   make agents-start  # start agent servers")
    print("   polyhegel simulate --mode hierarchical 'your prompt'")


async def main():
    """Run all examples"""
    print("🚀 Polyhegel Python API Examples")
    print("=" * 60)
    print("These examples show how to use Polyhegel programmatically.")
    print("Some examples require API keys, others work without them.")

    # Run examples
    await example_1_basic_simulation()
    await example_2_custom_temperatures()
    await example_3_tournament_selection()
    example_4_mock_strategies()
    await example_5_a2a_agents()

    show_next_steps()


if __name__ == "__main__":
    asyncio.run(main())
