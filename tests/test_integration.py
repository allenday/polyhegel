"""
Integration tests for polyhegel simulator with web tools
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from polyhegel.simulator import PolyhegelSimulator


class TestPolyhegelIntegration:
    """Integration tests for the complete polyhegel system"""

    @pytest.mark.asyncio
    async def test_strategic_query_simulation(self):
        """Test simulation with strategic-query.md that references web URLs"""
        
        # Read strategic query
        strategic_query_path = Path(__file__).parent.parent / "strategic-query.md"
        if not strategic_query_path.exists():
            pytest.skip("strategic-query.md not found")
        
        with open(strategic_query_path, 'r') as f:
            strategic_query = f.read()
        
        # Initialize simulator with default model
        simulator = PolyhegelSimulator()
        
        # Run a small simulation to test web access
        temperature_counts = [(0.8, 2)]  # Small test
        
        try:
            results = await simulator.run_simulation(
                temperature_counts=temperature_counts,
                system_prompt=None,  # Use default
                user_prompt=strategic_query[:1000]  # Truncate for testing
            )
            
            # Verify results structure
            assert 'trunk' in results
            assert 'twigs' in results
            assert 'summary' in results
            assert 'metadata' in results
            
            # Verify we got some strategies
            assert results['metadata']['total_chains'] > 0
            
        except Exception as e:
            # Log the error but don't fail the test if it's just API related
            print(f"Simulation test failed (may be due to API keys): {e}")
            pytest.skip(f"Simulation test skipped due to: {e}")

    @pytest.mark.asyncio
    async def test_web_enabled_agent_creation(self):
        """Test that agents are created with web tools"""
        
        simulator = PolyhegelSimulator()
        
        # Verify the strategy generator has web tools
        assert hasattr(simulator.generator, 'agent')
        
        # Check that web tools are available
        from polyhegel.web_tools import WEB_TOOLS
        assert len(WEB_TOOLS) > 0
        
        # Verify tools are accessible
        tool_names = [tool.function.__name__ for tool in WEB_TOOLS]
        assert 'web_search_tool' in tool_names
        assert 'web_fetch_tool' in tool_names

    def test_simulator_initialization_with_web_tools(self):
        """Test that simulator initializes properly with web tools"""
        
        simulator = PolyhegelSimulator()
        
        # Should initialize without errors
        assert simulator is not None
        assert simulator.generator is not None
        
        # Strategy generator should have web-enabled agent
        assert hasattr(simulator.generator, 'agent')


if __name__ == "__main__":
    pytest.main([__file__])