"""Generate the code reference pages and navigation.

This script automatically generates API documentation from the polyhegel source code,
creating markdown files with mkdocstrings references for each module.
"""

from pathlib import Path
import mkdocs_gen_files
import re

nav = mkdocs_gen_files.Nav()

src = Path(__file__).parent.parent
polyhegel_path = src / "polyhegel"

# Configuration for documentation generation
EXCLUDED_MODULES = {"__pycache__", "tests", "__main__.py", ".git", ".pytest_cache"}

# Patterns for modules that should be excluded
EXCLUDED_PATTERNS = [r".*__pycache__.*", r".*\.pyc$", r".*test.*\.py$", r".*_test\.py$"]


def is_public_module(path: Path) -> bool:
    """Determine if a module should be included in documentation.

    Args:
        path: Path to the Python file

    Returns:
        True if the module should be documented, False otherwise
    """
    path_str = str(path)
    parts = path.parts

    # Check excluded patterns
    for pattern in EXCLUDED_PATTERNS:
        if re.match(pattern, path_str):
            return False

    # Exclude private modules (starting with _), but allow __init__.py
    for part in parts:
        if part.startswith("_") and part != "__init__.py":
            return False

    # Exclude specific modules
    if any(excluded in parts for excluded in EXCLUDED_MODULES):
        return False

    return True


def format_module_name(module_path: Path) -> str:
    """Create a more readable module name for navigation.

    Args:
        module_path: Path to the module

    Returns:
        Formatted navigation label
    """
    parts = module_path.parts
    # Remove 'polyhegel' prefix and convert to title case
    formatted_parts = [part.replace("_", " ").title() for part in parts[1:]]
    return " - ".join(formatted_parts)


def get_module_summary(file_path: Path) -> str:
    """Extract a brief summary from the module's docstring.

    Args:
        file_path: Path to the Python file

    Returns:
        Brief summary of the module
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for module docstring
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            # Get first line as summary
            first_line = docstring.split("\n")[0].strip()
            if first_line:
                return first_line

        return "Module documentation"
    except Exception:
        return "Module documentation"


def count_classes_and_functions(file_path: Path) -> tuple[int, int]:
    """Count classes and functions in a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        Tuple of (class_count, function_count)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        class_count = len(re.findall(r"^class\s+\w+", content, re.MULTILINE))
        func_count = len(re.findall(r"^def\s+\w+", content, re.MULTILINE))

        return class_count, func_count
    except Exception:
        return 0, 0


# Generate reference pages for Python modules
print("🔨 Generating API reference documentation...")

total_modules = 0
total_classes = 0
total_functions = 0

for path in sorted(polyhegel_path.rglob("*.py")):
    if not is_public_module(path):
        continue

    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    # Handle __init__ files
    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    # Create a readable navigation label
    nav_label = format_module_name(module_path)
    nav[parts] = doc_path.as_posix()

    # Get module information
    module_summary = get_module_summary(path)
    class_count, func_count = count_classes_and_functions(path)

    total_modules += 1
    total_classes += class_count
    total_functions += func_count

    # Generate documentation for the module
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"# {nav_label}\n\n")

        # Add module summary if available
        if module_summary != "Module documentation":
            fd.write(f"{module_summary}\n\n")

        # Add quick stats
        if class_count > 0 or func_count > 0:
            fd.write("## Overview\n\n")
            if class_count > 0:
                fd.write(f"**Classes:** {class_count}")
                if func_count > 0:
                    fd.write(f" | **Functions:** {func_count}")
                fd.write("\n\n")
            elif func_count > 0:
                fd.write(f"**Functions:** {func_count}\n\n")

        # Add the main documentation reference
        fd.write("## Reference\n\n")
        fd.write(f"::: {ident}\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

print(f"✅ Generated documentation for {total_modules} modules ({total_classes} classes, {total_functions} functions)")

# Create an index page for the API Reference
with mkdocs_gen_files.open("reference/index.md", "w") as index_file:
    index_file.write(
        f"""# API Reference

This section provides comprehensive documentation for all public modules in the Polyhegel project.

## API Overview

**{total_modules}** modules documented with **{total_classes}** classes and **{total_functions}** functions.

## Quick Navigation

- [Core Modules](polyhegel/index.md)

## Documentation Structure

Each module's documentation includes:
- Module overview with summary statistics
- Class and function signatures  
- Detailed docstrings with parameter and return value documentation
- Example usage (where available)
- Source code links for easy reference

!!! tip "Docstring Style"
    All documentation follows the Google docstring style for consistency and clarity.

!!! info "Auto-Generated Content"
    This API reference is automatically generated from the source code and updated with each build.

## Contributing to Documentation

Found an issue or want to improve the documentation? 
[Contribute to our GitHub repository](https://github.com/allenday/polyhegel/blob/main/CONTRIBUTING.md)
"""
    )

# Generate the navigation summary
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
