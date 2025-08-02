"""
CLI interface for Polyhegel
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Union

from .simulator import PolyhegelSimulator
from .config import Config
from .models import StrategyChain, GenesisStrategy, StrategyStep

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def read_text_from_file(file_path: Union[str, Path]) -> str:
    """Read text content from various file formats."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Handle different file types
    if file_path.suffix.lower() in [".txt", ".md", ".py", ".js", ".html", ".css", ".json"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Try to read as text
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


async def run_demo(prompt: str, output_format: str):
    """Run a demonstration with mock data"""
    print("🚀 Welcome to Polyhegel Demo!")
    print("This demo shows how Polyhegel works without requiring API keys.\n")

    print(f"📋 Strategic Challenge: {prompt}\n")
    print("🔄 Generating mock strategies...")

    # Create mock strategies
    mock_strategies = create_mock_strategies(prompt)

    print(f"✅ Generated {len(mock_strategies)} strategy options\n")

    if output_format == "friendly":
        display_friendly_demo_results(mock_strategies, prompt)
    else:
        display_json_demo_results(mock_strategies, prompt)

    print("\n🎯 Next Steps:")
    print("1. Set up API keys: export ANTHROPIC_API_KEY=your_key")
    print("2. Run real simulation: polyhegel simulate --output results/ 'your prompt'")
    print("3. Explore Python API: from polyhegel import PolyhegelSimulator")
    print("\n📚 Full documentation: https://allendy.github.io/polyhegel/")


def create_mock_strategies(prompt: str) -> list[StrategyChain]:
    """Create mock strategies for demonstration"""
    strategies = []

    # Strategy 1: Conservative approach
    strategy1 = GenesisStrategy(
        title="Market Research & Validation Approach",
        steps=[
            StrategyStep(
                action="Conduct comprehensive market research",
                prerequisites=["Budget allocated", "Research team assembled"],
                outcome="Clear market understanding and customer validation",
                risks=["Research may reveal unfavorable market conditions"],
            ),
            StrategyStep(
                action="Develop minimum viable product (MVP)",
                prerequisites=["Market research complete", "Technical team ready"],
                outcome="Working prototype ready for testing",
                risks=["MVP may not meet market expectations"],
            ),
            StrategyStep(
                action="Launch limited beta program",
                prerequisites=["MVP completed", "Beta users identified"],
                outcome="Product validated with real users",
                risks=["Limited user feedback may not be representative"],
            ),
        ],
        alignment_score={"resource_acquisition": 3.5, "strategic_security": 4.2, "value_catalysis": 3.8},
        estimated_timeline="6-9 months",
        resource_requirements=["Market research budget", "Technical development team", "Beta user community"],
    )

    # Strategy 2: Aggressive approach
    strategy2 = GenesisStrategy(
        title="Rapid Market Entry Strategy",
        steps=[
            StrategyStep(
                action="Launch with existing product features",
                prerequisites=["Core product ready", "Marketing campaign prepared"],
                outcome="Immediate market presence and early revenue",
                risks=["Product may not be fully optimized"],
            ),
            StrategyStep(
                action="Scale marketing and customer acquisition",
                prerequisites=["Initial launch complete", "Marketing budget available"],
                outcome="Rapid customer growth and market share capture",
                risks=["High customer acquisition costs"],
            ),
            StrategyStep(
                action="Iterate based on market feedback",
                prerequisites=["Customer feedback collected", "Development capacity available"],
                outcome="Product-market fit achieved through rapid iteration",
                risks=["Fast iteration may introduce bugs or instability"],
            ),
        ],
        alignment_score={"resource_acquisition": 4.5, "strategic_security": 2.8, "value_catalysis": 4.7},
        estimated_timeline="3-4 months",
        resource_requirements=["Large marketing budget", "Agile development team", "Customer support infrastructure"],
    )

    # Strategy 3: Partnership approach
    strategy3 = GenesisStrategy(
        title="Strategic Partnership Launch",
        steps=[
            StrategyStep(
                action="Identify and secure key strategic partners",
                prerequisites=["Partnership strategy defined", "Business development team"],
                outcome="Strong partnerships established for market entry",
                risks=["Partner priorities may not align with timeline"],
            ),
            StrategyStep(
                action="Co-develop integrated solutions",
                prerequisites=["Partners onboarded", "Technical integration plan"],
                outcome="Enhanced product value through integration",
                risks=["Technical integration complexity"],
            ),
            StrategyStep(
                action="Launch through partner channels",
                prerequisites=["Integrated solution ready", "Partner sales training complete"],
                outcome="Leveraged distribution through established channels",
                risks=["Dependence on partner performance"],
            ),
        ],
        alignment_score={"resource_acquisition": 4.0, "strategic_security": 3.9, "value_catalysis": 4.3},
        estimated_timeline="4-6 months",
        resource_requirements=[
            "Business development team",
            "Technical integration resources",
            "Partner relationship management",
        ],
    )

    strategies.extend(
        [
            StrategyChain(strategy=strategy1, source_sample=0, temperature=0.3),
            StrategyChain(strategy=strategy2, source_sample=1, temperature=0.9),
            StrategyChain(strategy=strategy3, source_sample=2, temperature=0.7),
        ]
    )

    return strategies


def display_friendly_demo_results(strategies: list[StrategyChain], prompt: str):
    """Display demo results in a user-friendly format"""
    print("📊 Generated Strategy Options:\n")

    for i, chain in enumerate(strategies, 1):
        strategy = chain.strategy
        temp_desc = {0.3: "Conservative", 0.7: "Balanced", 0.9: "Aggressive"}[chain.temperature]

        print(f"🎯 Strategy {i}: {strategy.title}")
        print(f"   Approach: {temp_desc} (temperature: {chain.temperature})")
        print(f"   Timeline: {strategy.estimated_timeline}")
        print(f"   Key Steps: {len(strategy.steps)} execution phases")

        # Show top alignment score
        best_domain = max(strategy.alignment_score.items(), key=lambda x: x[1])
        print(f"   Strongest in: {best_domain[0].replace('_', ' ').title()} ({best_domain[1]:.1f}/5.0)")
        print()

    # Simulate trunk selection
    trunk_strategy = max(strategies, key=lambda s: sum(s.strategy.alignment_score.values()))
    print(f"🏆 Recommended Trunk Strategy: {trunk_strategy.strategy.title}")
    print(f"   Total alignment score: {sum(trunk_strategy.strategy.alignment_score.values()):.1f}")
    print("   Why: Highest overall strategic alignment across all domains")


def display_json_demo_results(strategies: list[StrategyChain], prompt: str):
    """Display demo results in JSON format"""
    results = {
        "prompt": prompt,
        "demo_mode": True,
        "total_strategies": len(strategies),
        "strategies": [],
        "trunk_recommendation": None,
    }

    for chain in strategies:
        strategy_data = {
            "title": chain.strategy.title,
            "temperature": chain.temperature,
            "timeline": chain.strategy.estimated_timeline,
            "alignment_scores": chain.strategy.alignment_score,
            "total_score": sum(chain.strategy.alignment_score.values()),
            "steps_count": len(chain.strategy.steps),
            "resource_requirements": chain.strategy.resource_requirements,
        }
        results["strategies"].append(strategy_data)

    # Find trunk strategy
    trunk_strategy = max(strategies, key=lambda s: sum(s.strategy.alignment_score.values()))
    results["trunk_recommendation"] = {
        "title": trunk_strategy.strategy.title,
        "total_score": sum(trunk_strategy.strategy.alignment_score.values()),
        "reasoning": "Highest overall strategic alignment",
    }

    print(json.dumps(results, indent=2))


async def run_discover(domain: str, output_format: str):
    """Discover available techniques and agents"""
    print("🔍 Discovering Polyhegel Capabilities...")

    # Try to load examples if available
    project_root = Path(__file__).parent.parent
    examples_path = project_root / "examples"

    if examples_path.exists():
        examples_str = str(examples_path)
        current_pythonpath = os.environ.get("PYTHONPATH", "")
        if examples_str not in current_pythonpath:
            new_pythonpath = f"{examples_str}:{current_pythonpath}" if current_pythonpath else examples_str
            os.environ["PYTHONPATH"] = new_pythonpath
            # Also add to sys.path for immediate use
            sys.path.insert(0, examples_str)

    capabilities = {}
    setup_tips = []

    # Discover based on domain selection
    if domain == "all" or domain == "common":
        capabilities["Common Techniques"] = discover_techniques("common")

    if domain == "all" or domain == "strategic":
        techniques = discover_techniques("strategic")
        if techniques:
            capabilities["Strategic Domain"] = techniques
        else:
            setup_tips.append("Strategic domain: Run `./scripts/polyhegel-setup.py with-examples` to enable")

    if domain == "all" or domain == "product":
        techniques = discover_techniques("product")
        if techniques:
            capabilities["Product Domain"] = techniques
        else:
            setup_tips.append("Product domain: Run `./scripts/polyhegel-setup.py with-examples` to enable")

    if domain == "all" or domain == "technical_architecture":
        techniques = discover_techniques("technical_architecture")
        if techniques:
            capabilities["Technical Architecture"] = techniques
        else:
            setup_tips.append("Technical Architecture: Run `./scripts/polyhegel-setup.py with-examples` to enable")

    if output_format == "friendly":
        display_friendly_discovery(capabilities, setup_tips)
    else:
        display_json_discovery(capabilities, setup_tips)


def discover_techniques(domain: str) -> list:
    """Discover techniques for a domain"""
    try:
        if domain == "common":
            from polyhegel.techniques.common.techniques import ALL_TECHNIQUES
        else:
            # Dynamic import for domain-specific techniques
            module_name = f"polyhegel.techniques.{domain}.techniques"
            module = __import__(module_name, fromlist=["ALL_TECHNIQUES"])
            ALL_TECHNIQUES = getattr(module, "ALL_TECHNIQUES")

        return [
            {
                "name": tech.name,
                "type": (
                    getattr(tech, "technique_type", {}).value
                    if hasattr(getattr(tech, "technique_type", {}), "value")
                    else "unknown"
                ),
            }
            for tech in ALL_TECHNIQUES
        ]
    except (ImportError, AttributeError):
        return []


def display_friendly_discovery(capabilities: dict, setup_tips: list):
    """Display discovery results in friendly format"""
    print("\n📋 Available Capabilities:")
    print("=" * 50)

    total_techniques = 0

    for category, techniques in capabilities.items():
        if techniques:
            print(f"\n🎯 {category} ({len(techniques)} techniques):")
            for tech in techniques[:5]:  # Show first 5
                print(f"   • {tech['name']} ({tech['type']})")
            if len(techniques) > 5:
                print(f"   ... and {len(techniques) - 5} more")
            total_techniques += len(techniques)

    print(f"\n📊 Total: {total_techniques} techniques discovered")

    if setup_tips:
        print("\n💡 Expand capabilities:")
        for tip in setup_tips:
            print(f"   {tip}")

    # Usage examples
    if total_techniques > 0:
        print("\n🚀 Usage Examples:")
        if "Common Techniques" in capabilities:
            print("   from polyhegel.techniques.common import ALL_TECHNIQUES")
        if "Strategic Domain" in capabilities:
            print("   from polyhegel.techniques.strategic import ALL_TECHNIQUES")
        if "Product Domain" in capabilities:
            print("   from polyhegel.techniques.product import ALL_TECHNIQUES")

    print("\n📚 Full setup guide: ./scripts/polyhegel-setup.py --help")


def display_json_discovery(capabilities: dict, setup_tips: list):
    """Display discovery results in JSON format"""
    results = {
        "capabilities": capabilities,
        "total_techniques": sum(len(techs) for techs in capabilities.values()),
        "setup_tips": setup_tips,
        "timestamp": str(datetime.now()),
    }
    print(json.dumps(results, indent=2))


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Polyhegel - General-purpose strategy trunk/twig simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simulation with default temperature mode
  python -m polyhegel simulate --output results/
  
  # Use hierarchical mode with A2A distributed agents  
  python -m polyhegel simulate --output results/ --mode hierarchical --user-prompt-file strategic-challenge.md
  
  # Use specific model and temperature settings (temperature mode)
  python -m polyhegel simulate --output results/ --model claude-3-haiku-20240307 --temperatures 0.8:5 0.9:10 1.0:5
  
  # Use custom system and user prompts from files
  python -m polyhegel simulate --output results/ --system-prompt-file system-prompt.md --user-prompt-file user-query.md
  
  # Use tournament selection instead of clustering
  python -m polyhegel simulate --output results/ --selection-method tournament --user-prompt-file strategic-challenge.md
  
  # List available models
  python -m polyhegel models

Environment Variables:
  API Keys (.env file):
  OPENAI_API_KEY=your_openai_key
  ANTHROPIC_API_KEY=your_anthropic_key  
  GOOGLE_API_KEY=your_google_key
  MISTRAL_API_KEY=your_mistral_key
  GROQ_API_KEY=your_groq_key
  XAI_API_KEY=your_xai_key
  
  A2A Agent Endpoints (hierarchical mode):
  POLYHEGEL_LEADER_URL=http://localhost:8001
  POLYHEGEL_FOLLOWER_RESOURCE_URL=http://localhost:8002/resource
  POLYHEGEL_FOLLOWER_SECURITY_URL=http://localhost:8002/security  
  POLYHEGEL_FOLLOWER_VALUE_URL=http://localhost:8002/value
  POLYHEGEL_FOLLOWER_GENERAL_URL=http://localhost:8002/general
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Demo command (no API keys required)
    demo_parser = subparsers.add_parser(
        "demo", help="Run a demonstration with sample strategies (no API keys required)"
    )
    demo_parser.add_argument(
        "prompt",
        nargs="?",
        default="Develop a go-to-market strategy for a new AI product",
        help="Strategic challenge to demonstrate (optional)",
    )
    demo_parser.add_argument(
        "--output-format",
        choices=["friendly", "json"],
        default="friendly",
        help="Output format: friendly summary or full JSON",
    )

    # Simulate command
    simulate_parser = subparsers.add_parser("simulate", help="Run strategy simulation")
    simulate_parser.add_argument(
        "prompt", nargs="?", help="Strategic challenge to analyze (optional, can use --user-prompt-file instead)"
    )
    simulate_parser.add_argument("--output", help="Output directory path (optional, defaults to current directory)")
    simulate_parser.add_argument("--model", default=Config.DEFAULT_MODEL, help="Default model to use")
    simulate_parser.add_argument("--leader-model", help="Model for leader agent (overrides --model)")
    simulate_parser.add_argument("--follower-model", help="Model for follower agents (defaults to leader model)")
    simulate_parser.add_argument("--api-key", help="API key (or set environment variables)")
    simulate_parser.add_argument(
        "--temperatures",
        nargs="+",
        type=str,
        default=[f"{t}:{c}" for t, c in Config.DEFAULT_TEMPERATURE_COUNTS],
        help='Temperature:count pairs (e.g., "0.8:5 0.9:10"). Default: 0.8:5 0.9:10 1.0:10 1.1:5',
    )
    simulate_parser.add_argument(
        "--system-prompt-file", help="Path to file containing system prompt (required for meaningful results)"
    )
    simulate_parser.add_argument("--user-prompt-file", help="Path to file containing user prompt")
    simulate_parser.add_argument(
        "--mode",
        choices=["temperature", "hierarchical"],
        default="temperature",
        help="Generation mode: temperature sampling or hierarchical agents (default: temperature)",
    )
    simulate_parser.add_argument(
        "--agent-endpoints",
        nargs="+",
        help="A2A agent endpoints for hierarchical mode (format: role=url). Example: --agent-endpoints leader=http://localhost:8001 resource=http://localhost:8002",
    )
    simulate_parser.add_argument(
        "--selection-method",
        choices=["clustering", "tournament"],
        default="clustering",
        help="Method for selecting trunk strategy: clustering or tournament (default: clustering)",
    )

    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument(
        "--with-availability", action="store_true", help="Show availability status based on API keys"
    )

    # Discover command (new)
    discover_parser = subparsers.add_parser(
        "discover", help="Discover available techniques and agents across all domains"
    )
    discover_parser.add_argument(
        "--domain",
        choices=["common", "strategic", "product", "technical_architecture", "all"],
        default="all",
        help="Domain to discover (default: all)",
    )
    discover_parser.add_argument(
        "--format", choices=["friendly", "json"], default="friendly", help="Output format (default: friendly)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "demo":
            # Run demo mode with mock data
            asyncio.run(run_demo(args.prompt, args.output_format))
            return

        if args.command == "models":
            # Use model manager directly for listing
            from .model_manager import ModelManager

            model_manager = ModelManager()

            if args.with_availability:
                models_info = model_manager.list_models_with_availability()
                print("Available providers with API key status:")
                for provider, info in models_info.items():
                    status = "✓" if info["available"] else "✗"
                    print(f"\n{provider.upper()} {status}: {info['description']}")
            else:
                models = model_manager.discover_available_models()
                print("Available providers:")
                for provider, description in models.items():
                    print(f"\n{provider.upper()}: {description}")
            return

        if args.command == "discover":
            # Run discovery with improved error handling
            asyncio.run(run_discover(args.domain, args.format))
            return

        if args.command == "simulate":
            # Load system prompt if provided
            system_prompt = None
            if args.system_prompt_file:
                try:
                    system_prompt = read_text_from_file(args.system_prompt_file)
                    logger.info(f"Loaded system prompt from: {args.system_prompt_file}")
                except Exception as e:
                    logger.error(f"Failed to load system prompt file: {str(e)}")
                    sys.exit(1)

            # Determine user prompt (from argument or file)
            user_prompt = None
            if args.prompt:
                # Validate that the prompt is not empty or just whitespace
                if not args.prompt.strip():
                    logger.error("Empty prompt provided")
                    print("❌ Error: Strategic challenge cannot be empty.")
                    print("\n💡 Quick solutions:")
                    print("1. Try the demo first: polyhegel demo")
                    print("2. Provide a meaningful challenge:")
                    print("   polyhegel simulate 'develop a market entry strategy'")
                    print("   polyhegel simulate 'optimize our pricing model'")
                    print("3. Use a prompt file: polyhegel simulate --user-prompt-file challenge.txt")
                    print("\n📚 More examples: https://allendy.github.io/polyhegel/getting-started/quickstart/")
                    sys.exit(1)

                user_prompt = args.prompt.strip()
                logger.info(f"Using prompt from command line: {args.prompt[:50]}...")
            elif args.user_prompt_file:
                try:
                    user_prompt = read_text_from_file(args.user_prompt_file)

                    # Validate that the file content is not empty
                    if not user_prompt.strip():
                        logger.error(f"Prompt file {args.user_prompt_file} is empty")
                        print(f"❌ Error: Prompt file '{args.user_prompt_file}' is empty.")
                        print("\n💡 Quick solutions:")
                        print("1. Try the demo first: polyhegel demo")
                        print("2. Add content to your prompt file with a strategic challenge")
                        print("3. Use inline prompt: polyhegel simulate 'your strategic challenge'")
                        print("\n📚 More examples: https://allendy.github.io/polyhegel/getting-started/quickstart/")
                        sys.exit(1)

                    user_prompt = user_prompt.strip()
                    logger.info(f"Loaded user prompt from: {args.user_prompt_file}")
                except Exception as e:
                    logger.error(f"Failed to load user prompt file: {str(e)}")
                    print(f"❌ Error: Could not read prompt file '{args.user_prompt_file}'")
                    print(f"   Details: {str(e)}")
                    print("\n💡 Quick solutions:")
                    print("1. Try the demo first: polyhegel demo")
                    print("2. Check the file path and permissions")
                    print("3. Use inline prompt: polyhegel simulate 'your strategic challenge'")
                    print("\n📚 More examples: https://allendy.github.io/polyhegel/getting-started/quickstart/")
                    sys.exit(1)
            else:
                logger.error("Must provide either a prompt argument or --user-prompt-file")
                print("❌ Error: No strategic challenge provided.")
                print("\n💡 Quick solutions:")
                print("1. Try the demo first: polyhegel demo")
                print("2. Provide a challenge directly:")
                print("   polyhegel simulate 'develop a market entry strategy'")
                print("   polyhegel simulate 'optimize our pricing model'")
                print("3. Use a prompt file:")
                print("   polyhegel simulate --user-prompt-file challenge.txt")
                print("\n📚 More examples: https://allendy.github.io/polyhegel/getting-started/quickstart/")
                sys.exit(1)

            # Determine models to use
            leader_model = args.leader_model or args.model
            follower_model = args.follower_model or leader_model

            # Initialize simulator with leader model
            try:
                simulator = PolyhegelSimulator(model_name=leader_model, api_key=args.api_key)
            except Exception as e:
                if "API" in str(e) or "key" in str(e).lower():
                    logger.error("API key configuration error")
                    print("\n❌ API Key Error:")
                    print("Polyhegel requires API keys to generate strategies.\n")
                    print("Quick solutions:")
                    print("1. Try the demo first: polyhegel demo")
                    print("2. Set up API keys:")
                    print("   export ANTHROPIC_API_KEY=your_key")
                    print("   export OPENAI_API_KEY=your_key")
                    print("3. Create a .env file with your keys\n")
                    print("📚 Setup guide: https://allendy.github.io/polyhegel/getting-started/installation/")
                    sys.exit(1)
                else:
                    raise e

            # TODO: Implement follower model support in the simulator architecture
            if follower_model != leader_model:
                logger.info(f"Using leader model: {leader_model}, follower model: {follower_model}")
                logger.warning(
                    "Multi-model leader/follower architecture not yet implemented - using leader model for all agents"
                )

            # Parse temperature counts
            temperature_counts = simulator.parse_temperature_counts(args.temperatures)
            logger.info(f"Temperature settings: {temperature_counts}")

            # Handle A2A agent endpoints for hierarchical mode
            if args.mode == "hierarchical" and args.agent_endpoints:
                # Parse agent endpoints from CLI arguments
                endpoint_overrides = {}
                for endpoint_arg in args.agent_endpoints:
                    if "=" in endpoint_arg:
                        role, url = endpoint_arg.split("=", 1)
                        role = role.strip().lower()
                        url = url.strip()

                        # Map role names to environment variable names
                        if role == "leader":
                            endpoint_overrides["POLYHEGEL_LEADER_URL"] = url
                        elif role in ["resource", "follower_resource"]:
                            endpoint_overrides["POLYHEGEL_FOLLOWER_RESOURCE_URL"] = url
                        elif role in ["security", "follower_security"]:
                            endpoint_overrides["POLYHEGEL_FOLLOWER_SECURITY_URL"] = url
                        elif role in ["value", "follower_value"]:
                            endpoint_overrides["POLYHEGEL_FOLLOWER_VALUE_URL"] = url
                        elif role in ["general", "follower_general"]:
                            endpoint_overrides["POLYHEGEL_FOLLOWER_GENERAL_URL"] = url
                        else:
                            logger.warning(f"Unknown agent role '{role}', ignoring endpoint {url}")

                # Apply endpoint overrides to environment
                import os

                for env_var, url in endpoint_overrides.items():
                    os.environ[env_var] = url
                    logger.info(f"Using A2A agent endpoint: {env_var}={url}")

            # Run simulation
            results = asyncio.run(
                simulator.run_simulation(
                    temperature_counts=temperature_counts,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    mode=args.mode,
                    selection_method=args.selection_method,
                )
            )

            # Create output directory
            output_dir = Path(args.output) if args.output else Path(".")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save results
            output_path = output_dir / "simulation_results.json"
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2, cls=NumpyEncoder)

            logger.info(f"Results saved to {output_path}")

            # Save individual strategy files
            if results["trunk"]:
                trunk_file = output_dir / "trunk_strategy.json"
                with open(trunk_file, "w") as f:
                    json.dump(results["trunk"], f, indent=2, cls=NumpyEncoder)

            for i, twig in enumerate(results["twigs"]):
                twig_file = output_dir / f"twig_strategy_{i+1}.json"
                with open(twig_file, "w") as f:
                    json.dump(twig, f, indent=2, cls=NumpyEncoder)

            # Display summary
            print("\nSimulation Complete!")
            print(f"Mode: {args.mode}")
            print(f"Model: {args.model}")
            if args.mode == "hierarchical":
                print(f"Leader model: {leader_model}")
                print(f"Follower model: {follower_model}")
            else:
                print(f"Temperature settings: {temperature_counts}")
            print(f"Total strategies generated: {results['metadata']['total_chains']}")
            print(f"Trunk identified: {results['trunk'] is not None}")
            print(f"Twigs found: {len(results['twigs'])}")
            print(f"\nSummary: {results['summary']}")
            print(f"\nResults saved to: {output_dir}")

    except Exception as e:
        logger.error(f"CLI execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
