# Copilot Instructions for Pydantic AI Democratic Swarm

## Project Overview

**Pydantic AI Democratic Swarm** is a revolutionary AI agent orchestration system that democratizes decision-making, prevents code duplication, and ensures efficient development across multiple applications and domains. The system uses democratic voting and consensus mechanisms to coordinate multiple specialized AI agents working together on complex tasks.

### Key Principles
- **Democratic Governance**: All agents vote on decisions with confidence-weighted consensus
- **Efficiency Enforcement**: Automatic prevention of code duplication and redundant functionality
- **Self-Optimization**: The swarm learns and improves its own efficiency over time
- **Multi-Domain Flexibility**: Easily adapts to different applications and problem domains
- **Type Safety**: 100% Pydantic validation throughout

## Architecture

### Directory Structure
```
src/pydantic_ai_swarm/
├── core/              # Core orchestration (orchestrator, base_agent, config)
├── governance/        # Democratic decision making (voting, consensus, confidence)
├── quality/           # Quality assurance (efficiency_enforcer, validation, monitoring)
├── agents/            # Domain-specific agents
├── tools/             # Tool ecosystem (standard tools, integrations)
├── communication/     # Agent communication systems
├── knowledge/         # Knowledge base and learning
├── templates/         # Templates for agents and tasks
└── utils/             # Utility functions

tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── e2e/               # End-to-end tests
└── fixtures/          # Test fixtures
```

## Code Standards

### Python Style Guide
- **Python Version**: 3.9+ (support through 3.12)
- **Style**: Follow PEP 8
- **Formatter**: Black (line length: 88)
- **Import Sorting**: isort with Black profile
- **Type Checking**: mypy with strict settings
- **Linter**: ruff

### Type Hints
- **REQUIRED**: All function parameters and return values must have type annotations
- Use `from typing import` for complex types
- Use Pydantic models for data validation
- Example:
```python
from typing import Dict, Any, Optional
from pydantic import BaseModel

async def execute_task(
    task: str, 
    context: Dict[str, Any], 
    timeout: Optional[float] = None
) -> TaskResult:
    """Execute a task with democratic voting."""
    pass
```

### Documentation
- **Docstring Style**: Google-style docstrings
- **REQUIRED**: All public APIs must have docstrings
- Include examples in docstrings for complex functionality
- Document all parameters, return values, and raised exceptions
- Example:
```python
async def build_consensus(
    self,
    proposal: ConsensusProposal,
    context: Dict[str, Any]
) -> ConsensusResult:
    """Build consensus among agents for a proposal.

    Args:
        proposal: The proposal to vote on with title and options
        context: Additional context for decision making

    Returns:
        ConsensusResult containing the decision and agreement level

    Raises:
        ConsensusError: If consensus cannot be reached

    Example:
        >>> result = await swarm.build_consensus(
        ...     proposal=ConsensusProposal(
        ...         title="Choose deployment",
        ...         options=["blue-green", "canary"]
        ...     ),
        ...     context={"domain": "devops"}
        ... )
    """
    pass
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `PydanticAISwarmOrchestrator`, `BaseAgent`)
- **Functions/Methods**: snake_case (e.g., `execute_task`, `calculate_confidence`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_AGENTS`, `DEFAULT_TIMEOUT`)
- **Private members**: Prefix with underscore (e.g., `_internal_state`)
- **Async functions**: Prefix with `async def` and use descriptive names

### Error Handling
- Use specific exception types
- Always provide meaningful error messages
- Log errors with appropriate levels (error, warning, info, debug)
- Use try/except blocks judiciously
- Example:
```python
from structlog import get_logger

logger = get_logger(__name__)

try:
    result = await agent.execute_task(task, context)
except AgentExecutionError as e:
    logger.error("agent_execution_failed", agent=agent.name, error=str(e))
    raise
```

## Testing Standards

### Test Structure
- **Unit tests**: `tests/unit/` - Test individual components in isolation
- **Integration tests**: `tests/integration/` - Test component interactions
- **End-to-end tests**: `tests/e2e/` - Test full workflows
- Mirror source structure in test directories

### Test Requirements
- Minimum 80% code coverage required
- Test file naming: `test_<module_name>.py`
- Test function naming: `test_<function_name>_<scenario>`
- Use pytest fixtures for common setup
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`

### Test Example
```python
import pytest
from pydantic_ai_swarm import PydanticAISwarmOrchestrator

@pytest.mark.unit
async def test_swarm_initialization_success():
    """Test successful swarm initialization."""
    swarm = PydanticAISwarmOrchestrator("TestSwarm")
    assert swarm.name == "TestSwarm"
    assert swarm.agents == []

@pytest.mark.integration
async def test_task_execution_with_voting():
    """Test task execution with democratic voting."""
    swarm = PydanticAISwarmOrchestrator("TestSwarm")
    await swarm.register_agent(MockAgent("agent1"))
    
    result = await swarm.execute_task("test task", {})
    assert result.success
    assert result.confidence_score > 0.0
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest -m unit

# Run with coverage
pytest tests/ --cov=pydantic_ai_swarm --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_orchestrator.py -v
```

## Build and Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/cbwinslow/pydantic-ai-democratic-swarm.git
cd pydantic-ai-democratic-swarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Code Quality Checks
```bash
# Format code
black src/

# Sort imports
isort src/

# Lint code
ruff check src/

# Type check
mypy src/

# Run all checks before committing
black src/ && isort src/ && ruff check src/ && mypy src/ && pytest tests/
```

### Pre-commit Hooks
This project uses pre-commit hooks to ensure code quality:
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Efficiency Rules & Guardrails

### CRITICAL: Code Reusability First
**NEVER create duplicate files or functions**. This is the most important rule in this codebase.

#### Before Creating ANY New Code
1. **SEARCH**: Use grep/search to find existing similar functionality
2. **ANALYZE**: Check existing agents, tools, and utilities
3. **MODIFY**: Prefer modifying/extending existing files over creating new ones
4. **CONSENSUS**: Get democratic consensus from swarm before creating new files

#### File Creation Rules
- ❌ **NEVER** create a new file if existing functionality exists
- ❌ **NEVER** duplicate existing agent classes or tools
- ❌ **NEVER** create redundant documentation files
- ✅ **ALWAYS** extend existing agents rather than creating new ones
- ✅ **ALWAYS** add to existing tool files rather than creating new ones
- ✅ **ALWAYS** modify existing utilities rather than duplicating

#### Code Modification Rules
- ✅ Modify existing files to add features
- ✅ Extend base classes for specialization
- ✅ Add methods to existing agents
- ❌ Never break existing APIs without deprecation
- ❌ Never modify core functionality without consensus

### Consensus Requirements
Different actions require different consensus levels:
- **Simple Extensions**: 60%+ consensus
- **Documentation Updates**: 70%+ consensus
- **Configuration Changes**: 75%+ consensus
- **File Creation**: 80%+ consensus
- **Agent Creation**: 90%+ consensus
- **Core Modifications**: 95%+ consensus

## Democratic Governance Patterns

### Agent Design Pattern
Agents must calculate confidence scores for all tasks:
```python
from pydantic_ai_swarm.core.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    """Custom agent for specific domain."""
    
    async def execute_task(
        self, 
        task: str, 
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute task with confidence calculation."""
        # Calculate confidence first
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < 0.7:
            return TaskResult(
                success=False, 
                error="Low confidence",
                confidence_score=confidence
            )
        
        # Execute with high confidence
        result = await self._perform_task(task, context)
        return TaskResult(
            success=True,
            data=result,
            confidence_score=confidence
        )
```

### Voting Pattern
Use voting for task assignment:
```python
from pydantic_ai_swarm.governance.voting import VotingMethod

swarm = PydanticAISwarmOrchestrator(
    "DemocraticSwarm",
    voting_method=VotingMethod.WEIGHTED,  # Confidence-weighted
    consensus_threshold=0.66
)
```

### Consensus Building Pattern
Use consensus for critical decisions:
```python
consensus = await swarm.build_consensus(
    proposal_title="Choose architecture",
    proposal_description="Select system architecture",
    options=["microservices", "monolith", "hybrid"],
    context={"domain": "system_design"}
)

if consensus.consensus_reached:
    selected = consensus.chosen_option
```

## Common Patterns

### Pydantic Models
Always use Pydantic for data validation:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class TaskRequest(BaseModel):
    """Request for task execution."""
    task_description: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    timeout: Optional[float] = Field(default=None, gt=0)
```

### Async Operations
All I/O operations must be async:
```python
async def register_agent(self, agent: BaseAgent) -> None:
    """Register an agent with the swarm."""
    # Validate agent
    await self._validate_agent(agent)
    
    # Check for duplicates
    if await self._agent_exists(agent.name):
        raise AgentAlreadyExistsError(f"Agent {agent.name} already registered")
    
    # Register
    self.agents.append(agent)
    await self._notify_agents(f"New agent registered: {agent.name}")
```

### Logging
Use structlog for structured logging:
```python
from structlog import get_logger

logger = get_logger(__name__)

# Good logging
logger.info(
    "task_executed",
    task_id=task.id,
    agent=agent.name,
    duration=duration,
    success=result.success
)

# Include context
logger.error(
    "consensus_failed",
    proposal=proposal.title,
    votes_for=votes_for,
    votes_against=votes_against,
    threshold=threshold
)
```

## Tools and Integrations

### Adding New Tools
Extend `RobustTool` for new functionality:
```python
from pydantic_ai_swarm.tools.robust_tool import RobustTool, ToolResult

class CustomTool(RobustTool):
    """Custom tool for specific operations."""
    
    def __init__(self, name: str = "custom_tool", description: str = "Performs custom operations"):
        """Initialize custom tool."""
        super().__init__(name, description)
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute tool functionality."""
        # Validate parameters
        validated = self._validate_parameters(parameters)
        
        # Execute
        result = await self._perform_operation(validated)
        
        return ToolResult(success=True, data=result)
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["custom_agent", "general_agent"]
```

## Dependencies

### Core Dependencies
- `pydantic>=2.0.0` - Data validation
- `openai>=1.0.0` - AI model integration
- `asyncio-mqtt>=0.16.0` - MQTT for agent communication
- `redis>=5.0.0` - Distributed state management
- `aioredis>=2.0.0` - Async Redis client
- `python-dotenv>=1.0.0` - Environment variable management
- `structlog>=23.0.0` - Structured logging
- `rich>=13.0.0` - Terminal output
- `click>=8.0.0` - CLI interface
- `pyyaml>=6.0` - YAML configuration

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.0.0` - Test coverage
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `mypy>=1.0.0` - Type checking
- `ruff>=0.1.0` - Linting
- `pre-commit>=3.0.0` - Pre-commit hooks
- `sphinx>=7.0.0` - Documentation
- `sphinx-rtd-theme>=1.3.0` - Documentation theme

## Performance Considerations

### Async Best Practices
- Use `asyncio.gather()` for parallel operations
- Avoid blocking operations in async functions
- Use connection pools for databases and external services
- Set appropriate timeouts for all I/O operations

### Resource Management
- Use context managers for resource cleanup
- Implement proper connection pooling
- Monitor memory usage in long-running agents
- Clean up completed tasks from queues

## Security

### API Keys and Secrets
- Never hardcode API keys or secrets
- Use environment variables via `python-dotenv`
- Store secrets in `.env` file (gitignored)
- Use secure credential management in production

### Input Validation
- Always validate inputs with Pydantic
- Sanitize user-provided data
- Implement rate limiting for external APIs
- Use type hints to prevent type confusion

## Contributing

### Commit Message Format
Follow conventional commits:
```
feat: Add new consensus algorithm
fix: Resolve voting calculation bug
docs: Update agent development guide
test: Add integration tests for orchestrator
refactor: Simplify agent registration flow
```

### Pull Request Process
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make minimal, focused changes
4. Add tests for new functionality
5. Ensure all tests pass and code is formatted
6. Update documentation if needed
7. Submit pull request with clear description

### Code Review Standards
- All PRs require passing CI checks
- Code coverage must not decrease
- Documentation must be updated
- Breaking changes must be clearly documented

## Additional Resources

- **README.md**: Project overview and quick start
- **CONTRIBUTING.md**: Detailed contribution guidelines
- **docs/efficiency-rules.md**: Comprehensive efficiency guardrails
- **docs/governance-system.md**: Democratic voting and consensus details
- **examples/**: Usage examples for different domains

## Quick Reference

### Most Common Commands
```bash
# Install dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Format and lint
black src/ && isort src/ && ruff check src/

# Type check
mypy src/

# Run example
python examples/content_creation.py
```

### Most Common Imports
```python
# Core
from pydantic_ai_swarm import (
    PydanticAISwarmOrchestrator,
    BaseAgent,
    TaskResult,
)

# Governance
from pydantic_ai_swarm.governance.voting import VotingMethod, VotingSystem
from pydantic_ai_swarm.governance.consensus import ConsensusAlgorithm

# Quality
from pydantic_ai_swarm.quality.efficiency_enforcer import EfficiencyEnforcer
```

---

**Remember**: This is a democratic system where efficiency and code reuse are paramount. Always search for existing solutions before creating new code, and ensure your contributions follow the established patterns and standards.
