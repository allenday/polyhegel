"""
Test prompt templates loading
"""

import pytest
from pathlib import Path
from polyhegel.prompts import load_prompt, PROMPTS_DIR


class TestPrompts:
    """Test prompt template functionality"""

    def test_prompts_directory_exists(self):
        """Test that prompts directory exists"""
        assert PROMPTS_DIR.exists()
        assert PROMPTS_DIR.is_dir()

    def test_compare_answer_template_exists(self):
        """Test that compare_answer.txt was copied"""
        compare_path = PROMPTS_DIR / "compare_answer.txt"
        assert compare_path.exists()

    def test_use_techniques_template_exists(self):
        """Test that use_techniques.txt was copied"""
        techniques_path = PROMPTS_DIR / "use_techniques.txt"
        assert techniques_path.exists()

    def test_load_prompt_function(self):
        """Test load_prompt function works"""
        content = load_prompt("compare_answer.txt")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Question:" in content

    def test_load_techniques_prompt(self):
        """Test loading techniques prompt"""
        content = load_prompt("use_techniques.txt")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "{key_technique}" in content

    def test_load_nonexistent_prompt_raises_error(self):
        """Test that loading non-existent prompt raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="Prompt template not found"):
            load_prompt("nonexistent_prompt.txt")

    def test_strategic_compare_template_exists(self):
        """Test that strategic_compare.txt template exists"""
        strategic_path = PROMPTS_DIR / "strategic_compare.txt"
        assert strategic_path.exists()

    def test_load_strategic_compare_prompt(self):
        """Test loading strategic comparison prompt"""
        content = load_prompt("strategic_compare.txt")
        assert isinstance(content, str)
        assert len(content) > 0
        assert "Strategic Situation:" in content
        assert "Strategic Viability" in content
        assert "Preferred Strategy Index:" in content