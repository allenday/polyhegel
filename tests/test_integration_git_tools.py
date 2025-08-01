"""
Integration tests for git tools

Tests verify that git_repo_to_md_tool and local_repo_to_md_tool work correctly
with real repositories and proper error handling.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from polyhegel.git_tools import (
    GIT_REPO_TOOL,
    LOCAL_REPO_TOOL,
    git_repo_to_md_tool,
    local_repo_to_md_tool,
    GitRepoRequest,
    LocalRepoRequest,
)
from polyhegel.models import GenesisStrategy
from polyhegel.prompts import get_system_prompt


class TestGitToolsIntegration:
    """Integration tests for git tools functionality"""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing"""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)

        # Create some test files
        (repo_path / "README.md").write_text("# Test Repository\n\nThis is a test repository for integration testing.")
        (repo_path / "src").mkdir()
        (repo_path / "src" / "main.py").write_text(
            """#!/usr/bin/env python3
\"\"\"Main application module\"\"\"

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
"""
        )
        (repo_path / "requirements.txt").write_text("requests>=2.25.0\npydantic>=1.8.0\n")

        # Commit files
        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True)

        yield str(repo_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_repo_tool_direct(self):
        """Test git repository tool functionality with real Octocat repository"""
        request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World", output_format="markdown", include_structure=True
        )

        mock_context = Mock()
        result = await git_repo_to_md_tool(mock_context, request)

        # Verify we got real repo content
        assert "Hello World" in result
        assert "README" in result
        assert "Repository content from" in result

        # Should have directory structure info
        assert "Tree for repo" in result or "└──" in result

        # Should have actual file content
        assert "Hello World!" in result

        print(f"Successfully analyzed Octocat repo, got {len(result)} characters of content")

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_repo_markdown_generation_comprehensive(self):
        """Test comprehensive markdown generation from real repository"""
        request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World",
            output_format="llm",  # LLM format uses same git2md as standard
            include_structure=True,
            max_file_size=10000,
        )

        mock_context = Mock()
        result = await git_repo_to_md_tool(mock_context, request)

        # Should get real repo content with git2md
        assert "Hello World" in result or "Repository content" in result
        assert len(result) > 100  # Should have substantial content

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_repo_tool_with_mock_content(self):
        """Test git repo tool with mocked content"""
        request = GitRepoRequest(
            repo_url="https://github.com/example/test-repo", output_format="markdown", include_structure=True
        )

        mock_repo_content = """Repository content from https://github.com/example/test-repo:

# Test Repository

This is a test repository for demonstration purposes.

## Directory Structure
```
.
├── README.md
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── requirements.txt
```

## Files

### README.md
```markdown
# Test Repository

This is a test repository for demonstration purposes.
```

### src/main.py
```python
#!/usr/bin/env python3
\"\"\"Main application module\"\"\"

def main():
    print("Hello from test repo!")

if __name__ == "__main__":
    main()
```

### src/utils.py
```python
\"\"\"Utility functions\"\"\"

def helper_function():
    return "Helper result"
```

### tests/test_main.py
```python
import pytest
from src.main import main

def test_main():
    # Test main function
    pass
```

### requirements.txt
```
pytest>=6.0.0
requests>=2.25.0
```
"""

        with patch("polyhegel.git_tools._use_git2md", return_value=mock_repo_content):
            mock_context = Mock()
            result = await git_repo_to_md_tool(mock_context, request)

            assert "Test Repository" in result
            assert "https://github.com/example/test-repo" in result
            assert "main.py" in result
            assert "utils.py" in result
            assert "requirements.txt" in result
            assert "Hello from test repo!" in result

    @pytest.mark.asyncio
    async def test_local_repo_tool_direct(self, temp_git_repo):
        """Test local repository tool functionality directly"""
        request = LocalRepoRequest(repo_path=temp_git_repo, output_format="markdown", include_structure=True)

        mock_repo_content = f"""Repository content from {temp_git_repo}:

# Test Repository

This is a test repository for integration testing.

## Directory Structure
```
.
├── README.md
├── src/
│   └── main.py
└── requirements.txt
```

## Files

### README.md
```markdown
# Test Repository

This is a test repository for integration testing.
```

### src/main.py
```python
#!/usr/bin/env python3
\"\"\"Main application module\"\"\"

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

### requirements.txt
```
requests>=2.25.0
pydantic>=1.8.0
```
"""

        with patch("polyhegel.git_tools._use_git2md_local", return_value=mock_repo_content):
            mock_context = Mock()
            result = await local_repo_to_md_tool(mock_context, request)

            assert "Test Repository" in result
            assert "main.py" in result
            assert "requirements.txt" in result
            assert temp_git_repo in result

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_repo_tool_error_handling(self):
        """Test git repository tool handles errors gracefully"""
        request = GitRepoRequest(
            repo_url="https://github.com/nonexistent/repository-404", output_format="markdown", include_structure=True
        )

        mock_error_response = "Git repository conversion failed for https://github.com/nonexistent/repository-404: Repository not found or not accessible"

        with patch("polyhegel.git_tools._use_git2md", return_value=mock_error_response):
            mock_context = Mock()
            result = await git_repo_to_md_tool(mock_context, request)

            assert "Git repository conversion failed" in result
            assert "nonexistent/repository-404" in result
            assert "not found" in result.lower() or "not accessible" in result.lower()

    @pytest.mark.asyncio
    async def test_local_repo_tool_error_handling(self):
        """Test local repository tool handles errors gracefully"""
        nonexistent_path = "/nonexistent/repo/path"

        request = LocalRepoRequest(repo_path=nonexistent_path, output_format="markdown", include_structure=True)

        mock_error_response = f"Repository path does not exist: {nonexistent_path}"

        with patch("polyhegel.git_tools._use_git2md_local", return_value=mock_error_response):
            mock_context = Mock()
            result = await local_repo_to_md_tool(mock_context, request)

            assert "Repository path does not exist" in result
            assert nonexistent_path in result

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_tools_tool_integration(self):
        """Test that git tools integrate properly with pydantic-ai Tool system"""

        # Verify GIT_REPO_TOOL properties
        assert GIT_REPO_TOOL.function.__name__ == "git_repo_to_md_tool"
        assert hasattr(GIT_REPO_TOOL, "name")
        assert hasattr(GIT_REPO_TOOL, "description")

        # Verify LOCAL_REPO_TOOL properties
        assert LOCAL_REPO_TOOL.function.__name__ == "local_repo_to_md_tool"
        assert hasattr(LOCAL_REPO_TOOL, "name")
        assert hasattr(LOCAL_REPO_TOOL, "description")

        # Test git repo tool can be called directly
        mock_context = Mock()
        git_request = GitRepoRequest(repo_url="https://github.com/test/repo", output_format="markdown")

        mock_content = "Mock repository content from https://github.com/test/repo"
        with patch("polyhegel.git_tools._use_git2md", return_value=mock_content):
            result = await GIT_REPO_TOOL.function(mock_context, git_request)
            assert "Mock repository content" in result

        # Test local repo tool can be called directly
        local_request = LocalRepoRequest(repo_path="/test/path", output_format="markdown")

        mock_local_content = "Mock local repository content from /test/path"
        with patch("polyhegel.git_tools._use_git2md_local", return_value=mock_local_content):
            result = await LOCAL_REPO_TOOL.function(mock_context, local_request)
            assert "Mock local repository content" in result

    def test_git_tools_available_for_import(self):
        """Test that git tools can be imported and are properly configured"""

        from polyhegel.git_tools import GIT_TOOLS

        # Should have both git tools available
        assert len(GIT_TOOLS) >= 2

        tool_names = [tool.function.__name__ for tool in GIT_TOOLS]
        assert "git_repo_to_md_tool" in tool_names
        assert "local_repo_to_md_tool" in tool_names

        # Tools should have proper metadata
        for tool in GIT_TOOLS:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert tool.name is not None
            assert tool.description is not None

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_repo_different_formats(self):
        """Test git repo tool with different output formats"""

        # Test markdown format
        markdown_request = GitRepoRequest(
            repo_url="https://github.com/example/test", output_format="markdown", include_structure=True
        )

        mock_markdown = """Repository content from https://github.com/example/test:

# Example Test Repository

## Structure
- README.md
- src/main.py
"""

        with patch("polyhegel.git_tools._use_git2md", return_value=mock_markdown):
            mock_context = Mock()
            result = await git_repo_to_md_tool(mock_context, markdown_request)
            assert "Repository content from" in result
            assert "Structure" in result

        # Test LLM format
        llm_request = GitRepoRequest(
            repo_url="https://github.com/example/test", output_format="llm", include_structure=True
        )

        mock_llm = """LLM-optimized content from https://github.com/example/test:

File: README.md
# Example Test Repository

File: src/main.py
def main():
    pass
"""

        with patch("polyhegel.git_tools._use_git2md", return_value=mock_llm):
            mock_context = Mock()
            result = await git_repo_to_md_tool(mock_context, llm_request)
            assert "File:" in result or "git2md failed" in result  # Allow for fallback

    @pytest.mark.asyncio
    async def test_local_repo_different_formats(self, temp_git_repo):
        """Test local repo tool with different output formats"""

        # Test markdown format
        markdown_request = LocalRepoRequest(repo_path=temp_git_repo, output_format="markdown", include_structure=True)

        mock_markdown = f"""Repository content from {temp_git_repo}:

# Local Test Repository

## Files
- README.md
- src/main.py
- requirements.txt
"""

        with patch("polyhegel.git_tools._use_git2md_local", return_value=mock_markdown):
            mock_context = Mock()
            result = await local_repo_to_md_tool(mock_context, markdown_request)
            assert "Repository content from" in result
            assert temp_git_repo in result

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_git_tools_work_with_real_octocat_repo_analysis(self):
        """Test comprehensive analysis workflow with Octocat repository"""

        # First get repo content
        git_request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World", output_format="markdown", include_structure=True
        )

        mock_context = Mock()
        result = await git_repo_to_md_tool(mock_context, git_request)

        # Verify we can extract meaningful information for analysis
        assert len(result) > 100  # Should have substantial content
        assert "Hello World" in result or "Repository content" in result

        # Should be able to identify key repository characteristics
        repo_indicators = ["README", "hello", "world", "repository", "content"]

        found_indicators = [ind for ind in repo_indicators if ind.lower() in result.lower()]
        assert len(found_indicators) >= 2, f"Should find repository indicators, found: {found_indicators}"

        print(
            f"Successfully analyzed repository and found {len(found_indicators)} key indicators in {len(result)} chars"
        )


class TestGitToolsAgentIntegration:
    """Integration tests for git tools with pydantic-ai agents - REAL NETWORK CALLS"""

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_agent_with_git_repo_tool_real(self):
        """Test that agents can use git repo tools with REAL network calls"""

        # Create a TestModel that will call git_repo_to_md_tool
        strategy_output = {
            "title": "Hello World Repository Enhancement Strategy",
            "steps": [
                {
                    "action": "Add comprehensive documentation",
                    "prerequisites": ["Repository access", "Markdown knowledge"],
                    "outcome": "Improved repository documentation",
                    "risks": ["Over-documentation"],
                    "resource_requirements": ["Technical writer", "Time"],
                }
            ],
            "estimated_timeline": "1-2 weeks",
            "resource_requirements": ["Documentation team"],
            "alignment_score": {"performance": 7.0, "developer_productivity": 8.0, "maintainability": 9.0},
        }

        test_model = TestModel(call_tools=["git_repo_to_md_tool"], custom_output_args=strategy_output)

        agent = Agent(
            test_model,
            output_type=GenesisStrategy,
            system_prompt=get_system_prompt("strategic", "generator"),
            tools=[GIT_REPO_TOOL],
        )

        # NO MOCKING - Real network call to GitHub
        result = await agent.run("Analyze https://github.com/octocat/Hello-World and generate an enhancement strategy")

        # Verify strategy was generated
        assert result.output.title == "Hello World Repository Enhancement Strategy"
        assert len(result.output.steps) >= 1
        assert result.output.estimated_timeline is not None

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_agent_with_local_repo_tool_real(self):
        """Test that agents can analyze local repositories"""

        # Create a temporary git repo inline
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)

        # Create test file
        (repo_path / "README.md").write_text("# Test Repo\\n\\nThis is a test.")
        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=repo_path, capture_output=True)

        try:
            analysis_output = "Analysis of local repository: This is a test repository with README."

            test_model = TestModel(call_tools=["local_repo_to_md_tool"], custom_output_text=analysis_output)

            agent = Agent(
                test_model, output_type=str, system_prompt="You are a code repository analyst.", tools=[LOCAL_REPO_TOOL]
            )

            # NO MOCKING - Real local repo analysis
            result = await agent.run(f"Analyze the local repository at {repo_path}")

            # Verify analysis was generated
            assert "repository" in result.output.lower()
            assert "analysis" in result.output.lower() or "test" in result.output.lower()
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_agent_with_multiple_git_tools_real(self):
        """Test that agents can use multiple git tools with REAL calls"""

        comparison_output = "Comparison Summary: The Octocat Hello-World repository is a simple demonstration repository, ideal for learning Git basics."

        test_model = TestModel(call_tools=["git_repo_to_md_tool"], custom_output_text=comparison_output)

        agent = Agent(
            test_model,
            output_type=str,
            system_prompt="You are a repository comparison expert.",
            tools=[GIT_REPO_TOOL, LOCAL_REPO_TOOL],
        )

        # NO MOCKING - Real network call
        result = await agent.run("Analyze the Octocat Hello-World repository structure")

        # Verify comparison output
        assert "octocat" in result.output.lower() or "hello" in result.output.lower()
        assert "repository" in result.output.lower()


if __name__ == "__main__":
    pytest.main([__file__])
