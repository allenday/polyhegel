# Release Management Guide

## Release Process Overview

Polyhegel follows semantic versioning (SemVer) and maintains a structured release process to ensure stability and clear communication of changes.

## Version Numbering

### Semantic Versioning (SemVer)
We use the format `MAJOR.MINOR.PATCH` where:

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backward-compatible functionality
- **PATCH**: Bug fixes, backward-compatible changes

### Version Examples
- `1.0.0` - Initial stable release
- `1.1.0` - New features added (backward compatible)
- `1.1.1` - Bug fixes (backward compatible)
- `2.0.0` - Breaking changes (not backward compatible)

### Pre-release Versions
- `1.2.0-alpha.1` - Alpha release for early testing
- `1.2.0-beta.1` - Beta release for broader testing
- `1.2.0-rc.1` - Release candidate, feature complete

## Release Types

### Major Releases (x.0.0)
**When to Release**:
- Breaking API changes
- Architectural changes requiring migration
- Removal of deprecated features
- Major new functionality that changes core behavior

**Process**:
1. Create release branch from `dev`
2. Update migration documentation
3. Create breaking change documentation
4. Extended testing period (2+ weeks)
5. Community feedback period
6. Release candidate testing

### Minor Releases (x.y.0)
**When to Release**:
- New features and capabilities
- New strategic techniques or domains
- Performance improvements
- New integrations or protocols

**Process**:
1. Feature freeze on `dev` branch
2. Comprehensive testing cycle
3. Documentation updates
4. Beta release for testing
5. Final release

### Patch Releases (x.y.z)
**When to Release**:
- Bug fixes
- Security patches
- Performance improvements
- Documentation corrections

**Process**:
1. Cherry-pick fixes to release branch
2. Focused testing on affected areas
3. Quick release cycle (same day to 1 week)

## Release Workflow

### 1. Pre-Release Planning

#### Release Planning Meeting
- Review upcoming features and fixes
- Assign version number based on changes
- Set release timeline and milestones
- Identify release manager

#### Feature Freeze
```bash
# Create release branch
git checkout dev
git pull origin dev
git checkout -b release/v1.2.0

# Update version in relevant files
# - pyproject.toml
# - polyhegel/__init__.py
# - docs/conf.py
```

### 2. Release Branch Preparation

#### Version Updates
Update version numbers in all relevant files:

```python
# polyhegel/__init__.py
__version__ = "1.2.0"

# pyproject.toml
[tool.poetry]
version = "1.2.0"

# docs/conf.py
version = "1.2.0"
release = "1.2.0"
```

#### Changelog Generation
```bash
# Generate changelog from commit messages
git log --oneline --no-merges v1.1.0..HEAD > CHANGELOG_draft.md

# Or use automated tools
conventional-changelog -p angular -i CHANGELOG.md -s
```

#### Documentation Updates
- Update API documentation
- Refresh getting started guides
- Update configuration examples
- Verify all links and references

### 3. Testing and Quality Assurance

#### Automated Testing
```bash
# Run full test suite
make test-all

# Run performance benchmarks
make benchmark

# Run security scans
make security-scan

# Check documentation build
make docs
```

#### Manual Testing Checklist
- [ ] Core strategy generation workflows
- [ ] A2A agent communication
- [ ] Refinement engine functionality
- [ ] Tournament selection system
- [ ] Telemetry and monitoring
- [ ] Error handling and recovery
- [ ] Memory usage and performance
- [ ] Integration with external services

#### Compatibility Testing
- [ ] Python 3.8+ compatibility
- [ ] Different AI model providers
- [ ] Various deployment environments
- [ ] Backward compatibility verification

### 4. Release Candidate Process

#### Create Release Candidate
```bash
# Tag release candidate
git tag -a v1.2.0-rc.1 -m "Release candidate 1.2.0-rc.1"
git push origin v1.2.0-rc.1

# Build and publish RC to test PyPI
poetry build
poetry publish --repository testpypi
```

#### RC Testing Period
- Deploy to staging environment
- Community testing feedback
- Documentation review
- Performance validation
- Integration testing with dependent projects

#### RC Feedback Integration
```bash
# Apply fixes to release branch
git checkout release/v1.2.0
# ... apply fixes ...
git commit -m "fix: address RC feedback"

# Create new RC if needed
git tag -a v1.2.0-rc.2 -m "Release candidate 1.2.0-rc.2"
```

### 5. Final Release

#### Release Preparation
```bash
# Final version update and commit
git checkout release/v1.2.0
# Ensure all version numbers are correct
git commit -m "chore: prepare for v1.2.0 release"

# Create release tag
git tag -a v1.2.0 -m "Release v1.2.0

## New Features
- Strategic technique extensibility framework
- Enhanced A2A agent coordination
- Performance improvements in strategy generation

## Bug Fixes  
- Fixed memory leak in refinement engine
- Resolved timeout issues in tournament selection

## Breaking Changes
None

## Migration Guide
No migration required from v1.1.x"

# Push tag
git push origin v1.2.0
```

#### Build and Publish
```bash
# Build distribution packages
poetry build

# Publish to PyPI
poetry publish

# Verify publication
pip install polyhegel==1.2.0
```

#### Merge Back to Main Branches
```bash
# Merge to main
git checkout main
git merge release/v1.2.0
git push origin main

# Merge to dev  
git checkout dev
git merge release/v1.2.0
git push origin dev

# Clean up release branch
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

## Release Documentation

### Changelog Format
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-01-15

### Added
- New strategic technique extensibility framework
- Enhanced tournament selection algorithms
- Memory usage optimization in strategy generation
- Support for custom evaluation criteria

### Changed
- Improved error messages in A2A client
- Updated default timeout values for better reliability
- Enhanced telemetry data collection

### Fixed
- Memory leak in recursive refinement engine
- Race condition in concurrent strategy generation
- Timeout handling in A2A agent communication

### Deprecated
- Old configuration format (will be removed in v2.0.0)
- Legacy strategy evaluation methods

### Security
- Updated dependencies to address security vulnerabilities
- Enhanced input validation in strategy generation

## [1.1.1] - 2024-01-02

### Fixed
- Critical bug in strategy chain serialization
- Performance regression in temperature sampling
```

### Migration Guides
For breaking changes, provide comprehensive migration documentation:

```markdown
# Migration Guide: v1.x to v2.0

## Overview
Version 2.0 introduces significant improvements to the strategic technique system
and A2A agent architecture. This guide helps you migrate existing code.

## Breaking Changes

### 1. Strategic Technique API Changes

#### Before (v1.x)
```python
from polyhegel.techniques import ResourceTechnique

technique = ResourceTechnique()
result = technique.apply(strategy, context)
```

#### After (v2.0)
```python
from polyhegel.strategic_techniques import get_technique, StrategyDomain

technique = get_technique("resource_optimization", StrategyDomain.RESOURCE_ACQUISITION)
result = await technique.generate_strategy(context)
```

### 2. Configuration Changes

#### Before (v1.x)
```python
config = {
    "model": "claude-3-haiku",
    "temperature": 0.7,
    "agents": ["leader", "follower"]
}
```

#### After (v2.0)  
```python
from polyhegel.config import PolyhegelConfig

config = PolyhegelConfig(
    model_name="claude-3-haiku-20240307",
    default_temperature=0.7,
    a2a_endpoints=A2AAgentEndpoints.from_env()
)
```

## Automated Migration

We provide a migration script to help automate common changes:

```bash
# Run migration script
python -m polyhegel.migration.v1_to_v2 --input-dir ./my_project --dry-run

# Apply migrations
python -m polyhegel.migration.v1_to_v2 --input-dir ./my_project --apply
```
```

### Release Notes Template
```markdown
# Polyhegel v1.2.0 Release Notes

## 🎉 What's New

### Strategic Technique Framework
We've introduced a powerful new framework for creating and managing strategic techniques. This allows for:
- Custom domain-specific strategy generation
- Pluggable evaluation criteria
- Performance-optimized technique selection

### Enhanced A2A Coordination
Improved agent-to-agent communication with:
- Better error handling and recovery
- Performance optimizations
- Enhanced security features

## 🚀 Improvements

### Performance
- 40% faster strategy generation through optimized model calls
- Reduced memory usage in long-running refinement sessions
- Improved concurrent processing capabilities

### Developer Experience
- Enhanced error messages with actionable guidance
- Improved documentation with more examples
- Better IDE support with comprehensive type hints

## 🐛 Bug Fixes
- Fixed memory leak in refinement engine affecting long sessions
- Resolved timeout issues in tournament selection
- Corrected serialization issues with complex strategy chains

## 📋 Full Changelog
See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🔄 Upgrade Instructions
```bash
pip install --upgrade polyhegel==1.2.0
```

No breaking changes - fully backward compatible with v1.1.x.

## 📚 Documentation
- [Getting Started Guide](https://polyhegel.readthedocs.io/en/latest/getting-started/)
- [API Reference](https://polyhegel.readthedocs.io/en/latest/api/)
- [Migration Guide](https://polyhegel.readthedocs.io/en/latest/migration/)

## 🤝 Contributors
Thanks to all contributors who made this release possible!
```

## Hotfix Process

### Emergency Fixes
For critical issues requiring immediate attention:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/v1.1.2

# Apply minimal fix
# ... make changes ...
git commit -m "fix: critical security vulnerability in strategy validation"

# Update version (patch increment)
# Update CHANGELOG.md
git commit -m "chore: bump version to v1.1.2"

# Tag and release
git tag -a v1.1.2 -m "Hotfix v1.1.2 - Security vulnerability fix"
git push origin v1.1.2

# Merge back to main and dev
git checkout main
git merge hotfix/v1.1.2
git push origin main

git checkout dev  
git merge hotfix/v1.1.2
git push origin dev

# Clean up
git branch -d hotfix/v1.1.2
```

## Release Monitoring

### Post-Release Monitoring
After each release, monitor:

1. **PyPI Download Statistics**
2. **GitHub Issues and Bug Reports**
3. **Community Feedback**
4. **Performance Metrics**
5. **Security Vulnerability Reports**

### Rollback Procedures
If critical issues are discovered:

```bash
# Yanking a release from PyPI (last resort)
poetry publish --repository pypi --yank "Critical security vulnerability"

# Publishing rollback release
git checkout v1.1.1  # Previous stable version
git checkout -b hotfix/v1.1.3-rollback
# Update version to v1.1.3
git tag -a v1.1.3 -m "Rollback release due to critical issue in v1.2.0"
```

## Release Automation

### GitHub Actions Workflow
```yaml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install Poetry
        run: pip install poetry
      - name: Build package
        run: poetry build
      - name: Publish to PyPI
        env:
          POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
        run: poetry publish
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

This structured release process ensures consistent, reliable, and well-documented releases that maintain the project's quality and user trust.