"""
Prompt templates for strategic reasoning and evaluation
"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

def load_prompt(filename: str) -> str:
    """Load a prompt template from file"""
    prompt_path = PROMPTS_DIR / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {filename}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()