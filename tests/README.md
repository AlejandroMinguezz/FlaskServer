# DirectIA Tests

This directory contains the test suite for the DirectIA Flask Server.

## Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_classifier.py    # Classifier tests
│   ├── test_ocr.py           # OCR tests
│   ├── test_pipeline.py      # Pipeline tests
│   └── test_utils.py         # Utility function tests
├── integration/          # Integration tests (require services)
│   └── test_api.py           # API endpoint tests
├── fixtures/             # Test fixtures and sample data
└── test_data/            # Temporary test data directory
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/unit/test_classifier.py
```

### Run Specific Test Class
```bash
pytest tests/unit/test_classifier.py::TestKeywordClassifier
```

### Run Specific Test
```bash
pytest tests/unit/test_classifier.py::TestKeywordClassifier::test_classify_factura
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

### Unit Tests
- **Fast** (< 1 second per test)
- **Isolated** (no external dependencies)
- Test individual functions and classes
- Mock external services

### Integration Tests
- **Slower** (may take several seconds)
- **Require services** (Flask app, databases)
- Test complete workflows
- Test API endpoints

## Writing Tests

### Basic Test Structure
```python
import pytest

def test_something():
    # Arrange
    input_data = "test"

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_output
```

### Using Fixtures
```python
def test_with_fixture(classifier):
    result = classifier.classify_text("test")
    assert 'tipo_documento' in result
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("FACTURA", "factura"),
    ("NÓMINA", "nomina"),
    ("CONTRATO", "contrato"),
])
def test_multiple_cases(input, expected, classifier):
    result = classifier.classify_text(input)
    assert result['tipo_documento'] == expected
```

## Test Requirements

Some tests require specific setup:

### ML Model Tests
- Requires trained model at `src/ia/models/tfidf_svm_v1/`
- Run: `python -m src.ia.training.train_model`
- Mark with: `@pytest.mark.requires_model`

### OCR Tests
- Requires Tesseract OCR installed
- Mark with: `@pytest.mark.requires_tesseract`

### Database Tests
- Requires PostgreSQL and MongoDB running
- Use Docker: `./start_databases.sh`
- Mark with: `@pytest.mark.requires_db`

## Continuous Integration

Tests can be run automatically on CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=src --cov-report=xml
```

## Troubleshooting

### ImportError: No module named 'src'
Make sure you're running pytest from the project root directory.

### Tests failing with "Model not found"
Train the ML model first:
```bash
python -m src.ia.training.train_model
```

### Tests timing out
Increase timeout in `pytest.ini` or skip slow tests:
```bash
pytest -m "not slow"
```

### Database connection errors
Make sure databases are running:
```bash
./start_databases.sh
```

## Coverage Goals

- **Overall**: > 80%
- **Core modules** (classifier, pipeline, OCR): > 90%
- **API routes**: > 70%
- **Utilities**: > 85%

## Best Practices

1. **Keep tests fast**: Unit tests should run in < 1 second
2. **Keep tests isolated**: Don't depend on other tests
3. **Use descriptive names**: `test_classify_factura_returns_correct_type`
4. **One assertion per test**: When possible
5. **Clean up resources**: Use fixtures with cleanup
6. **Mock external services**: Don't hit real APIs in tests
7. **Test edge cases**: Empty inputs, large files, special characters
8. **Document complex tests**: Add docstrings explaining what's being tested

## Adding New Tests

1. Determine if test is unit or integration
2. Create test file in appropriate directory
3. Write test following AAA pattern (Arrange, Act, Assert)
4. Add appropriate markers
5. Run test to verify it passes
6. Add to CI pipeline if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing Best Practices](https://realpython.com/pytest-python-testing/)
