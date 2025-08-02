"""
Git repository parsing tools for pydantic-ai agents in Polyhegel
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

logger = logging.getLogger(__name__)


class GitRepoRequest(BaseModel):
    """Request model for git repository parsing"""

    repo_url: str = Field(description="Git repository URL (GitHub, GitLab, etc.)")
    output_format: str = Field(default="markdown", description="Output format: 'markdown' or 'llm'")
    include_structure: bool = Field(default=True, description="Include directory structure")
    max_file_size: int = Field(default=50000, description="Maximum file size to include (bytes)")


class LocalRepoRequest(BaseModel):
    """Request model for local repository parsing"""

    repo_path: str = Field(description="Path to local git repository")
    output_format: str = Field(default="markdown", description="Output format: 'markdown' or 'llm'")
    include_structure: bool = Field(default=True, description="Include directory structure")
    max_file_size: int = Field(default=50000, description="Maximum file size to include (bytes)")


async def git_repo_to_md_tool(ctx, request: GitRepoRequest) -> str:
    """
    Convert a remote git repository to markdown using git2md tools

    Args:
        ctx: Tool context
        request: Git repository request parameters

    Returns:
        Repository content as markdown string
    """
    try:
        # Use git2md for all formats
        result = await _use_git2md(request.repo_url, request.max_file_size)

        # If LLM format is requested, enhance the output
        if request.output_format == "llm":
            return f"LLM-optimized content for {request.repo_url}:\n\n{result}"

        return result

    except Exception as e:
        logger.error(f"Git repo conversion failed for {request.repo_url}: {e}")
        return f"Git repository conversion failed for {request.repo_url}: {str(e)}"


async def local_repo_to_md_tool(ctx, request: LocalRepoRequest) -> str:
    """
    Convert a local git repository to markdown

    Args:
        ctx: Tool context
        request: Local repository request parameters

    Returns:
        Repository content as markdown string
    """
    try:
        repo_path = Path(request.repo_path)
        if not repo_path.exists():
            return f"Repository path does not exist: {request.repo_path}"

        if not (repo_path / ".git").exists():
            return f"Not a git repository: {request.repo_path}"

        # Use git2md for local repositories
        result = await _use_git2md_local(str(repo_path), request.max_file_size)

        # If LLM format is requested, enhance the output
        if request.output_format == "llm":
            return f"LLM-optimized content for {request.repo_path}:\n\n{result}"

        return result

    except Exception as e:
        logger.error(f"Local repo conversion failed for {request.repo_path}: {e}")
        return f"Local repository conversion failed for {request.repo_path}: {str(e)}"


async def _use_git2md(repo_url: str, max_file_size: int) -> str:
    """Use git2md for remote repositories"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone repository
            clone_cmd = ["git", "clone", "--depth", "1", repo_url, "repo"]
            clone_result = await asyncio.create_subprocess_exec(
                *clone_cmd, cwd=temp_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await clone_result.communicate()
            if clone_result.returncode != 0:
                return f"Failed to clone repository: {repo_url}"

            repo_path = Path(temp_dir) / "repo"
            return await _use_git2md_local(str(repo_path), max_file_size)

    except Exception as e:
        return f"Repository cloning failed for {repo_url}: {str(e)}"


async def _use_git2md_local(repo_path: str, max_file_size: int) -> str:
    """Use git2md for local repositories"""
    try:
        # Use git2md command line tool
        return await _run_git2md_command(repo_path, max_file_size)

    except Exception as e:
        return f"Local repository conversion failed for {repo_path}: {str(e)}"


async def _run_git2md_command(repo_path: str, max_file_size: int) -> str:
    """Run git2md as command line tool"""
    try:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False) as temp_file:
            cmd = ["git2md", repo_path, "-o", temp_file.name]
            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0 and Path(temp_file.name).exists():
                with open(temp_file.name, "r", encoding="utf-8") as f:
                    content = f.read()

                if len(content) > max_file_size:
                    content = content[:max_file_size] + "\n... [Content truncated]"

                Path(temp_file.name).unlink(missing_ok=True)
                return f"Repository content from {repo_path}:\n\n{content}"
            else:
                Path(temp_file.name).unlink(missing_ok=True)
                return f"git2md command failed: {stderr.decode()}"

    except Exception as e:
        return f"Command line git2md failed for {repo_path}: {str(e)}"


# Tool definitions for pydantic-ai
GIT_REPO_TOOL = Tool(git_repo_to_md_tool, description="Convert a remote git repository to markdown")
LOCAL_REPO_TOOL = Tool(local_repo_to_md_tool, description="Convert a local git repository to markdown")

# List of all git tools
GIT_TOOLS = [GIT_REPO_TOOL, LOCAL_REPO_TOOL]
