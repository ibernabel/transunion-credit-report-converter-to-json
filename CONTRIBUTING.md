# Contributing to TransUnion PDF to JSON

We love your input! We want to make contributing to TransUnion PDF to JSON as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Improving documentation
- Becoming a maintainer

## 🤝 We Develop with GitHub

We use GitHub to host code, track issues and feature requests, and accept pull requests.

## 📋 We Use [GitHub Flow](https://guides.github.com/introduction/flow/index.html)

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. **Fork** the repo and create your branch from `main`
2. If you've **added code**, add tests
3. If you've **changed APIs**, update the documentation
4. Ensure the **test suite passes**
5. Make sure your code **lints** (ruff, black, mypy)
6. **Issue that pull request!**

## 🛠️ Development Process

### 1. Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/transunion-pdf-to-json.git
cd transunion-pdf-to-json

# Create virtual environment (Python 3.12+ required)
python3.12 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 2. Make Your Changes

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Add tests for your changes
# ... create test files in tests/ ...
```

### 3. Test Your Changes

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
# Or: xdg-open htmlcov/index.html  # On Linux
```

### 4. Lint and Format Code

```bash
# Check code style with ruff
ruff check src/

# Format code with black
black src/

# Type check with mypy
mypy src/
```

### 5. Commit and Push

```bash
# Stage your changes
git add .

# Commit with conventional commit message
git commit -m "feat: add amazing feature"
# Or: fix:, docs:, refactor:, test:, chore:

# Push to your fork
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Provide a clear description of your changes
5. Link any related issues

## 📝 Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring (no functional changes)
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**

```
feat: add multi-currency support for EUR
fix: correct date parsing in personal data extraction
docs: update API usage examples in README
refactor: simplify PII scrubbing logic
test: add tests for account detail parsing
```

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names: `test_parse_personal_data_with_missing_fields`
- Include both positive and negative test cases

### Example Test

```python
import pytest
from src.parser.engine import ParserEngine

def test_parse_credit_score():
    """Test credit score extraction from report text."""
    text_sample = "SCORE: 750\nFactors: Payment history"
    parser = ParserEngine(text_sample)
    score = parser.parse_score()

    assert score.score == 750
    assert len(score.factors) > 0
```

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_parse_credit_score

# Run tests matching pattern
pytest -k "parse"
```

## 🎨 Code Style Guidelines

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Maximum line length: **100 characters**
- Use **type hints** for function parameters and returns
- Write **docstrings** for all public functions and classes

### Docstring Format

```python
def parse_credit_report(text: str) -> CreditReport:
    """
    Parse credit report text into structured data.

    Args:
        text: Raw text extracted from PDF

    Returns:
        CreditReport: Parsed and validated credit report data

    Raises:
        ValidationError: If text format is invalid
    """
    # Implementation
```

### Import Organization

```python
# Standard library imports
import os
from pathlib import Path

# Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# Local application imports
from src.parser.engine import ParserEngine
from src.models.report import CreditReport
```

## 🐛 Report Bugs Using GitHub Issues

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](../../issues/new).

### Great Bug Reports Include:

- **Quick summary** and/or background
- **Steps to reproduce**
  - Be specific!
  - Provide sample code if possible
- **What you expected** would happen
- **What actually happens**
- **Notes** on why you think this might be happening, or things you tried that didn't work

### Bug Report Template

```markdown
## Bug Description

A clear description of the bug.

## Steps to Reproduce

1. Upload PDF file '...'
2. Call endpoint '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- OS: Ubuntu 22.04
- Python: 3.12
- Docker: Yes/No

## Additional Context

Add any other context about the problem here.
```

## 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use case** - Why is this enhancement needed?
- **Proposed solution** - How should it work?
- **Alternatives considered** - What other approaches did you consider?
- **Additional context** - Screenshots, mockups, or examples

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all contributors, regardless of level of experience, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**

- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission

## 📄 License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.

## 🙏 Recognition

Contributors will be recognized in the project README and release notes.

## ❓ Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

---

## Reference

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/master/CONTRIBUTING.md).

**Thank you for contributing! 🎉**
