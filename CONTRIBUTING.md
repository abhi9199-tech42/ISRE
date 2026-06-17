# Contributing to ISRE

Thank you for your interest in contributing to the Intentional Semantic Reasoning Engine!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/ISRE.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -e ".[test]"`

## Development Workflow

### Code Style
- Use Python 3.10+ type hints
- Follow PEP 8 (enforced by ruff)
- Maximum line length: 100 characters

### Testing
- Write tests for new features
- Run tests: `pytest tests/`
- Maintain minimum 80% code coverage

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb in imperative mood
- Example: "Add semantic coherence scoring"

### Pull Request Process
1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit a pull request

## Architecture Guidelines

### Layer Separation
- **Compression Layer**: Only handles input processing
- **Graph Layer**: Only builds intent graphs
- **Reasoning Layer**: Only performs reasoning
- **Knowledge Layer**: Only integrates external knowledge
- **Reconstruction Layer**: Only generates output

### Adding New Components
1. Create an abstract base class (ABC) if needed
2. Implement the interface
3. Register with the appropriate processor
4. Add comprehensive tests

## Reporting Issues

- Use GitHub Issues
- Include minimal reproduction steps
- Specify Python version and OS
- Include error messages and stack traces

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.
