"""
CLI interface for Polyhegel
"""

import argparse
import asyncio
import json
import logging
import sys
import numpy as np
from pathlib import Path
from typing import Union

from .simulator import PolyhegelSimulator
from .config import Config

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def read_text_from_file(file_path: Union[str, Path]) -> str:
    """Read text content from various file formats."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Handle different file types
    if file_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Try to read as text
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Polyhegel - General-purpose strategy trunk/twig simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simulation with default temperature mode
  python -m polyhegel simulate --output results/
  
  # Use hierarchical mode with A2A distributed agents  
  python -m polyhegel simulate --output results/ --mode hierarchical --user-prompt-file strategic-challenge.md
  
  # Use specific model and temperature settings (temperature mode)
  python -m polyhegel simulate --output results/ --model claude-3-haiku-20240307 --temperatures 0.8:5 0.9:10 1.0:5
  
  # Use custom system and user prompts from files
  python -m polyhegel simulate --output results/ --system-prompt-file system-prompt.md --user-prompt-file user-query.md
  
  # List available models
  python -m polyhegel models

Environment Variables:
  API Keys (.env file):
  OPENAI_API_KEY=your_openai_key
  ANTHROPIC_API_KEY=your_anthropic_key  
  GOOGLE_API_KEY=your_google_key
  MISTRAL_API_KEY=your_mistral_key
  GROQ_API_KEY=your_groq_key
  XAI_API_KEY=your_xai_key
  
  A2A Agent Endpoints (hierarchical mode):
  POLYHEGEL_LEADER_URL=http://localhost:8001
  POLYHEGEL_FOLLOWER_RESOURCE_URL=http://localhost:8002/resource
  POLYHEGEL_FOLLOWER_SECURITY_URL=http://localhost:8002/security  
  POLYHEGEL_FOLLOWER_VALUE_URL=http://localhost:8002/value
  POLYHEGEL_FOLLOWER_GENERAL_URL=http://localhost:8002/general
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Simulate command
    simulate_parser = subparsers.add_parser('simulate', help='Run strategy simulation')
    simulate_parser.add_argument('--output', required=True, help='Output directory path')
    simulate_parser.add_argument('--model', default=Config.DEFAULT_MODEL, help='Default model to use')
    simulate_parser.add_argument('--leader-model', help='Model for leader agent (overrides --model)')
    simulate_parser.add_argument('--follower-model', help='Model for follower agents (defaults to leader model)')
    simulate_parser.add_argument('--api-key', help='API key (or set environment variables)')
    simulate_parser.add_argument(
        '--temperatures',
        nargs='+',
        type=str,
        default=[f"{t}:{c}" for t, c in Config.DEFAULT_TEMPERATURE_COUNTS],
        help='Temperature:count pairs (e.g., "0.8:5 0.9:10"). Default: 0.8:5 0.9:10 1.0:10 1.1:5'
    )
    simulate_parser.add_argument(
        '--system-prompt-file',
        help='Path to file containing system prompt (required for meaningful results)'
    )
    simulate_parser.add_argument(
        '--user-prompt-file',
        help='Path to file containing user prompt'
    )
    simulate_parser.add_argument(
        '--mode',
        choices=['temperature', 'hierarchical'],
        default='temperature',
        help='Generation mode: temperature sampling or hierarchical agents (default: temperature)'
    )
    simulate_parser.add_argument(
        '--agent-endpoints',
        nargs='+',
        help='A2A agent endpoints for hierarchical mode (format: role=url). Example: --agent-endpoints leader=http://localhost:8001 resource=http://localhost:8002'
    )
    
    # Models command
    models_parser = subparsers.add_parser('models', help='List available models')
    models_parser.add_argument('--with-availability', action='store_true', 
                              help='Show availability status based on API keys')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'models':
            # Use model manager directly for listing
            from .model_manager import ModelManager
            model_manager = ModelManager()
            
            if args.with_availability:
                models_info = model_manager.list_models_with_availability()
                print("Available providers with API key status:")
                for provider, info in models_info.items():
                    status = "✓" if info['available'] else "✗"
                    print(f"\n{provider.upper()} {status}: {info['description']}")
            else:
                models = model_manager.discover_available_models()
                print("Available providers:")
                for provider, description in models.items():
                    print(f"\n{provider.upper()}: {description}")
            return
        
        if args.command == 'simulate':
            # Load system prompt if provided
            system_prompt = None
            if args.system_prompt_file:
                try:
                    system_prompt = read_text_from_file(args.system_prompt_file)
                    logger.info(f"Loaded system prompt from: {args.system_prompt_file}")
                except Exception as e:
                    logger.error(f"Failed to load system prompt file: {str(e)}")
                    sys.exit(1)
            
            # Load user prompt from file
            user_prompt = None
            if args.user_prompt_file:
                try:
                    user_prompt = read_text_from_file(args.user_prompt_file)
                    logger.info(f"Loaded user prompt from: {args.user_prompt_file}")
                except Exception as e:
                    logger.error(f"Failed to load user prompt file: {str(e)}")
                    sys.exit(1)
            
            # Determine models to use
            leader_model = args.leader_model or args.model
            follower_model = args.follower_model or leader_model
            
            # Initialize simulator with leader model
            simulator = PolyhegelSimulator(model_name=leader_model, api_key=args.api_key)
            
            # TODO: Implement follower model support in the simulator architecture
            if follower_model != leader_model:
                logger.info(f"Using leader model: {leader_model}, follower model: {follower_model}")
                logger.warning("Multi-model leader/follower architecture not yet implemented - using leader model for all agents")
            
            # Parse temperature counts
            temperature_counts = simulator.parse_temperature_counts(args.temperatures)
            logger.info(f"Temperature settings: {temperature_counts}")
            
            # Handle A2A agent endpoints for hierarchical mode
            if args.mode == 'hierarchical' and args.agent_endpoints:
                # Parse agent endpoints from CLI arguments
                endpoint_overrides = {}
                for endpoint_arg in args.agent_endpoints:
                    if '=' in endpoint_arg:
                        role, url = endpoint_arg.split('=', 1)
                        role = role.strip().lower()
                        url = url.strip()
                        
                        # Map role names to environment variable names
                        if role == 'leader':
                            endpoint_overrides['POLYHEGEL_LEADER_URL'] = url
                        elif role in ['resource', 'follower_resource']:
                            endpoint_overrides['POLYHEGEL_FOLLOWER_RESOURCE_URL'] = url
                        elif role in ['security', 'follower_security']:
                            endpoint_overrides['POLYHEGEL_FOLLOWER_SECURITY_URL'] = url
                        elif role in ['value', 'follower_value']:
                            endpoint_overrides['POLYHEGEL_FOLLOWER_VALUE_URL'] = url
                        elif role in ['general', 'follower_general']:
                            endpoint_overrides['POLYHEGEL_FOLLOWER_GENERAL_URL'] = url
                        else:
                            logger.warning(f"Unknown agent role '{role}', ignoring endpoint {url}")
                
                # Apply endpoint overrides to environment
                import os
                for env_var, url in endpoint_overrides.items():
                    os.environ[env_var] = url
                    logger.info(f"Using A2A agent endpoint: {env_var}={url}")
            
            # Run simulation
            results = asyncio.run(simulator.run_simulation(
                temperature_counts=temperature_counts,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                mode=args.mode
            ))
            
            # Create output directory
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save results
            output_path = output_dir / 'simulation_results.json'
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, cls=NumpyEncoder)
            
            logger.info(f"Results saved to {output_path}")
            
            # Save individual strategy files
            if results['trunk']:
                trunk_file = output_dir / 'trunk_strategy.json'
                with open(trunk_file, 'w') as f:
                    json.dump(results['trunk'], f, indent=2, cls=NumpyEncoder)
            
            for i, twig in enumerate(results['twigs']):
                twig_file = output_dir / f'twig_strategy_{i+1}.json'
                with open(twig_file, 'w') as f:
                    json.dump(twig, f, indent=2, cls=NumpyEncoder)
            
            # Display summary
            print(f"\nSimulation Complete!")
            print(f"Mode: {args.mode}")
            print(f"Model: {args.model}")
            if args.mode == 'hierarchical':
                print(f"Leader model: {leader_model}")
                print(f"Follower model: {follower_model}")
            else:
                print(f"Temperature settings: {temperature_counts}")
            print(f"Total strategies generated: {results['metadata']['total_chains']}")
            print(f"Trunk identified: {results['trunk'] is not None}")
            print(f"Twigs found: {len(results['twigs'])}")
            print(f"\nSummary: {results['summary']}")
            print(f"\nResults saved to: {output_dir}")
            
    except Exception as e:
        logger.error(f"CLI execution failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()