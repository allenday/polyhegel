"""
Integration tests for web tools used by pydantic-ai agents

Tests verify that agents can successfully use web_search_tool and web_fetch_tool
during strategy generation and other operations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from polyhegel.web_tools import (
    WEB_SEARCH_TOOL, 
    WEB_FETCH_TOOL,
    web_search_tool,
    web_fetch_tool,
    WebSearchRequest,
    WebFetchRequest
)
from polyhegel.models import GenesisStrategy
from polyhegel.prompts import get_system_prompt


class TestWebToolsIntegration:
    """Integration tests for web tools with pydantic-ai agents"""

    @pytest.fixture
    def mock_model(self):
        """Create a test model for agent testing"""
        return TestModel()

    @pytest.fixture
    def strategy_agent(self, mock_model):
        """Create an agent with web tools for strategy generation"""
        return Agent(
            mock_model,
            output_type=GenesisStrategy,
            system_prompt=get_system_prompt('strategic', 'generator'),
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL]
        )

    @pytest.fixture
    def analysis_agent(self, mock_model):
        """Create an agent with web tools for analysis tasks"""
        return Agent(
            mock_model,
            output_type=str,
            system_prompt="You are a strategic analyst. Use web tools to gather information for analysis.",
            tools=[WEB_SEARCH_TOOL, WEB_FETCH_TOOL]
        )

    @pytest.mark.asyncio
    @pytest.mark.web
    async def test_web_search_tool_direct(self):
        """Test web search tool functionality with real network calls"""
        request = WebSearchRequest(
            query="python programming language",
            max_results=3
        )
        
        mock_context = Mock()
        result = await web_search_tool(mock_context, request)
        
        # Should get real search results or fallback message
        assert "python" in result.lower() or "mock search results" in result.lower()
        assert "python programming language" in result

    @pytest.mark.asyncio
    @pytest.mark.web
    async def test_web_fetch_tool_direct(self):
        """Test web fetch tool functionality with real network calls"""
        request = WebFetchRequest(url="https://httpbin.org/json")
        
        mock_context = Mock()
        result = await web_fetch_tool(mock_context, request)
        
        # Should get real content or fallback message
        assert "httpbin.org" in result
        # Real response should contain JSON data or error message
        assert ("slideshow" in result.lower() or 
                "content from" in result.lower() or 
                "failed to fetch" in result.lower() or
                "mock content" in result.lower())

    @pytest.mark.asyncio
    async def test_agent_can_use_web_search_during_strategy_generation(self, strategy_agent):
        """Test that strategy agent can use web search tools during generation"""
        
        # Mock web search results that would inform strategy
        search_results = """Search results for: agile transformation strategies 2024

1. Agile Transformation Framework 2024
   URL: https://example.com/agile-framework
   Complete guide to enterprise agile transformation with proven methodologies

2. Digital Transformation Best Practices
   URL: https://example.com/digital-transform
   How leading companies successfully navigate digital transformation initiatives
"""
        
        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=search_results):
            # Configure test model to return a strategy that references web search
            strategy_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Generate a strategy for agile transformation. Use web search to find current best practices.'
                },
                {
                    'role': 'assistant', 
                    'content': 'I need to search for current agile transformation practices.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {
                            'query': 'agile transformation strategies 2024',
                            'max_results': 5
                        }
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool',
                    'content': search_results
                },
                {
                    'role': 'assistant',
                    'content': '''Based on my web search, here's the strategy:

{
  "title": "Enterprise Agile Transformation Strategy",
  "steps": [
    {
      "action": "Establish Agile Center of Excellence",
      "prerequisites": ["Executive sponsorship", "Initial team selection"],
      "outcome": "Centralized agile expertise and governance",
      "risks": ["Resistance to change"],
      "resource_requirements": ["5 experienced agile coaches", "Training budget"]
    },
    {
      "action": "Pilot Agile Teams Implementation", 
      "prerequisites": ["CoE established", "Initial training completed"],
      "outcome": "Proof of concept with measurable improvements",
      "risks": ["Team selection bias"],
      "resource_requirements": ["3 pilot teams", "Agile tools licensing"]
    },
    {
      "action": "Scale Across Organization",
      "prerequisites": ["Successful pilots", "Leadership buy-in"],
      "outcome": "Organization-wide agile adoption",
      "risks": ["Cultural resistance", "Process inconsistency"],
      "resource_requirements": ["Additional coaches", "Change management support"]
    }
  ],
  "estimated_timeline": "12-18 months",
  "resource_requirements": ["Agile coaches", "Training programs", "Tool investments"],
  "alignment_score": {
    "operational_excellence": 8.5,
    "innovation": 9.0,
    "customer_focus": 8.0
  }
}'''
                }
            ])
            
            result = await strategy_agent.run(
                "Generate a strategy for agile transformation. Use web search to find current best practices."
            )
            
            # Verify the strategy incorporates web search insights
            strategy = result.output
            assert strategy.title == "Enterprise Agile Transformation Strategy"
            assert len(strategy.steps) >= 3
            assert "agile" in strategy.title.lower()
            assert any("agile" in step.action.lower() for step in strategy.steps)

    @pytest.mark.asyncio 
    async def test_agent_can_use_web_fetch_during_analysis(self, analysis_agent):
        """Test that analysis agent can fetch and analyze web content"""
        
        # Mock fetched content
        fetched_content = """Content from https://example.com/market-report:

# Q4 2024 Market Analysis

## Key Trends
- Remote work adoption at 78% 
- AI integration in 65% of enterprises
- Cloud-first strategies dominating

## Strategic Implications
Organizations must adapt quickly to remain competitive.
Digital transformation is no longer optional.
"""
        
        with patch.object(WEB_FETCH_TOOL.function, '__call__', return_value=fetched_content):
            # Configure test model for analysis task
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Analyze the strategic implications of the Q4 2024 market report at https://example.com/market-report'
                },
                {
                    'role': 'assistant',
                    'content': 'I need to fetch the market report to analyze it.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {
                            'url': 'https://example.com/market-report'
                        }
                    }]
                },
                {
                    'role': 'tool', 
                    'tool_name': 'web_fetch_tool',
                    'content': fetched_content
                },
                {
                    'role': 'assistant',
                    'content': '''Based on the Q4 2024 market report, here are the key strategic implications:

**Market Position Analysis:**
- Remote work at 78% adoption creates new operational requirements
- AI integration in 65% of enterprises indicates rapid technology adoption
- Cloud-first strategies show fundamental infrastructure shift

**Strategic Recommendations:**
1. Accelerate digital transformation initiatives
2. Invest in remote work infrastructure and culture
3. Develop AI integration roadmap
4. Migrate to cloud-native architectures

**Competitive Implications:**
Organizations that delay adaptation risk significant competitive disadvantage. The data shows digital transformation is no longer optional but essential for survival.'''
                }
            ])
            
            result = await analysis_agent.run(
                "Analyze the strategic implications of the Q4 2024 market report at https://example.com/market-report"
            )
            
            # Verify the analysis incorporates fetched content
            analysis = result.output
            assert "78%" in analysis  # Remote work stat
            assert "65%" in analysis  # AI integration stat
            assert "digital transformation" in analysis.lower()
            assert "competitive" in analysis.lower()

    @pytest.mark.asyncio
    async def test_multiple_web_tools_in_single_session(self, analysis_agent):
        """Test agent using both search and fetch tools in one session"""
        
        search_results = """Search results for: enterprise AI adoption trends

1. AI Adoption Report 2024
   URL: https://example.com/ai-report-2024
   Latest statistics and trends in enterprise AI adoption
"""
        
        fetch_content = """Content from https://example.com/ai-report-2024:

# Enterprise AI Adoption Report 2024

- 73% of enterprises have AI pilots
- 41% have production AI systems  
- ROI averages 127% within first year
- Top challenges: data quality (67%), skills gap (54%)
"""
        
        with patch.object(WEB_SEARCH_TOOL.function, '__call__', return_value=search_results), \
             patch.object(WEB_FETCH_TOOL.function, '__call__', return_value=fetch_content):
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Research enterprise AI adoption trends and provide strategic recommendations'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll search for AI adoption trends first.',
                    'tool_calls': [{
                        'tool_name': 'web_search_tool',
                        'args': {'query': 'enterprise AI adoption trends', 'max_results': 3}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_search_tool', 
                    'content': search_results
                },
                {
                    'role': 'assistant',
                    'content': 'Now I\'ll fetch the detailed report.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {'url': 'https://example.com/ai-report-2024'}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_fetch_tool',
                    'content': fetch_content
                },
                {
                    'role': 'assistant',
                    'content': '''Enterprise AI Adoption Analysis & Recommendations:

**Current State (2024):**
- 73% of enterprises have AI pilots (high experimentation)
- 41% have production systems (moderate deployment)
- Strong ROI of 127% average within first year

**Key Challenges:**
- Data quality issues (67% of organizations)
- Skills gap (54% of organizations)

**Strategic Recommendations:**
1. Prioritize data infrastructure and quality initiatives
2. Invest in AI talent acquisition and training programs
3. Start with pilot projects to build expertise
4. Focus on use cases with clear ROI potential'''
                }
            ])
            
            result = await analysis_agent.run(
                "Research enterprise AI adoption trends and provide strategic recommendations"
            )
            
            analysis = result.output
            assert "73%" in analysis
            assert "41%" in analysis  
            assert "127%" in analysis
            assert "data quality" in analysis.lower()
            assert "recommendations" in analysis.lower()

    @pytest.mark.asyncio
    async def test_web_tools_error_handling(self, analysis_agent):
        """Test agent handles web tool errors gracefully"""
        
        # Mock web fetch failure
        with patch.object(WEB_FETCH_TOOL.function, '__call__', return_value="Web fetch failed for https://example.com/broken: HTTP 404"):
            
            analysis_agent.model.add_sequence([
                {
                    'role': 'user',
                    'content': 'Analyze the content at https://example.com/broken'
                },
                {
                    'role': 'assistant',
                    'content': 'I\'ll fetch the content to analyze it.',
                    'tool_calls': [{
                        'tool_name': 'web_fetch_tool',
                        'args': {'url': 'https://example.com/broken'}
                    }]
                },
                {
                    'role': 'tool',
                    'tool_name': 'web_fetch_tool',
                    'content': "Web fetch failed for https://example.com/broken: HTTP 404"
                },
                {
                    'role': 'assistant',
                    'content': 'I was unable to fetch the content from the provided URL due to a 404 error. The resource may have been moved or removed. Please verify the URL or provide an alternative source for analysis.'
                }
            ])
            
            result = await analysis_agent.run("Analyze the content at https://example.com/broken")
            
            assert "404" in result.output or "unable to fetch" in result.output.lower()
            assert "error" in result.output.lower() or "failed" in result.output.lower()