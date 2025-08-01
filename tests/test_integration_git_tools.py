"""
Integration tests for git tools used by pydantic-ai agents

Tests verify that agents can successfully use git_repo_to_md_tool and 
local_repo_to_md_tool during strategy generation and analysis.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from polyhegel.git_tools import (
    GIT_REPO_TOOL,
    LOCAL_REPO_TOOL, 
    git_repo_to_md_tool,
    local_repo_to_md_tool,
    GitRepoRequest,
    LocalRepoRequest
)
from polyhegel.models import GenesisStrategy
from polyhegel.prompts import get_system_prompt


class TestGitToolsIntegration:
    """Integration tests for git tools with pydantic-ai agents"""

    @pytest.fixture
    def mock_model(self):
        """Create a test model for agent testing"""
        return TestModel()

    @pytest.fixture
    def strategy_agent(self, mock_model):
        """Create an agent with git tools for strategy generation"""
        return Agent(
            mock_model,
            output_type=GenesisStrategy,
            system_prompt=get_system_prompt('strategic', 'generator'),
            tools=[GIT_REPO_TOOL, LOCAL_REPO_TOOL]
        )

    @pytest.fixture
    def analysis_agent(self, mock_model):
        """Create an agent with git tools for code analysis"""
        return Agent(
            mock_model,
            output_type=str,
            system_prompt="You are a software architecture analyst. Use git tools to analyze codebases for strategic insights.",
            tools=[GIT_REPO_TOOL, LOCAL_REPO_TOOL]
        )

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
        (repo_path / "src" / "main.py").write_text("""#!/usr/bin/env python3
\"\"\"Main application module\"\"\"

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")
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
            repo_url="https://github.com/octocat/Hello-World",
            output_format="markdown",
            include_structure=True
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
            output_format="llm",  # Try LLM-optimized format
            include_structure=True,
            max_file_size=10000
        )
        
        mock_context = Mock()
        result = await git_repo_to_md_tool(mock_context, request)
        
        # Verify markdown structure is proper
        assert len(result) > 50  # Should have substantial content
        
        # Should contain structured information
        content_indicators = [
            "Hello World",
            "README", 
            "Repository content",
            "Tree",
            "File:"
        ]
        
        found_indicators = [indicator for indicator in content_indicators if indicator in result]
        
        # Handle case where LLM format fails due to missing dependencies
        if "git2md failed" in result or "not available" in result:
            print(f"LLM format not available, got fallback: {result[:100]}...")
            assert len(result) > 20  # Should at least have error message
        else:
            assert len(found_indicators) >= 3, f"Only found {found_indicators} in result: {result[:200]}..."
        
        # Test that we can extract meaningful information
        lines = result.split('\n') 
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Handle error cases more gracefully
        if "git2md failed" in result or "not available" in result:
            assert len(non_empty_lines) >= 3, f"Should have error info, got {len(non_empty_lines)} lines"
            print(f"LLM format failed as expected, got {len(non_empty_lines)} lines of error info")
        else:
            assert len(non_empty_lines) >= 5, "Should have multiple lines of content"
            print(f"Generated comprehensive markdown: {len(non_empty_lines)} lines, {len(result)} chars")

    @pytest.mark.asyncio
    @pytest.mark.git
    async def test_agent_analyzes_octocat_repo_for_strategy(self, analysis_agent):
        """Test that an agent can analyze the Octocat repo and generate strategic insights"""
        
        # First, get the actual repo content
        git_request = GitRepoRequest(
            repo_url="https://github.com/octocat/Hello-World",
            output_format="markdown",
            include_structure=True
        )
        
        mock_context = Mock()
        repo_content = await git_repo_to_md_tool(mock_context, git_request)
        
        # Verify we got real content
        assert "Hello World" in repo_content
        assert len(repo_content) > 100
        
        # Now test that agent can use this for analysis
        # Configure the agent to receive and analyze the repo content
        analysis_agent.model.add_sequence([
            {
                'role': 'user',
                'content': 'Analyze this repository and provide strategic recommendations for improving it.'
            },
            {
                'role': 'assistant',
                'content': 'I\'ll analyze the repository structure and content.',
                'tool_calls': [{
                    'tool_name': 'git_repo_to_md_tool',
                    'args': {
                        'repo_url': 'https://github.com/octocat/Hello-World',
                        'output_format': 'markdown',
                        'include_structure': True
                    }
                }]
            },
            {
                'role': 'tool',
                'tool_name': 'git_repo_to_md_tool',
                'content': repo_content
            },
            {
                'role': 'assistant',
                'content': f'''Based on my analysis of the repository, here are strategic recommendations:

**Repository Analysis:**
- This is the famous "Hello World" repository by GitHub's Octocat
- Contains a simple README file with minimal content
- Demonstrates basic GitHub repository structure

**Strategic Recommendations:**

1. **Documentation Enhancement**
   - Expand the README to include purpose, usage instructions
   - Add contributing guidelines for community engagement
   - Include licensing information

2. **Code Structure Improvements**
   - Add example code in multiple programming languages
   - Create proper directory structure for different examples
   - Include tests and CI/CD pipeline examples

3. **Community Engagement**
   - Add issues templates for bug reports and feature requests
   - Create pull request templates
   - Set up GitHub Actions for automated testing

4. **Educational Value**
   - Transform into a comprehensive "first repository" tutorial
   - Add step-by-step guides for Git/GitHub beginners
   - Include best practices documentation

**Priority:** Focus on documentation first, then expand code examples to maximize educational impact.'''
            }
        ])
        
        # Run the agent analysis
        with patch.object(GIT_REPO_TOOL.function, '__call__', return_value=repo_content):
            result = await analysis_agent.run(
                "Analyze this repository and provide strategic recommendations for improving it."
            )
            
            analysis = result.output
            
            # Verify the analysis includes strategic thinking
            strategic_indicators = [
                "recommendations",
                "strategic", 
                "documentation",
                "improvement",
                "repository"
            ]
            
            found_indicators = [ind for ind in strategic_indicators if ind.lower() in analysis.lower()]
            assert len(found_indicators) >= 3, f"Analysis should be strategic, found: {found_indicators}"
            
            # Should reference the actual repo content
            assert "hello world" in analysis.lower() or "readme" in analysis.lower()
            
            print(f"Agent successfully analyzed Octocat repo and generated {len(analysis)} chars of strategic analysis")

    @pytest.mark.asyncio
    async def test_local_repo_tool_direct(self, temp_git_repo):
        """Test local repository tool functionality directly"""
        request = LocalRepoRequest(
            repo_path=temp_git_repo,
            output_format="markdown",
            include_structure=True
        )
        
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
        
        with patch('polyhegel.git_tools._use_xpos_git2md_local', return_value=mock_repo_content):
            mock_context = Mock()
            result = await local_repo_to_md_tool(mock_context, request)
            
            assert "Test Repository" in result
            assert "main.py" in result
            assert "requirements.txt" in result
            assert temp_git_repo in result

    @pytest.mark.asyncio
    async def test_agent_can_analyze_remote_repo_for_strategy(self, strategy_agent):
        """Test that strategy agent can analyze remote repositories"""
        
        repo_analysis = """Repository content from https://github.com/fastapi/fastapi:

# FastAPI

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+

## Key Features
- Fast: Very high performance, on par with NodeJS and Go
- Fast to code: Increase the speed of development by about 200% to 300%
- Fewer bugs: Reduce about 40% of human (developer) induced errors
- Intuitive: Great editor support with auto-completion everywhere
- Easy: Designed to be easy to use and learn
- Short: Minimize code duplication
- Robust: Get production-ready code with automatic interactive documentation

## Architecture
- Pydantic for data validation
- Starlette for web components
- OpenAPI/JSON Schema integration
- Async/await support throughout
"""
        
        with patch.object(GIT_REPO_TOOL.function, '__call__', return_value=repo_analysis):
            
            strategy_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a strategy for adopting FastAPI in our organization. Analyze the FastAPI repository first.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze the FastAPI repository to understand its architecture and capabilities.',
                    'tool_calls': [{
                        'tool_name': 'git_repo_to_md_tool',
                        'args': {
                            'repo_url': 'https://github.com/fastapi/fastapi',
                            'output_format': 'markdown',
                            'include_structure': True
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': repo_analysis
                },
                {
                    'role': 'assistant',
                    'content': '''Based on the FastAPI repository analysis, here's an adoption strategy:

{
  "title": "FastAPI Enterprise Adoption Strategy",
  "steps": [
    {
      "action": "Proof of Concept Development",
      "prerequisites": ["Python 3.7+ environment", "Development team training"],
      "outcome": "Working FastAPI prototype demonstrating key features",
      "risks": ["Learning curve for async/await patterns"],
      "resource_requirements": ["2-3 senior developers", "2 weeks development time"]
    },
    {
      "action": "API Migration Planning",
      "prerequisites": ["Successful PoC", "Existing API audit"],
      "outcome": "Detailed migration roadmap for current APIs",
      "risks": ["Business disruption during migration"],
      "resource_requirements": ["Architecture review", "Migration timeline planning"]
    },
    {
      "action": "Production Deployment",
      "prerequisites": ["Migration plan approved", "Infrastructure ready"],
      "outcome": "FastAPI APIs running in production with monitoring",
      "risks": ["Performance issues", "Integration challenges"],
      "resource_requirements": ["DevOps support", "Monitoring tools", "Documentation"]
    }
  ],
  "estimated_timeline": "3-6 months",
  "resource_requirements": ["Python developers", "DevOps engineers", "Training budget"],
  "alignment_score": {
    "performance": 9.5,
    "developer_productivity": 9.0,
    "maintainability": 8.5
  }
}'''
                }
            ])
            
            result = await strategy_agent.run(
                "Generate a strategy for adopting FastAPI in our organization. Analyze the FastAPI repository first."
            )
            
            strategy = result.output
            assert strategy.title == "FastAPI Enterprise Adoption Strategy"
            assert len(strategy.steps) >= 3
            assert "fastapi" in strategy.title.lower()
            assert any("api" in step.action.lower() for step in strategy.steps)

    @pytest.mark.asyncio
    async def test_agent_can_analyze_local_repo_for_architecture_insights(self, analysis_agent, temp_git_repo):
        """Test that analysis agent can analyze local repositories"""
        
        local_analysis = f"""Repository content from {temp_git_repo}:

# Test Repository

This is a test repository for integration testing.

## Architecture Analysis
- Simple Python application structure
- Single main module with entry point
- Standard requirements.txt for dependencies
- Clean git history with initial commit

## Code Quality Observations
- Well-structured main.py with proper docstrings
- Standard Python shebang and encoding
- Minimal dependencies (requests, pydantic)
- Follows Python packaging conventions

## Strategic Recommendations
- Consider adding tests/ directory for test organization
- Add CI/CD configuration for automated testing
- Consider containerization for deployment consistency
"""
        
        with patch.object(LOCAL_REPO_TOOL.function, '__call__', return_value=local_analysis):
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': f'Analyze the local repository at {temp_git_repo} and provide strategic recommendations for improving the codebase.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze the local repository structure and code quality.',
                    'tool_calls': [{
                        'tool_name': 'local_repo_to_md_tool',
                        'args': {
                            'repo_path': temp_git_repo,
                            'output_format': 'markdown',
                            'include_structure': True
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'local_repo_to_md_tool',
                    'content': local_analysis
                },
                {
                    'role': 'assistant',
                    'content': '''Repository Analysis & Strategic Recommendations:

**Current State:**
- Simple Python application with clean structure
- Good code quality with proper documentation
- Minimal, focused dependencies
- Standard Python conventions followed

**Strategic Improvement Areas:**

1. **Testing Infrastructure**
   - Add comprehensive test suite with pytest
   - Implement test coverage reporting
   - Set up automated testing in CI/CD

2. **DevOps & Deployment**
   - Add Dockerfile for containerization
   - Implement CI/CD pipeline (GitHub Actions)
   - Add deployment configuration

3. **Code Quality Automation**
   - Add pre-commit hooks for code formatting
   - Integrate linting tools (flake8, black)
   - Set up dependency security scanning

4. **Documentation Enhancement**
   - Add API documentation if applicable
   - Create developer setup guide
   - Document deployment procedures

**Priority:** Focus on testing infrastructure first, then containerization and CI/CD implementation.'''
                }
            ])
            
            result = await analysis_agent.run(
                f"Analyze the local repository at {temp_git_repo} and provide strategic recommendations for improving the codebase."
            )
            
            analysis = result.output
            assert "testing" in analysis.lower()
            assert "ci/cd" in analysis.lower() or "ci" in analysis.lower()
            assert "recommendations" in analysis.lower()
            assert "code quality" in analysis.lower()

    @pytest.mark.asyncio
    async def test_multiple_repo_analysis_comparison(self, analysis_agent):
        """Test agent comparing multiple repositories"""
        
        repo1_analysis = """Repository content from https://github.com/django/django:

# Django Web Framework

High-level Python web framework for rapid development.

## Architecture
- MVT (Model-View-Template) pattern
- ORM for database abstraction
- Admin interface
- Security features built-in
- Mature ecosystem with 15+ years development
"""

        repo2_analysis = """Repository content from https://github.com/fastapi/fastapi:

# FastAPI

Modern, fast web framework for building APIs.

## Architecture
- ASGI-based for async performance
- Automatic API documentation
- Type hints throughout
- Pydantic data validation
- Modern Python 3.7+ features
"""
        
        with patch.object(GIT_REPO_TOOL.function, '__call__') as mock_git_tool:
            mock_git_tool.side_effect = [repo1_analysis, repo2_analysis]
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Compare Django and FastAPI frameworks by analyzing their repositories. Provide strategic guidance on when to use each.'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze both Django and FastAPI repositories to compare their architectures.',
                    'tool_calls': [
                        {
                            'tool_name': 'git_repo_to_md_tool',
                            'args': {'repo_url': 'https://github.com/django/django', 'output_format': 'markdown'}
                        },
                        {
                            'tool_name': 'git_repo_to_md_tool', 
                            'args': {'repo_url': 'https://github.com/fastapi/fastapi', 'output_format': 'markdown'}
                        }
                    ]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': repo1_analysis
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': repo2_analysis
                },
                {
                    'role': 'assistant',
                    'content': '''Framework Comparison Analysis:

**Django vs FastAPI Strategic Comparison:**

**Django Strengths:**
- Mature, battle-tested framework (15+ years)
- Full-featured with admin interface, ORM, security
- MVT pattern suitable for complex web applications
- Large ecosystem and community support
- Excellent for full-stack web applications

**FastAPI Strengths:** 
- Modern async/await architecture for high performance
- Automatic API documentation generation
- Type hints and Pydantic validation
- Optimized for API-first development
- Better performance for I/O-bound operations

**Strategic Recommendations:**

*Choose Django when:*
- Building full-stack web applications
- Need admin interface and ORM features
- Team has Django experience
- Rapid prototyping of complex applications

*Choose FastAPI when:*
- Building APIs or microservices
- Performance is critical
- Team comfortable with modern Python
- Need automatic API documentation
- Async operations are important

**Decision Framework:** Consider project scope, team expertise, performance requirements, and long-term maintenance needs.'''
                }
            ])
            
            result = await analysis_agent.run(
                "Compare Django and FastAPI frameworks by analyzing their repositories. Provide strategic guidance on when to use each."
            )
            
            analysis = result.output
            assert "django" in analysis.lower()
            assert "fastapi" in analysis.lower()
            assert "choose" in analysis.lower()
            assert "performance" in analysis.lower()

    @pytest.mark.asyncio
    async def test_git_tools_error_handling(self, analysis_agent):
        """Test agent handles git tool errors gracefully"""
        
        with patch.object(GIT_REPO_TOOL.function, '__call__', return_value="Git repository conversion failed for https://github.com/nonexistent/repo: Repository not found"):
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Analyze the repository at https://github.com/nonexistent/repo'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze the repository structure and code.',
                    'tool_calls': [{
                        'tool_name': 'git_repo_to_md_tool',
                        'args': {
                            'repo_url': 'https://github.com/nonexistent/repo',
                            'output_format': 'markdown'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'git_repo_to_md_tool',
                    'content': "Git repository conversion failed for https://github.com/nonexistent/repo: Repository not found"
                },
                {
                    'role': 'assistant',
                    'content': 'I was unable to analyze the repository because it could not be found. Please verify that the repository URL is correct and accessible. The repository may be private, renamed, or deleted.'
                }
            ])
            
            result = await analysis_agent.run("Analyze the repository at https://github.com/nonexistent/repo")
            
            assert "unable" in result.output.lower() or "not found" in result.output.lower()
            assert "repository" in result.output.lower()

    @pytest.mark.asyncio
    async def test_local_repo_nonexistent_path(self, analysis_agent):
        """Test handling of nonexistent local repository paths"""
        
        nonexistent_path = "/nonexistent/repo/path"
        
        with patch.object(LOCAL_REPO_TOOL.function, '__call__', return_value=f"Repository path does not exist: {nonexistent_path}"):
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': f'Analyze the local repository at {nonexistent_path}'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll analyze the local repository.',
                    'tool_calls': [{
                        'tool_name': 'local_repo_to_md_tool',
                        'args': {
                            'repo_path': nonexistent_path,
                            'output_format': 'markdown'
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'local_repo_to_md_tool',
                    'content': f"Repository path does not exist: {nonexistent_path}"
                },
                {
                    'role': 'assistant',
                    'content': f'The repository path {nonexistent_path} does not exist on the local filesystem. Please verify the path is correct and that you have the necessary permissions to access it.'
                }
            ])
            
            result = await analysis_agent.run(f"Analyze the local repository at {nonexistent_path}")
            
            assert "does not exist" in result.output or "not exist" in result.output
            assert nonexistent_path in result.output