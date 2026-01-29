# Testing Guide - TransUnion PDF to JSON API

Comprehensive guide for running and writing tests for the TransUnion parser.

---

## Test Suite Overview

The test suite provides comprehensive coverage for:

- ✅ **API Endpoints** - Health checks, parsing, error handling
- ✅ **Parser Engine** - Text extraction and data parsing
- ✅ **PII Scrubber** - Data privacy and masking
- ✅ **Concurrent Requests** - Load and stress testing
- ✅ **Edge Cases** - Error scenarios and validation

---

## Running Tests

### Prerequisites

```bash
# Install package with dev dependencies
pip install -e ".[dev]"

# Or install test dependencies separately
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with short traceback
pytest -v --tb=short
```

### Run Specific Tests

```bash
# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestHealthEndpoint

# Run specific test method
pytest tests/test_api.py::TestHealthEndpoint::test_health_check

# Run tests matching pattern
pytest -k "health"
pytest -k "parse"
```

### Run with Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Test Files

### `conftest.py`

**Shared test fixtures and configuration**

Fixtures available:

- `test_client` - FastAPI test client
- `test_files_dir` - Path to test files directory
- `test_pdf_path` - Path to test PDF file
- `test_output_dir` - Temporary output directory
- `sample_text_content` - Sample credit report text
- `sample_minimal_text` - Minimal valid text
- `mock_credit_report_data` - Mock report data dict
- `sample_invalid_pdf` - Invalid PDF content
- `sample_empty_file` - Empty file content

### `test_api.py`

**API endpoint tests**

Test classes:

- `TestHealthEndpoint` - Health check and root endpoint
- `TestParseEndpoint` - PDF parsing endpoint
- `TestAPIDocumentation` - Swagger/ReDoc availability
- `TestConcurrentRequests` - Concurrent request handling
- `TestErrorHandling` - Error scenarios and edge cases

### `test_core.py`

**Core parser and scrubber tests**

Tests:

- `test_parser_engine_basic` - Parser functionality
- `test_scrubber` - PII scrubbing

### `test_robustness.py`

**Robustness and edge case tests**

Tests for parser resilience with malformed input.

---

## Writing Tests

### Test Structure

```python
import pytest

class TestMyFeature:
    """Tests for my feature."""

    def test_basic_functionality(self, test_client):
        """Test basic feature functionality."""
        # Arrange
        data = {"key": "value"}

        # Act
        response = test_client.post("/endpoint", json=data)

        # Assert
        assert response.status_code == 200
        assert response.json()["result"] == "expected"
```

### Using Fixtures

```python
def test_with_sample_data(sample_text_content):
    """Test using sample text fixture."""
    from src.parser.engine import ParserEngine

    parser = ParserEngine(sample_text_content)
    result = parser.parse_inquirer()

    assert result.subscriber == "banco popular dominicano"
```

### Testing API Endpoints

```python
def test_endpoint(test_client):
    """Test API endpoint."""
    response = test_client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### Testing File Uploads

```python
def test_file_upload(test_client):
    """Test file upload endpoint."""
    files = {
        "file": ("test.pdf", b"content", "application/pdf")
    }
    response = test_client.post("/v1/parse", files=files)

    assert response.status_code in [200, 400, 500]
```

### Testing Error Handling

```python
def test_error_case(test_client):
    """Test error handling."""
    response = test_client.post("/v1/parse")  # Missing file

    assert response.status_code == 422
    assert "detail" in response.json()
```

### Skipping Tests

```python
import os
import pytest

@pytest.mark.skipif(
    not os.path.exists("test_file.pdf"),
    reason="Test file not available"
)
def test_with_file():
    """Test that requires external file."""
    pass
```

---

## Test Coverage Goals

| Component     | Target Coverage | Current Status |
| ------------- | --------------- | -------------- |
| API Routes    | 90%+            | ✅ Ready       |
| Parser Engine | 85%+            | ✅ Ready       |
| PII Scrubber  | 95%+            | ✅ Ready       |
| Models        | 80%+            | ✅ Ready       |
| Utilities     | 75%+            | ✅ Ready       |

---

## Test Data

### Sample Test Files

Create test files in `tests/test_files/`:

```
tests/test_files/
├── test_credit_report.pdf     # Valid credit report PDF
├── test_credit_report.txt     # Valid credit report text
├── invalid.pdf                # Invalid PDF for error testing
└── README.md                  # Description of test files
```

### Creating Test PDF

To create a test PDF from sample text:

```python
import fitz  # PyMuPDF

text = """Sample credit report text..."""
doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), text)
doc.save("tests/test_files/test_credit_report.pdf")
doc.close()
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Troubleshooting

### Common Issues

**Import Errors**

```bash
# Ensure package is installed
pip install -e .

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

**Test Discovery Issues**

```bash
# Verify pytest can find tests
pytest --collect-only

# Check pytest configuration
pytest --version
```

**Fixture Not Found**

```bash
# Ensure conftest.py is in tests/ directory
ls tests/conftest.py

# Check fixture naming
pytest --fixtures
```

**Async Test Failures**

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check async test markers
pytest --markers
```

---

## Best Practices

### Test Naming

- Use descriptive test names: `test_parse_valid_pdf_returns_json`
- Group related tests in classes
- Use docstrings to explain complex tests

### Test Independence

- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### Test Coverage

- Aim for high coverage but focus on critical paths
- Test both success and failure cases
- Include edge cases and boundary conditions

### Performance

- Keep tests fast (< 1 second per test)
- Use mocks for external dependencies
- Skip slow tests in CI with marks

---

## Test Commands Reference

```bash
# Basic test runs
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -x                       # Stop on first failure
pytest --tb=short              # Short traceback

# Test selection
pytest tests/test_api.py        # Run specific file
pytest -k "health"              # Run tests matching pattern
pytest -m "slow"                # Run tests with marker

# Coverage
pytest --cov=src                # Basic coverage
pytest --cov=src --cov-report=html  # HTML report
pytest --cov=src --cov-report=term-missing  # Show missing lines

# Debugging
pytest --pdb                    # Drop into debugger on failure
pytest -s                       # Don't capture output
pytest --lf                     # Run last failed tests
pytest --ff                     # Run failures first

# Parallel execution (requires pytest-xdist)
pytest -n auto                  # Run tests in parallel
```

---

## Next Steps

1. **Add more test files** - Create actual PDF samples
2. **Increase coverage** - Add more edge case tests
3. **Integration tests** - Test full workflows
4. **Performance tests** - Load testing and benchmarks
5. **CI/CD integration** - Automate testing in pipeline

---

**Happy Testing! 🧪**
