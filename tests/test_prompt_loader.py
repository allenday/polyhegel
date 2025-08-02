"""
Tests for centralized prompt loading system
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from polyhegel.prompts.loader import PromptLoader, PromptsConfig, PromptTemplate
from polyhegel.prompts import get_system_prompt, load_prompt


class TestPromptTemplate:
    """Test PromptTemplate pydantic model"""

    def test_valid_template(self):
        """Test valid template creation"""
        template = PromptTemplate(
            file="strategic/evaluate.md", description="Test prompt", parameters=["param1", "param2"]
        )

        assert template.file == "strategic/evaluate.md"
        assert template.description == "Test prompt"
        assert template.parameters == ["param1", "param2"]
        assert template.version == "1.0"  # default

    def test_invalid_file_extension(self):
        """Test validation of file extensions"""
        with pytest.raises(ValueError, match="must have .md or .txt extension"):
            PromptTemplate(file="invalid.py", description="Invalid file")


class TestPromptsConfig:
    """Test PromptsConfig pydantic model"""

    def test_valid_config(self):
        """Test valid configuration"""
        config_data = {
            "prompts": {
                "strategic": {"evaluator": {"file": "strategic/evaluate.md", "description": "Evaluator prompt"}}
            },
            "templates": {"test_template": {"file": "test.md", "description": "Test template"}},
            "version": "1.0",
            "schema_version": "1.0",
        }

        config = PromptsConfig(**config_data)
        assert "strategic" in config.prompts
        assert "evaluator" in config.prompts["strategic"]
        assert "test_template" in config.templates


class TestPromptLoader:
    """Test PromptLoader functionality"""

    def setup_method(self):
        """Set up test environment with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_dir = Path(self.temp_dir)

        # Create test configuration
        config = {
            "prompts": {
                "strategic": {
                    "evaluator": {"file": "strategic/evaluate.md", "description": "Strategic evaluator prompt"}
                },
                "general": {"default": {"file": "general/default.md", "description": "Default prompt"}},
            },
            "templates": {
                "test_template": {
                    "file": "templates/test.md",
                    "description": "Test template",
                    "parameters": ["param1", "param2"],
                }
            },
            "version": "1.0",
            "schema_version": "1.0",
        }

        # Write config file
        config_file = self.prompts_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        # Create prompt directories
        (self.prompts_dir / "strategic").mkdir(parents=True)
        (self.prompts_dir / "general").mkdir(parents=True)
        (self.prompts_dir / "templates").mkdir(parents=True)

        # Create test prompt files
        eval_prompt = self.prompts_dir / "strategic/evaluate.md"
        eval_prompt.write_text("You are a strategic evaluator.")

        default_prompt = self.prompts_dir / "general/default.md"
        default_prompt.write_text("You are a strategic planner.")

        template_file = self.prompts_dir / "templates/test.md"
        template_file.write_text("Template with {param1} and {param2}.")

        self.loader = PromptLoader(self.prompts_dir)

    def test_loader_initialization(self):
        """Test loader initialization"""
        assert self.loader.prompts_dir == self.prompts_dir
        assert self.loader.config_file.exists()

    def test_config_loading(self):
        """Test configuration loading and validation"""
        config = self.loader.config
        assert isinstance(config, PromptsConfig)
        assert "strategic" in config.prompts
        assert "evaluator" in config.prompts["strategic"]

    def test_get_system_prompt(self):
        """Test system prompt retrieval"""
        prompt = self.loader.get_system_prompt("strategic", "evaluator")
        assert prompt == "You are a strategic evaluator."

        # Test caching
        prompt2 = self.loader.get_system_prompt("strategic", "evaluator")
        assert prompt2 == prompt

    def test_get_template(self):
        """Test template retrieval with parameters"""
        template = self.loader.get_template("test_template", param1="value1", param2="value2")
        assert template == "Template with value1 and value2."

    def test_get_template_missing_param(self):
        """Test template with missing parameter"""
        with pytest.raises(ValueError, match="Missing required parameter"):
            self.loader.get_template("test_template", param1="value1")

    def test_invalid_category(self):
        """Test invalid prompt category"""
        with pytest.raises(ValueError, match="Unknown prompt category"):
            self.loader.get_system_prompt("invalid", "evaluator")

    def test_invalid_prompt_name(self):
        """Test invalid prompt name"""
        with pytest.raises(ValueError, match="Unknown prompt"):
            self.loader.get_system_prompt("strategic", "invalid")

    def test_missing_prompt_file(self):
        """Test missing prompt file handling"""
        # Create config with non-existent file
        config = {
            "prompts": {"test": {"missing": {"file": "missing.md", "description": "Missing file"}}},
            "templates": {},
            "version": "1.0",
        }

        config_file = self.prompts_dir / "config_missing.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        loader = PromptLoader(self.prompts_dir)
        loader.config_file = config_file
        loader._config = None  # Force reload

        with pytest.raises(FileNotFoundError):
            loader.get_system_prompt("test", "missing")

    def test_list_available_prompts(self):
        """Test listing available prompts"""
        prompts = self.loader.list_available_prompts()
        assert "strategic" in prompts
        assert "evaluator" in prompts["strategic"]
        assert "general" in prompts
        assert "default" in prompts["general"]

    def test_list_available_templates(self):
        """Test listing available templates"""
        templates = self.loader.list_available_templates()
        assert "test_template" in templates

    def test_validate_template_parameters(self):
        """Test template parameter validation"""
        # Valid parameters
        assert self.loader.validate_template_parameters("test_template", {"param1": "value1", "param2": "value2"})

        # Missing parameters
        assert not self.loader.validate_template_parameters("test_template", {"param1": "value1"})

    def test_get_prompt_info(self):
        """Test getting prompt metadata"""
        info = self.loader.get_prompt_info("strategic", "evaluator")
        assert isinstance(info, PromptTemplate)
        assert info.file == "strategic/evaluate.md"
        assert info.description == "Strategic evaluator prompt"


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_system_prompt_function(self):
        """Test get_system_prompt convenience function"""
        # This will use the real prompt loader with actual config
        try:
            prompt = get_system_prompt("strategic", "evaluator")
            assert isinstance(prompt, str)
            assert len(prompt) > 0
        except (FileNotFoundError, ValueError):
            # Expected if running without full prompt setup
            pytest.skip("Real prompt configuration not available")

    def test_get_template_function(self):
        """Test get_template convenience function"""
        try:
            # Test legacy compatibility
            template = load_prompt("strategic_compare.txt")
            assert isinstance(template, str)
            assert len(template) > 0
        except (FileNotFoundError, ValueError):
            # Expected if running without full prompt setup
            pytest.skip("Real prompt configuration not available")


class TestIntegration:
    """Integration tests with real prompt configuration"""

    def test_real_prompt_loading(self):
        """Test loading real prompts from the package"""
        try:
            loader = PromptLoader()

            # Test that we can load the real configuration
            config = loader.config
            assert isinstance(config, PromptsConfig)

            # Test that we can load real prompts
            prompts = loader.list_available_prompts()
            assert len(prompts) > 0

            templates = loader.list_available_templates()
            assert len(templates) > 0

        except FileNotFoundError:
            pytest.skip("Real prompt configuration not available in test environment")


if __name__ == "__main__":
    pytest.main([__file__])
