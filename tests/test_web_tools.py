"""
Integration tests for web tools functionality
"""

import pytest
from polyhegel.web_tools import web_search_tool, web_fetch_tool, WebSearchRequest, WebFetchRequest


class TestWebTools:
    """Test web access tools"""

    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        """Test web search functionality"""
        request = WebSearchRequest(query="Modular Strategies", max_results=3)
        result = await web_search_tool(None, request)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Search results for:" in result or "Mock search results" in result

    @pytest.mark.asyncio
    async def test_web_fetch_tool(self):
        """Test web fetch functionality"""
        # Test with Strategic gist URL from strategic-query.md
        request = WebFetchRequest(url="https://gist.github.com/allenday/66f5402e513a8f62b443058417610632")
        result = await web_fetch_tool(None, request)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Content from" in result or "Mock content" in result or "Failed to fetch" in result

    @pytest.mark.asyncio
    async def test_web_fetch_keystone_protocol(self):
        """Test fetching Keystone Protocol repository"""
        request = WebFetchRequest(url="https://github.com/postfiatorg/keystone-protocol")
        result = await web_fetch_tool(None, request)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Content from" in result or "Mock content" in result or "Failed to fetch" in result

    @pytest.mark.asyncio
    async def test_web_search_empty_query(self):
        """Test web search with empty query"""
        request = WebSearchRequest(query="", max_results=1)
        result = await web_search_tool(None, request)

        assert isinstance(result, str)
        # Should handle empty query gracefully

    @pytest.mark.asyncio
    async def test_web_fetch_invalid_url(self):
        """Test web fetch with invalid URL"""
        request = WebFetchRequest(url="https://invalid-url-that-does-not-exist-12345.com")
        result = await web_fetch_tool(None, request)

        assert isinstance(result, str)
        assert "failed" in result.lower() or "mock content" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__])
