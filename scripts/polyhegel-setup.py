#!/usr/bin/env python3
"""
Polyhegel Setup Automation

One-command setup for different usage patterns:
- polyhegel-setup core: Core only (immediate value)
- polyhegel-setup with-examples: Core + examples (extended functionality)
- polyhegel-setup dev: Full development setup
- polyhegel-setup discover: Show available techniques/agents across all domains
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


class PolyhegelSetup:
    """Automates polyhegel setup for different usage patterns"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.examples_path = self.project_root / "examples"

    def setup_core_only(self) -> bool:
        """Setup core polyhegel package only"""
        print("🏗️  Setting up Polyhegel Core (immediate value)...")

        try:
            # Verify core installation
            subprocess.run(
                [sys.executable, "-c", "import polyhegel; print('✓ Core installed')"], check=True, capture_output=True
            )

            print("✅ Core setup complete!")
            print("\n🚀 Quick start:")
            print("   polyhegel demo")
            print("   polyhegel demo 'Launch a fintech product'")
            print("\n📚 Next steps:")
            print("   - Try: polyhegel-setup with-examples (for strategic/product/tech domains)")
            print("   - Try: polyhegel-setup discover (see all available capabilities)")

            return True

        except subprocess.CalledProcessError:
            print("❌ Core installation not found. Run: pip install polyhegel")
            return False

    def setup_with_examples(self) -> bool:
        """Setup core + examples for extended functionality"""
        print("🏗️  Setting up Polyhegel with Examples (extended functionality)...")

        if not self.examples_path.exists():
            print(f"❌ Examples directory not found: {self.examples_path}")
            print("   This setup requires the full polyhegel repository")
            return False

        # Add examples to PYTHONPATH
        examples_str = str(self.examples_path)

        print(f"📁 Adding examples to PYTHONPATH: {examples_str}")

        # Update current session
        current_pythonpath = os.environ.get("PYTHONPATH", "")
        if examples_str not in current_pythonpath:
            new_pythonpath = f"{examples_str}:{current_pythonpath}" if current_pythonpath else examples_str
            os.environ["PYTHONPATH"] = new_pythonpath
            print("✓ Updated current session PYTHONPATH")

        # Test imports
        test_results = self._test_domain_imports()

        if all(test_results.values()):
            print("✅ Examples setup complete!")
            print("\n🚀 Quick start with examples:")
            print(
                "   python -c \"from polyhegel.techniques.strategic import ALL_TECHNIQUES; print(f'Strategic: {len(ALL_TECHNIQUES)} techniques')\""
            )
            print(
                "   python -c \"from polyhegel.techniques.product import ALL_TECHNIQUES; print(f'Product: {len(ALL_TECHNIQUES)} techniques')\""
            )
            print("\n📚 Make permanent:")
            print(f"   echo 'export PYTHONPATH=\"{examples_str}:$PYTHONPATH\"' >> ~/.bashrc")
            print(f"   echo 'export PYTHONPATH=\"{examples_str}:$PYTHONPATH\"' >> ~/.zshrc")

            self._create_activation_script(examples_str)
            return True
        else:
            print("❌ Some domain imports failed:")
            for domain, success in test_results.items():
                status = "✓" if success else "❌"
                print(f"   {status} {domain}")
            return False

    def setup_development(self) -> bool:
        """Setup full development environment"""
        print("🏗️  Setting up Polyhegel Development Environment...")

        try:
            # Install development dependencies
            print("📦 Installing development dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".[dev]"], cwd=self.project_root, check=True)

            # Setup examples PYTHONPATH
            if not self.setup_with_examples():
                return False

            # Create development aliases
            self._create_dev_aliases()

            # Setup pre-commit hooks
            print("🔧 Setting up pre-commit hooks...")
            try:
                subprocess.run(["pre-commit", "install"], cwd=self.project_root, check=True, capture_output=True)
                print("✓ Pre-commit hooks installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Pre-commit not available, skipping hooks")

            print("✅ Development setup complete!")
            print("\n🚀 Development quick start:")
            print("   make test              # Run tests")
            print("   make agents-start      # Start A2A agents")
            print("   make docs-serve        # Local documentation")
            print("   ./scripts/polyhegel-setup.py discover  # Explore capabilities")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Development setup failed: {e}")
            return False

    def discover_capabilities(self) -> bool:
        """Discover and display all available techniques and agents"""
        print("🔍 Discovering Polyhegel Capabilities...")

        # Try to load examples if available
        if self.examples_path.exists():
            examples_str = str(self.examples_path)
            current_pythonpath = os.environ.get("PYTHONPATH", "")
            if examples_str not in current_pythonpath:
                new_pythonpath = f"{examples_str}:{current_pythonpath}" if current_pythonpath else examples_str
                os.environ["PYTHONPATH"] = new_pythonpath

        capabilities = {
            "Core Techniques": self._discover_core_techniques(),
            "Strategic Domain": self._discover_domain_techniques("strategic"),
            "Product Domain": self._discover_domain_techniques("product"),
            "Technical Architecture": self._discover_domain_techniques("technical_architecture"),
        }

        print("\n📋 Available Capabilities:")
        print("=" * 50)

        total_techniques = 0
        for category, techniques in capabilities.items():
            if techniques:
                print(f"\n🎯 {category} ({len(techniques)} techniques):")
                for tech in techniques[:5]:  # Show first 5
                    print(f"   • {tech}")
                if len(techniques) > 5:
                    print(f"   ... and {len(techniques) - 5} more")
                total_techniques += len(techniques)
            else:
                print(f"\n⚠️  {category}: Not available (setup required)")

        print(f"\n📊 Total: {total_techniques} techniques across all domains")

        # Usage recommendations
        if total_techniques > 6:  # Has examples
            print("\n🚀 Usage Patterns:")
            print("   Core Only:     from polyhegel.techniques.common import ALL_TECHNIQUES")
            print("   Strategic:     from polyhegel.techniques.strategic import ALL_TECHNIQUES")
            print("   Product:       from polyhegel.techniques.product import ALL_TECHNIQUES")
        else:
            print("\n💡 Expand capabilities:")
            print("   polyhegel-setup with-examples  # Get strategic/product/tech-arch domains")

        return True

    def _test_domain_imports(self) -> Dict[str, bool]:
        """Test imports for all domains"""
        results = {}

        # Test core
        try:
            import polyhegel.techniques.common.techniques  # noqa: F401

            results["core"] = True
        except ImportError:
            results["core"] = False

        # Test domain extensions
        for domain in ["strategic", "product", "technical_architecture"]:
            try:
                exec(f"from polyhegel.techniques.{domain} import ALL_TECHNIQUES")
                results[domain] = True
            except ImportError:
                results[domain] = False

        return results

    def _discover_core_techniques(self) -> List[str]:
        """Discover core techniques"""
        try:
            from polyhegel.techniques.common.techniques import ALL_TECHNIQUES

            return [tech.name for tech in ALL_TECHNIQUES]
        except ImportError:
            return []

    def _discover_domain_techniques(self, domain: str) -> List[str]:
        """Discover techniques for a specific domain"""
        try:
            module = f"polyhegel.techniques.{domain}.techniques"
            exec(f"from {module} import ALL_TECHNIQUES")
            techniques = locals()["ALL_TECHNIQUES"]
            return [tech.name for tech in techniques]
        except (ImportError, KeyError):
            return []

    def _create_activation_script(self, examples_path: str):
        """Create a polyhegel activation script"""
        script_path = self.project_root / "polyhegel-activate"

        script_content = f"""#!/bin/bash
# Polyhegel Environment Activation
# Source this file to activate polyhegel with examples: source ./polyhegel-activate

export PYTHONPATH="{examples_path}:$PYTHONPATH"
echo "✅ Polyhegel activated with examples"
echo "🔍 Test: python -c 'from polyhegel.techniques.strategic import ALL_TECHNIQUES; print(f\"Strategic techniques: {{len(ALL_TECHNIQUES)}}\")"
"""

        with open(script_path, "w") as f:
            f.write(script_content)

        script_path.chmod(0o755)
        print(f"📄 Created activation script: {script_path}")
        print("   Usage: source ./polyhegel-activate")

    def _create_dev_aliases(self):
        """Create development aliases"""
        aliases_path = self.project_root / "polyhegel-dev-aliases"

        aliases_content = """#!/bin/bash
# Polyhegel Development Aliases
# Source this file: source ./polyhegel-dev-aliases

alias ph-test="make test"
alias ph-test-quick="make test-quick"
alias ph-agents="make agents-start"
alias ph-agents-stop="make agents-stop"
alias ph-docs="make docs-serve"
alias ph-discover="./scripts/polyhegel-setup.py discover"
alias ph-lint="make lint"
alias ph-format="make format"

echo "🔧 Polyhegel development aliases loaded"
echo "   ph-test, ph-agents, ph-docs, ph-discover, etc."
"""

        with open(aliases_path, "w") as f:
            f.write(aliases_content)

        aliases_path.chmod(0o755)
        print(f"📄 Created development aliases: {aliases_path}")
        print("   Usage: source ./polyhegel-dev-aliases")


def main():
    parser = argparse.ArgumentParser(
        description="Polyhegel Setup Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Patterns:
  core           - Core package only (immediate value, no setup)
  with-examples  - Core + examples (strategic/product/tech-arch domains)
  dev            - Full development environment
  discover       - Show all available techniques/agents

Examples:
  ./scripts/polyhegel-setup.py core
  ./scripts/polyhegel-setup.py with-examples  
  ./scripts/polyhegel-setup.py dev
  ./scripts/polyhegel-setup.py discover
        """,
    )

    parser.add_argument("mode", choices=["core", "with-examples", "dev", "discover"], help="Setup mode")

    args = parser.parse_args()

    setup = PolyhegelSetup()

    if args.mode == "core":
        success = setup.setup_core_only()
    elif args.mode == "with-examples":
        success = setup.setup_with_examples()
    elif args.mode == "dev":
        success = setup.setup_development()
    elif args.mode == "discover":
        success = setup.discover_capabilities()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
