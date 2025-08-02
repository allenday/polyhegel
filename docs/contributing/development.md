# Development Guide

## Getting Started

### Development Environment Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/allenday/polyhegel.git
   cd polyhegel
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Run initial tests**:
   ```bash
   make test
   ```

### Development Workflow

#### Branch Strategy
- `main`: Production-ready code
- `dev`: Integration branch for development
- `feature/*`: New features and enhancements
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

#### Making Changes
1. **Create feature branch**:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes**:
   ```bash
   make test          # Run all tests
   make lint          # Check code style
   make typecheck     # Run type checking
   ```

4. **Commit with clear messages**:
   ```bash
   git add .
   git commit -m "feat: add strategic refinement engine
   
   - Implement recursive strategy improvement
   - Add performance tracking and metrics
   - Include convergence detection logic"
   ```

5. **Push and create pull request**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR via GitHub interface
   ```

## Code Standards

### Python Style Guide

#### Code Formatting
- **Black**: Automatic code formatting
- **Line length**: 120 characters maximum
- **Import organization**: Use isort for consistent import ordering

```python
# Good example
from typing import Dict, List, Optional
import logging

from polyhegel.models import StrategyChain
from polyhegel.telemetry import get_telemetry_collector

logger = logging.getLogger(__name__)
```

#### Type Hints
All public functions must include comprehensive type hints:

```python
from typing import Dict, List, Optional, Union
from polyhegel.models import StrategyChain

async def generate_strategies(
    self,
    temperature_counts: List[Tuple[float, int]], 
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
) -> List[StrategyChain]:
    """Generate multiple strategies at different temperatures."""
    # Implementation here
```

#### Documentation Standards
All modules, classes, and public functions require Google-style docstrings:

```python
class StrategyGenerator:
    """Core component for generating strategic solutions using AI models.
    
    This class orchestrates strategy generation through temperature sampling,
    technique application, and quality assessment. It integrates with various
    AI models and provides comprehensive telemetry for monitoring and optimization.
    
    Attributes:
        model_name: Name of the AI model to use for generation.
        techniques: List of strategic techniques to apply.
        telemetry_collector: System for collecting performance metrics.
    
    Example:
        >>> generator = StrategyGenerator("claude-3-haiku-20240307")
        >>> strategies = await generator.generate_strategies(
        ...     temperature_counts=[(0.7, 3)],
        ...     user_prompt="Expand into European markets"
        ... )
    """
    
    def __init__(self, model_name: str, techniques: Optional[List[str]] = None):
        """Initialize the strategy generator.
        
        Args:
            model_name: Name of the AI model to use.
            techniques: Optional list of technique names to apply.
            
        Raises:
            ValueError: If model_name is not supported.
        """
```

### Testing Standards

#### Test Organization
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions  
├── e2e/           # End-to-end workflow tests
└── fixtures/      # Test data and mock objects
```

#### Test Writing Guidelines

```python
import pytest
from unittest.mock import AsyncMock, Mock
from polyhegel.strategy_generator import StrategyGenerator

class TestStrategyGenerator:
    """Test suite for StrategyGenerator class."""
    
    @pytest.fixture
    def mock_model(self):
        """Mock AI model for testing."""
        model = AsyncMock()
        model.generate.return_value = {"content": "Mock strategy response"}
        return model
    
    @pytest.fixture  
    def generator(self, mock_model):
        """Strategy generator instance with mocked dependencies."""
        return StrategyGenerator(model=mock_model)
    
    @pytest.mark.asyncio
    async def test_generate_strategies_success(self, generator):
        """Test successful strategy generation."""
        # Arrange
        temperature_counts = [(0.7, 2)]
        user_prompt = "Test strategy challenge"
        
        # Act
        result = await generator.generate_strategies(
            temperature_counts=temperature_counts,
            user_prompt=user_prompt
        )
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(s, StrategyChain) for s in result)
        assert all(s.temperature == 0.7 for s in result)
    
    @pytest.mark.asyncio
    async def test_generate_strategies_empty_prompt_raises_error(self, generator):
        """Test that empty prompt raises appropriate error."""
        with pytest.raises(ValueError, match="User prompt cannot be empty"):
            await generator.generate_strategies(
                temperature_counts=[(0.7, 1)],
                user_prompt=""
            )
```

#### Test Coverage Requirements
- **Minimum coverage**: 80% overall
- **Critical components**: 95% coverage required
- **New features**: Must include comprehensive tests

```bash
# Check coverage
make coverage

# Generate coverage report
coverage report
coverage html  # Creates htmlcov/ directory
```

## Architecture Guidelines

### Component Design Principles

#### Single Responsibility
Each class and module should have one clear purpose:

```python
# Good: Clear single responsibility
class PerformanceTracker:
    """Tracks and analyzes strategy performance metrics."""
    
    def record_performance(self, strategy: StrategyChain, metrics: StrategicMetrics) -> None:
        """Record performance data for a strategy."""
        
    def get_performance_history(self, strategy_id: str) -> List[PerformanceRecord]:
        """Retrieve historical performance data."""

# Bad: Multiple responsibilities mixed
class StrategyManagerAndPerformanceTrackerAndTelemetryCollector:
    """Does too many things."""
```

#### Dependency Injection
Use dependency injection for testability and flexibility:

```python
class RecursiveRefinementEngine:
    def __init__(
        self,
        performance_tracker: Optional[PerformanceTracker] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        feedback_loop: Optional[FeedbackLoop] = None
    ):
        # Use provided dependencies or create defaults
        self.performance_tracker = performance_tracker or PerformanceTracker()
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.feedback_loop = feedback_loop or FeedbackLoop()
```

#### Error Handling Strategy
Implement comprehensive error handling with proper logging:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class StrategyEvaluationError(Exception):
    """Raised when strategy evaluation fails."""
    pass

async def evaluate_strategy(self, strategy: StrategyChain) -> StrategicMetrics:
    """Evaluate strategy performance with comprehensive error handling."""
    try:
        # Attempt evaluation
        raw_metrics = await self._collect_raw_metrics(strategy)
        processed_metrics = self._process_metrics(raw_metrics)
        
        logger.info(f"Successfully evaluated strategy: {strategy.strategy.title}")
        return processed_metrics
        
    except ModelTimeoutError as e:
        logger.error(f"Model timeout during strategy evaluation: {e}")
        # Return fallback metrics rather than failing completely
        return self._create_fallback_metrics(strategy)
        
    except ValidationError as e:
        logger.error(f"Strategy validation failed: {e}")
        raise StrategyEvaluationError(f"Invalid strategy format: {e}") from e
        
    except Exception as e:
        logger.error(f"Unexpected error during strategy evaluation: {e}")
        # Re-raise with context
        raise StrategyEvaluationError(f"Evaluation failed for strategy {strategy.strategy.title}") from e
```

### Performance Considerations

#### Async/Await Best Practices
```python
import asyncio
from typing import List

# Good: Concurrent execution
async def generate_multiple_strategies(self, prompts: List[str]) -> List[StrategyChain]:
    """Generate strategies concurrently for better performance."""
    tasks = [
        self.generate_single_strategy(prompt) 
        for prompt in prompts
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and log errors
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Strategy generation failed for prompt {i}: {result}")
        else:
            successful_results.append(result)
    
    return successful_results

# Bad: Sequential execution
async def generate_multiple_strategies_slow(self, prompts: List[str]) -> List[StrategyChain]:
    """Generate strategies sequentially (slow)."""
    results = []
    for prompt in prompts:
        strategy = await self.generate_single_strategy(prompt)
        results.append(strategy)
    return results
```

#### Memory Management
```python
from contextlib import asynccontextmanager
import gc

@asynccontextmanager
async def managed_strategy_generation(self):
    """Context manager for memory-efficient strategy generation."""
    try:
        # Initialize resources
        self._initialize_generation_resources()
        yield self
    finally:
        # Clean up resources
        self._cleanup_generation_resources()
        gc.collect()  # Force garbage collection for large operations
```

## Development Tools

### IDE Configuration

#### VS Code Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "120"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.rulers": [120],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

#### PyCharm Settings
- Enable Black formatter in Settings > Tools > External Tools
- Configure pytest as test runner in Settings > Tools > Python Integrated Tools
- Set line length to 120 in Settings > Editor > Code Style > Python

### Debugging Guidelines

#### Logging Configuration
```python
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('polyhegel.log')
    ]
)

# Component-specific loggers
strategy_logger = logging.getLogger('polyhegel.strategy')
refinement_logger = logging.getLogger('polyhegel.refinement')
a2a_logger = logging.getLogger('polyhegel.a2a')
```

#### Debug Mode Features
```python
import os
from polyhegel.config import DEBUG_MODE

if DEBUG_MODE:
    # Enable detailed logging
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Save intermediate results
    SAVE_DEBUG_ARTIFACTS = True
    DEBUG_OUTPUT_DIR = "debug_output"
    
    # Extended timeouts for debugging
    DEFAULT_TIMEOUT = 300  # 5 minutes instead of 30 seconds
```

## Continuous Integration

### GitHub Actions Workflow
The project uses automated CI/CD with the following checks:

1. **Linting and Formatting**:
   ```bash
   make lint          # flake8, black, isort
   make typecheck     # mypy type checking
   ```

2. **Testing**:
   ```bash
   make test          # pytest with coverage
   make test-integration  # integration tests
   ```

3. **Documentation**:
   ```bash
   make docs          # build documentation
   make docs-check    # verify documentation completeness
   ```

### Pre-commit Hooks
Configured hooks run automatically before each commit:
- Black code formatting
- isort import sorting  
- flake8 linting
- mypy type checking
- trailing whitespace removal

## Performance Profiling

### Memory Profiling
```python
from memory_profiler import profile
import psutil
import os

@profile
def memory_intensive_operation():
    """Profile memory usage of strategy generation."""
    # Your code here
    pass

def log_memory_usage(operation_name: str):
    """Log current memory usage."""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    logger.info(f"{operation_name} - Memory usage: {memory_mb:.2f} MB")
```

### Performance Benchmarking
```python
import time
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def benchmark_operation(operation_name: str):
    """Benchmark async operation performance."""
    start_time = time.perf_counter()
    start_memory = psutil.Process().memory_info().rss
    
    try:
        yield
    finally:
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss
        
        duration = end_time - start_time
        memory_delta = (end_memory - start_memory) / 1024 / 1024
        
        logger.info(f"{operation_name} - Duration: {duration:.3f}s, Memory: {memory_delta:+.2f}MB")
```

## Contributing Checklist

Before submitting a pull request, ensure:

- [ ] Code follows style guidelines (black, isort, flake8)
- [ ] All functions have proper type hints
- [ ] Comprehensive docstrings for public APIs
- [ ] Unit tests cover new functionality (>80% coverage)
- [ ] Integration tests for end-to-end workflows
- [ ] Documentation updated for new features
- [ ] Performance impact assessed for critical paths
- [ ] Error handling implemented with proper logging
- [ ] Memory usage considered for large operations
- [ ] Backward compatibility maintained where possible