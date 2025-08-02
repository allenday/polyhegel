#!/usr/bin/env python3
"""
Release management script for Polyhegel

This script helps manage version bumps and release preparation.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "r") as f:
        content = f.read()

    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def update_version_files(new_version: str) -> None:
    """Update version in all relevant files"""
    files_to_update = [
        ("pyproject.toml", r'version = "[^"]+"', f'version = "{new_version}"'),
        ("polyhegel/__init__.py", r'__version__ = "[^"]+"', f'__version__ = "{new_version}"'),
    ]

    for file_path, pattern, replacement in files_to_update:
        full_path = Path(__file__).parent.parent / file_path

        with open(full_path, "r") as f:
            content = f.read()

        new_content = re.sub(pattern, replacement, content)

        if new_content == content:
            print(f"⚠️  No version found to update in {file_path}")
            continue

        with open(full_path, "w") as f:
            f.write(new_content)

        print(f"✅ Updated {file_path} to version {new_version}")


def parse_version(version: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into components"""
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$"
    match = re.match(pattern, version)

    if not match:
        raise ValueError(f"Invalid version format: {version}. Expected: X.Y.Z or X.Y.Z-suffix")

    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix or ""


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type"""
    major, minor, patch, suffix = parse_version(current)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    elif bump_type == "prerelease":
        if suffix:
            # If already a prerelease, increment the number
            if "." in suffix:
                base, num = suffix.rsplit(".", 1)
                try:
                    new_num = int(num) + 1
                    return f"{major}.{minor}.{patch}-{base}.{new_num}"
                except ValueError:
                    pass
            return f"{major}.{minor}.{patch}-{suffix}.1"
        else:
            return f"{major}.{minor}.{patch}-alpha.1"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def check_git_status() -> bool:
    """Check if git working directory is clean"""
    result = run_command(["git", "status", "--porcelain"], check=False)
    return result.returncode == 0 and not result.stdout.strip()


def create_release_commit(version: str) -> None:
    """Create a release commit"""
    # Add version files
    run_command(["git", "add", "pyproject.toml", "polyhegel/__init__.py"])

    # Create commit
    commit_msg = f"Release v{version}\n\n🤖 Generated with release script"
    run_command(["git", "commit", "-m", commit_msg])

    print(f"✅ Created release commit for v{version}")


def create_git_tag(version: str) -> None:
    """Create a git tag for the release"""
    tag_name = f"v{version}"
    tag_msg = f"Release {tag_name}"

    run_command(["git", "tag", "-a", tag_name, "-m", tag_msg])
    print(f"✅ Created git tag {tag_name}")


def main():
    parser = argparse.ArgumentParser(description="Manage Polyhegel releases")
    parser.add_argument("action", choices=["bump", "tag", "current"], help="Action to perform")
    parser.add_argument(
        "bump_type",
        nargs="?",
        choices=["major", "minor", "patch", "prerelease"],
        help="Type of version bump (required for 'bump' action)",
    )
    parser.add_argument("--version", help="Specific version to set (alternative to bump_type)")
    parser.add_argument("--commit", action="store_true", help="Create a git commit for the version bump")
    parser.add_argument("--tag", action="store_true", help="Create a git tag for the release")
    parser.add_argument("--push", action="store_true", help="Push commits and tags to origin")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    args = parser.parse_args()

    try:
        current_version = get_current_version()

        if args.action == "current":
            print(f"Current version: {current_version}")
            return

        if args.action == "bump":
            if not args.bump_type and not args.version:
                parser.error("bump action requires either bump_type or --version")

            if args.version:
                new_version = args.version
                # Validate version format
                parse_version(new_version)
            else:
                new_version = bump_version(current_version, args.bump_type)

            print(f"Bumping version: {current_version} → {new_version}")

            if args.dry_run:
                print("🔍 Dry run mode - no changes made")
                return

            # Check git status
            if (args.commit or args.tag) and not check_git_status():
                print("❌ Git working directory is not clean. Commit or stash changes first.")
                sys.exit(1)

            # Update version files
            update_version_files(new_version)

            # Create commit if requested
            if args.commit:
                create_release_commit(new_version)

            # Create tag if requested
            if args.tag:
                create_git_tag(new_version)

            # Push if requested
            if args.push:
                run_command(["git", "push"])
                run_command(["git", "push", "--tags"])
                print("✅ Pushed commits and tags to origin")

            print(f"🚀 Version bumped to {new_version}")

            if not args.commit:
                print("💡 Use --commit to create a release commit")
            if not args.tag:
                print("💡 Use --tag to create a git tag")
            if not args.push:
                print("💡 Use --push to push to origin")

        elif args.action == "tag":
            if args.dry_run:
                print(f"🔍 Would create tag v{current_version}")
                return

            create_git_tag(current_version)

            if args.push:
                run_command(["git", "push", "--tags"])
                print("✅ Pushed tags to origin")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
