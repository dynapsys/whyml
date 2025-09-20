# Contributing to PASVG

Thank you for your interest in contributing to PASVG (Project Artifact SVG)! This document will guide you through the contribution process.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
- Check if the issue has already been reported
- Provide a clear title and description
- Include steps to reproduce
- Describe the expected vs. actual behavior
- Include screenshots if applicable

### Suggesting Enhancements
- Explain the feature/improvement
- Describe why it would be useful
- Provide examples of the proposed changes

### Development
- Fix bugs
- Implement new features
- Improve documentation
- Write tests
- Improve performance

## Development Workflow

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/pasvg.git
   cd pasvg
   ```
3. **Set up** the development environment:
   ```bash
   make install-dev
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes**
6. **Run tests** to ensure everything works:
   ```bash
   make test
   make lint
   ```
7. **Commit** your changes with a descriptive message:
   ```bash
   git commit -m "Your detailed description of changes"
   ```
8. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Open a Pull Request**

## Pull Request Process

1. Ensure your PR has a clear description of the problem and solution
2. Include tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass
5. Request review from project maintainers

## Code Style

We use the following tools to maintain code quality:

```bash
# Run linters
make lint

# Format code
make format
```

## Testing

All contributions must include appropriate tests:

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Validate example files
make validate
```

## Reporting Issues

When reporting issues, please include:
- PASVG version
- Python version
- Steps to reproduce
- Expected vs. actual behavior
- Any relevant error messages

## Feature Requests

For feature requests, please:
1. Describe the feature
2. Explain the use case
3. Suggest implementation details if possible

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.

---
*Thank you for contributing to PASVG!* 🚀
