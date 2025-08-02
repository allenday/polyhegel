"""
Tests for strategic technique prompt templates
"""

import pytest
from pathlib import Path
from polyhegel.strategic_techniques import (
    StrategyDomain,
    get_technique_by_name,
    get_techniques_for_domain,
    RESOURCE_ACQUISITION_TECHNIQUES,
)


class TestStrategicTechniquePrompts:
    """Test strategic technique prompt functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.prompts_dir = Path(__file__).parent.parent / "polyhegel" / "prompts"
        self.techniques_template = self.prompts_dir / "strategic_techniques.txt"

    def test_strategic_techniques_template_exists(self):
        """Test that the strategic techniques template exists"""
        assert self.techniques_template.exists()

    def test_strategic_techniques_template_format(self):
        """Test that the template has proper format placeholders"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Check for required placeholders
        required_placeholders = [
            "{strategic_challenge}",
            "{key_technique}",
            "{domain}",
            "{technique_description}",
            "{technique_use_cases}",
        ]

        for placeholder in required_placeholders:
            assert placeholder in template_content, f"Missing placeholder: {placeholder}"

    def test_template_formatting_with_real_technique(self):
        """Test formatting template with actual strategic technique"""
        # Get a real technique
        technique = RESOURCE_ACQUISITION_TECHNIQUES[0]  # Stakeholder Alignment Matrix

        with open(self.techniques_template, "r") as f:
            template = f.read()

        # Format use cases as bullet points
        use_cases_text = "\n".join([f"- {use_case}" for use_case in technique.use_cases])

        # Test that we can format the template
        formatted_prompt = template.format(
            strategic_challenge="Build a sustainable funding model for an AI research initiative",
            key_technique=technique.name,
            domain=technique.domain.value,
            technique_description=technique.description,
            technique_use_cases=use_cases_text,
        )

        # Verify formatting worked
        assert technique.name in formatted_prompt
        assert technique.description in formatted_prompt
        assert technique.domain.value in formatted_prompt
        assert "Build a sustainable funding model" in formatted_prompt

        # Check that all placeholders were replaced
        assert "{" not in formatted_prompt or "}" not in formatted_prompt

    def test_template_structure_elements(self):
        """Test that template includes strategic planning structure"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Check for strategic planning elements
        strategic_elements = [
            "Strategic Plan Title:",
            "Strategic Steps:",
            "Alignment Scores",
            "Strategic Coherence:",
            "Strategic Domain Alignment:",
            "Implementation Feasibility:",
            "Risk Management:",
            "Stakeholder Value:",
            "Estimated Timeline:",
            "Resource Requirements:",
        ]

        for element in strategic_elements:
            assert element in template_content, f"Missing strategic element: {element}"

    def test_template_domain_integration(self):
        """Test that template properly integrates strategic domains"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Should reference strategic domain multiple times
        domain_references = template_content.count("{domain}")
        assert domain_references >= 2, "Should reference strategic domain at least twice"

        # Should mention alignment with strategy domain
        assert "alignment with" in template_content.lower() and "strategy domain" in template_content.lower()

    def test_template_with_different_domains(self):
        """Test template formatting with different strategic domains"""
        with open(self.techniques_template, "r") as f:
            template = f.read()

        # Test with each domain
        for domain in StrategyDomain:
            techniques = get_techniques_for_domain(domain)
            if techniques:
                technique = techniques[0]
                use_cases_text = "\n".join([f"- {use_case}" for use_case in technique.use_cases])

                formatted_prompt = template.format(
                    strategic_challenge="Test strategic challenge",
                    key_technique=technique.name,
                    domain=technique.domain.value,
                    technique_description=technique.description,
                    technique_use_cases=use_cases_text,
                )

                # Should contain domain-specific content
                assert technique.domain.value in formatted_prompt
                assert technique.name in formatted_prompt

    def test_template_output_format(self):
        """Test that template specifies proper output format"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Should not require LaTeX formatting (unlike original mathematical template)
        assert "\\boxed{" not in template_content
        assert "LaTeX" not in template_content

        # Should specify structured output
        assert "Strategic Plan Title:" in template_content
        assert "1-5 scale" in template_content

    def test_step_by_step_guidance(self):
        """Test that template provides step-by-step guidance"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Should provide clear instructions
        guidance_elements = [
            "step-by-step",
            "Apply this strategic technique",
            "Detail your strategic reasoning",
            "Ensure alignment",
        ]

        for element in guidance_elements:
            assert element in template_content, f"Missing guidance element: {element}"

    def test_comprehensive_strategic_framework(self):
        """Test that template covers comprehensive strategic planning"""
        with open(self.techniques_template, "r") as f:
            template_content = f.read()

        # Should cover key strategic planning aspects
        planning_aspects = ["prerequisites", "outcome", "risks", "confidence level", "timeline", "resources"]

        for aspect in planning_aspects:
            assert aspect in template_content.lower(), f"Missing planning aspect: {aspect}"


def test_prompt_template_integration():
    """Integration test for prompt template with strategic techniques"""
    prompts_dir = Path(__file__).parent.parent / "polyhegel" / "prompts"
    template_file = prompts_dir / "strategic_techniques.txt"

    # Load template
    with open(template_file, "r") as f:
        template = f.read()

    # Test with a real scenario
    technique = get_technique_by_name("Stakeholder Alignment Matrix")
    assert technique is not None

    use_cases_text = "\n".join([f"- {use_case}" for use_case in technique.use_cases])

    formatted_prompt = template.format(
        strategic_challenge="Develop a strategy to build consensus around hotdog taxonomy classification",
        key_technique=technique.name,
        domain=technique.domain.value,
        technique_description=technique.description,
        technique_use_cases=use_cases_text,
    )

    # Verify the result is coherent and complete
    assert len(formatted_prompt) > 500  # Should be substantial
    assert "hotdog taxonomy" in formatted_prompt
    assert "Stakeholder Alignment Matrix" in formatted_prompt
    assert "resource_acquisition" in formatted_prompt  # Strategic domain
    assert "Strategic Plan Title:" in formatted_prompt


if __name__ == "__main__":
    pytest.main([__file__])
