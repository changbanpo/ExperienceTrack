# Contributing to exprule

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository and clone it locally
2. Install dependencies with `poetry install`
3. Create a new branch for your feature/bugfix

## Development Workflow

1. Make your changes
2. Add tests for any new functionality
3. Run tests with `poetry run pytest`
4. Format code with `poetry run black .` and `poetry run isort .`
5. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small and focused

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=exprule
```
