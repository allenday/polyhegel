"""Generate the code reference pages and navigation."""

from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

src = Path(__file__).parent.parent
polyhegel_path = src / "polyhegel"


def is_public_module(path):
    """Determine if a module should be included in documentation."""
    # Exclude private modules, test modules, and __main__
    parts = path.parts
    return not any(part.startswith("_") for part in parts) and "tests" not in parts and parts[-1] != "__main__.py"


def format_module_name(module_path):
    """Create a more readable module name for navigation."""
    parts = module_path.parts
    # Remove 'polyhegel' prefix and convert to title case
    formatted_parts = [part.replace("_", " ").title() for part in parts[1:]]
    return " - ".join(formatted_parts)


# Generate reference pages for Python modules
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

    # Generate documentation for the module
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"# {nav_label}\n\n")
        fd.write(f"::: {ident}\n")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

# Create an index page for the API Reference
with mkdocs_gen_files.open("reference/index.md", "w") as index_file:
    index_file.write(
        """# API Reference

This section provides comprehensive documentation for all public modules in the Polyhegel project.

## Quick Navigation

- [Core Modules](polyhegel/)

## Documentation Structure

Each module's documentation includes:
- Class and function signatures
- Detailed docstrings
- Example usage (where available)

!!! tip "Docstring Style"
    All documentation follows the Google docstring style for consistency and clarity.

## Contributing to Documentation

Found an issue or want to improve the documentation? 
[Contribute to our GitHub repository](https://github.com/allenday/polyhegel/blob/main/CONTRIBUTING.md)
"""
    )

# Generate the navigation summary
with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
