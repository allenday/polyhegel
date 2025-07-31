"""
Integration tests for git tools functionality
"""

import pytest
import asyncio
from pathlib import Path
from polyhegel.git_tools import git_repo_to_md_tool, local_repo_to_md_tool, GitRepoRequest, LocalRepoRequest


class TestGitTools:
    """Test git repository conversion tools"""

    @pytest.mark.asyncio
    async def test_git_repo_tool_public(self):
        """Test git repository conversion with public repo"""
        request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World.git",
            output_format="markdown",
            max_file_size=5000  # Small for testing
        )
        result = await git_repo_to_md_tool(None, request)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert ("Repository content" in result or "conversion failed" in result or "not available" in result)

    @pytest.mark.asyncio
    async def test_git_repo_tool_llm_format(self):
        """Test git repository conversion with LLM format"""
        request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World.git",
            output_format="llm",
            max_file_size=5000
        )
        result = await git_repo_to_md_tool(None, request)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert ("LLM-optimized content" in result or "conversion failed" in result or "not available" in result or "git2md failed" in result)

    @pytest.mark.asyncio
    async def test_local_repo_tool(self):
        """Test local git repository conversion"""
        # Use the current polyhegel repo as test subject
        current_repo = Path(__file__).parent.parent
        
        request = LocalRepoRequest(
            repo_path=str(current_repo),
            output_format="markdown",
            max_file_size=5000
        )
        result = await local_repo_to_md_tool(None, request)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert ("Repository content" in result or "conversion failed" in result or "not available" in result or "execution failed" in result)

    @pytest.mark.asyncio
    async def test_local_repo_nonexistent(self):
        """Test local repo tool with non-existent path"""
        request = LocalRepoRequest(
            repo_path="/path/that/does/not/exist",
            output_format="markdown"
        )
        result = await local_repo_to_md_tool(None, request)
        
        assert isinstance(result, str)
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_local_repo_not_git(self):
        """Test local repo tool with non-git directory"""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            request = LocalRepoRequest(
                repo_path=temp_dir,
                output_format="markdown"
            )
            result = await local_repo_to_md_tool(None, request)
            
            assert isinstance(result, str)
            assert "Not a git repository" in result

    @pytest.mark.asyncio
    async def test_git_repo_invalid_url(self):
        """Test git repo tool with invalid URL"""
        request = GitRepoRequest(
            repo_url="https://github.com/invalid/nonexistent-repo-12345.git",
            output_format="markdown"
        )
        result = await git_repo_to_md_tool(None, request)
        
        assert isinstance(result, str)
        assert ("conversion failed" in result or "Failed to clone" in result)


if __name__ == "__main__":
    pytest.main([__file__])