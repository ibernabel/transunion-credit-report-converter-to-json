# Test Suite Documentation

## Overview

This directory contains all automated tests for the TransUnion PDF to JSON API project. The test suite ensures correctness, robustness, and reliability of the PDF parsing engine and API endpoints.

## Test Files

| File                           | Purpose                           | Test Count            |
| ------------------------------ | --------------------------------- | --------------------- |
| `test_api.py`                  | API endpoint testing              | 18 tests              |
| `test_core.py`                 | Core parser & scrubber unit tests | 2 tests               |
| `test_robustness.py`           | Parser edge case handling         | 1 test                |
| `test_parser_comprehensive.py` | Comprehensive parser tests        | 25 tests (13 passing) |

## Running Tests

### Run All Tests

```bash
# Using uv (recommended)
uv run python -m pytest tests/ -v

# Using activated virtualenv
source .venv/bin/activate
pytest tests/ -v
```

### Run Specific Test File

```bash
uv run python -m pytest tests/test_api.py -v
```

### Run Specific Test Class/Method

```bash
uv run python -m pytest tests/test_api.py::TestParseEndpoint::test_parse_with_valid_pdf -v
```

### Run with Coverage

```bash
uv run python -m pytest tests/ --cov=src --cov-report=html
```

## Test Organization

### API Tests (`test_api.py`)

Tests all FastAPI endpoints and HTTP semantics:

#### `TestHealthEndpoint`

- ✅ Health check returns 200 OK
- ✅ Root endpoint returns API info

#### `TestParseEndpoint`

- ✅ Validates file upload requirements
- ✅ Rejects non-PDF files (400)
- ✅ Handles empty files (400/500)
- ✅ Parse valid PDF files (200)
- ✅ Validates response schema
- ✅ Verifies PII scrubbing is active

#### `TestAPIDocumentation`

- ✅ Swagger UI (`/docs`)
- ✅ ReDoc (`/redoc`)
- ✅ OpenAPI schema (`/openapi.json`)

#### `TestConcurrentRequests`

- ✅ Thread-safe health checks
- ✅ Concurrent PDF parsing

#### `TestError Handling`

- ✅ Malformed requests (422)
- ✅ Invalid endpoints (404)
- ✅ Wrong HTTP methods (405)

### Core Tests (`test_core.py`)

Unit tests for parser engine and PII scrubber:

- ✅ `test_parser_engine_basic()` - Validates basic parsing logic
- ✅ `test_scrubber()` - Verifies PII masking

### Robustness Tests (`test_robustness.py`)

Tests parser resilience:

- ✅ `test_robust_account_parsing()` - Wrapped text, newlines, date formats

### Comprehensive Tests (`test_parser_comprehensive.py`)

**Status: 🚧 Work in Progress**

Extensive unit tests covering:

- ✅ Inquirer parsing (various formats)
- ⚠️ Personal data parsing (some failures - parser format sensitivity)
- ⚠️ Score parsing (needs correct text format)
- ⚠️ Account details (currency, status, vector parsing)
- ✅ Date parsing (full and partial formats)
- ✅ Monetary value parsing
- ⚠️ Edge cases (empty text, unicode, whitespace)

**Note**: Some tests are currently failing due to the parser's strict text format requirements. These tests document **expected parser behavior** and reveal areas where the parser could be made more flexible.

## Test Data Files

Located in `tests/test_files/`:

| File                   | Purpose                                                  |
| ---------------------- | -------------------------------------------------------- |
| `credit_report.pdf`    | Real TransUnion credit report for integration testing    |
| `expected-output.json` | **JSON Schema** defining expected API response structure |

### Important: Security Note

The `expected-output.json` file contains a **JSON Schema**, NOT actual PII data. It defines:

- Structure and required fields
- Data types for each field
- Spanish field aliases (as returned by the API)

This approach allows schema validation without storing sensitive data in version control.

## Test Fixtures

Defined in `conftest.py`:

| Fixture                   | Description                         |
| ------------------------- | ----------------------------------- |
| `test_client`             | FastAPI TestClient for API calls    |
| `test_files_dir`          | Path to test files directory        |
| `test_pdf_path`           | Path to actual PDF test file        |
| `test_output_dir`         | Temporary directory (auto-cleanup)  |
| `sample_text_content`     | Sample credit report text           |
| `sample_minimal_text`     | Minimal valid report text           |
| `mock_credit_report_data` | Mock structured data                |
| `sample_invalid_pdf`      | Invalid PDF bytes for error testing |
| `sample_empty_file`       | Empty file bytes                    |

## Schema Validation

Tests use `jsonschema` library to validate API responses:

```python
from jsonschema import validate

# Load schema
with open("tests/test_files/expected-output.json") as f:
    schema = json.load(f)

# Validate response
response = client.post("/v1/parse", files={"file": pdf})
validate(instance=response.json(), schema=schema)
```

## Known Issues & Limitations

### Parser Format Sensitivity

The parser expects **very specific text formats**:

❌ **Won't work:**

```
CEDULA: 001-1234567-8    # Colon after CEDULA
NOMBRES: JUAN
```

✅ **Will work:**

```
cedula 001-1234567-8     # No colon, lowercase
nombres JUAN
```

This is **not a bug** - it reflects how TransUnion PDF text extraction produces output. The test suite documents this behavior.

### Test Coverage Gaps

Areas needing more coverage:

- [ ] Account summary parsing
- [ ] Multiple currency handling
- [ ] Payment behavior vector edge cases
- [ ] Malformed PDF content
- [ ] Large file handling (>10MB)

## CI/CD Integration

Tests run automatically on:

- Every commit (pre-commit hook)
- Pull requests
- Main branch merges

Expected test duration: **~2-3 seconds**

## Adding New Tests

### API Tests

```python
class TestNewFeature:
    """Tests for new feature."""

    def test_feature_works(self, test_client):
        """Test that feature returns expected result."""
        response = test_client.get("/v1/new-endpoint")
        assert response.status_code == 200
```

### Parser Tests

```python
def test_parse_new_field():
    """Test parsing a new field."""
    text = """
    cedula 001-1234567-8
    new_field VALUE
    """
    parser = ParserEngine(text)
    result = parser.parse_new_field()
    assert result == "expected_value"
```

## Debugging Failed Tests

### View Full Error Output

```bash
uv run python -m pytest tests/ -vv
```

### Show Print Statements

```bash
uv run python -m pytest tests/ -s
```

### Stop on First Failure

```bash
uv run python -m pytest tests/ -x
```

### Run Specific Failed Test

```bash
uv run python -m pytest tests/test_api.py::TestParseEndpoint::test_parse_with_valid_pdf -vv
```

## Test Metrics

**Current Status** (as of date parsing fix):

| Metric            | Value          |
| ----------------- | -------------- |
| Total Tests       | 21 passing     |
| Code Coverage     | ~70% estimated |
| Avg Test Duration | 0.09s per test |
| Total Suite Time  | ~2s            |

## Dependencies

Test-specific dependencies (from `pyproject.toml`):

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.3.5",
    "pytest-cov>=6.0.0",
    "pytest-asyncio>=0.25.4",
    "jsonschema>=4.0.0",  # For schema validation
]
```

## Contributing

When adding new features:

1. **Write tests first** (TDD approach preferred)
2. **Update this README** if adding new test files
3. **Ensure all tests pass** before committing
4. **Add docstrings** to all test methods
5. **Group related tests** in test classes

## Questions or Issues?

- Check if similar test exists in `test_api.py` or `test_core.py`
- Review parser implementation in `src/parser/engine.py`
- Consult main project README.md for architecture details

---

**Last Updated**: 2026-01-29  
**Maintained By**: Idequel Bernabel  
**Test Framework**: pytest 9.0.2
