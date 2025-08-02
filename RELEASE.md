# Release Management Guide

This document describes the release process for Polyhegel.

## Release Types

- **Major Release** (X.0.0): Breaking changes, major new features
- **Minor Release** (X.Y.0): New features, backwards compatible
- **Patch Release** (X.Y.Z): Bug fixes, minor improvements
- **Pre-release** (X.Y.Z-alpha.N): Development versions for testing

## Release Process

### Automated Release (Recommended)

1. **Prepare the release**:
   ```bash
   # Bump version and create commit/tag
   python scripts/release.py bump minor --commit --tag
   
   # Push to trigger release workflow
   git push origin main --tags
   ```

2. **Trigger GitHub Release**:
   - Go to GitHub Actions
   - Select "Release" workflow
   - Click "Run workflow"
   - Enter version (e.g., "1.2.0")
   - Choose if it's a pre-release
   - Click "Run workflow"

3. **Monitor the release**:
   - The workflow will validate, build, test, and create the GitHub release
   - Documentation will be automatically deployed
   - Release assets (wheel, source dist) will be attached

### Manual Release Steps

If you need to create a release manually:

1. **Update version**:
   ```bash
   # Check current version
   python scripts/release.py current
   
   # Update to specific version
   python scripts/release.py bump --version 1.2.0 --commit --tag
   ```

2. **Push changes**:
   ```bash
   git push origin main --tags
   ```

3. **Create GitHub Release**:
   - Go to GitHub Releases page
   - Click "Create a new release"
   - Select the version tag
   - Add release notes
   - Publish release

4. **Build and upload packages**:
   ```bash
   # Build packages
   make build
   
   # Upload to GitHub release manually if needed
   gh release upload v1.2.0 dist/*
   ```

## Release Workflow Details

The automated release workflow (`release.yml`) performs:

### 1. Validation Phase
- ✅ Version format validation
- ✅ Full test suite execution
- ✅ Package build verification
- ✅ Installation testing

### 2. GitHub Release Creation
- ✅ Automatic changelog generation
- ✅ Tag creation
- ✅ Release notes formatting
- ✅ Pre-release flag handling

### 3. Build and Publish Phase
- ✅ Package building (wheel + source dist)
- ✅ Package verification with twine
- ✅ GitHub release asset upload
- 🚧 PyPI publishing (commented out - enable when ready)

### 4. Documentation Deployment
- ✅ Documentation building
- ✅ GitHub Pages deployment
- ✅ Version-specific docs

### 5. Notification
- ✅ Release summary with status of all phases

## Pre-release Testing

For testing releases without affecting production:

```bash
# Create pre-release version
python scripts/release.py bump prerelease --commit --tag

# Push and create pre-release
git push origin main --tags
# Then use GitHub Actions with "Is this a pre-release?" checked
```

## Version Management

The project uses semantic versioning with these files:
- `pyproject.toml` - Main version declaration
- `polyhegel/__init__.py` - Python package version

Both are automatically updated by the release script.

## Release Checklist

Before creating a release:

- [ ] All tests passing on main branch
- [ ] Documentation is up to date
- [ ] CHANGELOG entries added (or will be auto-generated)
- [ ] Version bump is appropriate for changes
- [ ] No known critical bugs
- [ ] Dependencies are up to date and secure

## Emergency Releases

For critical bug fixes:

1. Create hotfix branch from main
2. Apply minimal fix
3. Use patch version bump
4. Fast-track through testing
5. Create patch release immediately

## PyPI Publishing

When ready to publish to PyPI:

1. Uncomment PyPI publishing steps in `release.yml`
2. Add these secrets to GitHub:
   - `PYPI_API_TOKEN` - For production PyPI
   - `TEST_PYPI_API_TOKEN` - For testing

3. Pre-releases go to TestPyPI, full releases to PyPI

## Rollback Process

If a release needs rollback:

1. **Immediate**: Remove from PyPI if published
2. **Create hotfix**: New patch version with fixes
3. **Communication**: Update release notes, notify users
4. **GitHub**: Mark problematic release as draft/pre-release

## Release Notes Template

```markdown
## What's Changed in vX.Y.Z

### 🚀 New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes  
- Fix 1 description
- Fix 2 description

### 📚 Documentation
- Doc improvement 1
- Doc improvement 2

### 🔧 Internal Changes
- Internal change 1
- Internal change 2

**Full Changelog**: https://github.com/allenday/polyhegel/compare/vX.Y.Z-1...vX.Y.Z
```

## Monitoring Releases

After release:
- Monitor GitHub Issues for bug reports
- Check documentation site deployment
- Verify package installation from PyPI
- Monitor download/usage metrics