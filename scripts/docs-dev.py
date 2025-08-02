#!/usr/bin/env python3
"""
Documentation Development Helper Script

This script provides utilities to improve the documentation development experience:
- Auto-watch and rebuild documentation
- Check for broken links
- Validate documentation structure
- Generate documentation summaries
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Optional
import os
import re

# Script directory and project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SITE_DIR = PROJECT_ROOT / "site"


def run_command(
    cmd: List[str], capture_output: bool = False, cwd: Optional[Path] = None
) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    if cwd is None:
        cwd = PROJECT_ROOT

    print(f"🔧 Running: {' '.join(cmd)}")

    if capture_output:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, cwd=cwd)

    return result


def check_docs_dependencies():
    """Check if required documentation dependencies are installed."""
    print("🔍 Checking documentation dependencies...")

    required_packages = [
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings",
        "mkdocs-gen-files",
        "mkdocs-literate-nav",
        "mkdocs-section-index",
    ]

    missing_packages = []

    for package in required_packages:
        result = run_command([sys.executable, "-c", f"import {package.replace('-', '_')}"], capture_output=True)
        if result.returncode != 0:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -e .[dev]")
        return False

    print("✅ All documentation dependencies are installed")
    return True


def build_docs(mode: str = "default"):
    """Build documentation with different modes."""
    if not check_docs_dependencies():
        return False

    if mode == "fast":
        cmd = [sys.executable, "-m", "mkdocs", "build", "--clean", "--quiet"]
    elif mode == "strict":
        cmd = [sys.executable, "-m", "mkdocs", "build", "--strict", "--verbose"]
    else:
        cmd = [sys.executable, "-m", "mkdocs", "build"]

    result = run_command(cmd)
    return result.returncode == 0


def serve_docs(port: int = 8000, auto_reload: bool = True):
    """Serve documentation locally with optional auto-reload."""
    if not check_docs_dependencies():
        return False

    cmd = [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", f"127.0.0.1:{port}"]

    if not auto_reload:
        cmd.append("--no-livereload")

    print(f"🌐 Starting documentation server at http://127.0.0.1:{port}")
    print("📝 Documentation will auto-reload on changes")
    print("👋 Press Ctrl+C to stop")

    try:
        run_command(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Documentation server stopped")

    return True


def validate_docs_structure():
    """Validate documentation structure and report issues."""
    print("🔍 Validating documentation structure...")

    issues = []

    # Check for required files
    required_files = [
        "docs/index.md",
        "docs/getting-started/installation.md",
        "docs/getting-started/quickstart.md",
        "mkdocs.yml",
    ]

    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists():
            issues.append(f"Missing required file: {file_path}")

    # Check mkdocs.yml structure
    mkdocs_yml = PROJECT_ROOT / "mkdocs.yml"
    if mkdocs_yml.exists():
        with open(mkdocs_yml, "r") as f:
            content = f.read()

        # Check for essential configuration
        if "site_name:" not in content:
            issues.append("mkdocs.yml missing site_name")
        if "nav:" not in content:
            issues.append("mkdocs.yml missing navigation configuration")
        if "theme:" not in content:
            issues.append("mkdocs.yml missing theme configuration")

    # Check for orphaned documentation files
    nav_files = set()
    nav_pattern = r"^\s*-\s*.*:\s*(.+\.md)$"

    if mkdocs_yml.exists():
        with open(mkdocs_yml, "r") as f:
            for line in f:
                match = re.search(nav_pattern, line)
                if match:
                    nav_files.add(match.group(1))

    # Find all markdown files
    all_md_files = set()
    for md_file in DOCS_DIR.rglob("*.md"):
        rel_path = md_file.relative_to(DOCS_DIR)
        all_md_files.add(str(rel_path))

    # Find orphaned files (excluding generated ones)
    orphaned_files = all_md_files - nav_files
    orphaned_files = {f for f in orphaned_files if not f.startswith("reference/")}

    if orphaned_files:
        issues.append(f"Orphaned documentation files (not in nav): {', '.join(sorted(orphaned_files))}")

    # Report results
    if issues:
        print("❌ Documentation structure issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("✅ Documentation structure is valid")
        return True


def check_broken_links():
    """Check for broken internal links in documentation."""
    print("🔗 Checking for broken internal links...")

    broken_links = []

    for md_file in DOCS_DIR.rglob("*.md"):
        if "reference/" in str(md_file):  # Skip generated files
            continue

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(link_pattern, content)

        for link_text, link_url in matches:
            # Skip external links, anchors, mailto links, and generated reference links
            if (
                link_url.startswith(("http", "mailto:", "#", "reference/"))
                or link_url.startswith("../")
                and not link_url.endswith(".md")
            ):
                continue

            # Resolve relative paths
            if link_url.startswith("./"):
                link_url = link_url[2:]

            target_path = md_file.parent / link_url
            if not target_path.exists():
                # Try relative to docs root
                target_path = DOCS_DIR / link_url
                if not target_path.exists():
                    rel_file = md_file.relative_to(DOCS_DIR)
                    broken_links.append(f"{rel_file}: {link_text} -> {link_url}")

    if broken_links:
        print("❌ Broken internal links found:")
        for link in broken_links[:10]:  # Show first 10
            print(f"  • {link}")
        if len(broken_links) > 10:
            print(f"  ... and {len(broken_links) - 10} more")
        return False
    else:
        print("✅ No broken internal links found")
        return True


def generate_docs_summary():
    """Generate a summary of documentation status."""
    print("📊 Generating documentation summary...")

    # Count files by type
    md_files = list(DOCS_DIR.rglob("*.md"))
    non_generated = [f for f in md_files if "reference/" not in str(f)]

    # Count words
    total_words = 0
    for md_file in non_generated:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple word count (excluding code blocks)
                content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
                words = len(content.split())
                total_words += words
        except Exception:
            pass

    print(
        f"""
📈 Documentation Summary:
  • Total documentation files: {len(non_generated)}
  • Generated API files: {len(md_files) - len(non_generated)}
  • Estimated word count: {total_words:,}
  • Documentation directory: {DOCS_DIR}
  • Build output directory: {SITE_DIR}
    """
    )


def clean_docs():
    """Clean documentation build artifacts."""
    print("🧹 Cleaning documentation build artifacts...")

    dirs_to_clean = [SITE_DIR, DOCS_DIR / "reference" / "polyhegel"]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            import shutil

            shutil.rmtree(dir_path)
            print(f"  • Removed {dir_path}")

    print("✅ Documentation artifacts cleaned")


def main():
    """Main entry point for the documentation development script."""
    parser = argparse.ArgumentParser(
        description="Documentation Development Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s serve                    # Serve docs locally
  %(prog)s build --mode=fast       # Fast build
  %(prog)s validate                # Check structure
  %(prog)s check-links             # Find broken links
  %(prog)s summary                 # Show docs stats
  %(prog)s clean                   # Clean build artifacts
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve documentation locally")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to serve on")
    serve_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build documentation")
    build_parser.add_argument("--mode", choices=["default", "fast", "strict"], default="default", help="Build mode")

    # Validate command
    subparsers.add_parser("validate", help="Validate documentation structure")

    # Check links command
    subparsers.add_parser("check-links", help="Check for broken internal links")

    # Summary command
    subparsers.add_parser("summary", help="Generate documentation summary")

    # Clean command
    subparsers.add_parser("clean", help="Clean build artifacts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Change to project root
    os.chdir(PROJECT_ROOT)

    success = True

    if args.command == "serve":
        success = serve_docs(args.port, not args.no_reload)
    elif args.command == "build":
        success = build_docs(args.mode)
    elif args.command == "validate":
        success = validate_docs_structure()
    elif args.command == "check-links":
        success = check_broken_links()
    elif args.command == "summary":
        generate_docs_summary()
    elif args.command == "clean":
        clean_docs()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
