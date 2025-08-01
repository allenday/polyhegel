"""
Web access tools for pydantic-ai agents in Polyhegel
"""

import logging
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

logger = logging.getLogger(__name__)


class WebSearchRequest(BaseModel):
    """Request model for web search"""
    query: str = Field(description="Search query to execute")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class WebFetchRequest(BaseModel):
    """Request model for web fetch"""
    url: str = Field(description="URL to fetch content from")


class WebSearchResult(BaseModel):
    """Result model for web search"""
    title: str
    url: str
    snippet: str
    

class WebFetchResult(BaseModel):
    """Result model for web fetch"""
    url: str
    content: str
    status_code: int
    error: Optional[str] = None


async def web_search_tool(ctx, request: WebSearchRequest) -> str:
    """
    Search the web using DuckDuckGo
    
    Args:
        ctx: Tool context
        request: Search request parameters
        
    Returns:
        Formatted search results as string
    """
    try:
        # Import duckduckgo_search if available
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            logger.warning("duckduckgo_search not available, using mock results")
            return f"Mock search results for: {request.query}\n[Install duckduckgo-search for real web search]"
        
        # Perform search
        with DDGS() as ddgs:
            results = list(ddgs.text(request.query, max_results=request.max_results))
        
        if not results:
            return f"No search results found for: {request.query}"
        
        # Format results
        formatted_results = [f"Search results for: {request.query}\n"]
        for i, result in enumerate(results, 1):
            formatted_results.append(f"{i}. {result.get('title', 'No title')}")
            formatted_results.append(f"   URL: {result.get('href', 'No URL')}")
            formatted_results.append(f"   {result.get('body', 'No snippet')}\n")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Web search failed: {str(e)}"


async def web_fetch_tool(ctx, request: WebFetchRequest) -> str:
    """
    Fetch content from a URL
    
    Args:
        ctx: Tool context
        request: Fetch request parameters
        
    Returns:
        Fetched content as string
    """
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                request.url,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'Polyhegel/1.0 Strategic Simulator'}
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    # Truncate if too long
                    if len(content) > 10000:
                        content = content[:10000] + "\n... [Content truncated]"
                    return f"Content from {request.url}:\n\n{content}"
                else:
                    return f"Failed to fetch {request.url}: HTTP {response.status}"
                    
    except ImportError:
        logger.warning("aiohttp not available, using mock fetch")
        return f"Mock content from {request.url}\n[Install aiohttp for real web fetch]"
    except Exception as e:
        logger.error(f"Web fetch failed for {request.url}: {e}")
        return f"Web fetch failed for {request.url}: {str(e)}"


# Tool definitions for pydantic-ai
WEB_SEARCH_TOOL = Tool(web_search_tool, description="Search the web for information", max_retries=0)
WEB_FETCH_TOOL = Tool(web_fetch_tool, description="Fetch content from a specific URL", max_retries=0)

# List of all web tools
WEB_TOOLS = [WEB_SEARCH_TOOL, WEB_FETCH_TOOL]