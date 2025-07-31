"""
Tests for Polyhegel data models
"""

import pytest
from pydantic import ValidationError

from polyhegel.models import (
    StrategyStep, GenesisStrategy, StrategicTheme, ThemeCategory, StrategyChain
)


class TestStrategyStep:
    """Test StrategyStep model"""
    
    def test_strategy_step_creation(self):
        """Test creating a strategy step"""
        step = StrategyStep(
            action="Test action",
            prerequisites=["Prerequisite 1", "Prerequisite 2"],
            outcome="Expected outcome",
            risks=["Risk 1", "Risk 2"],
            confidence=0.8
        )
        
        assert step.action == "Test action"
        assert len(step.prerequisites) == 2
        assert step.outcome == "Expected outcome"
        assert len(step.risks) == 2
        assert step.confidence == 0.8

    def test_strategy_step_defaults(self):
        """Test strategy step with default values"""
        step = StrategyStep(
            action="Test action",
            prerequisites=[],
            outcome="Expected outcome",
            risks=[]
        )
        
        assert step.confidence == 0.8  # Default value


class TestGenesisStrategy:
    """Test GenesisStrategy model"""
    
    def test_genesis_strategy_creation(self):
        """Test creating a complete genesis strategy"""
        steps = [
            StrategyStep(
                action="Step 1",
                prerequisites=["Prereq 1"],
                outcome="Outcome 1",
                risks=["Risk 1"]
            ),
            StrategyStep(
                action="Step 2", 
                prerequisites=["Prereq 2"],
                outcome="Outcome 2",
                risks=["Risk 2"]
            )
        ]
        
        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=steps,
            alignment_score={"Strategic Alignment": 4.5, "Implementation Feasibility": 3.8},
            estimated_timeline="6 months",
            resource_requirements=["Team", "Budget", "Technology"]
        )
        
        assert strategy.title == "Test Strategy"
        assert len(strategy.steps) == 2
        assert strategy.alignment_score["Strategic Alignment"] == 4.5
        assert strategy.estimated_timeline == "6 months"
        assert len(strategy.resource_requirements) == 3


class TestThemeCategory:
    """Test ThemeCategory enum"""
    
    def test_theme_categories(self):
        """Test all theme category values"""
        assert ThemeCategory.RESOURCE_ACQUISITION == "resource_acquisition"
        assert ThemeCategory.STRATEGIC_SECURITY == "strategic_security"
        assert ThemeCategory.VALUE_CATALYSIS == "value_catalysis"
        assert ThemeCategory.CROSS_CUTTING == "cross_cutting"
        assert ThemeCategory.FOUNDATIONAL == "foundational"


class TestStrategicTheme:
    """Test StrategicTheme model"""
    
    def test_strategic_theme_creation(self):
        """Test creating a strategic theme"""
        theme = StrategicTheme(
            title="Multi-Stakeholder Platform Strategy",
            category=ThemeCategory.VALUE_CATALYSIS,
            description="Develop a platform that enables multiple stakeholders to collaborate and create shared value through coordinated strategic initiatives.",
            clm_alignment={"2.1": 3.5, "2.2": 2.8, "2.3": 4.8},
            priority_level="high",
            complexity_estimate="complex",
            key_concepts=["collaboration", "value creation", "platform", "stakeholders"],
            success_criteria=[
                "Platform launches with 3+ stakeholder groups",
                "Measurable value creation within 6 months",
                "Self-sustaining ecosystem development"
            ],
            potential_risks=[
                "Stakeholder coordination challenges",
                "Platform adoption resistance"
            ],
            strategic_context="Critical for long-term ecosystem development"
        )
        
        assert theme.title == "Multi-Stakeholder Platform Strategy"
        assert theme.category == ThemeCategory.VALUE_CATALYSIS
        assert len(theme.description) > 50
        assert theme.clm_alignment["2.3"] == 4.8
        assert theme.priority_level == "high"
        assert theme.complexity_estimate == "complex"
        assert len(theme.key_concepts) == 4
        assert len(theme.success_criteria) == 3
        assert len(theme.potential_risks) == 2

    def test_strategic_theme_defaults(self):
        """Test strategic theme with default values"""
        theme = StrategicTheme(
            title="Basic Theme",
            category=ThemeCategory.FOUNDATIONAL,
            description="A foundational strategic theme that provides basic infrastructure and capabilities for other strategic initiatives.",
            key_concepts=["foundation", "infrastructure"],
            success_criteria=["Infrastructure established"]
        )
        
        assert theme.priority_level == "medium"
        assert theme.complexity_estimate == "moderate"
        assert theme.potential_risks == []
        assert theme.strategic_context is None
        assert theme.clm_alignment == {}

    def test_theme_validation_title_length(self):
        """Test title length validation"""
        # Too short
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Hi",  # Too short
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                key_concepts=["test"],
                success_criteria=["Success"]
            )
        
        # Too long
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="A" * 101,  # Too long (>100 chars)
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                key_concepts=["test"],
                success_criteria=["Success"]
            )

    def test_theme_validation_description_length(self):
        """Test description length validation"""
        # Too short
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Valid Title",
                category=ThemeCategory.FOUNDATIONAL,
                description="Short",  # Too short
                key_concepts=["test"],
                success_criteria=["Success"]
            )

    def test_clm_alignment_validation(self):
        """Test Strategic alignment validation"""
        # Invalid mandate
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                clm_alignment={"2.4": 4.0},  # Invalid mandate
                key_concepts=["test"],
                success_criteria=["Success"]
            )
        
        # Invalid score (too high)
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                clm_alignment={"2.1": 6.0},  # Score too high
                key_concepts=["test"],
                success_criteria=["Success"]
            )
        
        # Invalid score (too low)
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                clm_alignment={"2.1": 0.5},  # Score too low
                key_concepts=["test"],
                success_criteria=["Success"]
            )

    def test_key_concepts_validation(self):
        """Test key concepts validation"""
        # Empty key concepts
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                key_concepts=[],  # Empty
                success_criteria=["Success"]
            )

    def test_success_criteria_validation(self):
        """Test success criteria validation"""
        # Empty success criteria
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A description that meets the minimum length requirement for validation.",
                key_concepts=["test"],
                success_criteria=[]  # Empty
            )

    def test_get_primary_mandate(self):
        """Test getting primary Strategic mandate"""
        theme = StrategicTheme(
            title="Test Theme",
            category=ThemeCategory.CROSS_CUTTING,
            description="A theme that spans multiple Strategic mandates with varying alignment scores.",
            clm_alignment={"2.1": 3.0, "2.2": 4.5, "2.3": 2.8},
            key_concepts=["cross-cutting"],
            success_criteria=["Success across mandates"]
        )
        
        assert theme.get_primary_mandate() == "2.2"  # Highest score
        
        # Test with no alignment
        theme_no_alignment = StrategicTheme(
            title="No Alignment Theme",
            category=ThemeCategory.FOUNDATIONAL,
            description="A theme without Strategic alignment scores specified for testing purposes.",
            key_concepts=["foundation"],
            success_criteria=["Basic success"]
        )
        
        assert theme_no_alignment.get_primary_mandate() is None

    def test_is_cross_cutting(self):
        """Test cross-cutting theme detection"""
        # Cross-cutting theme (multiple high scores)
        cross_cutting_theme = StrategicTheme(
            title="Cross-Cutting Theme",
            category=ThemeCategory.CROSS_CUTTING,
            description="A strategic theme that spans multiple Strategic mandates with high alignment.",
            clm_alignment={"2.1": 4.0, "2.2": 4.2, "2.3": 2.5},
            key_concepts=["cross-cutting"],
            success_criteria=["Multi-mandate success"]
        )
        
        assert cross_cutting_theme.is_cross_cutting() is True
        
        # Single-mandate theme
        single_mandate_theme = StrategicTheme(
            title="Single Mandate Theme",
            category=ThemeCategory.RESOURCE_ACQUISITION,
            description="A strategic theme focused primarily on resource acquisition activities.",
            clm_alignment={"2.1": 4.5, "2.2": 2.0, "2.3": 1.8},
            key_concepts=["resources"],
            success_criteria=["Resource acquisition success"]
        )
        
        assert single_mandate_theme.is_cross_cutting() is False

    def test_get_alignment_summary(self):
        """Test alignment summary generation"""
        theme = StrategicTheme(
            title="Test Theme",
            category=ThemeCategory.VALUE_CATALYSIS,
            description="A theme for testing alignment summary generation functionality.",
            clm_alignment={"2.1": 3.5, "2.2": 4.0, "2.3": 4.8},
            key_concepts=["testing"],
            success_criteria=["Summary generated correctly"]
        )
        
        summary = theme.get_alignment_summary()
        assert "Resource Acquisition: 3.5/5.0" in summary
        assert "Strategic Security: 4.0/5.0" in summary
        assert "Value Catalysis: 4.8/5.0" in summary
        
        # Test with no alignment
        no_alignment_theme = StrategicTheme(
            title="No Alignment Theme",
            category=ThemeCategory.FOUNDATIONAL,
            description="A theme without alignment scores for testing summary functionality.",
            key_concepts=["no-alignment"],
            success_criteria=["Test no alignment case"]
        )
        
        summary = no_alignment_theme.get_alignment_summary()
        assert summary == "No Strategic alignment specified"

    def test_priority_levels(self):
        """Test valid priority levels"""
        valid_priorities = ["critical", "high", "medium", "low"]
        
        for priority in valid_priorities:
            theme = StrategicTheme(
                title="Priority Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A theme for testing different priority levels in the strategic planning system.",
                priority_level=priority,
                key_concepts=["priority"],
                success_criteria=["Priority set correctly"]
            )
            assert theme.priority_level == priority

    def test_complexity_estimates(self):
        """Test valid complexity estimates"""
        valid_complexities = ["simple", "moderate", "complex", "highly_complex"]
        
        for complexity in valid_complexities:
            theme = StrategicTheme(
                title="Complexity Test Theme",
                category=ThemeCategory.FOUNDATIONAL,
                description="A theme for testing different complexity estimates in strategic planning.",
                complexity_estimate=complexity,
                key_concepts=["complexity"],
                success_criteria=["Complexity estimated correctly"]
            )
            assert theme.complexity_estimate == complexity

    def test_max_items_validation(self):
        """Test maximum items validation"""
        # Too many key concepts
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Too Many Concepts",
                category=ThemeCategory.FOUNDATIONAL,
                description="A theme with too many key concepts for validation testing purposes.",
                key_concepts=["concept" + str(i) for i in range(11)],  # 11 > 10 max
                success_criteria=["Success"]
            )
        
        # Too many success criteria
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Too Many Criteria",
                category=ThemeCategory.FOUNDATIONAL,  
                description="A theme with too many success criteria for validation testing purposes.",
                key_concepts=["concept"],
                success_criteria=["criterion" + str(i) for i in range(6)]  # 6 > 5 max
            )
        
        # Too many risks
        with pytest.raises(ValidationError):
            StrategicTheme(
                title="Too Many Risks",
                category=ThemeCategory.FOUNDATIONAL,
                description="A theme with too many potential risks for validation testing purposes.",
                key_concepts=["concept"],
                success_criteria=["Success"],
                potential_risks=["risk" + str(i) for i in range(6)]  # 6 > 5 max
            )


class TestStrategyChain:
    """Test StrategyChain dataclass"""
    
    def test_strategy_chain_creation(self):
        """Test creating a strategy chain"""
        strategy = GenesisStrategy(
            title="Test Strategy",
            steps=[
                StrategyStep(
                    action="Test Action",
                    prerequisites=["Prereq"],
                    outcome="Outcome",
                    risks=["Risk"]
                )
            ],
            alignment_score={"test": 4.0},
            estimated_timeline="3 months",
            resource_requirements=["Resources"]
        )
        
        chain = StrategyChain(
            strategy=strategy,
            source_sample=1,
            temperature=0.8,
            technique_name="Test Technique",
            technique_mandate="2.1"
        )
        
        assert chain.strategy.title == "Test Strategy"
        assert chain.source_sample == 1
        assert chain.temperature == 0.8
        assert chain.technique_name == "Test Technique"
        assert chain.technique_mandate == "2.1"
        assert chain.cluster_label == -1  # Default
        assert chain.is_trunk is False  # Default
        assert chain.is_twig is False  # Default


if __name__ == "__main__":
    pytest.main([__file__])