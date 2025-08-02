#!/usr/bin/env python3
"""
Polyhegel Doctor - Diagnose and Fix Common DX Issues

Automatically detects and provides solutions for common setup and usage problems.

Usage:
  ./scripts/polyhegel-doctor.py [--fix] [--domain DOMAIN]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class HealthCheck:
    """Individual health check with diagnostic and fix capabilities"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "unknown"
        self.message = ""
        self.fix_command = None
        self.fix_description = ""

    def run(self) -> bool:
        """Run the health check. Override in subclasses."""
        raise NotImplementedError

    def fix(self) -> bool:
        """Apply the fix. Override in subclasses."""
        if self.fix_command:
            try:
                subprocess.run(self.fix_command, shell=True, check=True)
                return True
            except subprocess.CalledProcessError:
                return False
        return False


class CoreInstallationCheck(HealthCheck):
    """Check if core polyhegel is installed"""

    def __init__(self):
        super().__init__("Core Installation", "Verify polyhegel core package is installed")
        self.fix_command = "pip install polyhegel"
        self.fix_description = "Install polyhegel core package"

    def run(self) -> bool:
        try:
            import polyhegel

            self.status = "✅ OK"
            self.message = f"Core installed at: {polyhegel.__file__}"
            return True
        except ImportError:
            self.status = "❌ FAIL"
            self.message = "Core polyhegel package not found"
            return False


class PythonPathCheck(HealthCheck):
    """Check if examples directory is in PYTHONPATH"""

    def __init__(self, project_root: Path):
        super().__init__("PYTHONPATH Configuration", "Verify examples directory is accessible")
        self.project_root = project_root
        self.examples_path = project_root / "examples"
        self.fix_description = "Add examples to PYTHONPATH"

    def run(self) -> bool:
        if not self.examples_path.exists():
            self.status = "⚠️  SKIP"
            self.message = f"Examples directory not found: {self.examples_path}"
            return True  # Not an error if we don't have examples

        examples_str = str(self.examples_path)
        current_pythonpath = os.environ.get("PYTHONPATH", "")

        if examples_str in current_pythonpath or examples_str in sys.path:
            self.status = "✅ OK"
            self.message = f"Examples directory accessible: {examples_str}"
            return True
        else:
            self.status = "❌ FAIL"
            self.message = f"Examples directory not in PYTHONPATH: {examples_str}"
            self.fix_command = f'export PYTHONPATH="{examples_str}:$PYTHONPATH"'
            return False

    def fix(self) -> bool:
        """Add examples to current Python path"""
        examples_str = str(self.examples_path)
        if examples_str not in sys.path:
            sys.path.insert(0, examples_str)

        current_pythonpath = os.environ.get("PYTHONPATH", "")
        if examples_str not in current_pythonpath:
            new_pythonpath = f"{examples_str}:{current_pythonpath}" if current_pythonpath else examples_str
            os.environ["PYTHONPATH"] = new_pythonpath

        return True


class DomainImportCheck(HealthCheck):
    """Check if domain-specific techniques can be imported"""

    def __init__(self, domain: str):
        super().__init__(f"{domain.title()} Domain Import", f"Verify {domain} techniques can be imported")
        self.domain = domain
        self.fix_description = f"Setup examples to enable {domain} domain"
        self.fix_command = "./scripts/polyhegel-setup.py with-examples"

    def run(self) -> bool:
        try:
            if self.domain == "common":
                from polyhegel.techniques.common.techniques import ALL_TECHNIQUES
            else:
                module_name = f"polyhegel.techniques.{self.domain}.techniques"
                module = __import__(module_name, fromlist=["ALL_TECHNIQUES"])
                ALL_TECHNIQUES = getattr(module, "ALL_TECHNIQUES")

            technique_count = len(ALL_TECHNIQUES)
            self.status = "✅ OK"
            self.message = f"{technique_count} techniques available"
            return True

        except ImportError as e:
            self.status = "❌ FAIL"
            self.message = f"Import failed: {str(e)}"
            return False


class APIKeyCheck(HealthCheck):
    """Check if required API keys are configured"""

    def __init__(self):
        super().__init__("API Keys Configuration", "Verify AI model API keys are configured")
        self.api_keys = [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "GOOGLE_API_KEY",
            "MISTRAL_API_KEY",
            "GROQ_API_KEY",
            "XAI_API_KEY",
        ]
        self.fix_description = "Configure at least one AI model API key"

    def run(self) -> bool:
        configured_keys = []
        for key in self.api_keys:
            if os.getenv(key):
                configured_keys.append(key)

        if configured_keys:
            self.status = "✅ OK"
            self.message = f"API keys configured: {', '.join(configured_keys)}"
            return True
        else:
            self.status = "⚠️  WARN"
            self.message = "No API keys found. Demo mode only."
            return True  # Not a failure, just a warning


class AgentServerCheck(HealthCheck):
    """Check if A2A agent servers are running"""

    def __init__(self):
        super().__init__("A2A Agent Servers", "Check if A2A agent servers are running")
        self.fix_command = "make agents-start"
        self.fix_description = "Start A2A agent servers"

    def run(self) -> bool:
        # Check common ports for agents
        agent_ports = [8001, 8002, 8003, 8004, 8005, 7001, 7002, 7003, 7004, 7005, 7006]
        running_agents = []

        for port in agent_ports:
            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                if result == 0:
                    running_agents.append(port)
            except Exception:
                pass

        if running_agents:
            self.status = "✅ OK"
            self.message = f"Agents running on ports: {running_agents}"
            return True
        else:
            self.status = "⚠️  INFO"
            self.message = "No A2A agents detected (not required for basic usage)"
            return True  # Not a failure


class PolyhegelDoctor:
    """Main diagnostic and fix orchestrator"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.checks: List[HealthCheck] = []
        self._initialize_checks()

    def _initialize_checks(self):
        """Initialize all health checks"""
        self.checks = [
            CoreInstallationCheck(),
            PythonPathCheck(self.project_root),
            DomainImportCheck("common"),
            DomainImportCheck("strategic"),
            DomainImportCheck("product"),
            DomainImportCheck("technical_architecture"),
            APIKeyCheck(),
            AgentServerCheck(),
        ]

    def run_diagnostics(self, fix_issues: bool = False) -> Tuple[List[HealthCheck], List[HealthCheck]]:
        """Run all diagnostics and optionally fix issues"""
        passed = []
        failed = []

        print("🏥 Polyhegel Health Check")
        print("=" * 50)

        for check in self.checks:
            print(f"\n🔍 {check.name}: {check.description}")

            success = check.run()
            print(f"   {check.status} {check.message}")

            if success:
                passed.append(check)
            else:
                failed.append(check)

                if fix_issues and check.fix_command:
                    print(f"   🔧 Attempting fix: {check.fix_description}")
                    if check.fix():
                        print("   ✅ Fix applied successfully")
                        # Re-run the check
                        if check.run():
                            failed.remove(check)
                            passed.append(check)
                            print(f"   ✅ {check.status} {check.message}")
                    else:
                        print("   ❌ Fix failed")

        return passed, failed

    def generate_report(self, passed: List[HealthCheck], failed: List[HealthCheck]):
        """Generate diagnostic report with recommendations"""
        print("\n📊 Diagnostic Summary")
        print("=" * 50)
        print(f"✅ Passed: {len(passed)}")
        print(f"❌ Failed: {len(failed)}")

        if failed:
            print("\n🔧 Recommended Fixes:")
            for check in failed:
                if check.fix_command:
                    print(f"\n• {check.name}:")
                    print(f"  Issue: {check.message}")
                    print(f"  Fix: {check.fix_description}")
                    print(f"  Command: {check.fix_command}")

        # Provide contextual recommendations
        print("\n💡 Quick Solutions:")

        core_failed = any(isinstance(check, CoreInstallationCheck) for check in failed)
        pythonpath_failed = any(isinstance(check, PythonPathCheck) for check in failed)
        domain_failed = any(isinstance(check, DomainImportCheck) and check.domain != "common" for check in failed)

        if core_failed:
            print("   pip install polyhegel")
        elif pythonpath_failed or domain_failed:
            print("   make dx-setup-examples  # Enable domain extensions")
        elif not failed:
            print("   🎉 All systems operational! Try:")
            print("   polyhegel demo")
            print("   make dx-discover")

        print("\n📚 Resources:")
        print("   ./scripts/polyhegel-setup.py --help")
        print("   make dx-discover")
        print("   GETTING_STARTED.md")


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose and fix common polyhegel DX issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./scripts/polyhegel-doctor.py                    # Run diagnostics
  ./scripts/polyhegel-doctor.py --fix             # Run diagnostics and attempt fixes
  ./scripts/polyhegel-doctor.py --domain strategic # Focus on strategic domain
        """,
    )

    parser.add_argument("--fix", action="store_true", help="Attempt to automatically fix detected issues")
    parser.add_argument(
        "--domain",
        choices=["common", "strategic", "product", "technical_architecture"],
        help="Focus diagnostics on specific domain",
    )

    args = parser.parse_args()

    doctor = PolyhegelDoctor()

    # Filter checks if domain specified
    if args.domain:
        doctor.checks = [
            check for check in doctor.checks if not isinstance(check, DomainImportCheck) or check.domain == args.domain
        ]

    passed, failed = doctor.run_diagnostics(fix_issues=args.fix)
    doctor.generate_report(passed, failed)

    # Exit with error code if there are unfixed failures
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
