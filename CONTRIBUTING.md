# Contributing to Pydantic AI Democratic Swarm

Thank you for your interest in contributing to the Pydantic AI Democratic Swarm! This document provides guidelines and information for contributors.

## 🏗️ Development Setup

### Prerequisites
- Python 3.9+
- Git
- A GitHub account

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/pydantic-ai-democratic-swarm.git
cd pydantic-ai-democratic-swarm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/
```

## 📋 Development Workflow

### 1. Choose an Issue
- Check the [Issues](../../issues) page for tasks to work on
- Comment on the issue to indicate you're working on it
- Create a feature branch from `main`

### 2. Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Ensure tests pass
pytest tests/

# Format code
black src/
isort src/

# Type check
mypy src/

# Lint
ruff check src/
```

### 3. Testing
- Write tests for new functionality
- Ensure all existing tests pass
- Add integration tests for complex features
- Test edge cases and error conditions

### 4. Documentation
- Update docstrings for public APIs
- Add examples for new features
- Update README if needed
- Ensure documentation builds

### 5. Commit and Push
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add amazing new feature

- Description of changes
- Breaking changes (if any)
- Related issues"

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request
- Go to the repository on GitHub
- Click "New Pull Request"
- Select your feature branch
- Fill out the pull request template
- Request review from maintainers

## 🎯 Code Standards

### Python Style
- Follow PEP 8
- Use type hints for all function parameters and return values
- Write descriptive variable and function names
- Keep functions small and focused

### Documentation
- Use Google-style docstrings
- Document all public APIs
- Include examples in docstrings where helpful
- Keep README and docs up to date

### Testing
- Write unit tests for all new code
- Aim for 80%+ code coverage
- Test edge cases and error conditions
- Use descriptive test names

### Commit Messages
- Use conventional commit format
- Start with type: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Keep first line under 50 characters
- Use body for detailed explanations

## 🏗️ Architecture Guidelines

### Agent Design
- Extend `BaseAgent` for new agent types
- Implement required abstract methods
- Follow the confidence-based decision pattern
- Register capabilities with the efficiency enforcer

### Tool Design
- Extend `BaseTool` for new tools
- Declare compatible agents
- Handle errors gracefully
- Include comprehensive validation

### Swarm Integration
- Use the orchestrator for task coordination
- Respect efficiency enforcer decisions
- Implement proper error handling
- Follow democratic consensus patterns

## 🚨 Efficiency Rules

All contributions must follow the [Efficiency Rules](../docs/efficiency-rules.md):

- **No Code Duplication**: Always check for existing functionality first
- **Consensus Required**: Major changes need swarm consensus
- **Documentation Required**: All public APIs must be documented
- **Testing Required**: All code must have adequate test coverage

## 📞 Getting Help

- 📧 **Discussions**: Use [GitHub Discussions](../../discussions) for questions
- 🐛 **Issues**: Report bugs via [GitHub Issues](../../issues)
- 💬 **Discord**: Join our community Discord (link in README)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for contributing to the Pydantic AI Democratic Swarm! 🎉
