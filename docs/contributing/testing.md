# Testing Guide

## Testing Philosophy

Polyhegel follows a comprehensive testing strategy that ensures reliability, performance, and maintainability across all components. Our testing approach emphasizes:

- **Test-Driven Development (TDD)**: Write tests before implementation when possible
- **Comprehensive Coverage**: Aim for >80% code coverage, >95% for critical components
- **Integration Focus**: Test component interactions and real-world workflows
- **Performance Validation**: Include performance benchmarks in critical paths

## Test Organization

### Directory Structure
```
tests/
├── unit/                   # Unit tests for individual components
│   ├── test_strategy_generator.py
│   ├── test_refinement_engine.py
│   ├── test_a2a_client.py
│   └── ...
├── integration/           # Integration tests for component interactions
│   ├── test_end_to_end_workflows.py
│   ├── test_a2a_integration.py
│   └── ...
├── performance/          # Performance and benchmark tests
│   ├── test_generation_performance.py
│   └── test_memory_usage.py
├── fixtures/             # Test data and mock objects
│   ├── sample_strategies.json
│   ├── mock_responses.py
│   └── ...
└── conftest.py          # Shared pytest fixtures
```

### Test Categories

#### Unit Tests
Focus on individual components in isolation:

```python
import pytest
from unittest.mock import AsyncMock, Mock, patch
from polyhegel.strategy_generator import StrategyGenerator
from polyhegel.models import StrategyChain, GenesisStrategy

class TestStrategyGenerator:
    """Test suite for StrategyGenerator class."""
    
    @pytest.fixture
    def mock_model(self):
        """Mock AI model for isolated testing."""
        model = AsyncMock()
        model.generate_content.return_value = {
            "title": "Mock Strategy",
            "steps": [{"action": "Mock action", "outcome": "Mock outcome"}]
        }
        return model
    
    @pytest.fixture
    def generator(self, mock_model):
        """Strategy generator with mocked dependencies."""
        with patch('polyhegel.strategy_generator.get_model') as mock_get_model:
            mock_get_model.return_value = mock_model  
            return StrategyGenerator("mock-model")
    
    @pytest.mark.asyncio
    async def test_generate_single_strategy_success(self, generator):
        """Test successful single strategy generation."""
        # Arrange
        user_prompt = "Test strategic challenge"
        temperature = 0.7
        
        # Act
        result = await generator.generate_single_strategy(user_prompt, temperature)
        
        # Assert
        assert isinstance(result, StrategyChain)
        assert result.strategy.title == "Mock Strategy"
        assert result.temperature == temperature
        assert len(result.strategy.steps) == 1
    
    @pytest.mark.asyncio
    async def test_generate_strategies_multiple_temperatures(self, generator):
        """Test strategy generation with multiple temperature settings."""
        # Arrange
        temperature_counts = [(0.3, 2), (0.7, 3)]
        user_prompt = "Multi-temperature test"
        
        # Act
        results = await generator.generate_strategies(
            temperature_counts=temperature_counts,
            user_prompt=user_prompt
        )
        
        # Assert
        assert len(results) == 5  # 2 + 3 strategies
        temp_0_3_count = sum(1 for r in results if r.temperature == 0.3)
        temp_0_7_count = sum(1 for r in results if r.temperature == 0.7)
        assert temp_0_3_count == 2
        assert temp_0_7_count == 3
    
    def test_validate_temperature_counts_invalid_input(self, generator):
        """Test validation of temperature_counts parameter."""
        invalid_inputs = [
            [],  # Empty list
            [(2.0, 1)],  # Temperature > 1.0
            [(-0.1, 1)],  # Temperature < 0.0
            [(0.7, 0)],  # Zero count
            [(0.7, -1)]  # Negative count
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                generator._validate_temperature_counts(invalid_input)
```

#### Integration Tests
Test component interactions and workflows:

```python
import pytest
import asyncio
from polyhegel.strategy_generator import StrategyGenerator
from polyhegel.refinement.recursive import RecursiveRefinementEngine
from polyhegel.clients.a2a_client import PolyhegelA2AClient
from polyhegel.simulator import PolyhegelSimulator

class TestEndToEndWorkflows:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def integration_config(self):
        """Configuration for integration testing."""
        return {
            "model_name": "claude-3-haiku-20240307",
            "timeout": 30,
            "max_retries": 2
        }
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_strategy_generation_to_refinement_workflow(self, integration_config):
        """Test complete workflow from generation through refinement."""
        # Arrange
        generator = StrategyGenerator(integration_config["model_name"])
        refinement_engine = RecursiveRefinementEngine()
        
        user_prompt = "Develop a customer acquisition strategy for B2B SaaS"
        
        # Act - Generate initial strategies
        initial_strategies = await generator.generate_strategies(
            temperature_counts=[(0.7, 2)],
            user_prompt=user_prompt
        )
        
        # Act - Refine the best strategy
        best_initial = max(initial_strategies, key=lambda s: s.strategy.alignment_score.get('overall', 0))
        
        refinement_session = await refinement_engine.refine_strategy(
            strategy=best_initial,
            user_prompt=user_prompt
        )
        
        # Assert
        assert len(initial_strategies) == 2
        assert refinement_session.is_complete
        assert refinement_session.best_score > 0
        assert refinement_session.current_generation >= 1
        assert len(refinement_session.generations) >= 2  # Original + at least 1 refinement
    
    @pytest.mark.asyncio 
    @pytest.mark.integration
    async def test_a2a_hierarchical_strategy_generation(self, integration_config):
        """Test A2A agent coordination for hierarchical strategy development."""
        # This test requires A2A agents to be running
        pytest.skip("Requires running A2A agent infrastructure")
        
        # Arrange
        from polyhegel.clients.a2a_client import A2AAgentEndpoints
        endpoints = A2AAgentEndpoints()  # Use default localhost endpoints
        
        async with PolyhegelA2AClient(endpoints) as client:
            # Act - Verify agent availability first
            availability = await client.verify_agent_availability()
            
            if not any(availability.values()):
                pytest.skip("No A2A agents available for integration test")
            
            # Act - Generate hierarchical strategies
            strategies = await client.generate_hierarchical_strategies(
                strategic_challenge="Launch new product in competitive market",
                max_themes=3
            )
            
            # Assert
            assert len(strategies) > 0
            assert all(isinstance(s, StrategyChain) for s in strategies)
            assert all(s.strategy.title for s in strategies)  # All have titles
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simulation_with_tournament_selection(self, integration_config):
        """Test simulation workflow with tournament-based selection."""
        # Arrange
        simulator = PolyhegelSimulator(integration_config["model_name"])
        
        # Act
        results = await simulator.run_simulation(
            temperature_counts=[(0.5, 2), (0.8, 2)],
            system_prompt="Generate comprehensive market entry strategies",
            user_prompt="Enter the European fintech market with our payment platform",
            mode="temperature",
            selection_method="tournament"
        )
        
        # Assert
        assert len(results) == 4  # 2 + 2 strategies
        assert all(isinstance(r, StrategyChain) for r in results)
        
        # Verify tournament selection worked (strategies should be ranked)
        scores = [r.strategy.alignment_score.get('overall', 0) for r in results]
        assert scores == sorted(scores, reverse=True)  # Should be sorted by score
```

#### Performance Tests
Validate performance characteristics:

```python
import pytest
import time
import asyncio
import psutil
import os
from memory_profiler import profile

class TestPerformanceCharacteristics:
    """Performance tests to ensure system meets requirements."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_strategy_generation_performance(self):
        """Test that strategy generation meets performance requirements."""
        from polyhegel.strategy_generator import StrategyGenerator
        
        generator = StrategyGenerator("claude-3-haiku-20240307")
        
        # Measure generation time
        start_time = time.perf_counter()
        
        strategies = await generator.generate_strategies(
            temperature_counts=[(0.7, 5)],
            user_prompt="Optimize supply chain operations for manufacturing company"
        )
        
        end_time = time.perf_counter()
        generation_time = end_time - start_time
        
        # Assert performance requirements
        assert len(strategies) == 5
        assert generation_time < 60.0  # Should complete within 1 minute
        assert generation_time / len(strategies) < 15.0  # < 15 seconds per strategy
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_generation_scalability(self):
        """Test system behavior under concurrent load."""
        from polyhegel.strategy_generator import StrategyGenerator
        
        generator = StrategyGenerator("claude-3-haiku-20240307")
        
        # Create multiple concurrent generation tasks
        tasks = []
        for i in range(5):
            task = generator.generate_strategies(
                temperature_counts=[(0.7, 2)],
                user_prompt=f"Strategic challenge {i}"
            )
            tasks.append(task)
        
        # Measure concurrent execution
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks)
        end_time = time.perf_counter()
        
        concurrent_time = end_time - start_time
        
        # Assert scalability requirements  
        assert len(results) == 5
        assert all(len(result) == 2 for result in results)  # All tasks completed
        assert concurrent_time < 90.0  # Concurrent should be faster than sequential
    
    @pytest.mark.performance
    def test_memory_usage_within_limits(self):
        """Test that memory usage stays within reasonable bounds."""
        import gc
        
        # Get baseline memory usage
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        from polyhegel.strategy_generator import StrategyGenerator
        generator = StrategyGenerator("claude-3-haiku-20240307")
        
        # Simulate multiple generation cycles
        for _ in range(10):
            # This would normally be async, but we're testing memory patterns
            generator._create_strategy_chain(
                title="Test Strategy",
                steps=[{"action": "Test", "outcome": "Test"}] * 50,  # Large strategy
                temperature=0.7,
                source_sample=0
            )
        
        # Check memory usage
        gc.collect()
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        
        # Assert memory requirements
        assert memory_increase < 500  # Should not increase by more than 500MB
        
        # Clean up
        del generator
        gc.collect()
```

## Test Configuration

### pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=polyhegel
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --tb=short
testpaths = tests
markers =
    unit: Unit tests for individual components
    integration: Integration tests requiring multiple components
    performance: Performance and benchmark tests
    slow: Tests that take more than 10 seconds
    a2a: Tests requiring A2A agent infrastructure
    llm: Tests requiring real LLM API calls
python_files = test_*.py
python_classes = Test*
python_functions = test_*
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### Shared Fixtures (`conftest.py`)
```python
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
import json
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_strategy_data():
    """Load sample strategy data for testing."""
    with open(TEST_DATA_DIR / "sample_strategies.json") as f:
        return json.load(f)

@pytest.fixture
def mock_llm_model():
    """Mock LLM model for testing without API calls."""
    model = AsyncMock()
    
    # Default responses for common scenarios
    model.generate_content.return_value = {
        "title": "Test Strategy",
        "steps": [
            {"action": "Analyze market", "outcome": "Market understanding"},
            {"action": "Develop plan", "outcome": "Strategic plan"},
            {"action": "Execute plan", "outcome": "Desired results"}
        ],
        "alignment_score": {"overall": 7.5, "feasibility": 8.0, "innovation": 7.0}
    }
    
    return model

@pytest.fixture
def mock_telemetry_collector():
    """Mock telemetry collector for testing."""
    collector = Mock()
    collector.record_event.return_value = None
    collector.increment_counter.return_value = None
    collector.set_gauge.return_value = None
    collector.get_metrics.return_value = {}
    return collector

@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir

# Performance testing fixtures
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "max_generation_time": 60.0,
        "max_memory_increase_mb": 500,
        "concurrent_task_limit": 10
    }

# A2A testing fixtures
@pytest.fixture
def mock_a2a_endpoints():
    """Mock A2A endpoint configuration."""
    from polyhegel.clients.a2a_client import A2AAgentEndpoints
    return A2AAgentEndpoints(
        leader_url="http://mock-leader:8001",
        follower_resource_url="http://mock-resource:8002",
        follower_security_url="http://mock-security:8003",
        follower_value_url="http://mock-value:8004",
        follower_general_url="http://mock-general:8005"
    )
```

## Testing Best Practices

### Test Isolation
Ensure tests don't interfere with each other:

```python
import pytest
from unittest.mock import patch

class TestStrategyRefinement:
    """Example of proper test isolation."""
    
    @pytest.fixture(autouse=True)
    def setup_test_isolation(self):
        """Set up clean state for each test."""
        # Clear any global state
        from polyhegel.telemetry import clear_global_collectors
        clear_global_collectors()
        
        # Reset environment variables
        with patch.dict('os.environ', {}, clear=True):
            yield
    
    @pytest.mark.asyncio
    async def test_refinement_with_fresh_state(self):
        """Test runs with completely fresh state."""
        # Test implementation with confidence that state is clean
        pass
```

### Parameterized Testing
Use parametrization for comprehensive coverage:

```python
import pytest

class TestTemperatureValidation:
    """Test temperature validation with various inputs."""
    
    @pytest.mark.parametrize("temperature,expected_valid", [
        (0.0, True),
        (0.5, True), 
        (1.0, True),
        (-0.1, False),
        (1.1, False),
        (None, False),
        ("0.5", False),  # String instead of float
    ])
    def test_temperature_validation(self, temperature, expected_valid):
        """Test temperature validation logic."""
        from polyhegel.strategy_generator import validate_temperature
        
        if expected_valid:
            assert validate_temperature(temperature) is True
        else:
            with pytest.raises(ValueError):
                validate_temperature(temperature)
    
    @pytest.mark.parametrize("temperature_counts,expected_total", [
        ([(0.3, 1), (0.7, 2)], 3),
        ([(0.5, 5)], 5),
        ([(0.1, 1), (0.3, 1), (0.5, 1), (0.7, 1), (0.9, 1)], 5),
    ])
    @pytest.mark.asyncio
    async def test_strategy_generation_counts(self, temperature_counts, expected_total):
        """Test that strategy generation produces expected counts."""
        from polyhegel.strategy_generator import StrategyGenerator
        
        generator = StrategyGenerator("mock-model")
        with patch.object(generator, '_generate_single_strategy') as mock_generate:
            mock_generate.return_value = Mock()  # Mock strategy
            
            results = await generator.generate_strategies(
                temperature_counts=temperature_counts,
                user_prompt="Test prompt"
            )
            
            assert len(results) == expected_total
```

### Async Testing Patterns
Proper patterns for testing async code:

```python
import pytest
import asyncio
from unittest.mock import AsyncMock

class TestAsyncOperations:
    """Examples of async testing patterns."""
    
    @pytest.mark.asyncio
    async def test_async_with_timeout(self):
        """Test async operation with timeout."""
        async def slow_operation():
            await asyncio.sleep(0.1)
            return "completed"
        
        # Test that operation completes within timeout
        result = await asyncio.wait_for(slow_operation(), timeout=1.0)
        assert result == "completed"
    
    @pytest.mark.asyncio
    async def test_async_exception_handling(self):
        """Test proper async exception handling."""
        async def failing_operation():
            raise ValueError("Operation failed")
        
        with pytest.raises(ValueError, match="Operation failed"):
            await failing_operation()
    
    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self):
        """Test concurrent async operations."""
        async def mock_strategy_generation(delay):
            await asyncio.sleep(delay)
            return f"strategy_{delay}"
        
        # Run operations concurrently
        tasks = [
            mock_strategy_generation(0.01),
            mock_strategy_generation(0.02),
            mock_strategy_generation(0.03),
        ]
        
        results = await asyncio.gather(*tasks)
        assert len(results) == 3
        assert all(result.startswith("strategy_") for result in results)
```

## Coverage and Reporting

### Coverage Configuration (`.coveragerc`)
```ini
[run]
source = polyhegel
omit = 
    */tests/*
    */test_*
    */venv/*
    */build/*
    */dist/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
```

### Running Tests and Coverage
```bash
# Run all tests with coverage
make test

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "not slow"             # Skip slow tests
pytest -m "performance"          # Performance tests only

# Run with detailed output
pytest -v --tb=long

# Run specific test file or function
pytest tests/unit/test_strategy_generator.py
pytest tests/unit/test_strategy_generator.py::TestStrategyGenerator::test_generate_single_strategy

# Generate coverage reports
pytest --cov=polyhegel --cov-report=html
pytest --cov=polyhegel --cov-report=term-missing
```

### Performance Benchmarking
```bash
# Run performance tests
pytest -m performance --benchmark-only

# Generate performance reports
pytest -m performance --benchmark-save=baseline
pytest -m performance --benchmark-compare=baseline
```

## Mock Testing Strategies

### External Service Mocking
```python
import pytest
from unittest.mock import patch, AsyncMock
import httpx

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for external API calls."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        # Configure default responses
        mock_instance.get.return_value.status_code = 200
        mock_instance.get.return_value.json.return_value = {"status": "healthy"}
        mock_instance.post.return_value.status_code = 200
        mock_instance.post.return_value.json.return_value = {"result": "success"}
        
        yield mock_instance

@pytest.mark.asyncio
async def test_a2a_client_with_mocked_http(mock_http_client):
    """Test A2A client with mocked HTTP responses."""
    from polyhegel.clients.a2a_client import PolyhegelA2AClient, A2AAgentEndpoints
    
    endpoints = A2AAgentEndpoints()
    async with PolyhegelA2AClient(endpoints) as client:
        availability = await client.verify_agent_availability()
        
        # Assert based on mocked responses
        assert all(available for available in availability.values())
```

### Database and File System Mocking
```python
import pytest
from unittest.mock import patch, mock_open
import json

@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    file_contents = {
        "/path/to/config.json": json.dumps({"model": "claude-3-haiku", "timeout": 30}),
        "/path/to/strategies.json": json.dumps([{"title": "Test Strategy", "steps": []}])
    }
    
    def mock_open_func(filename, mode='r'):
        if filename in file_contents:
            return mock_open(read_data=file_contents[filename]).return_value
        else:
            raise FileNotFoundError(f"No such file: {filename}")
    
    with patch('builtins.open', side_effect=mock_open_func):
        with patch('pathlib.Path.exists', return_value=True):
            yield
```

This comprehensive testing guide ensures that the Polyhegel system maintains high quality and reliability across all components and use cases.