"""
Full integration test for polyhegel simulator with strategic query
"""

import pytest
import asyncio
import json
from pathlib import Path
from polyhegel.simulator import PolyhegelSimulator


class TestFullIntegration:
    """Full end-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_strategic_query_full_simulation(self):
        """Test complete simulation with strategic-query.md and cache results"""
        
        # Setup paths
        test_dir = Path(__file__).parent
        project_root = test_dir.parent
        output_dir = test_dir / "out"
        output_dir.mkdir(exist_ok=True)
        
        # Check for required files
        strategic_query_path = project_root / "strategic-query.md"
        keystone_prompt_path = project_root / "keystone-agent-prompt.md"
        
        if not strategic_query_path.exists():
            pytest.skip("strategic-query.md not found")
        if not keystone_prompt_path.exists():
            pytest.skip("keystone-agent-prompt.md not found")
        
        # Read prompts
        with open(strategic_query_path, 'r') as f:
            user_prompt = f.read()
        
        with open(keystone_prompt_path, 'r') as f:
            system_prompt = f.read()
        
        # Initialize simulator with claude-3-haiku (should be available)
        simulator = PolyhegelSimulator(model_name="claude-3-haiku-20240307")
        
        # Generate 3 samples at single temperature for speed
        temperature_counts = [(0.8, 3)]
        
        try:
            print("\n=== Running Strategic Query Simulation ===")
            print(f"Using model: claude-3-haiku-20240307")
            print(f"Temperature settings: {temperature_counts}")
            print(f"System prompt length: {len(system_prompt)} chars")
            print(f"User prompt length: {len(user_prompt)} chars")
            
            results = await simulator.run_simulation(
                temperature_counts=temperature_counts,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Verify results structure
            assert 'trunk' in results
            assert 'twigs' in results
            assert 'summary' in results
            assert 'metadata' in results
            
            # Verify we got strategies
            assert results['metadata']['total_chains'] >= 1
            print(f"Generated {results['metadata']['total_chains']} strategies")
            
            # Save results to cache directory
            cache_file = output_dir / 'strategic_simulation_cache.json'
            with open(cache_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"Results cached to: {cache_file}")
            
            # Save individual components for analysis
            if results['trunk']:
                trunk_file = output_dir / 'trunk_strategy.json'
                with open(trunk_file, 'w') as f:
                    json.dump(results['trunk'], f, indent=2, default=str)
                print(f"Trunk strategy saved to: {trunk_file}")
            
            for i, twig in enumerate(results['twigs']):
                twig_file = output_dir / f'twig_strategy_{i+1}.json'
                with open(twig_file, 'w') as f:
                    json.dump(twig, f, indent=2, default=str)
                print(f"Twig {i+1} saved to: {twig_file}")
            
            # Save summary
            summary_file = output_dir / 'simulation_summary.txt'
            with open(summary_file, 'w') as f:
                f.write("=== POLYHEGEL STRATEGIC SIMULATION SUMMARY ===\n\n")
                f.write(f"Model: claude-3-haiku-20240307\n")
                f.write(f"Total Strategies Generated: {results['metadata']['total_chains']}\n")
                f.write(f"Trunk Identified: {results['trunk'] is not None}\n")
                f.write(f"Twigs Found: {len(results['twigs'])}\n\n")
                f.write("SUMMARY:\n")
                f.write(results['summary'])
                f.write("\n\n=== METADATA ===\n")
                f.write(json.dumps(results['metadata'], indent=2, default=str))
            
            print(f"Summary saved to: {summary_file}")
            
            # Create a test report
            report_file = output_dir / 'test_report.md'
            with open(report_file, 'w') as f:
                f.write("# Polyhegel Strategic Simulation Test Report\n\n")
                f.write(f"**Test Date:** {results['metadata'].get('timestamp', 'Unknown')}\n")
                f.write(f"**Model Used:** claude-3-haiku-20240307\n")
                f.write(f"**Temperature Settings:** {temperature_counts}\n")
                f.write(f"**Total Strategies:** {results['metadata']['total_chains']}\n\n")
                
                f.write("## Results Overview\n\n")
                f.write(f"- **Trunk Strategy:** {'✓ Identified' if results['trunk'] else '✗ Not identified'}\n")
                f.write(f"- **Alternative Twigs:** {len(results['twigs'])} found\n")
                f.write(f"- **Web Tools:** {'✓ Available' if 'web_search_tool' in str(results) or 'web_fetch_tool' in str(results) else '? Not explicitly used'}\n")
                f.write(f"- **Git Tools:** {'✓ Available' if 'git_repo_to_md_tool' in str(results) else '? Not explicitly used'}\n\n")
                
                f.write("## Strategic Summary\n\n")
                f.write(results['summary'])
                f.write("\n\n## Files Generated\n\n")
                f.write("- `strategic_simulation_cache.json` - Complete results\n")
                f.write("- `trunk_strategy.json` - Primary strategy path\n")
                f.write("- `twig_strategy_*.json` - Alternative strategy paths\n")
                f.write("- `simulation_summary.txt` - Human-readable summary\n")
                f.write("- `test_report.md` - This report\n")
            
            print(f"Test report saved to: {report_file}")
            print("\n=== Integration Test Completed Successfully ===")
            
            # Assertions for pytest
            assert len(results['summary']) > 100  # Should have meaningful summary
            assert cache_file.exists()
            assert summary_file.exists()
            assert report_file.exists()
            
        except Exception as e:
            print(f"\nSimulation failed: {e}")
            # Still save error info for debugging
            error_file = output_dir / 'simulation_error.json'
            with open(error_file, 'w') as f:
                json.dump({
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'model': 'claude-3-haiku-20240307',
                    'temperature_counts': temperature_counts
                }, f, indent=2)
            
            # Don't fail the test if it's just API related
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip(f"Simulation test skipped due to API issue: {e}")
            else:
                raise

    def test_cache_directory_setup(self):
        """Test that cache directory is properly set up"""
        test_dir = Path(__file__).parent
        output_dir = test_dir / "out"
        output_dir.mkdir(exist_ok=True)
        
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Create a marker file to indicate this is a test cache
        marker_file = output_dir / '.test_cache_marker'
        with open(marker_file, 'w') as f:
            f.write("This directory contains cached polyhegel test results\n")
            f.write("Generated by tests/test_full_integration.py\n")
        
        assert marker_file.exists()


if __name__ == "__main__":
    # Run the integration test directly
    import logging
    logging.basicConfig(level=logging.INFO)
    
    test = TestFullIntegration()
    asyncio.run(test.test_strategic_query_full_simulation())